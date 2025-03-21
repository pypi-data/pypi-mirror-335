# Authentication Debugging Guide

This document provides detailed information about the enhanced logging implemented in the Mesh SDK to help diagnose authentication issues.

## Overview

Authentication failures in the Mesh SDK can manifest in various ways, most commonly as 404 errors when trying to access API endpoints. We've added comprehensive logging throughout the authentication process to help identify and resolve these issues.

## Enabling Debug Logging

To take advantage of the enhanced logging, you need to enable debug mode:

```python
import os
import logging

# Set DEBUG environment variable
os.environ["DEBUG"] = "true"

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mesh_debug.log')
    ]
)
```

## Authentication Process

The authentication process in the Mesh SDK follows these steps:

1. **Token Check**: First, the system checks if a valid token already exists in secure storage.
2. **Token Validation**: If a token exists, it's validated to ensure it hasn't expired.
3. **Token Refresh**: If the token is expired but a refresh token is available, the system attempts to refresh the token.
4. **New Authentication**: If no token exists or refresh fails, the system initiates a new authentication flow (browser-based or device code).
5. **Token Storage**: After successful authentication, the token is stored securely.
6. **Request Authorization**: When making API requests, the token is added to the request headers.

## Common Authentication Issues

### 1. Token Storage Issues

The SDK attempts to store tokens securely using the system keyring. If the keyring is not accessible, it falls back to file-based storage.

**Symptoms**:
- Authentication appears successful, but subsequent requests fail
- Logs show successful authentication but token retrieval fails

**Debug logs to look for**:
- `"Storing token"` followed by `"Failed to store token"`
- `"No token data found in storage"` despite previous successful authentication

### 2. Token Refresh Failures

When a token expires, the SDK attempts to refresh it using the refresh token.

**Symptoms**:
- API requests suddenly start failing after working previously
- 404 errors after a period of successful operation

**Debug logs to look for**:
- `"Token is not valid or expired"`
- `"Attempting to refresh token"`
- `"Token refresh failed"`

### 3. Authorization Header Issues

Even with a valid token, the Authorization header might not be properly added to requests.

**Symptoms**:
- 404 errors despite successful authentication
- Server logs showing unauthorized requests

**Debug logs to look for**:
- `"Added Authorization header with token"`
- `"No Authorization header in request despite authentication"`

## Diagnostic Log Examples

### Successful Authentication Flow

```
DEBUG - mesh.auth - Checking for existing token
DEBUG - mesh.auth - ✓ Found existing token
DEBUG - mesh.auth - Token: abcde...12345
DEBUG - mesh.auth - Token expires at: 2023-06-01 12:00:00
DEBUG - mesh.auth - Checking if token is valid
DEBUG - mesh.auth - ✓ Token is valid, using existing token
DEBUG - mesh.client - Added Authorization header with token: abcde...12345
```

### Token Refresh Flow

```
DEBUG - mesh.auth - Checking for existing token
DEBUG - mesh.auth - ✓ Found existing token
DEBUG - mesh.auth - Token: abcde...12345
DEBUG - mesh.auth - Token expires at: 2023-05-01 12:00:00
DEBUG - mesh.auth - ✗ Token is not valid or expired
DEBUG - mesh.auth - Attempting to refresh token
DEBUG - mesh.auth - Using refresh endpoint: https://api.example.com/auth/refresh
DEBUG - mesh.auth - Sending refresh request to backend
DEBUG - mesh.auth - Refresh response status code: 200
DEBUG - mesh.auth - ✓ Received successful response from refresh endpoint
DEBUG - mesh.auth - New access token: fghij...67890
DEBUG - mesh.auth - Token expires at: 2023-06-01 12:00:00
DEBUG - mesh.auth - Storing refreshed token
DEBUG - mesh.auth - ✓ Successfully stored refreshed token
```

### Authentication Failure

```
DEBUG - mesh.auth - Checking for existing token
DEBUG - mesh.auth - ✗ No existing token found
DEBUG - mesh.auth - Starting new authentication flow
DEBUG - mesh.auth - Using browser flow for interactive authentication
DEBUG - mesh.auth - ✗ Authentication failed
DEBUG - mesh.client - ✗ No authentication token available for request headers
DEBUG - mesh.client - ✗ Failed to authenticate for request
```

## Using the Diagnostic Script

We've created a comprehensive diagnostic script that can help identify authentication issues. You can find it in the SDK repository as `diagnose_auth_issue.py`.

Run the script with:

```bash
python diagnose_auth_issue.py
```

The script will:
- Check your environment configuration
- Verify if you have a valid token
- Test if the API server is reachable
- Attempt direct API requests
- Test SDK requests
- Provide recommendations based on the results

## Troubleshooting Steps

1. **Clear the token and re-authenticate**:
   ```python
   from mesh.token_manager import clear_token
   clear_token()
   # Then run mesh-auth
   ```

2. **Check keyring access**:
   ```python
   import keyring
   # Try to store and retrieve a test value
   keyring.set_password("mesh-test", "test-user", "test-value")
   value = keyring.get_password("mesh-test", "test-user")
   print(f"Retrieved value: {value}")
   ```

3. **Verify API URL**:
   ```python
   from mesh.config import get_config
   config = get_config()
   print(f"API URL: {config.get('api_url')}")
   ```

4. **Test direct API request**:
   ```python
   import requests
   from mesh.token_manager import get_token
   
   token_data = get_token()
   if token_data and "access_token" in token_data:
       headers = {"Authorization": f"Bearer {token_data['access_token']}"}
       response = requests.get("https://api.example.com/api/v1/user", headers=headers)
       print(f"Status code: {response.status_code}")
       print(f"Response: {response.text}")
   ```

## Conclusion

The enhanced logging in the Mesh SDK provides detailed insights into the authentication process, helping to diagnose and resolve issues quickly. By examining the logs, you can identify exactly where in the authentication flow the problem is occurring and take appropriate action to resolve it.

If you continue to experience issues after following this guide, please contact support with your debug logs for further assistance.
