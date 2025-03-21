"""
Mesh API Client

This module provides a comprehensive client for interacting with the Mesh API,
including key management, Zero-Knowledge Proofs, chat completions, and usage tracking.
"""

import json
import os
import time
import hashlib
import logging
import requests
import threading
from typing import Dict, Any, Optional, List, Set, Union

# Import configuration
from .config import (
    get_config, is_debug_enabled, get_default_model, get_default_provider,
    is_thinking_enabled, get_default_thinking_budget, get_default_thinking_max_tokens,
    get_default_model_with_override, get_all_config, get_auth_config_endpoint, 
    get_auth_url_endpoint, get_token_exchange_endpoint, get_token_validate_endpoint
)

# Import token manager and auth functions
from .token_manager import store_token, get_token, is_token_valid, clear_token
from .auth import authenticate, refresh_auth_token, authenticate_with_browser

# Import models
from .models import normalize_model_name, get_provider_for_model, MODEL_ALIASES, PROVIDER_MODELS

# Set up logging
logger = logging.getLogger("mesh_client")
logger.setLevel(logging.WARNING)  # Default to WARNING to reduce verbosity
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Configure requests and urllib3 logging based on debug mode
if os.environ.get("DEBUG", "").lower() in ('true', '1', 'yes'):
    # In debug mode, set requests and urllib3 to INFO to see more details
    logging.getLogger("requests").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.INFO)
else:
    # Otherwise, keep them at WARNING to reduce noise
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

# Default configuration
DEFAULT_CONFIG = {
    "normalize_response": True,
    "original_response": False,
    "return_content_only": True,
    "debug": False
}

class MeshClient:
    """
    Unified client for the Mesh API with key management, ZKP, and chat capabilities
    
    This client provides a unified interface to interact with both the main API server
    and the ZKP microservice. It handles:
    
    1. Basic key management (store/retrieve keys)
    2. Chat functionality with OpenAI and Anthropic models
    3. Usage tracking and billing
    
    Authentication is handled automatically using the backend-managed flow.
    """
    
    def __init__(
        self,
        api_url=None,
        auth_token=None,
        response_format=None,
        auto_refresh=True,
        health_monitor=True
    ):
        """
        Initialize the Mesh client with optional parameters.
        
        Args:
            api_url: URL of the API server (defaults to configured value)
            auth_token: Optional auth token (for backward compatibility)
            response_format: Default response format for chat (dict or string)
            auto_refresh: Whether to automatically refresh tokens
            health_monitor: Whether to monitor token health
        """
        # Configure logging
        self.logger = logging.getLogger("MeshClient")
        self.logger.setLevel(logging.WARNING)  # Default to WARNING
        
        # Set debug mode if enabled
        if is_debug_enabled():
            self.logger.setLevel(logging.DEBUG)
            self.logger.debug("Debug mode enabled")
            logging.getLogger("mesh_client").setLevel(logging.DEBUG)
        
        # Set up token management
        self._auth_token = None
        self._token_data = None
        self.auto_refresh = auto_refresh
        
        # Set server URLs, using config values as defaults
        self.api_url = api_url or get_config("MESH_API_URL")
        
        # Use provided auth token or try to load from storage
        if auth_token:
            self.auth_token = auth_token
        else:
            self._load_token()
        
        # Configure response format
        self.config = DEFAULT_CONFIG.copy()
        if response_format:
            if isinstance(response_format, dict):
                self.config.update(response_format)
            elif response_format.lower() == "string":
                self.config["return_content_only"] = True
            elif response_format.lower() == "dict":
                self.config["return_content_only"] = False
        
        # Initialize user profile attributes
        self._profile_checked = False
        self._user_profile = None
        
        # Start token health monitor if enabled
        if health_monitor and auto_refresh:
            self._start_token_health_monitor()
    
    def _load_token(self) -> None:
        """Load authentication token from secure storage"""
        token_data = get_token()
        if token_data and isinstance(token_data, dict):
            self._token_data = token_data
            self._auth_token = token_data.get("access_token")
            self.logger.debug("Loaded auth token from storage")
    
    def _validate_token(self) -> bool:
        """
        Validate the current authentication token.
        
        First performs a local validation check based on token expiration.
        If the backend supports the /auth/validate endpoint, also validates with the backend.
        
        Returns:
            bool: True if the token is valid, False otherwise
        """
        # No token data or token, not valid
        if not self._token_data or not self._auth_token:
            self.logger.debug("No token data available to validate")
            return False
            
        # Log token information for debugging
        self.logger.debug(f"Validating token: {self._auth_token[:5]}...{self._auth_token[-5:] if len(self._auth_token) > 10 else ''}")
        
        # First do a local check based on expiration
        token_valid = is_token_valid(self._token_data)
        self.logger.debug(f"Local token validation result: {token_valid}")
        
        if not token_valid:
            # Token is locally known to be expired, but we have refresh capability
            if self.auto_refresh and "refresh_token" in self._token_data:
                self.logger.debug("Token expired but refresh capability available")
                refresh_result = self._refresh_token()
                self.logger.debug(f"Token refresh result: {refresh_result}")
                return refresh_result
            else:
                self.logger.debug("Token expired and no refresh capability")
                return False
                
        # At this point, we know the token is not expired locally
        # Try to validate with backend if possible
        try:
            # Only attempt backend validation if token passes basic structure check
            if self._auth_token and len(self._auth_token.split('.')) == 3:
                self.logger.debug("Token has valid JWT format (3 parts)")
                
                # Try using the backend /auth/validate endpoint to validate the token
                validate_url = get_token_validate_endpoint()
                headers = {"Authorization": f"Bearer {self._auth_token}"}
                
                try:
                    # Use a short timeout to avoid hanging if endpoint doesn't respond
                    response = requests.get(validate_url, headers=headers, timeout=3)
                    
                    if response.status_code == 200:
                        self.logger.debug("Token validated by backend")
                        return True
                    elif response.status_code == 404:
                        # Endpoint doesn't exist, this is fine - fall back to local validation
                        self.logger.debug("Backend validation endpoint not available, using local validation")
                        return True  # Already passed local validation above
                    elif response.status_code in (401, 403):
                        # Token is actually invalid according to backend
                        self.logger.debug("Backend rejected token as invalid")
                        if self.auto_refresh and "refresh_token" in self._token_data:
                            self.logger.debug("Attempting token refresh after validation failure")
                            return self._refresh_token()
                        return False
                    else:
                        # Other error, fall back to local validation
                        self.logger.debug(f"Unexpected response from validation endpoint: {response.status_code}")
                        return True  # Already passed local validation
                        
                except requests.RequestException as e:
                    # Connection error, can't reach validation endpoint
                    self.logger.debug(f"Could not connect to validation endpoint: {str(e)}")
                    return True  # Fall back to local validation which already passed
            else:
                self.logger.debug("Token does not have valid JWT format")
                return False
                
        except Exception as e:
            self.logger.warning(f"Error during token validation: {str(e)}")
            # Default to local expiration check which already passed
            return True
    
    def _refresh_token(self) -> bool:
        """
        Refresh the authentication token.
        
        Returns:
            bool: True if refresh succeeded, False otherwise
        """
        if not self._token_data or "refresh_token" not in self._token_data:
            self.logger.debug("No refresh token available")
            return False
        
        refresh_token = self._token_data.get("refresh_token")
        if not refresh_token:
            self.logger.debug("Refresh token is empty")
            return False
        
        self.logger.debug("Attempting to refresh token")
        
        # Try to refresh the token
        try:
            new_token_data = refresh_auth_token(refresh_token=refresh_token)
            
            if new_token_data and "access_token" in new_token_data:
                # Update the token data and auth token
                self._token_data = new_token_data
                self._auth_token = new_token_data.get("access_token")
                
                # Store the new token
                store_token(new_token_data)
                
                self.logger.debug("Successfully refreshed token")
                return True
            else:
                self.logger.warning("Token refresh failed")
                return False
        except Exception as e:
            self.logger.warning(f"Error during token refresh: {str(e)}")
            return False
    
    def _authenticate(self) -> bool:
        """
        Authenticate with the backend.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Try to authenticate
            token_data = authenticate()
            
            if token_data and "access_token" in token_data:
                # Update the token data and auth token
                self._token_data = token_data
                self._auth_token = token_data.get("access_token")
                
                self.logger.debug("Authentication successful")
                return True
            else:
                self.logger.warning("Authentication failed")
                return False
        except Exception as e:
            self.logger.warning(f"Error during authentication: {str(e)}")
            return False
    
    @property
    def auth_token(self) -> str:
        """Get the authentication token"""
        return self._auth_token
    
    @auth_token.setter
    def auth_token(self, value: str):
        """Set the authentication token and persist it to secure storage"""
        self._auth_token = value
        
        # Store the token in the token manager
        if value:
            # Create minimal token data if we only have the token string
            expires_at = time.time() + 3600  # Default expiry of 1 hour
            token_data = {
                "access_token": value,
                "expires_at": expires_at
            }
            
            # Preserve refresh token if we have it
            if self._token_data and "refresh_token" in self._token_data:
                token_data["refresh_token"] = self._token_data["refresh_token"]
                
            # Store in token manager
            store_token(token_data)
            self._token_data = token_data
            
            logger.debug("Stored token in token manager")
    
    def _get_url(self, endpoint: str) -> str:
        """
        Get the full URL for an API endpoint
        
        Args:
            endpoint: The endpoint path (e.g., '/v1/chat')
            
        Returns:
            str: The full URL
        """
        # Ensure endpoint starts with a slash
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
            
        # Looking at server.js, all endpoints are properly mapped to /api/v1/...
        # Just ensure we are using the standardized paths
        if endpoint.startswith('/api/v1/'):
            # Already using the standardized API path, nothing to change
            pass
        elif endpoint == '/chat/completions':
            endpoint = '/api/v1/chat/completions'
        elif endpoint == '/completions':
            endpoint = '/api/v1/completions'
        elif endpoint == '/storeKey':
            endpoint = '/api/v1/storeKey'
        elif endpoint == '/getKey':
            endpoint = '/api/v1/getKey'
        elif endpoint == '/listKeys':
            endpoint = '/api/v1/listKeys'
        
        # IMPORTANT: For compatibility with the server's route mapping,
        # use /v1/mesh/chat instead of /api/v1/chat/completions as a fallback
        # if the server doesn't properly handle the standardized path
        if endpoint == '/api/v1/chat/completions':
            # Try the legacy endpoint since the server should map this correctly
            endpoint = '/v1/mesh/chat'
            self.logger.debug(f"Using legacy endpoint mapping: /api/v1/chat/completions -> {endpoint}")
        
        # Log the full URL for debugging
        full_url = f"{self.api_url}{endpoint}"
        self.logger.debug(f"Constructed API URL: {full_url}")
        
        return full_url
    
    def _ensure_authenticated(self) -> bool:
        """
        Make sure we're authenticated to the service
        
        This method will:
        1. Check if we have a valid token
        2. If not, try to refresh the token
        3. If that fails, initiate the authentication flow
        
        Returns:
            bool: True if authentication succeeded
        """
        # If we're already authenticated with a valid token, we're done
        if self._validate_token():
            self.logger.debug("Already authenticated with valid token")
            return True
            
        self.logger.info("No valid token, trying authentication")
        
        # Try to authenticate
        return self._authenticate()
    
    def clear_token(self) -> bool:
        """
        Clear the stored authentication token
        
        This is useful for testing authentication flows or logging out.
        
        Returns:
            bool: True if token was cleared successfully
        """
        try:
            # Clear in-memory token
            self._token_data = None
            self._auth_token = None
            
            # Clear stored token
            clear_token()
            
            self.logger.info("Token cleared successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing token: {str(e)}")
            return False
    
    def _get_headers(self, additional_headers=None) -> Dict[str, str]:
        """
        Get headers with authentication if available
        
        Args:
            additional_headers: Additional headers to include
            
        Returns:
            dict: Headers with authentication if available
        """
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add auth token if available
        if self._auth_token:
            # Make sure token doesn't have any accidental whitespace
            token = self._auth_token.strip()
            headers["Authorization"] = f"Bearer {token}"
            
        else:
            logger.warning("No authentication token available for request")
        
        # Add additional headers
        if additional_headers:
            headers.update(additional_headers)
            
        return headers
    
    def _start_token_health_monitor(self):
        """Start background thread to monitor token health"""
        def monitor_token_health():
            """Background thread to monitor token health"""
            while True:
                try:
                    # Check if we need to refresh the token
                    # Only refresh if we have less than 5 minutes left
                    if self._token_data and "expires_at" in self._token_data:
                        expires_at = self._token_data["expires_at"]
                        now = time.time()
                        time_to_expiry = expires_at - now
                        
                        if time_to_expiry < 300:  # Less than 5 minutes
                            self.logger.debug("Token about to expire, refreshing...")
                            self._refresh_token()
                except Exception as e:
                    self.logger.error(f"Error in token health monitor: {str(e)}")
                
                # Sleep for 1 minute
                time.sleep(60)
        
        # Start the monitor thread
        monitor_thread = threading.Thread(target=monitor_token_health)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def _ensure_user_registered(self) -> Dict[str, Any]:
        """
        Ensure the user is registered with the backend
        
        This method:
        1. Gets the user profile from the backend
        2. Stores it in memory for later use
        
        Returns:
            dict: User profile if successful, None otherwise
        """
        # Return cached profile if we already checked
        if self._profile_checked and self._user_profile:
            return self._user_profile
        
        # Make sure we're authenticated
        if not self._ensure_authenticated():
            self.logger.error("Could not authenticate to get user profile")
            return None
        
        # Get the user profile from the backend
        try:
            profile_url = f"{self.api_url}/auth/profile"
            headers = self._get_headers()
            
            response = requests.get(profile_url, headers=headers)
            if response.status_code == 200:
                profile_data = response.json()
                self.logger.debug(f"Received user profile data: {profile_data}")
                self._user_profile = profile_data
                self._profile_checked = True
                
                # Log the structure to help with debugging
                if 'profile' in profile_data:
                    self.logger.debug("Profile data has nested 'profile' key")
                if 'id' in profile_data:
                    self.logger.debug("Profile data has 'id' key at root level")
                elif profile_data.get('profile', {}).get('id'):
                    self.logger.debug("Profile data has 'id' key in nested 'profile'")
                    
                return self._user_profile
            else:
                self.logger.warning(f"Failed to get user profile: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error getting user profile: {str(e)}")
            return None
    
    # =========================
    # Key Management Methods
    # =========================
    
    def store_key(self, key_name: str = None, key_value: str = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Store a key in the Mesh API
        
        Args:
            key_name: Name of the key (will be stored as {userId}_{key_name})
            key_value: Value of the key to store
            user_id: Optional User ID to associate with the key. If not provided, extracted from auth token.
            
        Returns:
            dict: Result of the operation
        """
        # Validate required parameters
        if not key_name or not key_value:
            return {
                "success": False,
                "error": "Missing required parameters: key_name and key_value must be provided"
            }
            
        # Ensure we're authenticated
        if not self._ensure_authenticated():
            return {
                "success": False,
                "error": "Authentication failed",
                "details": "Could not authenticate with Auth0"
            }
        
        # Get user profile to extract user ID if not provided
        if not user_id:
            if not self._user_profile:
                self._ensure_user_registered()
            
            # Debug the user profile
            self.logger.debug(f"User profile: {self._user_profile}")
            
            if self._user_profile and 'id' in self._user_profile:
                user_id = self._user_profile.get('id')
                logger.info(f"Using user ID from profile: {user_id}")
            elif self._user_profile and 'profile' in self._user_profile and 'id' in self._user_profile['profile']:
                # Try the nested profile structure
                user_id = self._user_profile['profile'].get('id')
                logger.info(f"Using user ID from nested profile: {user_id}")
            else:
                return {
                    "success": False,
                    "error": "User ID not provided and could not be extracted from authentication token",
                    "troubleshooting": [
                        "Provide a user_id parameter",
                        "Ensure you are properly authenticated",
                        "Check that the server URL is correct"
                    ]
                }
        
        # Create the storage path: {userId}_{key_name}
        storage_path = f"{user_id}_{key_name}"
        logger.info(f"Storing key with path: {storage_path}")
        
        url = self._get_url("/api/v1/storeKey")
        self.logger.debug(f"Using storeKey URL: {url}")
        
        # Make the request
        headers = self._get_headers()
        payload = {
            "userId": user_id,
            "keyName": storage_path,  # Use the combined path as key name
            "keyValue": key_value
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                # Add our parameters to the response for verification
                result.update({
                    "storagePath": storage_path,
                    "originalKeyName": key_name
                })
                return result
            else:
                # Simple error handling with clean error messages
                error_data = response.json() if response.content else {}
                self.logger.error(f"Failed to store key: {url} → {response.status_code}")
                
                return {
                    "success": False,
                    "error": f"Failed to store key: {response.status_code}",
                    "details": error_data
                }
                
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }
    
    def get_key(self, key_name: str = None, user_id: Optional[str] = None) -> Optional[str]:
        """
        Get a key from the Mesh API
        
        Args:
            key_name: Name of the key (will be retrieved using {userId}_{key_name})
            user_id: Optional User ID to retrieve key for. If not provided, extracted from auth token.
            
        Returns:
            str: The key value if found, None if not found or error occurs
        """
        # Validate required parameters
        if not key_name:
            logger.error("Missing required parameter: key_name")
            return None
                
        # Ensure we're authenticated
        if not self._ensure_authenticated():
            logger.error("Authentication failed")
            return None
        
        # Get user profile to extract user ID if not provided
        if not user_id:
            if not self._user_profile:
                self._ensure_user_registered()
            
            # Debug the user profile
            self.logger.debug(f"User profile: {self._user_profile}")
            
            if self._user_profile and 'id' in self._user_profile:
                user_id = self._user_profile.get('id')
                logger.info(f"Using user ID from profile: {user_id}")
            elif self._user_profile and 'profile' in self._user_profile and 'id' in self._user_profile['profile']:
                # Try the nested profile structure
                user_id = self._user_profile['profile'].get('id')
                logger.info(f"Using user ID from nested profile: {user_id}")
            else:
                logger.error("Could not determine user ID")
                return None
        
        # Create the storage path: {userId}_{key_name}
        storage_path = f"{user_id}_{key_name}"
        logger.info(f"Retrieving key with path: {storage_path}")
        
        # Make the request
        url = self._get_url("/api/v1/getKey")
        self.logger.debug(f"Using getKey URL: {url}")
        headers = self._get_headers()
        params = {
            "userId": user_id,
            "keyName": storage_path  # Use the combined path as key name
        }
        
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Return None if request failed
                if not result.get("success"):
                    logger.warning(f"Key retrieval failed: {result.get('error', 'Unknown error')}")
                    return None
                    
                # Return the key value - handle both response formats
                key_value = result.get("keyValue") or result.get("key")
                if key_value:
                    logger.info(f"Successfully retrieved key for path: {storage_path}")
                    return key_value
                else:
                    logger.warning(f"No key value found in response for path: {storage_path}")
                    return None
            else:
                # Simple error logging
                logger.error(f"Failed to retrieve key: {url} → {response.status_code}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return None
    
    def list_keys(self, user_id: Optional[str] = None) -> List[str]:
        """
        List all keys stored for a user
        
        Args:
            user_id: Optional User ID to list keys for. If not provided, extracted from auth token.
            
        Returns:
            List[str]: A list of key names (without the user_id prefix)
        """
        # Ensure we're authenticated
        if not self._ensure_authenticated():
            logger.error("Authentication failed")
            return []
        
        # Get user profile to extract user ID if not provided
        if not user_id:
            if not self._user_profile:
                self._ensure_user_registered()
            
            # Debug the user profile
            self.logger.debug(f"User profile for list_keys: {self._user_profile}")
            
            if self._user_profile and 'id' in self._user_profile:
                user_id = self._user_profile.get('id')
                logger.info(f"Using user ID from profile: {user_id}")
            elif self._user_profile and 'profile' in self._user_profile and 'id' in self._user_profile['profile']:
                # Try the nested profile structure
                user_id = self._user_profile['profile'].get('id')
                logger.info(f"Using user ID from nested profile: {user_id}")
            else:
                logger.error("Could not determine user ID")
                return []
        
        # Make the request
        url = self._get_url("/api/v1/listKeys")
        self.logger.debug(f"Using listKeys URL: {url}")
        headers = self._get_headers()
        params = {"userId": user_id}
        
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract keys from response
                keys = result.get("keys", [])
                
                # Strip the user ID prefix from the keys
                prefix = f"{user_id}_"
                stripped_keys = []
                
                for key in keys:
                    if key.startswith(prefix):
                        stripped_keys.append(key[len(prefix):])
                    else:
                        stripped_keys.append(key)
                
                return stripped_keys
            else:
                # Simple error logging
                logger.error(f"Failed to list keys: {url} → {response.status_code}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return []
    
    # =========================
    # Chat Methods
    # =========================
    
    def _fetch_user_profile(self):
        """
        Fetch user profile to ensure the user exists in the database.
        This should be called after authentication to create the user if needed.
        
        Returns:
            bool: True if profile was successfully fetched, False otherwise
        """
        self.logger.debug("Fetching user profile to ensure user exists in database")
        profile_url = self._get_url("/auth/profile")
        
        try:
            headers = self._get_headers()
            self.logger.debug(f"Calling profile endpoint: {profile_url}")
            
            response = requests.get(
                profile_url,
                headers=headers
            )
            
            if response.status_code == 200:
                self.logger.debug("✓ User profile successfully fetched/created")
                return True
            else:
                self.logger.warning(f"Failed to fetch/create profile: {response.status_code}")
                return False
        except Exception as e:
            self.logger.warning(f"Error fetching profile: {str(e)}")
            return False
    
    def chat(
        self, 
        message: Union[str, List[Dict[str, str]]], 
        model: Optional[str] = None, 
        provider: Optional[str] = None,
        image_path: Optional[Union[str, List[str]]] = None,  # Original parameter for backward compatibility
        images: Optional[Union[str, List[str]]] = None,      # New parameter (more intuitive API)
        _retry_attempt: int = 0,  # Internal parameter to track retries
        **kwargs
    ) -> Union[Dict[str, Any], str]:
        """
        Send a chat message to an AI model, optionally with images
        
        This method supports both string messages and message arrays, with optional image attachments.
        
        Args:
            message: The message to send (string or message array)
            model: The model to use (e.g. "gpt-4", "claude-3-5-sonnet", "gemini-pro-vision")
            provider: The provider to use (e.g. "openai", "anthropic", "google")
            images: Path to image file(s) to include with the message (preferred parameter name)
            image_path: Alternate name for images parameter (maintained for backward compatibility)
            **kwargs: Additional options for the chat request
            
        Returns:
            Union[Dict[str, Any], str]: The chat response
            
        Examples:
            # Simple text chat
            response = client.chat("Hello, how are you?")
            
            # Chat with an image
            response = client.chat("What's in this image?", images="image.jpg")
            
            # Chat with multiple images
            response = client.chat("Compare these images", images=["image1.jpg", "image2.jpg"])
        """
        # Ensure we're authenticated
        if not self._ensure_authenticated():
            raise Exception("Authentication failed")
            
        # Determine model and provider
        if not model and not provider:
            # Neither specified, use defaults
            provider = get_default_provider()
            model = get_default_model(provider)
            self.logger.debug(f"Using default provider {provider} and model {model}")
        elif model and not provider:
            # Model specified but not provider, determine provider from model
            normalized_model = normalize_model_name(model)
            provider = get_provider_for_model(normalized_model)
            model = normalized_model
            self.logger.debug(f"Using provider {provider} determined from model {model}")
        elif not model and provider:
            # Provider specified but not model, use default model for provider
            provider = provider.lower()
            model = get_default_model(provider)
            self.logger.debug(f"Using default model {model} for provider {provider}")
        else:
            # Both specified, normalize model and ensure provider is lowercase
            model = normalize_model_name(model)
            provider = provider.lower()
            self.logger.debug(f"Using specified provider {provider} and model {model}")
            
        # Ensure provider is lowercase (just to be safe)
        provider = provider.lower()
        
        # Log the provider we're using for debugging
        self.logger.debug(f"Using provider: {provider} for model: {model}")
        
        # Convert string message to message array if needed
        messages = []
        if isinstance(message, str):
            messages = [{"role": "user", "content": message}]
        elif isinstance(message, list):
            messages = message
        else:
            raise ValueError("Message must be a string or a list of message objects")
        
        # Handle image path(s) if provided
        # Use 'images' parameter if provided, fall back to 'image_path' for backward compatibility
        image_input = images if images is not None else image_path
        
        if image_input:
            import base64
            import os
            import math
            
            # Convert to list if it's a single string
            image_paths = [image_input] if isinstance(image_input, str) else image_input
            
            # Check if model supports vision
            if not model or not any(vision_model in model.lower() for vision_model in ["vision", "gpt-4o", "gpt-4-v", "claude-3", "gemini"]):
                # Auto-upgrade to a vision-capable model
                if provider == "openai":
                    model = "gpt-4o"  # Use the latest GPT-4o model which supports vision
                    self.logger.info(f"Using latest OpenAI vision model: {model}")
                elif provider == "anthropic":
                    model = "claude-3-7-sonnet-20250219"  # Use Claude 3.7 Sonnet
                    self.logger.info(f"Using latest Anthropic vision model: {model}")
                elif provider == "google":
                    # Use Gemini 2.0 Flash Experimental for image generation capabilities
                    model = "gemini-2.0-flash-exp-image-generation"
                    self.logger.info(f"Using latest Google image-capable model: {model}")
            
            # Check image sizes and potentially resize before processing
            # According to docs, optimal image size is up to 1568px on the long edge
            # and no more than ~1.15 megapixels for best performance
            
            try:
                # Import PIL for image processing (if available)
                from PIL import Image
                has_pil = True
            except ImportError:
                self.logger.warning("PIL/Pillow not installed. Image optimization skipped. Install with: pip install Pillow")
                has_pil = False
            
            # For each image, read file and add to message
            image_contents = []
            
            # Limit number of images based on provider limits
            max_images = 5
            if len(image_paths) > max_images:
                self.logger.warning(f"Too many images provided. Using only the first {max_images} images.")
                image_paths = image_paths[:max_images]
            
            for img_path in image_paths:
                if not os.path.exists(img_path):
                    raise FileNotFoundError(f"Image file not found: {img_path}")
                
                # Check and optimize image if PIL is available
                if has_pil:
                    try:
                        with Image.open(img_path) as img:
                            # Get image dimensions
                            width, height = img.size
                            
                            # Check if image is too large (per Claude guidelines)
                            if width > 8000 or height > 8000:
                                raise ValueError(f"Image too large: {width}x{height}. Maximum dimensions: 8000x8000px")
                            
                            # Calculate if we need to resize for better performance
                            megapixels = (width * height) / 1_000_000
                            max_dimension = max(width, height)
                            
                            # Optimal size according to Claude docs:
                            # - Long edge <= 1568px 
                            # - Size <= 1.15 megapixels
                            if megapixels > 1.15 or max_dimension > 1568:
                                self.logger.info(f"Optimizing image size: {width}x{height} ({megapixels:.2f} MP)")
                                
                                # Calculate new dimensions
                                scale = min(1568 / max_dimension, math.sqrt(1.15 / megapixels))
                                new_width = int(width * scale)
                                new_height = int(height * scale)
                                
                                # Resize image
                                img = img.resize((new_width, new_height), Image.LANCZOS)
                                self.logger.info(f"Image resized to: {new_width}x{new_height}")
                                
                                # Save to a temporary file
                                import tempfile
                                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(img_path)[1]) as tmp:
                                    img.save(tmp.name)
                                    tmp_path = tmp.name
                                
                                # Use the optimized image
                                with open(tmp_path, "rb") as f:
                                    image_data = f.read()
                                    
                                # Clean up temporary file
                                try:
                                    os.unlink(tmp_path)
                                except:
                                    pass
                                    
                            else:
                                # Image is already optimal size, just read it
                                with open(img_path, "rb") as f:
                                    image_data = f.read()
                    except Exception as e:
                        self.logger.warning(f"Image optimization failed: {str(e)}. Using original image.")
                        with open(img_path, "rb") as f:
                            image_data = f.read()
                else:
                    # PIL not available, just read the image as-is
                    with open(img_path, "rb") as f:
                        image_data = f.read()
                
                # Encode as base64
                base64_image = base64.b64encode(image_data).decode("utf-8")
                
                # Get MIME type based on file content and extension
                mime_type = "image/jpeg"  # default
                
                # Try to detect MIME type from file magic bytes
                try:
                    import imghdr
                    img_type = imghdr.what(None, h=image_data[:32])
                    
                    if img_type == 'jpeg' or img_type == 'jpg':
                        mime_type = 'image/jpeg'
                    elif img_type == 'png':
                        mime_type = 'image/png'
                    elif img_type == 'gif':
                        mime_type = 'image/gif'
                    elif img_type == 'webp':
                        mime_type = 'image/webp'
                    else:
                        # Fallback to extension if magic detection fails
                        ext = os.path.splitext(img_path)[1].lower()
                        if ext == ".png":
                            mime_type = "image/png"
                        elif ext == ".gif":
                            mime_type = "image/gif"
                        elif ext == ".webp":
                            mime_type = "image/webp"
                        elif ext in [".jpg", ".jpeg"]:
                            mime_type = "image/jpeg"
                    
                    self.logger.debug(f"Detected MIME type for image: {mime_type}")
                except (ImportError, Exception) as e:
                    # Fallback to extension if imghdr is not available or fails
                    self.logger.debug(f"MIME type detection failed: {str(e)}, using extension")
                    ext = os.path.splitext(img_path)[1].lower()
                    if ext == ".png":
                        mime_type = "image/png"
                    elif ext == ".gif":
                        mime_type = "image/gif"
                    elif ext == ".webp":
                        mime_type = "image/webp"
                    elif ext in [".jpg", ".jpeg"]:
                        mime_type = "image/jpeg"
                
                # Format image content based on provider
                # Each provider has a different API format for multimodal requests
                if provider == "openai":
                    # OpenAI format (GPT-4V, GPT-4o) - Official API reference:
                    # https://platform.openai.com/docs/guides/vision
                    # 
                    # Example:
                    # {
                    #   "role": "user", 
                    #   "content": [
                    #     {"type": "text", "text": "What's in this image?"},
                    #     {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
                    #   ]
                    # }
                    image_contents.append({
                        "type": "image_url",  # Use image_url type according to latest API
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}",
                            "detail": "high"  # Request high detail for best results
                        }
                    })
                    
                    self.logger.debug(f"Added image in OpenAI format ({len(base64_image)} bytes)")
                    
                elif provider == "anthropic":
                    # Anthropic Claude 3 format - Official API reference:
                    # https://docs.anthropic.com/claude/reference/messages-images
                    #
                    # Example:
                    # {
                    #   "role": "user",
                    #   "content": [
                    #     {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": "..."}},
                    #     {"type": "text", "text": "What's in this image?"}
                    #   ]
                    # }
                    image_contents.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": base64_image
                        }
                    })
                    
                    self.logger.debug(f"Added image in Claude format ({len(base64_image)} bytes)")
                    
                elif provider == "google":
                    # Google Gemini format - Official API reference:
                    # https://ai.google.dev/gemini-api/docs/prompting/images
                    #
                    # Gemini 1.x format:
                    # { 
                    #   "inline_data": { 
                    #     "mime_type": "image/jpeg", 
                    #     "data": "..." 
                    #   }
                    # }
                    #
                    # Gemini 2.0 format:
                    # {
                    #   "inlineData": {
                    #     "mimeType": "image/jpeg",
                    #     "data": "..."
                    #   }
                    # }
                    
                    # Handle both Gemini 1.x and 2.0
                    if model and "2.0" in model:
                        # Gemini 2.0 format (snake_case according to Google API docs)
                        image_contents.append({
                            "inline_data": {  # snake_case for Gemini 2.0
                                "mime_type": mime_type,  # snake_case
                                "data": base64_image
                            }
                        })
                        self.logger.debug(f"Added image in Gemini 2.0 format ({len(base64_image)} bytes)")
                    else:
                        # Gemini 1.x format (snake_case)
                        image_contents.append({
                            "inline_data": {  # snake_case for Gemini 1.0
                                "mime_type": mime_type,  # snake_case
                                "data": base64_image
                            }
                        })
                        self.logger.debug(f"Added image in Gemini 1.x format ({len(base64_image)} bytes)")
                else:
                    # Unknown provider, use a generic format and log warning
                    self.logger.warning(f"Unknown provider '{provider}' for image formatting, using generic format")
                    image_contents.append({
                        "image": {
                            "mime_type": mime_type,
                            "data": base64_image
                        }
                    })
            
            # If user provided a string message, add it to the first message with images
            if isinstance(message, str):
                self.logger.debug(f"Formatting message with text and {len(image_contents)} images for provider {provider}")
                
                # Create a new message with both text and images
                if provider == "openai":
                    # OpenAI format (array of content items)
                    # Auto-upgrade to latest vision model if needed
                    if model and "vision" in model and not "gpt-4o" in model:
                        model = "gpt-4o"
                        self.logger.info(f"Using latest OpenAI vision model: {model}")
                    
                    # Best practice for OpenAI: place text first, then images
                    messages = [{
                        "role": "user",
                        "content": [{"type": "text", "text": message}] + image_contents
                    }]
                    self.logger.debug(f"Created OpenAI format message with {len(image_contents)} images")
                    
                elif provider == "anthropic":
                    # Anthropic Claude 3 format
                    # Best practice for Claude: place images first, then text
                    content = image_contents.copy()
                    content.append({"type": "text", "text": message})
                    
                    messages = [{
                        "role": "user",
                        "content": content
                    }]
                    self.logger.debug(f"Created Claude format message with {len(image_contents)} images")
                    
                elif provider == "google":
                    # Google Gemini format varies between 1.0 and 2.0
                    if model and "2.0" in model:
                        # Gemini 2.0 format
                        messages = [{
                            "role": "user",
                            "parts": [{"text": message}] + image_contents
                        }]
                        self.logger.debug(f"Created Gemini 2.0 format message with {len(image_contents)} images")
                        
                        # For Gemini 2.0 with image generation, we need responseModalities
                        if "image-generation" in model:
                            # Set responseModalities for Gemini 2.0 image generation (using Title Case as per Google docs)
                            kwargs["generationConfig"] = kwargs.get("generationConfig", {})
                            kwargs["generationConfig"]["responseModalities"] = ["Text", "Image"]
                            self.logger.info("Set responseModalities for Gemini 2.0 image generation")
                    else:
                        # Gemini 1.x format
                        messages = [{
                            "role": "user",
                            "parts": [
                                {"text": message},
                                *image_contents
                            ]
                        }]
                        self.logger.debug(f"Created Gemini 1.x format message with {len(image_contents)} images")
            
            # If it's a message array, add images to the last user message
            else:
                self.logger.debug(f"Adding {len(image_contents)} images to message array for provider {provider}")
                
                # Find last user message
                last_user_msg_index = None
                for i in range(len(messages) - 1, -1, -1):
                    if messages[i].get("role") == "user":
                        last_user_msg_index = i
                        break
                        
                if last_user_msg_index is None:
                    # No user messages found, create one
                    self.logger.warning("No user messages found in array, adding a new one with images")
                    if provider == "openai":
                        messages.append({
                            "role": "user",
                            "content": image_contents + [{"type": "text", "text": ""}]
                        })
                    elif provider == "anthropic":
                        messages.append({
                            "role": "user",
                            "content": image_contents + [{"type": "text", "text": ""}]
                        })
                    elif provider == "google":
                        if model and "2.0" in model:
                            messages.append({
                                "role": "user",
                                "parts": [{"text": ""}] + image_contents
                            })
                        else:
                            messages.append({
                                "role": "user",
                                "parts": [{"text": ""}, *image_contents]
                            })
                else:
                    # Add images to the last user message
                    i = last_user_msg_index
                    
                    if provider == "openai":
                        # Convert text to content array with images
                        text_content = messages[i].get("content", "")
                        
                        # Format based on content type
                        if isinstance(text_content, str):
                            # Convert string to text object in array
                            messages[i]["content"] = [{"type": "text", "text": text_content}] + image_contents
                        elif isinstance(text_content, list):
                            # It's already a list, add images
                            # Find text items
                            text_items = [item for item in text_content if item.get("type") == "text"]
                            # Add images
                            messages[i]["content"] = text_items + image_contents
                        else:
                            # Unknown format, convert to standard format
                            self.logger.warning(f"Unexpected content format in OpenAI message: {type(text_content)}")
                            messages[i]["content"] = [{"type": "text", "text": str(text_content)}] + image_contents
                            
                        self.logger.debug(f"Updated OpenAI message with {len(image_contents)} images")
                        
                    elif provider == "anthropic":
                        # Get existing content
                        existing_content = messages[i].get("content", "")
                        
                        if isinstance(existing_content, str):
                            # Convert to content array format
                            # Best practice for Claude: images first, then text
                            messages[i]["content"] = image_contents + [{"type": "text", "text": existing_content}]
                        elif isinstance(existing_content, list):
                            # If it's already an array, add images at the beginning
                            messages[i]["content"] = image_contents + existing_content
                        else:
                            # Unknown format, convert to standard format
                            self.logger.warning(f"Unexpected content format in Claude message: {type(existing_content)}")
                            messages[i]["content"] = image_contents + [{"type": "text", "text": str(existing_content)}]
                            
                        self.logger.debug(f"Updated Claude message with {len(image_contents)} images")
                        
                    elif provider == "google":
                        # For Gemini, handle based on model version
                        if model and "2.0" in model:
                            # Get existing text
                            text_content = messages[i].get("content", "")
                            if isinstance(text_content, str):
                                text_part = {"text": text_content}
                            else:
                                text_part = {"text": str(text_content)}
                                
                            # Add parts with text and images
                            messages[i]["parts"] = [text_part] + image_contents
                            
                            # For Gemini 2.0 with image generation, we need responseModalities
                            if "image-generation" in model:
                                kwargs["generationConfig"] = kwargs.get("generationConfig", {})
                                kwargs["generationConfig"]["responseModalities"] = ["Text", "Image"]
                                self.logger.info("Set responseModalities for Gemini 2.0 image generation")
                        else:
                            # Gemini 1.x format
                            # Get existing text
                            text_content = messages[i].get("content", "")
                            if isinstance(text_content, str):
                                text_part = {"text": text_content}
                            else:
                                text_part = {"text": str(text_content)}
                                
                            # Add parts with text and images
                            messages[i]["parts"] = [text_part, *image_contents]
                            
                        self.logger.debug(f"Updated Gemini message with {len(image_contents)} images")
        
        # Important: Determine provider for model if not explicitly specified
        # This is crucial for ensuring the right provider is used
        if not provider and model:
            provider = get_provider_for_model(model)
            self.logger.debug(f"Setting provider to {provider} based on model name {model}")
        elif not provider:
            provider = get_default_provider()
            self.logger.debug(f"Using default provider: {provider}")
        
        # Prepare request payload with correct provider
        payload = {
            "model": model,
            "messages": messages,
            "provider": provider.lower(),  # Explicitly include provider (lowercase)
            **kwargs
        }
        
        self.logger.debug(f"Final provider used in payload: {provider.lower()}")
        
        # Debug log the full payload
        self.logger.debug(f"Chat request payload: {payload}")
        
        # Make the request
        # Important: Always use v1/mesh/chat for chat completions due to server routing issues
        # with the newer /api/v1/chat/completions endpoint
        url = self._get_url("/v1/mesh/chat")
        self.logger.debug(f"Using legacy endpoint /v1/mesh/chat directly to avoid 404 errors")
        
        # Ensure we're authenticated before making the request
        self.logger.debug("Ensuring authentication before chat request")
        if not self._ensure_authenticated():
            self.logger.error("\u2717 Failed to authenticate for chat request")
            raise Exception("Authentication failed. Please run 'mesh-auth' to authenticate.")
        
        # Get headers with authentication token
        headers = self._get_headers()
        
        # Verify that Authorization header is present
        if "Authorization" not in headers:
            self.logger.error("\u2717 No Authorization header in request despite authentication")
            # Try one more direct approach to add the header
            if self._auth_token:
                token = self._auth_token.strip()
                headers["Authorization"] = f"Bearer {token}"
                self.logger.debug(f"Manually added Authorization header: {token[:5]}...{token[-5:] if len(token) > 10 else ''}")
            else:
                self.logger.error("\u2717 No auth token available after authentication")
        
        # Log detailed request information in debug mode
        self.logger.debug(f"Making API request to: {url}")
        self.logger.debug(f"Request headers: {headers}")
        self.logger.debug(f"Request payload: {json.dumps(payload, indent=2)}")
        
        try:
            self.logger.info(f"Sending chat completion request to {url}")
            response = requests.post(
                url,
                headers=headers,
                json=payload
            )
            self.logger.debug(f"Received response with status code: {response.status_code}")
            self.logger.debug(f"Response headers: {dict(response.headers)}")
            
            # If we get a 404 using the /v1/mesh/chat endpoint, try the old /api/v1/chat/completions as a fallback
            # Also try to create the user profile if it doesn't exist
            if response.status_code == 404:
                # First, check if this is a retry attempt to avoid infinite loops
                if _retry_attempt < 2:  # Limit to 2 retries
                    # Try to create the user by calling the profile endpoint
                    self.logger.warning("Received 404 error, attempting to create user profile")
                    profile_created = self._fetch_user_profile()
                    
                    if profile_created:
                        self.logger.info("User profile created/fetched successfully, retrying chat request")
                        # Retry the request with increased retry counter
                        return self.chat(
                            message=message,
                            model=model,
                            provider=provider,
                            _retry_attempt=_retry_attempt + 1,
                            **kwargs
                        )
                
                # Original fallback logic
                if '/v1/mesh/chat' in url:
                    fallback_url = f"{self.api_url}/api/v1/chat/completions"
                    self.logger.warning(f"Legacy endpoint returned 404. Trying fallback to {fallback_url}")
                    
                    # Make fallback request to standardized endpoint
                    fallback_response = requests.post(
                        fallback_url,
                        headers=headers,
                        json=payload
                    )
                    
                    if fallback_response.status_code == 200:
                        self.logger.info("Fallback to standardized endpoint succeeded")
                        response = fallback_response
                    else:
                        self.logger.warning(f"Fallback also failed with status code: {fallback_response.status_code}")
                        # Continue with original response and error handling
            
            if response.status_code == 200:
                result = response.json()
                
                # Format response based on configuration
                # Debug log raw result
                self.logger.debug(f"Raw API response: {result}")
                
                if self.config["return_content_only"]:
                    # Try to extract content from different response formats
                    # 1. Check standard OpenAI format
                    if "choices" in result and len(result["choices"]) > 0:
                        message = result["choices"][0].get("message", {})
                        content = message.get("content", "")
                        if content:
                            return content
                    
                    # 2. Check for direct content field (server might be normalizing responses)
                    if "content" in result:
                        return result["content"]
                        
                    # 3. Try format used by some providers
                    if "message" in result:
                        return result["message"].get("content", "")
                    
                    # If we can't find content in any recognized format, return empty string
                    self.logger.warning(f"Could not extract content from response: {result}")
                    return ""
                else:
                    # Return the full response
                    return result
            else:
                # Create clear error messages
                status_code = response.status_code
                error_msg = f"Chat request failed: {status_code}"
                
                # Log the error with detailed information
                self.logger.error(f"Request to {url} failed with status {status_code}")
                
                # Try to log response content for debugging
                try:
                    response_text = response.text
                    self.logger.debug(f"Response content: {response_text[:500]}{'...' if len(response_text) > 500 else ''}")
                except Exception as e:
                    self.logger.debug(f"Could not read response content: {str(e)}")
                
                # Provide more specific error messages for common status codes
                if status_code == 404:
                    self.logger.error("404 Error: This could be due to authentication failure or the endpoint not existing")
                    # Log authentication details for debugging
                    self.logger.debug(f"Authentication token present: {bool(self._auth_token)}")
                    self.logger.debug(f"API URL: {self.api_url}")
                    self.logger.debug(f"Endpoint: {url}")
                    
                    # Extract endpoint from URL for error messages
                    endpoint_path = url.replace(self.api_url, '')
                    
                    # Check if we have a valid token
                    if not self._auth_token:
                        error_msg = f"Chat request failed (404): No authentication token found. Please authenticate using 'mesh-auth' command."
                    elif '/v1/mesh/chat' in url:
                        # We're already using the legacy endpoint which should work
                        error_msg = f"Chat request failed (404): Server configuration issue. The server at {self.api_url} is not properly handling the legacy endpoint /v1/mesh/chat. Please report this issue."
                    elif '/api/v1/chat/completions' in url:
                        # Suggest using the direct approach with legacy endpoint
                        error_msg = f"Chat request failed (404): Endpoint not found. Try using MeshClient(api_url='{self.api_url}') and directly call client.chat() instead."
                    else:
                        error_msg = f"Chat request failed (404): Endpoint not found or authentication failed. Verify the API URL and authentication."
                    
                    # Add a special note for mesh.chat() failures with a suggestion to fix
                    if '/chat/completions' in url:
                        self.logger.error("Note: For direct top-level API usage, consider upgrading to mesh-sdk>=1.4.5 which contains a fix for this issue")
                        error_msg += " Please upgrade to mesh-sdk>=1.4.5 with 'pip install --upgrade mesh-sdk'"
                elif status_code == 401 or status_code == 403:
                    error_msg = f"Chat request failed ({status_code}): Authentication failed. Please authenticate using 'mesh-auth' command."
                    self.logger.debug("Authentication token may be invalid or expired")
                
                # Try to get more details from the response
                try:
                    error_data = response.json()
                    self.logger.debug(f"Error response JSON: {json.dumps(error_data, indent=2)}")
                    if "error" in error_data:
                        error_msg = f"{error_msg} - {error_data['error'].get('message', '')}"
                        self.logger.error(f"Error details: {error_data['error']}")
                except Exception as e:
                    self.logger.debug(f"Could not parse error response as JSON: {str(e)}")
                    
                # Raise exception with helpful message
                raise Exception(error_msg)
                
        except requests.RequestException as e:
            # Log detailed information about the request exception
            self.logger.error(f"Request error: {str(e)}")
            self.logger.debug(f"Request exception type: {type(e).__name__}")
            
            # Log more details based on the exception type
            if isinstance(e, requests.ConnectionError):
                self.logger.error(f"Connection error: Could not connect to {url}")
                self.logger.debug("This may indicate that the server is down or unreachable")
            elif isinstance(e, requests.Timeout):
                self.logger.error(f"Timeout error: Request to {url} timed out")
            elif isinstance(e, requests.TooManyRedirects):
                self.logger.error(f"Redirect error: Too many redirects for {url}")
            
            # Raise a more informative exception
            raise Exception(f"Request failed: {str(e)}. Check server availability and network connection.")
    
    def image(
        self,
        prompt: str,
        image_path: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        size: Optional[str] = None,
        n: Optional[int] = None,
        output_path: Optional[str] = None,
        quality: Optional[str] = None,
        response_format: Optional[str] = None,
        **kwargs
    ) -> Union[str, List[str], Dict[str, Any]]:
        """Generate or modify an image using AI.
        
        Args:
            prompt: Text description of the image to generate or modification to apply
            image_path: Path to an input image (if modifying an existing image)
            model: Model to use (e.g., "gemini-1.0-pro-vision", "dall-e-3")
            provider: Provider to use ("google" or "openai")
            size: Size of the output image (e.g., "1024x1024")
            n: Number of images to generate
            output_path: Path to save the generated image(s)
            quality: Image quality (e.g., "standard", "hd")
            response_format: Format of the response ("url" or "b64_json")
            **kwargs: Additional parameters to pass to the provider API
            
        Returns:
            If output_path is specified, returns the output path(s).
            Otherwise, returns the URL(s) or base64 data of the generated image(s).
            If return_content_only is False, returns the full API response.
        """
        import base64
        import os
        from .models import normalize_model_name, get_provider_for_model, get_default_provider
        
        # Check for required parameters
        if not prompt:
            raise ValueError("Prompt is required")
        
        # Ensure we're authenticated
        if not self._ensure_authenticated():
            raise Exception("Authentication failed")
        
        # Determine provider (default: Google for images)
        if not provider:
            provider = get_default_provider() or "google"
        provider = provider.lower()
        
        # Normalize model name if provided
        if model:
            model = normalize_model_name(model)
        else:
            # Default model based on provider
            if provider == "google":
                # Use Gemini 2.0 Flash Experimental for image generation capabilities
                model = "gemini-2.0-flash-exp-image-generation"
            elif provider == "openai":
                model = "dall-e-3"
        
        # Determine endpoint and payload based on whether we're generating or modifying
        if image_path:
            # Image modification - we need to load the image and process it
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Read the image file and convert to base64
            with open(image_path, "rb") as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode("utf-8")
            
            # Use vision endpoint for modification
            endpoint = "/api/v1/images/vision"
            payload = {
                "provider": provider,
                "prompt": prompt,
                "image": image_base64,
                "model": model,
            }
            
            # Add optional parameters
            if response_format:
                payload["response_format"] = response_format
            
            # Add any additional kwargs
            payload.update(kwargs)
            
        else:
            # Image generation - simpler payload
            endpoint = "/api/v1/images/generate"
            payload = {
                "provider": provider,
                "prompt": prompt,
                "model": model
            }
            
            # Add optional parameters
            if size:
                payload["size"] = size
            if n:
                payload["n"] = n
            if quality:
                payload["quality"] = quality
            if response_format:
                payload["response_format"] = response_format
                
            # For Gemini 2.0 Flash Experimental, we need to add responseModalities
            if provider == "google" and "gemini-2.0" in model:
                # Set up generation config with responseModalities (using Title Case as per Google docs)
                payload["generationConfig"] = payload.get("generationConfig", {})
                payload["generationConfig"]["responseModalities"] = ["Text", "Image"]
                self.logger.info("Set responseModalities for Gemini 2.0 image generation")
            
            # Add any additional kwargs
            payload.update(kwargs)
        
        # Get the url and headers
        url = self._get_url(endpoint)
        headers = self._get_headers()
        
        # Make the request
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            # Handle the response
            if response.status_code == 200:
                result = response.json()
                
                # Return full response if requested
                if not self.return_content_only:
                    return result
                
                # Extract image data
                images = []
                
                if "data" in result:
                    for item in result["data"]:
                        if "url" in item:
                            images.append(item["url"])
                        elif "b64_json" in item:
                            images.append(item["b64_json"])
                
                # Save images if output path is specified
                if output_path and images:
                    saved_paths = []
                    
                    for i, image_data in enumerate(images):
                        # Determine file path and extension
                        if n and n > 1:
                            # If multiple images, append index
                            filename, ext = os.path.splitext(output_path)
                            if not ext:
                                ext = ".png"
                            path = f"{filename}_{i}{ext}"
                        else:
                            # Single image
                            path = output_path
                            if not os.path.splitext(path)[1]:
                                # No extension specified, add .png
                                path += ".png"
                        
                        # Save the image
                        if image_data.startswith("http"):
                            # URL - download the image
                            img_response = requests.get(image_data)
                            if img_response.status_code == 200:
                                with open(path, "wb") as f:
                                    f.write(img_response.content)
                                saved_paths.append(path)
                        else:
                            # Base64 - decode and save
                            with open(path, "wb") as f:
                                f.write(base64.b64decode(image_data))
                            saved_paths.append(path)
                    
                    # Return saved paths
                    return saved_paths[0] if len(saved_paths) == 1 else saved_paths
                
                # Return image data
                return images[0] if len(images) == 1 else images
                
            else:
                # Handle error response
                error_msg = f"Image request failed: {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = f"Image request failed: {error_data['error']}"
                except:
                    pass
                
                raise Exception(error_msg)
                
        except requests.RequestException as e:
            # Handle request exceptions
            raise Exception(f"Image request failed: {str(e)}")
    
    def stream_chat(
        self, 
        message: Union[str, List[Dict[str, str]]], 
        model: Optional[str] = None, 
        provider: Optional[str] = None,
        **kwargs
    ):
        """
        Stream a chat response from an AI model
        
        This method returns a generator that yields response chunks as they arrive.
        
        Args:
            message: The message to send (string or message array)
            model: The model to use (e.g. "gpt-4", "claude-3-5-sonnet")
            provider: The provider to use (e.g. "openai", "anthropic")
            **kwargs: Additional options for the chat request
            
        Yields:
            str: Response chunks as they arrive
        """
        # Ensure we're authenticated
        if not self._ensure_authenticated():
            raise Exception("Authentication failed")
        
        # Determine provider and model
        provider = (provider or get_default_provider()).lower()
        
        if model:
            # Normalize the model name if provided
            model = normalize_model_name(model)
        else:
            # Use default model for the provider
            model = get_default_model(provider)
        
        # If provider wasn't specified but model was, infer provider from model
        if not provider and model:
            provider = get_provider_for_model(model)
        
        # Convert string message to message array if needed
        messages = []
        if isinstance(message, str):
            messages = [{"role": "user", "content": message}]
        elif isinstance(message, list):
            messages = message
        else:
            raise ValueError("Message must be a string or a list of message objects")
        
        # Prepare request payload
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            **kwargs
        }
        
        # Make the request
        url = self._get_url("/api/v1/chat/completions")
        headers = self._get_headers()
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                stream=True
            )
            
            if response.status_code == 200:
                # Process the stream
                content = ""
                for line in response.iter_lines():
                    if line:
                        # Remove "data: " prefix if present
                        line_text = line.decode('utf-8')
                        if line_text.startswith("data: "):
                            line_text = line_text[6:]
                        
                        # Skip any non-JSON lines
                        if not line_text or line_text == "[DONE]":
                            continue
                        
                        try:
                            data = json.loads(line_text)
                            
                            # Extract content from response
                            if "choices" in data and len(data["choices"]) > 0:
                                chunk = data["choices"][0]
                                if "delta" in chunk and "content" in chunk["delta"]:
                                    content_chunk = chunk["delta"]["content"]
                                    content += content_chunk
                                    yield content_chunk
                        except json.JSONDecodeError:
                            # Skip invalid JSON
                            pass
            else:
                error_msg = f"Stream chat request failed: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = f"{error_msg} - {error_data.get('error', {}).get('message', '')}"
                except:
                    pass
                
                raise Exception(error_msg)
                
        except requests.RequestException as e:
            raise Exception(f"Stream request failed: {str(e)}")