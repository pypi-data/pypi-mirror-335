#!/usr/bin/env python
"""
CLI tool to create a .env file with Mesh token information for deployment environments.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

from ..auth import authenticate, is_authenticated
from ..token_manager import get_token, HEADLESS_MODE

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def create_env_file(output_path=None, force=False):
    """
    Create a .env file with Mesh token information for deployment.
    
    Args:
        output_path: Path to write the .env file to. If None, writes to ./.env
        force: If True, overwrites existing file without asking
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Determine output path
    if not output_path:
        output_path = os.path.join(os.getcwd(), ".env")
    output_path = os.path.abspath(output_path)
    
    # Check if file exists
    if os.path.exists(output_path) and not force:
        response = input(f"File {output_path} already exists. Overwrite? (y/N): ")
        if response.lower() != "y":
            logger.info("Operation cancelled.")
            return False
    
    # Check if authenticated
    if not is_authenticated():
        logger.info("Not authenticated. Starting authentication process...")
        
        # Force headless mode for authentication
        os.environ["MESH_HEADLESS"] = "true"
        
        # Authenticate and get token
        token_data = authenticate(headless=True)
        if not token_data:
            logger.error("Authentication failed. Please try again.")
            return False
    
    # Get token data
    token_data = get_token()
    if not token_data or "access_token" not in token_data or "refresh_token" not in token_data:
        logger.error("No valid token found. Please authenticate first.")
        return False
    
    # Create .env file content
    env_content = """# Mesh SDK Environment Variables
# Generated for deployment environments (Render, etc.)
# Copy these variables to your deployment environment
MESH_HEADLESS=true
MESH_TOKEN_FROM_ENV=true
"""
    # Add token data
    env_content += f"MESH_ACCESS_TOKEN={token_data['access_token']}\n"
    env_content += f"MESH_REFRESH_TOKEN={token_data['refresh_token']}\n"
    
    expires_at = token_data.get("expires_at", 0)
    env_content += f"MESH_TOKEN_EXPIRES_AT={expires_at}\n"
    env_content += "MESH_EXTENDED_TOKEN_LIFETIME=true\n"
    
    # Add expiration info as comment
    if expires_at:
        import datetime
        expiry_date = datetime.datetime.fromtimestamp(expires_at).strftime('%Y-%m-%d %H:%M:%S')
        env_content += f"\n# Token expires: {expiry_date}\n"
    
    # Write to file
    try:
        with open(output_path, "w") as f:
            f.write(env_content)
        
        # Set permissions to be secure
        try:
            os.chmod(output_path, 0o600)  # Read/write for owner only
        except Exception as e:
            logger.warning(f"Could not set file permissions: {e}")
        
        logger.info(f"✅ Environment file created: {output_path}")
        logger.info(f"   Now you can upload this file to your deployment platform")
        logger.info(f"   or copy the variables to your environment settings.")
        return True
    except Exception as e:
        logger.error(f"Error creating .env file: {e}")
        return False


def main():
    """Main entry point for the command."""
    parser = argparse.ArgumentParser(
        description="Create a .env file with Mesh token information for deployment environments."
    )
    parser.add_argument(
        "-o", "--output", 
        help="Path to write the .env file to (default: ./.env)"
    )
    parser.add_argument(
        "-f", "--force", 
        action="store_true", 
        help="Overwrite existing file without asking"
    )
    args = parser.parse_args()
    
    success = create_env_file(args.output, args.force)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
