# Mesh SDK Authentication

## Overview

The Mesh SDK provides a secure and resilient authentication system that utilizes backend-managed authentication flows. This document explains how authentication works in the SDK and provides guidelines for proper implementation.

## Authentication Flow

1. **Backend-Driven Authentication**
   - The SDK uses a browser-based OAuth flow managed by the backend server
   - When authentication is required, a browser window will open to the Auth0 login page
   - After successful login, Auth0 redirects back to the SDK with an authentication code
   - The SDK exchanges this code for tokens via the backend server

2. **Token Management**
   - Access tokens and refresh tokens are securely stored in the system keychain
   - Tokens are automatically refreshed when they expire
   - Token validation is performed both locally and with the backend when available

3. **Local vs. Backend Validation**
   - The SDK performs both local and backend token validation
   - Local validation checks the token format and expiration time
   - Backend validation (when available) provides additional security by verifying with Auth0
   - The SDK gracefully falls back to local validation if the backend validation endpoint is unreachable

## Usage

```python
# Import the client
from mesh import MeshClient

# Create a client - authentication will be triggered when needed
client = MeshClient()

# Making an API call (authentication will be triggered if needed)
response = client.chat("Hello, world!")
```

## Top-Level Functions

The SDK also provides top-level functions that handle authentication automatically:

```python
# Import the SDK
import mesh

# Use top-level functions (authentication handled automatically)
response = mesh.chat("What is 5 + 7?")
keys = mesh.list_keys()
```

## Configuration

The authentication system can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `AUTH0_DOMAIN` | Auth0 domain | dev-hzpwy8oqs2ojss6r.us.auth0.com |
| `AUTH0_CLIENT_ID` | Auth0 client ID | Ky6gtf5PPUs1IpIFdm91ttQs4Oxpj0Nq |
| `AUTH0_AUDIENCE` | Auth0 audience | https://mesh-abh5.onrender.com |
| `MESH_API_URL` | Mesh API URL | https://mesh-abh5.onrender.com |
| `AUTH0_CALLBACK_PORT` | Local callback port | 8000 |
| `AUTO_REFRESH` | Enable token auto-refresh | true |

## Deprecated Authentication Methods

Direct token authentication via the `auth_token` property is deprecated and will be removed in a future version. It is recommended to use the backend-driven authentication flow instead.

```python
# Deprecated (not recommended)
client = MeshClient(auth_token="your_token")

# Recommended
client = MeshClient()  # Will use backend-driven authentication
```

## Headless Authentication

The SDK supports authentication in headless environments (servers, containers, CI/CD pipelines) using device code flow.

### Automatic Detection

The SDK automatically detects headless environments and uses the appropriate authentication flow:

- In environments with a browser (desktop, laptop), it uses browser-based authentication
- In headless environments (servers, containers), it automatically uses device code flow
- In Jupyter/IPython notebooks, it uses device code flow with inline authentication prompts

### Forcing Headless Mode

You can force headless mode by setting the `MESH_HEADLESS` environment variable:

```bash
# Force headless mode (use device code flow)
export MESH_HEADLESS=true
```

This is useful for:
- Containerized environments (Docker, Kubernetes)
- Server deployments (AWS, GCP, Azure, Render)
- CI/CD pipelines (GitHub Actions, GitLab CI)
- SSH sessions without X11 forwarding

### Using Device Code Flow

When in headless mode, the SDK will:

1. Generate a device code and user code
2. Display a URL and user code to enter
3. Wait for the authentication to complete

Example output:
```
To authenticate, visit: https://auth0.com/activate
And enter code: ABCD-EFGH
```

### Environment Variables for Headless Environments

| Variable | Description | Default |
|----------|-------------|---------|
| `MESH_HEADLESS` | Force headless mode | false |
| `MESH_DEVICE_TIMEOUT` | Timeout for device flow (seconds) | 300 |

## Edge Cases and Troubleshooting

### Missing Validation Endpoint

If the backend server does not have the `/auth/validate` endpoint available (such as when using certain hosting providers), the SDK will automatically fall back to local token validation. This ensures the SDK works reliably regardless of the backend configuration.

### Network Issues

The SDK is designed to handle network issues gracefully:
- All requests include configurable timeouts
- Retry logic is implemented for transient failures
- Token refresh is attempted when authentication errors occur

### Authentication Failure

If authentication fails:
1. Check your internet connection
2. Verify that the Auth0 configuration is correct
3. Check if the backend server is running and accessible
4. Try running `mesh-auth` from the command line to manually trigger authentication
5. Check the logs for more detailed error messages (set `DEBUG=true` for verbose logging)

### Headless Environment Issues

If experiencing issues in headless environments:
1. Set `MESH_HEADLESS=true` to force device code flow
2. Check for common container/server environment variables (`DOCKER`, `RENDER`, etc.)
3. For Linux servers, ensure `DISPLAY` is not set if you want to force headless mode
4. Review logs with `DEBUG=true` for detailed authentication debugging information
