# Changelog

## [1.4.15] - 2025-03-20

### Added
- New CLI utility `mesh-env` to generate environment variables file for deployment
- Simplified deployment process for headless environments like Render

## [1.4.14] - 2025-03-20

### Improved
- Added automatic token printing in headless mode for easier deployment
- Updated token printing format for simple copy/paste into environment variables
- Enhanced documentation for token management in headless environments

## [1.4.13] - 2025-03-20

### Improved
- Enhanced token management for headless environments
- Improved token storage reliability in server/container deployments
- Updated clear_token function to properly handle headless environments
- Added comprehensive documentation for headless authentication in gotchas.md
- Prioritize file-based token storage in headless environments for improved reliability
- Added automatic token printing and environment variable instructions in headless mode
- Simplified deployment on ephemeral platforms like Render with automatic token information display

## [1.4.12] - 2025-03-20

### Added
- Enhanced documentation for headless mode authentication
- Added detailed instructions for using device code flow in containerized environments
- Improved troubleshooting guide for headless environment authentication issues

## [1.4.11] - 2025-03-20

### Fixed
- Improved headless environment detection for more reliable authentication
- Added automatic fallback to device code flow in server/container environments
- Enhanced browser detection to fail faster in headless environments
- Added `MESH_HEADLESS` environment variable to force headless authentication mode
- Fixed authentication flow in Render, Docker and other containerized environments

## [1.4.10] - 2025-03-20

### Added
- Added `llm.txt` file for simple reference of Mesh SDK usage
- Simplified README with more beginner-friendly examples
- Improved documentation for vision functionality

## [1.4.9] - 2025-03-20

### Fixed
- Fixed Google Gemini vision integration to ensure proper image processing
- Enhanced message formatting for Gemini 2.0 models to use snake_case format (`inline_data`, `mime_type`) as required by the Google API
- Improved server-side handling of different message formats between providers
- Added comprehensive logging to help debug vision requests
- Ensured cross-provider compatibility for vision functionality

## [1.4.8] - 2025-03-17

### Fixed
- Fixed critical issue where Claude models were incorrectly routed to the OpenAI provider
- Improved provider detection for all Claude models
- Fixed user creation during authentication to ensure profile exists in the database
- Enhanced endpoint fallback for more reliable chat completions
- Added automatic provider inference from model names
- Direct use of legacy endpoint `/v1/mesh/chat` for chat completions
- Added smart fallback mechanism to try standard endpoint if legacy fails
- Improved error messages with specific troubleshooting advice

## [1.4.7] - 2025-03-16

### Fixed
- Enhanced fix for 404 error in top-level `mesh.chat()` function
- Added detailed logging to help diagnose endpoint connection issues

## [1.4.5] - 2025-03-16

### Fixed
- Initial fix for 404 error in top-level `mesh.chat()` function 
- Modified URL mapping to use legacy endpoint `/v1/mesh/chat` 
- Added more robust error handling for endpoint issues

## [1.3.0] - 2025-03-12

### Added
- Improved token validation with automatic fallback to local validation when backend endpoints are unavailable
- Resilient authentication handling with better error reporting
- Added timeout parameter to all request methods for better network performance

### Changed
- Streamlined authentication flow to exclusively use backend-driven authentication
- Deprecated direct token authentication via auth_token property in favor of backend flow
- Enhanced error handling for network issues and missing endpoints

### Fixed
- Fixed timeout parameter handling in request methods
- Fixed token validation to work with remote servers where /auth/validate endpoint may not be available
- Fixed authentication flow to prevent repeated authentication attempts

## [1.2.1] - 2025-03-01

### Fixed
- Fixed Claude model aliasing to ensure proper version-specific model IDs are sent to the API
- Added server-side model normalization to prevent "model: claude" not found errors
- Improved documentation for using Claude models with the SDK

### Added
- Documentation section on Claude model aliases and proper usage
- Additional logging for model normalization

## [1.2.0] - 2025-03-01

### Added
- Automatic user ID extraction from authentication token for key management
- Made `user_id` parameter optional in `store_key` and `get_key` methods
- Added parameter validation for key management methods
- Updated documentation on key management in README.md

### Changed
- Improved key management interface for simpler API usage
- Enhanced error messages with specific troubleshooting steps for key management

## [1.1.0] - 2025-02-28

### Added
- Automatic user registration before chat requests to ensure users exist in the database
- Support for both "message" and "prompt" formats in chat requests for better compatibility
- Improved endpoint fallback strategy to support both new and legacy endpoints
- Comprehensive troubleshooting section in README.md
- Detailed documentation on chat functionality and user registration

### Fixed
- Fixed chat functionality by ensuring user registration before chat requests
- Fixed authentication token handling for better compatibility with different server configurations
- Fixed endpoint URL handling to support both new and legacy endpoints
- Fixed request format to support both "message" and "prompt" fields

### Changed
- Updated README.md with comprehensive documentation on authentication, chat, and troubleshooting
- Improved error messages with specific troubleshooting steps
- Enhanced logging for better debugging

## [1.0.0] - 2025-01-01

### Added
- Initial release of the Mesh SDK
- Support for key management
- Support for Zero-Knowledge Proofs
- Support for chat completions
- Support for usage tracking 