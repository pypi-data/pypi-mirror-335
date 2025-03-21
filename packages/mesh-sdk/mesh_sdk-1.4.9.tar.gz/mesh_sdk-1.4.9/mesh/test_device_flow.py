#!/usr/bin/env python3
"""
Test authentication using the device code flow.

This script tests the device code flow authentication method in the Mesh SDK,
which does not require a local server for callback handling.
"""

import os
import sys
import logging
import time
import json
import requests
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_device_flow")

# Backend URL
MESH_API_URL = "https://mesh-abh5.onrender.com"

def get_device_code():
    """
    Get a device code from the backend to start the device flow.
    
    Returns:
        dict: Device code information including verification URL and user code
    """
    endpoints_to_try = [
        f"{MESH_API_URL}/api/v1/auth/device-code",
        f"{MESH_API_URL}/auth/device-code",
        f"{MESH_API_URL}/v1/mesh/auth/device-code"
    ]
    
    for endpoint in endpoints_to_try:
        try:
            logger.info(f"Requesting device code from {endpoint}")
            response = requests.post(endpoint)
            
            if response.status_code == 200:
                device_data = response.json()
                logger.info(f"Retrieved device code info: {json.dumps(device_data)}")
                return device_data
            else:
                logger.warning(f"Failed to get device code from {endpoint}: {response.status_code} - {response.text}")
        except Exception as e:
            logger.warning(f"Error requesting device code from {endpoint}: {str(e)}")
    
    logger.error("All device code endpoints failed")
    return None

def poll_for_token(device_code):
    """
    Poll the backend for token completion.
    
    Args:
        device_code: The device code obtained from get_device_code
        
    Returns:
        dict: Token data if successful, None otherwise
    """
    polling_endpoints = [
        f"{MESH_API_URL}/api/v1/auth/token-status",
        f"{MESH_API_URL}/auth/token-status",
        f"{MESH_API_URL}/v1/mesh/auth/token-status"
    ]
    
    interval = device_code.get("interval", 5)
    expires_in = device_code.get("expires_in", 900)
    start_time = time.time()
    
    # Use the device_code from the response
    device_code_value = device_code.get("device_code")
    
    if not device_code_value:
        logger.error("No device_code in response")
        return None
    
    logger.info(f"Polling for token completion every {interval} seconds (expires in {expires_in} seconds)")
    
    while time.time() - start_time < expires_in:
        for endpoint in polling_endpoints:
            try:
                response = requests.post(
                    endpoint, 
                    json={"device_code": device_code_value}
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    
                    # Check if we have a token or still need to wait
                    if "token" in token_data:
                        logger.info("Token received!")
                        return token_data["token"]
                    elif token_data.get("status") == "pending":
                        logger.info("User has not completed authentication yet...")
                        break  # Try again after interval
                    else:
                        logger.warning(f"Unexpected response from {endpoint}: {json.dumps(token_data)}")
                        break
                elif response.status_code == 400 and "authorization_pending" in response.text.lower():
                    # Still waiting for the user
                    logger.info("Still waiting for user authorization...")
                    break
                else:
                    logger.warning(f"Failed to check token status: {response.status_code} - {response.text}")
            except Exception as e:
                logger.warning(f"Error checking token status: {str(e)}")
        
        # Sleep before trying again
        time.sleep(interval)
    
    logger.error("Device code expired without receiving a token")
    return None

def main():
    try:
        # Check if running in a notebook environment
        in_notebook = False
        try:
            from IPython import get_ipython
            if get_ipython() is not None:
                in_notebook = True
        except ImportError:
            pass
            
        # Clear any existing tokens
        from mesh.token_manager import clear_token
        clear_token()
        logger.info("Cleared existing tokens")
        
        # Step 1: Get a device code
        device_code_info = get_device_code()
        if not device_code_info:
            logger.error("Failed to get device code")
            return False
        
        # Show information to the user
        verification_url = device_code_info.get("verification_uri_complete") or device_code_info.get("verification_uri")
        user_code = device_code_info.get("user_code", "")
        
        # Display authentication instructions based on environment
        if in_notebook:
            from IPython.display import display, HTML, Markdown
            
            # Create a styled HTML card for the authentication instructions
            html_content = f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; border: 1px solid #dee2e6;">
                <h2 style="margin-top: 0; color: #212529;">DEVICE CODE AUTHENTICATION</h2>
                <p>Complete these steps to authenticate:</p>
                <ol>
                    <li>
                        <p><strong>Click the button below to open the authentication page:</strong></p>
                        <div style="margin: 10px 0;">
                            <a href="{verification_url}" target="_blank" style="display: inline-block; background-color: #4285f4; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; font-weight: bold;">
                                Authenticate with code: {user_code}
                            </a>
                        </div>
                    </li>
                    <li>
                        <p><strong>If the code isn't pre-filled, enter this code:</strong></p>
                        <div style="background-color: #e9ecef; padding: 8px 12px; border-radius: 4px; font-family: monospace; font-size: 18px; letter-spacing: 2px;">
                            {user_code}
                        </div>
                    </li>
                    <li>
                        <p><strong>Complete the authentication process in your browser</strong></p>
                    </li>
                </ol>
            </div>
            """
            display(HTML(html_content))
            
            # Also show waiting message
            display(Markdown("*Waiting for you to complete authentication in the browser...*"))
        else:
            print("\n" + "=" * 60)
            print("DEVICE CODE AUTHENTICATION")
            print("=" * 60)
            
            if "verification_uri_complete" in device_code_info:
                print(f"\n1. Open this URL in your browser:")
                print(f"   {verification_url}")
                print("\n2. The code should be pre-filled, but if not, enter:")
                print(f"   {user_code}")
            else:
                print(f"\n1. Open this URL in your browser: {device_code_info.get('verification_uri')}")
                print(f"\n2. Enter this code: {user_code}")
            
            print("\n3. Complete the authentication process in your browser")
            print("=" * 60)
            
            # Step 2: Poll for token
            print("\nWaiting for you to complete authentication in the browser...")
        token_data = poll_for_token(device_code_info)
        
        if not token_data:
            logger.error("Failed to get token using device code flow")
            return False
        
        # Step 3: Store the token
        from mesh.token_manager import store_token
        store_token(token_data)
        logger.info("Token stored successfully")
        
        # Step 4: Test the token by getting the user profile
        access_token = token_data.get("access_token")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        profile_endpoints = [
            f"{MESH_API_URL}/api/v1/auth/profile",
            f"{MESH_API_URL}/auth/profile",
            f"{MESH_API_URL}/v1/mesh/auth/profile"
        ]
        
        profile_response = None
        for endpoint in profile_endpoints:
            try:
                logger.info(f"Getting user profile from {endpoint}")
                response = requests.get(endpoint, headers=headers)
                
                if response.status_code == 200:
                    profile_response = response
                    break
                else:
                    logger.warning(f"Profile endpoint {endpoint} returned status {response.status_code}")
            except Exception as e:
                logger.warning(f"Failed to get profile from {endpoint}: {str(e)}")
        
        if not profile_response:
            logger.error("All profile endpoints failed")
            return False
        
        try:
            profile_data = profile_response.json()
            credits = profile_data.get('profile', {}).get('credits', 'N/A')
            
            if in_notebook:
                from IPython.display import display, HTML, clear_output
                
                # Clear previous waiting message
                clear_output(wait=True)
                
                # Show success message with a styled box
                success_html = f"""
                <div style="background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 10px 0; border: 1px solid #c3e6cb;">
                    <h2 style="margin-top: 0; color: #155724;">✅ AUTHENTICATION SUCCESSFUL!</h2>
                    <p style="color: #155724; font-size: 16px;">User profile retrieved with <strong>{credits}</strong> credits.</p>
                    <p style="color: #155724; margin-bottom: 0;">You can now use the Mesh SDK in this notebook.</p>
                </div>
                """
                display(HTML(success_html))
            else:
                print("\n" + "=" * 60)
                print("✅ AUTHENTICATION SUCCESSFUL!")
                print(f"✅ User profile retrieved with {credits} credits")
                print("=" * 60 + "\n")
            
            return True
        except Exception as e:
            logger.error(f"Error parsing profile response: {str(e)}")
            
            if in_notebook:
                from IPython.display import display, HTML, clear_output
                
                # Clear previous waiting message
                clear_output(wait=True)
                
                # Show error message
                error_html = f"""
                <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 10px 0; border: 1px solid #f5c6cb;">
                    <h2 style="margin-top: 0; color: #721c24;">❌ AUTHENTICATION ERROR</h2>
                    <p style="color: #721c24;">Could not retrieve user profile information.</p>
                    <p style="color: #721c24; margin-bottom: 0; font-family: monospace; font-size: 12px;">{str(e)}</p>
                </div>
                """
                display(HTML(error_html))
            
            return False
    
    except Exception as e:
        logger.error(f"Error during device code authentication: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 