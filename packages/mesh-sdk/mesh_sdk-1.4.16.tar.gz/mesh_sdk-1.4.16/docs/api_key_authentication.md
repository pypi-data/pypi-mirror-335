# API Key Authentication

## Overview

API keys provide a more reliable authentication method for headless environments (servers, CI/CD pipelines, etc.) compared to token-based authentication. Unlike tokens which expire and may need refreshing, API keys remain valid until explicitly revoked.

## When to Use API Keys

Use API keys when:

- Deploying to headless environments (servers, containers, CI/CD)
- Setting up long-running processes
- Authenticating in environments where token storage is unreliable
- Automating workflows that require persistent authentication

## Generating an API Key

You can generate an API key using the `mesh-pre-deploy` command-line tool:

```bash
# Generate an API key with auto-generated name
mesh-pre-deploy

# Generate an API key with a custom name
mesh-pre-deploy --name "production-server"
```

The command will:
1. Authenticate you if needed
2. Generate a new API key
3. Display the key and instructions for using it

**Important:** The API key will only be shown once during generation. Make sure to save it in a secure location.

## Using API Keys

There are two ways to use an API key:

### 1. Environment Variable (Recommended)

Set the `MESH_API_KEY` environment variable:

```bash
# In your deployment environment (Render, Heroku, etc.)
export MESH_API_KEY="mesh_yourapikey123456"
```

For deployment platforms, add it to your environment variables:
- **Render**: Add as an environment variable in the dashboard
- **Heroku**: `heroku config:set MESH_API_KEY=mesh_yourapikey123456`
- **Docker**: Use `-e MESH_API_KEY=mesh_yourapikey123456` or add to docker-compose.yml

### 2. Programmatic Usage

You can also set the API key programmatically:

```python
import os
# Set the API key before importing mesh or initializing the SDK
os.environ["MESH_API_KEY"] = "mesh_yourapikey123456"

# Then initialize as usual
import mesh
mesh.init()
```

## How It Works

The SDK automatically detects headless environments and checks for an API key before falling back to token-based authentication. When an API key is present:

1. The SDK will use it for all API requests
2. No token expiration or refresh logic is needed
3. Requests are authenticated using the `ApiKey` authorization scheme

## Security Considerations

API keys have the same permissions as your user account. To keep them secure:

- Never commit API keys to source control
- Use environment variables or secure vaults to store them
- Limit the number of API keys in circulation
- Rotate API keys periodically 
- Delete unused API keys via the Mesh web interface

## Managing API Keys

You can manage your API keys through the Mesh web interface:

1. Log in to your Mesh account
2. Navigate to the API Keys section
3. View, create or delete API keys

## Troubleshooting

If you encounter authentication issues with API keys:

1. Verify the API key starts with `mesh_`
2. Ensure the environment variable is correctly set
3. Check that the API key hasn't been revoked in the web interface
4. Try generating a new API key with `mesh-pre-deploy`

## Migrating from Token Authentication

If you're currently using token-based authentication with environment variables:

1. Generate a new API key with `mesh-pre-deploy`
2. Replace your token environment variables (`MESH_ACCESS_TOKEN`, `MESH_REFRESH_TOKEN`, etc.) with just `MESH_API_KEY`
3. Remove any token refresh logic or expiration handling

This will provide more reliable authentication for your deployments.
