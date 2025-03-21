"""
Authentication Module for Mesh SDK

This module handles authentication with the Mesh backend API.
"""

import os
import sys
import time
import json
import logging
import webbrowser
import urllib.parse
import requests
import random
import socket
import http.server
import socketserver
import threading
from typing import Dict, Any, Optional, Tuple, List, Union

# Import token manager functions
from .token_manager import store_token, get_token, is_token_valid, clear_token

# Import configuration
from .config import (
    get_config, 
    get_auth_config_endpoint, 
    get_auth_url_endpoint, 
    get_token_exchange_endpoint,
    get_token_refresh_endpoint
)

# Configure logging
logger = logging.getLogger("mesh.auth")

# Set debug level if DEBUG environment variable is set
if os.environ.get("DEBUG", "").lower() in ('true', '1', 'yes'):
    logger.setLevel(logging.DEBUG)
    # Add a handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

# Auth0 configuration cache
AUTH0_CONFIG_CACHE = {}

def is_authenticated() -> bool:
    """Check if the user is authenticated with a valid token.
    
    Returns:
        bool: True if a valid token exists, False otherwise
    """
    logger.debug("Checking authentication status")
    token_data = get_token()
    
    if token_data is None:
        logger.debug("\u2717 No token data found")
        return False
        
    is_valid = is_token_valid(token_data)
    if is_valid:
        logger.debug("\u2713 Valid authentication token found")
        # Log partial token for debugging
        if "access_token" in token_data:
            token = token_data["access_token"]
            logger.debug(f"Token: {token[:5]}...{token[-5:] if len(token) > 10 else ''}")
    else:
        logger.debug("\u2717 Token found but is invalid or expired")
        
    return is_valid

def get_auth0_config(is_device_flow=False) -> Dict[str, str]:
    """
    Get Auth0 configuration from the backend.
    
    Args:
        is_device_flow: If True, request the device flow client ID
    
    Returns:
        Dict[str, str]: Auth0 configuration including domain, client_id, and audience
    """
    global AUTH0_CONFIG_CACHE
    
    # Use a cache key that includes the flow type
    cache_key = "device" if is_device_flow else "default"
    
    # Return cached config if available and not empty
    if cache_key in AUTH0_CONFIG_CACHE and all(AUTH0_CONFIG_CACHE[cache_key].values()):
        return AUTH0_CONFIG_CACHE[cache_key]
    
    try:
        # Fetch Auth0 configuration from the backend, specifying device flow if needed
        url = get_auth_config_endpoint()
        if is_device_flow:
            url = f"{url}?flow=device"
            
        logger.debug(f"Fetching Auth0 configuration from {url}")
        response = requests.get(url)
        response.raise_for_status()
        
        config = response.json()
        if config and "domain" in config and "client_id" in config:
            # Update cache
            if not isinstance(AUTH0_CONFIG_CACHE, dict):
                AUTH0_CONFIG_CACHE = {}
            AUTH0_CONFIG_CACHE[cache_key] = config
            return config
        else:
            logger.error("Invalid Auth0 configuration received from backend")
            return {}
    except Exception as e:
        logger.error(f"Failed to fetch Auth0 configuration from backend: {str(e)}")
        return {}

def _find_available_port(start_port=8000, end_port=9000):
    """Find an available port within a range."""
    for port in range(start_port, end_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    return None

def authenticate(headless=False) -> Dict[str, Any]:
    """
    Authenticate with the Mesh backend.
    
    This function handles the authentication flow:
    1. First checks for an existing valid token in secure storage
    2. If token exists but is expired, tries to refresh it
    3. Otherwise, initiates browser-based auth, falling back to device flow if needed
    
    Args:
        headless: If True, use device code flow instead of browser-based auth
        
    Returns:
        dict: Token data if authentication successful, None otherwise
    """
    logger.debug(f"Starting authentication process (headless={headless})")
    
    # Check if we already have a valid token
    logger.debug("Checking for existing token")
    token_data = get_token()
    
    if token_data is None:
        logger.debug("\u2717 No existing token found")
    else:
        logger.debug("\u2713 Found existing token")
        # Log token details for debugging
        if "access_token" in token_data:
            token = token_data["access_token"]
            logger.debug(f"Token: {token[:5]}...{token[-5:] if len(token) > 10 else ''}")
        if "expires_at" in token_data:
            import datetime
            expires = datetime.datetime.fromtimestamp(token_data["expires_at"])
            logger.debug(f"Token expires at: {expires}")
        if "refresh_token" in token_data:
            logger.debug("Refresh token is available")
        else:
            logger.debug("\u2717 No refresh token available")
    
    # If token exists but is invalid, try to refresh it first
    if token_data and not is_token_valid(token_data):
        logger.info("Token exists but is invalid or expired, attempting to refresh")
        try:
            # Try refreshing the token using the backend endpoint
            refresh_token = token_data.get("refresh_token")
            if refresh_token:
                logger.debug(f"Attempting to refresh token using refresh_token: {refresh_token[:5]}...{refresh_token[-5:] if len(refresh_token) > 10 else ''}")
                refreshed_token = refresh_auth_token(refresh_token=refresh_token)
                
                if refreshed_token and is_token_valid(refreshed_token):
                    logger.info("\u2713 Successfully refreshed token")
                    # Log new token details
                    if "access_token" in refreshed_token:
                        new_token = refreshed_token["access_token"]
                        logger.debug(f"New token: {new_token[:5]}...{new_token[-5:] if len(new_token) > 10 else ''}")
                        
                        # Call profile endpoint to ensure user exists in the database
                        try:
                            config = get_config()
                            base_url = config.get("endpoint", "https://api.getmesh.ai")
                            profile_url = f"{base_url}/auth/profile"
                            
                            logger.debug(f"Calling profile endpoint after token refresh: {profile_url}")
                            profile_response = requests.get(
                                profile_url,
                                headers={"Authorization": f"Bearer {new_token}"}
                            )
                            
                            if profile_response.status_code == 200:
                                logger.debug("\u2713 Profile endpoint called successfully after refresh")
                            else:
                                logger.warning(f"\u2717 Failed to call profile endpoint after refresh: {profile_response.status_code}")
                        except Exception as e:
                            logger.warning(f"Error calling profile endpoint after refresh: {str(e)}")
                            
                    return refreshed_token
                else:
                    logger.info("\u2717 Token refresh failed, will proceed with new authentication")
            else:
                logger.debug("\u2717 No refresh token available, cannot refresh")
        except Exception as e:
            logger.warning(f"\u2717 Error during token refresh: {str(e)}")
            logger.debug(f"Exception type: {type(e).__name__}")
    elif token_data and is_token_valid(token_data):
        logger.info("\u2713 Using existing valid token")
        
        # Call profile endpoint to ensure user exists in the database
        try:
            config = get_config()
            base_url = config.get("endpoint", "https://api.getmesh.ai")
            profile_url = f"{base_url}/auth/profile"
            
            logger.debug(f"Calling profile endpoint to ensure user exists: {profile_url}")
            response = requests.get(
                profile_url,
                headers={"Authorization": f"Bearer {token_data['access_token']}"}
            )
            
            if response.status_code == 200:
                logger.debug("\u2713 Profile endpoint called successfully")
            else:
                logger.warning(f"\u2717 Failed to call profile endpoint: {response.status_code}")
        except Exception as e:
            logger.warning(f"Error calling profile endpoint: {str(e)}")
            
        return token_data
    
    # Detect if we're in a headless or notebook environment
    if not headless:
        # Check for notebook environment
        try:
            from IPython import get_ipython
            if get_ipython() is not None:
                logger.info("Detected Jupyter/IPython environment")
                headless = True
        except ImportError:
            pass

    # If explicitly headless or in notebook, use device flow
    if headless:
        return authenticate_device_flow()
    
    # Try browser-based authentication first
    try:
        logger.info("Attempting browser-based authentication")
        token_data = authenticate_with_browser()
        if token_data:
            return token_data
    except Exception as e:
        logger.warning(f"Browser-based authentication failed: {str(e)}. Falling back to device flow.")
    
    # If browser auth failed or unavailable, fall back to device flow
    logger.info("Falling back to device code flow")
    return authenticate_device_flow()

def authenticate_with_browser() -> Dict[str, Any]:
    """
    Authenticate using a browser-based flow with a temporary local HTTP server.
    
    This method:
    1. Finds an available port for the callback server
    2. Gets an auth URL from the backend
    3. Opens the browser for the user to authenticate
    4. Captures the authorization code from the callback
    5. Exchanges the code for tokens via the backend
    
    Returns:
        dict: Token data if authentication successful, None otherwise
    """
    # Find an available port for the callback server
    callback_port = _find_available_port()
    if not callback_port:
        logger.error("Could not find an available port for the callback server")
        return None
    
    logger.info(f"Using port {callback_port} for authentication callback")
    callback_uri = f"http://localhost:{callback_port}/callback"
    auth_code = {}
    
    # Define handler for the callback
    class CallbackHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)
            if "code" in qs:
                auth_code["code"] = qs["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Authentication successful. You may close this window.</h1></body></html>")
            else:
                self.send_response(400)
                self.end_headers()
        def log_message(self, format, *args):
            return  # Suppress log messages
    
    # Try to set up the callback server
    try:
        # Create a server with a random port that's available
        with socketserver.TCPServer(("", callback_port), CallbackHandler) as httpd:
            server_thread = threading.Thread(target=httpd.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            # Generate a state value for CSRF protection
            state = f"mesh_auth_{int(time.time())}_{random.randint(1000, 9999)}"
            
            # Request an auth URL from the backend
            auth_url_data = {
                "redirect_uri": callback_uri,
                "scope": "openid profile email offline_access",
                "state": state
            }
            
            logger.info(f"Requesting auth URL using callback URI: {callback_uri}")
            try:
                auth_url_response = requests.post(get_auth_url_endpoint(), json=auth_url_data)
                auth_url_response.raise_for_status()
                auth_url_result = auth_url_response.json()
                
                if "auth_url" not in auth_url_result:
                    logger.error("No auth_url received from backend")
                    httpd.shutdown()
                    return None
                
                auth_url = auth_url_result["auth_url"]
                logger.info(f"Opening browser to: {auth_url}")
                
                # Open the browser for the user to authenticate
                try:
                    webbrowser.open(auth_url)
                    print(f"If your browser doesn't open automatically, please visit: {auth_url}")
                except Exception as e:
                    logger.warning(f"Could not open browser automatically: {str(e)}")
                    print(f"Please open this URL in your browser to authenticate: {auth_url}")
                
                # Wait for the callback with the authorization code
                timeout = 300  # 5 minutes
                poll_interval = 1
                start = time.time()
                while time.time() - start < timeout:
                    if "code" in auth_code:
                        break
                    time.sleep(poll_interval)
                
                httpd.shutdown()
                
                # If we didn't get a code, the authentication failed
                if "code" not in auth_code:
                    logger.error("Authentication timed out, did not receive code")
                    return None
                
                # Exchange the code for tokens
                code = auth_code["code"]
                logger.info("Authorization code received, exchanging for tokens")
                token_data = exchange_code_for_token(code, callback_uri)
                
                if not token_data or "access_token" not in token_data:
                    logger.error("Token exchange failed")
                    return None
                
                # Store the token
                store_token(token_data)
                logger.info("Authentication successful")
                
                # Call profile endpoint to create user in database
                try:
                    if "access_token" in token_data:
                        config = get_config()
                        base_url = config.get("endpoint", "https://api.getmesh.ai")
                        profile_url = f"{base_url}/auth/profile"
                        
                        logger.debug(f"Calling profile endpoint after new authentication: {profile_url}")
                        profile_response = requests.get(
                            profile_url,
                            headers={"Authorization": f"Bearer {token_data['access_token']}"}
                        )
                        
                        if profile_response.status_code == 200:
                            logger.debug("\u2713 Profile endpoint called successfully - user created if needed")
                        else:
                            logger.warning(f"\u2717 Failed to call profile endpoint: {profile_response.status_code}")
                except Exception as e:
                    logger.warning(f"Error calling profile endpoint after authentication: {str(e)}")
                
                return token_data
                
            except requests.RequestException as e:
                logger.error(f"Error requesting auth URL: {str(e)}")
                httpd.shutdown()
                return None
                
    except Exception as e:
        logger.error(f"Error with authentication callback server: {str(e)}")
        return None

def exchange_code_for_token(code: str, callback_uri: str) -> Dict[str, Any]:
    """
    Exchange authorization code for token using the backend endpoint.

    Args:
        code: Authorization code from Auth0
        callback_uri: The callback URI that was used to get the code
        
    Returns:
        dict: Token data or empty dict if exchange failed
    """
    logger.debug("Starting code exchange process")
    logger.debug(f"Code: {code[:5]}...{code[-5:] if len(code) > 10 else ''}")
    logger.debug(f"Callback URI: {callback_uri}")
    
    try:
        exchange_url = get_token_exchange_endpoint()
        exchange_data = {
            "code": code,
            "redirect_uri": callback_uri
        }
        
        logger.debug(f"Exchanging code for token at: {exchange_url}")
        logger.debug(f"Exchange data: {exchange_data}")
        
        response = requests.post(exchange_url, json=exchange_data)
        logger.debug(f"Exchange response status code: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"\u2717 Code exchange failed with status code: {response.status_code}")
            try:
                error_data = response.json()
                logger.error(f"Error details: {error_data}")
            except:
                logger.error(f"Response text: {response.text[:200]}...")
            return {}
            
        response.raise_for_status()
        
        token_data = response.json()
        logger.debug("\u2713 Successfully exchanged code for token")
        
        # Log token details for debugging
        if "access_token" in token_data:
            token = token_data["access_token"]
            logger.debug(f"Access token: {token[:5]}...{token[-5:] if len(token) > 10 else ''}")
        else:
            logger.warning("\u2717 Response missing access_token")
            logger.debug(f"Response keys: {list(token_data.keys())}")
        
        # Add expires_at field if not present
        if "expires_in" in token_data and "expires_at" not in token_data:
            token_data["expires_at"] = int(time.time()) + token_data["expires_in"]
            import datetime
            expires = datetime.datetime.fromtimestamp(token_data["expires_at"])
            logger.debug(f"Token expires at: {expires}")
            
        # Store the token
        logger.debug("Storing token")
        store_result = store_token(token_data)
        if store_result:
            logger.debug("\u2713 Successfully stored token")
        else:
            logger.warning("\u2717 Failed to store token")
            
        return token_data
    except Exception as e:
        logger.error(f"\u2717 Error exchanging code for token: {str(e)}")
        logger.debug(f"Exception type: {type(e).__name__}")
        return {}

def refresh_auth_token(refresh_token=None):
    """
    Refresh an Auth0 token using the refresh token.
    
    Args:
        refresh_token: Refresh token to use
        
    Returns:
        dict: New token data or None if refresh failed
    """
    logger.debug("Starting token refresh process")
    
    # If no refresh token was provided, try to get it from the stored token
    if not refresh_token:
        logger.debug("No refresh token provided, attempting to retrieve from storage")
        token_data = get_token()
        if token_data:
            logger.debug("\u2713 Found token data in storage")
            refresh_token = token_data.get("refresh_token")
            if refresh_token:
                logger.debug(f"Retrieved refresh token: {refresh_token[:5]}...{refresh_token[-5:] if len(refresh_token) > 10 else ''}")
            else:
                logger.warning("\u2717 Token data exists but no refresh_token found")
                if token_data.keys():
                    logger.debug(f"Available token keys: {list(token_data.keys())}")
        else:
            logger.warning("\u2717 No token data found in storage")
    else:
        logger.debug(f"Using provided refresh token: {refresh_token[:5]}...{refresh_token[-5:] if len(refresh_token) > 10 else ''}")
    
    # If we still don't have a refresh token, we can't refresh
    if not refresh_token:
        logger.warning("\u2717 No refresh token available, cannot refresh token")
        return None
    
    # If the refresh token is empty, we can't refresh
    if not refresh_token.strip():
        logger.warning("\u2717 Refresh token is empty, cannot refresh token")
        return None
    
    logger.info("Attempting to refresh token")
    refresh_endpoint = get_token_refresh_endpoint()
    logger.debug(f"Using refresh endpoint: {refresh_endpoint}")
    
    try:
        # Try to refresh using the backend
        logger.debug("Sending refresh request to backend")
        response = requests.post(
            refresh_endpoint,
            json={"refresh_token": refresh_token},
            headers={"Content-Type": "application/json"}
        )
        
        logger.debug(f"Refresh response status code: {response.status_code}")
        
        if response.status_code == 200:
            logger.debug("\u2713 Received successful response from refresh endpoint")
            token_data = response.json()
            
            # Log token details for debugging
            if "access_token" in token_data:
                token = token_data["access_token"]
                logger.debug(f"New access token: {token[:5]}...{token[-5:] if len(token) > 10 else ''}")
            else:
                logger.warning("\u2717 Response missing access_token")
                logger.debug(f"Response keys: {list(token_data.keys())}")
            
            # Add expires_at for convenience
            if "expires_in" in token_data:
                token_data["expires_at"] = int(time.time()) + token_data["expires_in"]
                import datetime
                expires = datetime.datetime.fromtimestamp(token_data["expires_at"])
                logger.debug(f"Token expires at: {expires}")
            
            # Store the new token
            logger.debug("Storing refreshed token")
            store_result = store_token(token_data)
            if store_result:
                logger.debug("\u2713 Successfully stored refreshed token")
            else:
                logger.warning("\u2717 Failed to store refreshed token")
            
            logger.info("\u2713 Successfully refreshed token")
            return token_data
        else:
            logger.warning(f"\u2717 Token refresh failed: {response.status_code}")
            try:
                error_data = response.json()
                logger.warning(f"Error details: {error_data}")
            except:
                logger.warning(f"Response text: {response.text[:200]}...")
            return None
    except Exception as e:
        logger.warning(f"\u2717 Token refresh failed: {str(e)}")
        logger.debug(f"Exception type: {type(e).__name__}")
        return None

def get_device_code(headless=False) -> Tuple[str, str]:
    """Get a device code from Auth0 for the device flow authentication.
    
    This is useful for headless environments, CLI tools, or notebook environments.
    
    Args:
        headless: If True, only return codes without printing to console
        
    Returns:
        Tuple[str, str]: A tuple of (user_code, verification_uri) for the authentication
    """
    try:
        # Check if running in Jupyter/IPython environment
        in_notebook = False
        try:
            from IPython import get_ipython
            if get_ipython() is not None:
                in_notebook = True
        except ImportError:
            pass
        
        # First get the auth0 config from the backend, specifying this is for device flow
        auth0_config = get_auth0_config(is_device_flow=True)
        if not auth0_config:
            logger.error("Could not get Auth0 configuration")
            return (None, None)
        
        # Get a device code from Auth0
        device_code_url = f"https://{auth0_config['domain']}/oauth/device/code"
        device_code_data = {
            "client_id": auth0_config['client_id'],
            "scope": "openid profile email offline_access",
            "audience": auth0_config.get('audience', '')
        }
        
        device_response = requests.post(device_code_url, data=device_code_data)
        device_response.raise_for_status()
        device_result = device_response.json()
        
        if "verification_uri_complete" not in device_result or "device_code" not in device_result:
            logger.error("Invalid device code response")
            return (None, None)
        
        verification_uri = device_result["verification_uri_complete"]
        user_code = device_result.get("user_code", "")
        
        # Store device_code in a global context for poll_for_device_token
        global _device_code_data
        _device_code_data = device_result
        
        # Unless headless mode is enabled, display the verification URI
        if not headless:
            # Display the verification URI for the user, with enhanced rendering for notebooks
            if in_notebook:
                from IPython.display import display, HTML, Markdown
                expiry = device_result.get("expires_in", 900)
                
                html_content = f"""
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; border: 1px solid #dee2e6;">
                    <h3 style="margin-top: 0;">Mesh SDK Authentication</h3>
                    <p>To authenticate the Mesh SDK, please click the button below or visit this URL on any device:</p>
                    <div style="margin: 15px 0;">
                        <a href="{verification_uri}" target="_blank" style="display: inline-block; background-color: #4285f4; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; font-weight: bold;">
                            Authenticate with code: {user_code}
                        </a>
                    </div>
                    <p style="margin-bottom: 0; font-size: 90%; color: #6c757d;">This code will expire in {expiry} seconds.</p>
                </div>
                """
                display(HTML(html_content))
            else:
                # Standard console output for CLI environments
                print(f"\nTo authenticate the Mesh SDK, please visit this URL on any device:")
                print(f"\n{verification_uri}\n")
                if user_code:
                    print(f"Your verification code is: {user_code}")
                print(f"This code will expire in {device_result.get('expires_in', 900)} seconds.\n")
        
        return (user_code, verification_uri)
        
    except Exception as e:
        logger.error(f"Error getting device code: {str(e)}")
        return (None, None)

def poll_for_device_token(wait_message=True) -> Dict[str, Any]:
    """Poll for token using device code.
    
    This should be called after get_device_code() to wait for the user to complete authentication.
    
    Args:
        wait_message: Whether to display waiting messages
        
    Returns:
        Dict[str, Any]: Token data if successful, None otherwise
    """
    try:
        # Check if running in Jupyter/IPython environment
        in_notebook = False
        try:
            from IPython import get_ipython
            if get_ipython() is not None:
                in_notebook = True
        except ImportError:
            pass
            
        # Use the global device code data stored by get_device_code()
        global _device_code_data
        if not _device_code_data:
            logger.error("No device code data found. Call get_device_code() first.")
            return None
            
        device_result = _device_code_data
        auth0_config = get_auth0_config(is_device_flow=True)
        
        if not auth0_config:
            logger.error("Could not get Auth0 configuration")
            return None
            
        verification_uri = device_result["verification_uri_complete"]
        device_code = device_result["device_code"]
        polling_interval = device_result.get("interval", 5)
        expiry = device_result.get("expires_in", 900)  # Default to 15 minutes
        
        # Show waiting message if requested
        if wait_message:
            if in_notebook:
                from IPython.display import display, Markdown
                # Show waiting message
                display(Markdown("*Waiting for authentication... You can continue working in other cells while this completes.*"))
            else:
                print("Waiting for authentication to complete...")
        
        # Poll for token
        token_url = f"https://{auth0_config['domain']}/oauth/token"
        start_time = time.time()
        
        if in_notebook:
            from IPython.display import clear_output, display, HTML
        
        while time.time() - start_time < expiry:
            try:
                token_response = requests.post(token_url, data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "device_code": device_code,
                    "client_id": auth0_config['client_id']
                })
                
                if token_response.status_code == 200:
                    token_data = token_response.json()
                    if "access_token" not in token_data:
                        logger.error("Token response missing access_token")
                        return None
                    
                    # Add expires_at for convenience
                    if "expires_in" in token_data:
                        token_data["expires_at"] = int(time.time()) + token_data["expires_in"]
                    
                    # Store the token
                    store_token(token_data)
                    
                    if in_notebook:
                        clear_output(wait=True)
                        display(HTML("""
                        <div style="background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 10px 0; border: 1px solid #c3e6cb;">
                            <h3 style="margin-top: 0; color: #155724;">Authentication Successful!</h3>
                            <p style="margin-bottom: 0; color: #155724;">You can now use the Mesh SDK.</p>
                        </div>
                        """))
                    else:
                        print("\nAuthentication successful! You can now use the Mesh SDK.")
                    
                    return token_data
                elif token_response.status_code == 403:
                    # User has not yet authorized
                    time.sleep(polling_interval)
                else:
                    error_data = token_response.json()
                    error = error_data.get("error", "unknown_error")
                    
                    if error == "expired_token":
                        logger.error("Device code expired")
                        if in_notebook:
                            clear_output(wait=True)
                            display(HTML("""
                            <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 10px 0; border: 1px solid #f5c6cb;">
                                <h3 style="margin-top: 0; color: #721c24;">Authentication Failed</h3>
                                <p style="margin-bottom: 0; color: #721c24;">The device code has expired. Please try again.</p>
                            </div>
                            """))
                        else:
                            print("\nThe device code has expired. Please try again.")
                        return None
                    elif error == "access_denied":
                        logger.error("User denied access")
                        if in_notebook:
                            clear_output(wait=True)
                            display(HTML("""
                            <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 10px 0; border: 1px solid #f5c6cb;">
                                <h3 style="margin-top: 0; color: #721c24;">Authentication Denied</h3>
                                <p style="margin-bottom: 0; color: #721c24;">Authentication was denied. Please try again.</p>
                            </div>
                            """))
                        else:
                            print("\nAuthentication was denied. Please try again.")
                        return None
                    else:
                        time.sleep(polling_interval)
            except Exception as e:
                logger.error(f"Error polling for token: {str(e)}")
                time.sleep(polling_interval)
        
        if in_notebook:
            clear_output(wait=True)
            display(HTML("""
            <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 10px 0; border: 1px solid #f5c6cb;">
                <h3 style="margin-top: 0; color: #721c24;">Authentication Timed Out</h3>
                <p style="margin-bottom: 0; color: #721c24;">Authentication timed out. Please try again.</p>
            </div>
            """))
        else:
            print("\nAuthentication timed out. Please try again.")
        return None
        
    except Exception as e:
        logger.error(f"Error during device flow authentication: {str(e)}")
        return None

# Global variable to store device code data between get_device_code and poll_for_device_token
_device_code_data = None

def authenticate_device_flow():
    """
    Authenticate using device code flow.
    
    This is useful for headless environments, CLI tools, or notebook environments like Colab.
    
    Returns:
        dict: Token data if authentication successful, None otherwise
    """
    # Get device code
    user_code, verification_uri = get_device_code()
    if not user_code or not verification_uri:
        return None
        
    # Poll for token
    token_data = poll_for_device_token()
    
    # Call profile endpoint to create user in database
    if token_data and "access_token" in token_data:
        try:
            config = get_config()
            base_url = config.get("endpoint", "https://api.getmesh.ai")
            profile_url = f"{base_url}/auth/profile"
            
            logger.debug(f"Calling profile endpoint after device flow authentication: {profile_url}")
            profile_response = requests.get(
                profile_url,
                headers={"Authorization": f"Bearer {token_data['access_token']}"}
            )
            
            if profile_response.status_code == 200:
                logger.debug("\u2713 Profile endpoint called successfully - user created if needed")
            else:
                logger.warning(f"\u2717 Failed to call profile endpoint: {profile_response.status_code}")
        except Exception as e:
            logger.warning(f"Error calling profile endpoint after device flow authentication: {str(e)}")
    
    return token_data