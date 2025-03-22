#!/usr/bin/env python3
"""
Mesh Authentication CLI

This script provides a command-line interface for authenticating with Mesh.
It can be used directly or as a post-install script.
"""

import os
import sys
import argparse
import logging
from . import auth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mesh.auth_cli")

def main():
    """Run the authentication flow"""
    parser = argparse.ArgumentParser(description="Authenticate with Mesh")
    parser.add_argument("--force", action="store_true", help="Force a new login even if already authenticated")
    parser.add_argument("--headless", action="store_true", help="Use device code flow instead of browser")
    parser.add_argument("--clear", action="store_true", help="Clear existing tokens and exit")
    args = parser.parse_args()
    
    if args.clear:
        from .token_manager import clear_token
        clear_token()
        print("Authentication tokens cleared successfully.")
        return 0
    
    print("Starting Mesh authentication...")
    
    try:
        if args.force:
            # Clear existing token first if forcing re-authentication
            from .token_manager import clear_token
            clear_token()
        
        # Authenticate with the appropriate flow
        token_data = auth.authenticate(headless=args.headless)
        
        if token_data:
            print("\n✅ Authentication successful!")
            print("You can now use the Mesh SDK without further authentication.")
            return 0
        else:
            print("\n❌ Authentication failed.")
            print("Please try again or use the --headless option for a device code flow.")
            return 1
            
    except KeyboardInterrupt:
        print("\nAuthentication cancelled.")
        return 1
    except Exception as e:
        print(f"\n❌ Error during authentication: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())