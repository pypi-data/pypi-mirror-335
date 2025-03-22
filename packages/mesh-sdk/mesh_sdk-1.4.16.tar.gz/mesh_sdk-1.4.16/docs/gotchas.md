# Mesh SDK Gotchas and Edge Cases

## Package Naming

- The SDK is published on PyPI as `mesh-sdk` (not `mesh`)
- All imports still use `import mesh` despite the package being named `mesh-sdk`
- Installation is done via `pip install mesh-sdk`

## Authentication

- The backend validation endpoint `/auth/validate` may return 404 on some server configurations
- The SDK automatically falls back to local validation when backend validation fails
- Direct token authentication via `auth_token` property is deprecated and will be removed in a future version
- **404 Errors**: When calling `mesh.chat()` or other API endpoints, a 404 error often indicates an authentication issue rather than a missing endpoint. The server returns 404 instead of 401 for security reasons.

## Network Issues

- All API requests include a configurable timeout parameter (default: 60 seconds)
- When backend validation endpoints are unavailable, local validation is used as a fallback
- If authentication server is unreachable during initial login, the browser-based flow may hang

## Installation Issues

- Post-install authentication may fail in CI/CD environments
- The `mesh-auth` command-line tool can be used to authenticate manually when needed
- Python environments with strict external management settings may require using `--break-system-packages` or virtual environments

## Import Concerns

- Top-level functions (e.g., `mesh.chat()`) will automatically trigger authentication when needed
- The module structure maintains backward compatibility despite the package name change
- Environment variables are still used the same way regardless of package name

## Headless Authentication

### Understanding Headless Mode

Headless mode is activated in one of these conditions:

- When the `MESH_HEADLESS` environment variable is set to `true`, `1`, or `yes`
- When running in a container or server environment without a display
- When running in certain CI/CD environments

### Token Storage in Headless Environments

- In headless environments, authentication tokens are stored in a file (`~/.mesh/token.json`)
- In desktop environments, tokens are stored primarily in the system keychain, with file storage as a fallback
- The SDK automatically detects headless environments and adjusts storage methods accordingly

### Environment Variable Token Storage

For ephemeral environments like Render where the filesystem doesn't persist between deployments, you can store tokens in environment variables.

#### Automatic Token Printing

In headless environments, the SDK will automatically print token information and instructions when you authenticate. This makes it easy to deploy your application on platforms like Render:

1. Run your application locally in headless mode once to authenticate
2. Copy the printed environment variables to your Render dashboard
3. Deploy your application with these environment variables set

#### Manual Token Printing

The SDK also includes a utility to manually print your current tokens in a format suitable for environment variables:

```bash
python -c "from mesh.token_manager import print_token_env_instructions; print_token_env_instructions()"
```

#### Environment File Generation

For easier deployment, the SDK includes a CLI utility that automatically creates a `.env` file with your current token information:

```bash
# Generate a .env file in the current directory
mesh-env

# Specify a custom output path
mesh-env -o /path/to/my-env-file.env

# Force overwrite without confirmation prompt
mesh-env -f
```

This command will:
1. Automatically authenticate if you're not already authenticated
2. Create a secure `.env` file with all required environment variables
3. Add expiration information as a comment

You can then:
- Upload this file to your deployment platform
- Copy the variables to your environment settings in Render or similar platforms
- Use a tool like `python-dotenv` to load these variables in your application

```bash
# Run this after authenticating to get your token information
python -m mesh.cli.print_tokens
```

Both the automatic and manual token printing will output your tokens with instructions for both shell environments and Render dashboard:

```bash
# Enable environment variable token storage
export MESH_TOKEN_FROM_ENV=true

# Set token values in environment
export MESH_ACCESS_TOKEN=your_access_token
export MESH_REFRESH_TOKEN=your_refresh_token
export MESH_TOKEN_EXPIRES_AT=expiration_timestamp
```

You can then copy these values to your Render dashboard as environment variables for your deployment.

### Extended Token Lifetimes

By default, the SDK will request extended token lifetimes in headless environments to reduce the frequency of re-authentication. This behavior can be controlled with:

```bash
# Enable extended token lifetimes (default is true)
export MESH_EXTENDED_TOKEN_LIFETIME=true
```

Extended tokens typically last much longer than standard tokens, making them better suited for long-running server applications.

### Configuring Headless Mode

If you need to force headless mode (for example, if automatic detection fails):

```bash
export MESH_HEADLESS="true"
```

For containerized deployments, include this environment variable in your container configuration:

```yaml
# Docker Compose example
environment:
  - MESH_HEADLESS=true
```

### Troubleshooting Headless Authentication

- If tokens aren't persisting between sessions, ensure the `~/.mesh` directory exists and is writable
- Check logs for token storage issues by enabling debug mode: `export DEBUG="true"`
- In containerized environments, consider mounting a persistent volume at `~/.mesh` to maintain tokens across container restarts

## Troubleshooting 404 Errors

If you encounter a 404 error when using the `mesh.chat()` function or other API endpoints, follow these steps:

1. **Authenticate**: Run the `mesh-auth` command to ensure you have a valid authentication token:
   ```bash
   mesh-auth
   ```
   If the command is not in your PATH, use the full path as shown in the installation output.

2. **Enable Debug Mode**: Set the DEBUG environment variable to get more detailed error information:
   ```bash
   export DEBUG="true"
   ```

3. **Verify API URL**: If you're running a local server or using a different API endpoint, set the MESH_API_URL environment variable:
   ```bash
   export MESH_API_URL="https://your-api-server.com"
   ```

4. **Check SSL**: If you're seeing SSL-related warnings (e.g., about LibreSSL vs OpenSSL), they are typically informational and not the cause of 404 errors.

5. **Verify Server Status**: Ensure the server at the configured API URL is running and accessible.

## Enhanced Authentication Diagnostics

We've added enhanced logging throughout the authentication process to help diagnose issues. To take advantage of this:

1. **Enable debug mode**:
   ```python
   import os
   os.environ["DEBUG"] = "true"
   ```

2. **Configure detailed logging**:
   ```python
   import logging
   logging.basicConfig(
       level=logging.DEBUG,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       handlers=[
           logging.StreamHandler(),
           logging.FileHandler('mesh_debug.log')
       ]
   )
   ```

3. **Use the diagnostic script**:
   
   We've created a comprehensive diagnostic script that can help identify authentication issues. Create a file named `diagnose_auth_issue.py` with the following content:
   
   ```python
   #!/usr/bin/env python3
   """
   Mesh SDK Authentication and API Diagnostics
   
   This script performs a comprehensive diagnosis of authentication and API issues
   with the Mesh SDK, focusing on the 404 error that can occur when authentication fails.
   """
   
   import os
   import sys
   import json
   import logging
   import requests
   import time
   from pathlib import Path
   
   # Set up logging
   logging.basicConfig(
       level=logging.DEBUG,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       handlers=[
           logging.StreamHandler(),
           logging.FileHandler('mesh_diagnostics.log')
       ]
   )
   
   logger = logging.getLogger("mesh_diagnostics")
   
   # Enable debug mode for Mesh SDK
   os.environ["DEBUG"] = "true"
   
   # Import Mesh SDK components
   try:
       import mesh
       from mesh.client import MeshClient
       from mesh.token_manager import get_token, is_token_valid, clear_token
       from mesh.config import get_config
       logger.info("✅ Successfully imported Mesh SDK")
   except ImportError as e:
       logger.error(f"❌ Failed to import Mesh SDK: {str(e)}")
       logger.info("Please ensure Mesh SDK is installed: pip install mesh-sdk")
       sys.exit(1)
   
   # Run the script with: python diagnose_auth_issue.py
   ```
   
   The full script is available in the SDK repository. This script will:
   - Check your environment configuration
   - Verify if you have a valid token
   - Test if the API server is reachable
   - Attempt direct API requests
   - Test SDK requests
   - Provide recommendations based on the results

### Common Authentication Issues

1. **Keyring Access Issues**:
   - On some systems, the keyring may not be accessible or properly configured
   - The SDK will fall back to file-based storage, but this may not always work correctly
   - Check the logs for keyring-related errors

2. **Token Refresh Failures**:
   - If your token is expired, the system will attempt to refresh it
   - Refresh failures can occur if the refresh token is invalid or expired
   - Look for refresh-related log messages to diagnose

3. **Authorization Header Problems**:
   - Even with a valid token, the Authorization header might not be properly added
   - Debug logs will show the exact headers being sent with requests
   - Verify that the Authorization header contains "Bearer" followed by your token

4. **Environment Variables**:
   - Check if `MESH_API_URL` is set correctly if you're using a custom API endpoint
   - The `DEBUG` environment variable can be set to "true" for more detailed logs
