"""
Mesh API Key Generation for Pre-Deployment

This CLI tool generates an API key for use in headless environments (servers, CI/CD).
It provides a more reliable authentication method than token-based auth for deployments.
"""

import sys
import os
import json
import logging
import argparse
import requests
import random
import string
from typing import Dict, Any, Optional, Tuple

from mesh.auth import authenticate, is_authenticated
from mesh.token_manager import get_token, print_token_env_instructions
from mesh.config import get_api_url

# Configure logging
logger = logging.getLogger("mesh.cli.pre_deploy")

def generate_api_key(name: str = None) -> Optional[Dict[str, Any]]:
    """
    Generate a new API key for use in headless environments.
    
    Args:
        name: Optional name for the API key (defaults to auto-generated name if not provided)
        
    Returns:
        Dict with API key information or None if generation failed
    """
    # Make sure user is authenticated
    if not is_authenticated():
        print("\n⚠️  Authentication required to generate API key ⚠️")
        print("Please authenticate first...")
        auth_success = authenticate()
        if not auth_success:
            print("\n❌ Authentication failed. Unable to generate API key.")
            return None
    
    # Get token for authorization
    token_data = get_token()
    if not token_data:
        print("\n❌ Failed to retrieve authentication token.")
        return None
    
    # Prepare authorization header
    if "auth_type" in token_data and token_data["auth_type"] == "api_key":
        # Already using API key
        headers = {
            "Authorization": f"ApiKey {token_data['api_key']}"
        }
    else:
        # Using token
        headers = {
            "Authorization": f"Bearer {token_data.get('access_token', '')}"
        }
    
    # Generate a descriptive name if not provided
    if not name:
        # Generate random suffix
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        import platform
        import socket
        system = platform.system().lower()
        try:
            hostname = socket.gethostname()
            # Use only first part of hostname for privacy
            hostname_part = hostname.split('.')[0]
            # Limit length
            if len(hostname_part) > 15:
                hostname_part = hostname_part[:15]
        except:
            hostname_part = "unknown"
            
        name = f"{system}-{hostname_part}-{suffix}"
    
    # Call API to create key
    try:
        url = f"{get_api_url()}/api/v1/api-keys"
        payload = {"name": name}
        
        print(f"\n🔑 Generating API key named '{name}'...")
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            error_msg = f"Error {response.status_code}"
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_msg = f"Error: {error_data['error']}"
            except:
                pass
            print(f"\n❌ Failed to generate API key: {error_msg}")
            return None
            
        api_key_data = response.json()
        if not api_key_data.get("success") or "api_key" not in api_key_data:
            print("\n❌ Failed to generate API key: Invalid server response")
            return None
            
        return api_key_data["api_key"]
        
    except Exception as e:
        print(f"\n❌ Failed to generate API key: {str(e)}")
        return None

def print_api_key_instructions(api_key_data: Dict[str, Any]) -> None:
    """
    Print the API key information with deployment instructions.
    
    Args:
        api_key_data: API key data from server response
    """
    # Extract API key info
    api_key = api_key_data.get("api_key", "")
    key_id = api_key_data.get("key_id", "")
    name = api_key_data.get("name", "")
    created_at = api_key_data.get("created_at", "")
    
    # Create a more user-friendly display
    print("\n" + "=" * 60)
    print("🎉 API KEY GENERATED SUCCESSFULLY! 🎉".center(60))
    print("=" * 60)
    
    print("\n📋 API KEY DETAILS:")
    print(f"  • ID: {key_id}")
    print(f"  • Name: {name}")
    print(f"  • Created: {created_at}")
    
    print("\n🔐 API KEY (COPY THIS, IT WILL ONLY BE SHOWN ONCE):")
    print(f"  {api_key}")
    
    print("\n📝 ENVIRONMENT VARIABLE:")
    print("  Add this to your deployment environment (Render, Heroku, etc.):")
    print(f"  MESH_API_KEY={api_key}")
    
    print("\n📦 .ENV FILE FORMAT:")
    print(f"  MESH_API_KEY='{api_key}'")
    
    print("\n🚀 USAGE INSTRUCTIONS:")
    print("  1. Set the MESH_API_KEY environment variable in your deployment")
    print("  2. The SDK will automatically use this API key in headless environments")
    print("  3. API keys don't expire, but can be revoked at any time")
    print("  4. For security, keep this key secret and never commit it to source control")
    print("  5. You can manage API keys through the Mesh web interface")
    
    print("\n⚠️  IMPORTANT: This API key will ONLY be shown once!")
    print("   If you lose it, you'll need to generate a new one.")
    print("=" * 60)

def run_pre_deploy() -> int:
    """
    CLI entrypoint for mesh-pre-deploy command
    
    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="Generate an API key for headless environments (servers, CI/CD)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mesh-pre-deploy                      Generate API key with auto-generated name
  mesh-pre-deploy --name "prod-server" Generate API key named "prod-server"
"""
    )
    
    parser.add_argument(
        "--name", "-n",
        help="Custom name for the API key (default: auto-generated)",
        type=str,
        default=None
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Generate API key
    api_key_data = generate_api_key(args.name)
    
    if not api_key_data:
        return 1
        
    # Print instructions
    print_api_key_instructions(api_key_data)
    
    return 0

if __name__ == "__main__":
    sys.exit(run_pre_deploy())
