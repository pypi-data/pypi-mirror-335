"""
Token Manager for Mesh SDK

This module handles secure storage and retrieval of authentication tokens
using the system keychain or secure storage.
"""

import os
import json
import time
import logging
import keyring
import platform
import sys
from pathlib import Path

# Configure logging
logger = logging.getLogger("mesh.token_manager")

# Set debug level if DEBUG environment variable is set
if os.environ.get("DEBUG", "").lower() in ('true', '1', 'yes'):
    logger.setLevel(logging.DEBUG)
    # Add a handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

# Constants for token storage
SERVICE_NAME = "mesh-sdk"
USERNAME = "default"

# Determine if we're in a headless environment
def is_headless() -> bool:
    """Detect if we're running in a headless environment"""
    # Check for explicit headless flag
    if os.environ.get("MESH_HEADLESS", "").lower() in ('true', '1', 'yes'):
        logger.debug("MESH_HEADLESS environment variable set to true")
        return True
        
    # Check for common server/container environment variables
    for env_var in ["DOCKER", "KUBERNETES_SERVICE_HOST", "RENDER", "AWS_LAMBDA_FUNCTION_NAME", "GOOGLE_CLOUD_PROJECT"]:
        if os.environ.get(env_var):
            logger.debug(f"Detected server environment: {env_var} is set")
            return True
    
    # Check for CI/CD environments
    for env_var in ["CI", "GITHUB_ACTIONS", "GITLAB_CI", "TRAVIS", "JENKINS_URL"]:
        if os.environ.get(env_var):
            logger.debug(f"Detected CI environment: {env_var} is set")
            return True
            
    # Check for display environment on Linux
    if platform.system() == "Linux" and not os.environ.get("DISPLAY"):
        logger.debug("No DISPLAY environment variable on Linux - likely headless")
        return True
        
    # Check for IPython/Jupyter environments
    try:
        if 'ipykernel' in sys.modules or 'IPython' in sys.modules:
            logger.debug("Detected IPython/Jupyter environment")
            # IPython/Jupyter typically means no system keychain access
            return True
    except Exception:
        pass
        
    return False

# Determine token storage location based on environment
HEADLESS_MODE = is_headless()

# Set token file path - use alternate location for containers/servers
if HEADLESS_MODE:
    # For headless environments, store in a location that's likely to be writable
    # First try the current working directory
    TOKEN_FILE_PATH = os.path.join(os.getcwd(), ".mesh_token.json")
    # If that's not writable, use /tmp or equivalent
    if not os.access(os.path.dirname(TOKEN_FILE_PATH), os.W_OK):
        TOKEN_FILE_PATH = os.path.join(os.path.join(os.path.sep, "tmp"), ".mesh_token.json")
        
    logger.debug(f"Headless mode detected - using token file path: {TOKEN_FILE_PATH}")
else:
    # For desktop environments, use home directory
    TOKEN_FILE_PATH = os.path.join(str(Path.home()), ".mesh", "token.json")

def _ensure_dir_exists(file_path: str) -> None:
    """Ensure the directory for a file exists"""
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def store_token(token_data: dict) -> bool:
    """Store token data securely
    
    Args:
        token_data: Token data including access_token, expires_at, etc.
        
    Returns:
        bool: True if token was stored successfully
    """
    if not token_data:
        logger.error("Attempted to store empty token data")
        return False
        
    logger.debug(f"Storing token data: access_token present: {bool('access_token' in token_data)}, "  
                f"expires_at: {token_data.get('expires_at', 'not set')}, "  
                f"refresh_token present: {bool('refresh_token' in token_data)}")
    
    try:
        # Serialize token data
        token_json = json.dumps(token_data)
        logger.debug(f"Token JSON serialized, length: {len(token_json)} characters")
        
        # In headless environments, prioritize file storage
        if HEADLESS_MODE:
            logger.debug(f"Headless environment detected - using file storage at {TOKEN_FILE_PATH}")
            # Ensure the directory exists
            _ensure_dir_exists(TOKEN_FILE_PATH)
            
            # Write the token to file
            with open(TOKEN_FILE_PATH, "w") as f:
                json.dump(token_data, f)
            logger.debug(f"Token data written to file, size: {os.path.getsize(TOKEN_FILE_PATH)} bytes")
            
            # Set proper permissions on the file if possible
            try:
                os.chmod(TOKEN_FILE_PATH, 0o600)  # Read/write only for the owner
                logger.debug("File permissions set to 0600 (owner read/write only)")
            except Exception as perm_error:
                logger.warning(f"Could not set file permissions: {str(perm_error)}")
                
            logger.debug("✓ Token stored in file for headless environment")
            return True
        else:
            # In desktop environments, try keychain first
            try:
                logger.debug(f"Attempting to store token in keyring using service={SERVICE_NAME}, username={USERNAME}")
                keyring.set_password(SERVICE_NAME, USERNAME, token_json)
                logger.debug("✓ Token successfully stored in system keychain")
                return True
            except Exception as e:
                logger.warning(f"✗ Could not store token in keychain: {str(e)}")
                logger.debug(f"Keyring backend being used: {keyring.get_keyring().__class__.__name__}")
                
                # Fall back to file storage with best-effort security
                logger.debug(f"Falling back to file storage at {TOKEN_FILE_PATH}")
                _ensure_dir_exists(TOKEN_FILE_PATH)
                with open(TOKEN_FILE_PATH, "w") as f:
                    json.dump(token_data, f)
                logger.debug(f"Token data written to file, size: {os.path.getsize(TOKEN_FILE_PATH)} bytes")
                
                # Set proper permissions on the file
                try:
                    os.chmod(TOKEN_FILE_PATH, 0o600)  # Read/write only for the owner
                    logger.debug("File permissions set to 0600 (owner read/write only)")
                except Exception as perm_error:
                    logger.warning(f"Could not set file permissions: {str(perm_error)}")
                
                logger.debug("✓ Token stored in file as fallback")
                return True
    except Exception as e:
        logger.error(f"✗ Failed to store token: {str(e)}")
        return False

def get_token() -> dict:
    """Retrieve token data
    
    Returns:
        dict: Token data or None if not found
    """
    logger.debug(f"Attempting to retrieve token data")
    
    # In headless environments, prioritize file storage
    if HEADLESS_MODE:
        logger.debug(f"Headless environment detected - checking for token file at {TOKEN_FILE_PATH}")
        try:
            if os.path.exists(TOKEN_FILE_PATH):
                logger.debug(f"Token file exists, size: {os.path.getsize(TOKEN_FILE_PATH)} bytes")
                with open(TOKEN_FILE_PATH, "r") as f:
                    try:
                        token_data = json.load(f)
                        logger.debug(f"✓ Token successfully loaded from file")
                        logger.debug(f"Token data: access_token present: {bool('access_token' in token_data)}, "  
                                    f"expires_at: {token_data.get('expires_at', 'not set')}, "  
                                    f"refresh_token present: {bool('refresh_token' in token_data)}")
                        return token_data
                    except json.JSONDecodeError as json_err:
                        logger.error(f"✗ Failed to parse token JSON from file: {str(json_err)}")
                        # Read and log the raw file content for debugging
                        f.seek(0)
                        content = f.read()
                        logger.debug(f"Invalid JSON from file: {content[:50]}..." if len(content) > 50 else f"Invalid JSON: {content}")
            else:
                logger.debug(f"✗ Token file does not exist at {TOKEN_FILE_PATH}")
        except Exception as e:
            logger.warning(f"✗ Could not read token from file: {str(e)}")
    else:
        # First try system keychain for desktop environments
        try:
            logger.debug(f"Trying to get token from keyring using service={SERVICE_NAME}, username={USERNAME}")
            logger.debug(f"Keyring backend being used: {keyring.get_keyring().__class__.__name__}")
            
            token_json = keyring.get_password(SERVICE_NAME, USERNAME)
            if token_json:
                logger.debug(f"✓ Token found in keyring, JSON length: {len(token_json)} characters")
                try:
                    token_data = json.loads(token_json)
                    logger.debug(f"✓ Token JSON successfully parsed")
                    logger.debug(f"Token data: access_token present: {bool('access_token' in token_data)}, "  
                                f"expires_at: {token_data.get('expires_at', 'not set')}, "  
                                f"refresh_token present: {bool('refresh_token' in token_data)}")
                    return token_data
                except json.JSONDecodeError as json_err:
                    logger.error(f"✗ Failed to parse token JSON from keyring: {str(json_err)}")
                    logger.debug(f"Invalid JSON from keyring: {token_json[:50]}..." if len(token_json) > 50 else f"Invalid JSON: {token_json}")
            else:
                logger.debug(f"✗ No token found in keyring")
        except Exception as e:
            logger.warning(f"✗ Could not retrieve token from keychain: {str(e)}")
        
        # Fall back to file storage for desktop environments
        logger.debug(f"Checking for token file at {TOKEN_FILE_PATH}")
        try:
            if os.path.exists(TOKEN_FILE_PATH):
                logger.debug(f"Token file exists, size: {os.path.getsize(TOKEN_FILE_PATH)} bytes")
                with open(TOKEN_FILE_PATH, "r") as f:
                    try:
                        token_data = json.load(f)
                        logger.debug(f"✓ Token successfully loaded from file")
                        logger.debug(f"Token data: access_token present: {bool('access_token' in token_data)}, "  
                                    f"expires_at: {token_data.get('expires_at', 'not set')}, "  
                                    f"refresh_token present: {bool('refresh_token' in token_data)}")
                        return token_data
                    except json.JSONDecodeError as json_err:
                        logger.error(f"✗ Failed to parse token JSON from file: {str(json_err)}")
                        # Read and log the raw file content for debugging
                        f.seek(0)
                        content = f.read()
                        logger.debug(f"Invalid JSON from file: {content[:50]}..." if len(content) > 50 else f"Invalid JSON: {content}")
            else:
                logger.debug(f"✗ Token file does not exist")
        except Exception as e:
            logger.warning(f"✗ Could not read token from file: {str(e)}")
    
    logger.debug(f"✗ No valid token found in keyring or file storage")
    return None

# Alias for get_token for consistency with naming in other parts of the code
def load_token() -> dict:
    """Alias for get_token() - Retrieve token data
    
    Returns:
        dict: Token data or None if not found
    """
    return get_token()

def clear_token() -> bool:
    """Clear stored token
    
    Returns:
        bool: True if token was cleared successfully
    """
    logger.debug(f"Attempting to clear token data")
    success = False
    
    # Handle based on environment
    if HEADLESS_MODE:
        logger.debug(f"Headless environment detected - only clearing token file")
        # Only clear from file in headless environments
        if os.path.exists(TOKEN_FILE_PATH):
            try:
                logger.debug(f"Token file exists at {TOKEN_FILE_PATH}, attempting to remove")
                os.remove(TOKEN_FILE_PATH)
                logger.debug("✓ Token successfully cleared from file")
                success = True
            except Exception as e:
                logger.warning(f"✗ Could not clear token from file: {str(e)}")
        else:
            logger.debug(f"No token file found at {TOKEN_FILE_PATH}")
            # Mark as success if there's nothing to clear
            success = True
    else:
        # In desktop environments, clear from both keychain and file
        keychain_success = False
        file_success = False
        
        # Clear from keychain
        try:
            logger.debug(f"Attempting to delete token from keyring (service={SERVICE_NAME}, username={USERNAME})")
            keyring.delete_password(SERVICE_NAME, USERNAME)
            logger.debug("✓ Token successfully cleared from keychain")
            keychain_success = True
        except Exception as e:
            logger.warning(f"✗ Could not clear token from keychain: {str(e)}")
            logger.debug(f"Keyring backend being used: {keyring.get_keyring().__class__.__name__}")
        
        # Clear from file
        if os.path.exists(TOKEN_FILE_PATH):
            try:
                logger.debug(f"Token file exists at {TOKEN_FILE_PATH}, attempting to remove")
                os.remove(TOKEN_FILE_PATH)
                logger.debug("✓ Token successfully cleared from file")
                file_success = True
            except Exception as e:
                logger.warning(f"✗ Could not clear token from file: {str(e)}")
        else:
            logger.debug(f"No token file found at {TOKEN_FILE_PATH}")
            # Mark file clearing as success if there's no file to clear
            file_success = True
        
        # Success if at least one method worked
        success = keychain_success or file_success
    
    if success:
        logger.debug("✓ Token successfully cleared")
    else:
        logger.error("✗ Failed to clear token")
        
    return success

def is_token_valid(token_data: dict) -> bool:
    """Check if token is still valid
    
    Args:
        token_data: Token data including expires_at
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    logger.debug(f"Checking token validity")
    
    if not token_data:
        logger.debug(f"✗ Token data is None or empty")
        return False
    
    # Check for access token
    if "access_token" not in token_data:
        logger.debug(f"✗ No access_token field in token data")
        return False
    
    # Check access token format
    access_token = token_data.get("access_token")
    if not access_token or not isinstance(access_token, str) or len(access_token) < 10:
        logger.debug(f"✗ Invalid access_token format or length")
        return False
    
    # Check for expiration
    if "expires_at" not in token_data:
        logger.debug(f"✗ No expires_at field in token data")
        return False
        
    expires_at = token_data.get("expires_at", 0)
    current_time = time.time()
    
    # Add buffer time to avoid edge cases
    buffer_seconds = 300  # 5 minutes
    is_valid = current_time < expires_at - buffer_seconds
    
    if is_valid:
        # Calculate and log time until expiration
        time_left = expires_at - current_time
        hours, remainder = divmod(time_left, 3600)
        minutes, seconds = divmod(remainder, 60)
        logger.debug(f"✓ Token is valid. Expires in: {int(hours)}h {int(minutes)}m {int(seconds)}s")
    else:
        # Log expiration information
        if current_time > expires_at:
            expired_ago = current_time - expires_at
            hours, remainder = divmod(expired_ago, 3600)
            minutes, seconds = divmod(remainder, 60)
            logger.debug(f"✗ Token has expired {int(hours)}h {int(minutes)}m {int(seconds)}s ago")
        else:
            # Token is in the buffer zone
            buffer_time = expires_at - current_time
            minutes, seconds = divmod(buffer_time, 60)
            logger.debug(f"✗ Token is in buffer zone, expires in {int(minutes)}m {int(seconds)}s (buffer is {buffer_seconds/60}m)")
    
    return is_valid