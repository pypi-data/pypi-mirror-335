#!/usr/bin/env python3
"""
Test script for the Mesh SDK authentication flow.

This script tests the authentication flow for the Mesh SDK.
It attempts to authenticate using the backend-managed flow.
"""

import logging
import os
import sys
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mesh.test")

# Import Mesh SDK
from mesh_improved import auth, token_manager

def test_auth():
    """Test the authentication flow"""
    # Clear any existing tokens
    token_manager.clear_token()
    print("Testing authentication...")
    
    # Try to authenticate
    token_data = auth.authenticate()
    
    if token_data and "access_token" in token_data:
        print(f"Authentication successful!")
        print(f"Token expires at: {time.ctime(token_data.get('expires_at', 0))}")
        if "refresh_token" in token_data:
            print("Refresh token is available for automatic renewal")
        return True
    else:
        print("Authentication failed.")
        return False

def test_refresh():
    """Test token refresh"""
    # Try to get an existing token
    token_data = token_manager.get_token()
    
    if not token_data or "refresh_token" not in token_data:
        print("No refresh token available. Please authenticate first.")
        return False
    
    print("Testing token refresh...")
    
    # Try to refresh the token
    new_token_data = auth.refresh_auth_token(token_data.get("refresh_token"))
    
    if new_token_data and "access_token" in new_token_data:
        print(f"Token refresh successful!")
        print(f"New token expires at: {time.ctime(new_token_data.get('expires_at', 0))}")
        return True
    else:
        print("Token refresh failed.")
        return False

if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "refresh":
            test_refresh()
        elif sys.argv[1] == "clear":
            token_manager.clear_token()
            print("Tokens cleared.")
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Usage: test_auth.py [refresh|clear]")
    else:
        test_auth()