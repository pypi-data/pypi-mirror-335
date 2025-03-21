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
        # First try to store in system keychain
        token_json = json.dumps(token_data)
        logger.debug(f"Token JSON serialized, length: {len(token_json)} characters")
        
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
    
    # First try system keychain
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
    
    # Fall back to file storage
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
    logger.debug(f"Attempting to clear token from all storage locations")
    success = True
    
    # Clear from keychain
    try:
        logger.debug(f"Attempting to delete token from keyring (service={SERVICE_NAME}, username={USERNAME})")
        keyring.delete_password(SERVICE_NAME, USERNAME)
        logger.debug("✓ Token successfully cleared from keychain")
    except Exception as e:
        logger.warning(f"✗ Could not clear token from keychain: {str(e)}")
        logger.debug(f"Keyring backend being used: {keyring.get_keyring().__class__.__name__}")
        success = False
    
    # Clear from file
    logger.debug(f"Checking for token file at {TOKEN_FILE_PATH}")
    if os.path.exists(TOKEN_FILE_PATH):
        try:
            logger.debug(f"Token file exists, attempting to remove")
            os.remove(TOKEN_FILE_PATH)
            logger.debug("✓ Token successfully cleared from file")
        except Exception as e:
            logger.warning(f"✗ Could not clear token from file: {str(e)}")
            success = False
    else:
        logger.debug("No token file found to clear")
    
    if success:
        logger.debug("✓ Token successfully cleared from all storage locations")
    else:
        logger.warning("⚠ Token clearing was partially successful or failed")
        
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