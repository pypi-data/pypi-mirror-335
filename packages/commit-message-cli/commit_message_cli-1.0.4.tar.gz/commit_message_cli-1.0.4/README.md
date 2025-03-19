# Commit Message CLI

A CLI tool that generates commit messages using AI. This tool integrates with your git workflow to analyze staged changes and generate meaningful commit messages.

## Features

- Generates commit messages from git diffs
- Supports branch name and issue key context
- Secure authentication via Auth0 device flow
- Debug logging for troubleshooting
- Handles compressed and encoded responses
- Configurable via config file or environment variables

## Installation

```bash
pip install commit-message-cli
```

## Configuration

The tool requires configuration for authentication and API access. Create a `~/.commit-message-cli/config.json` file with the following structure:

```json
{
  "auth0_domain": "your-auth0-domain.auth0.com",
  "auth0_client_id": "your-auth0-client-id",
  "auth0_audience": "your-auth0-audience",
  "api_domain": "api.example.com"
}
```

Alternatively, you can set these values via environment variables:

- `COMMIT_MESSAGE_CLI_AUTH0_DOMAIN`
- `COMMIT_MESSAGE_CLI_AUTH0_CLIENT_ID`
- `COMMIT_MESSAGE_CLI_AUTH0_AUDIENCE`
- `COMMIT_MESSAGE_CLI_API_DOMAIN`

## Usage

### Basic Usage

```bash
# Generate a commit message for staged changes
commit-message-cli

# Generate a commit message with an issue key
commit-message-cli -i JIRA-123

# Generate a commit message for a specific branch
commit-message-cli -b feature/my-branch

# Generate a commit message from a specific diff file
commit-message-cli -f path/to/diff.txt

# Generate a commit message with debug logging
SMOOTHDEV_DEBUG=1 commit-message-cli
```

### Command Line Options

```
-d, --diff       Git diff content (if not using staged changes)
-f, --file       File containing git diff
-b, --branch     Branch name (defaults to current branch)
-i, --issue      Issue number or key
-c, --config     Custom config file path
--debug          Enable debug logging
```

## Authentication

The tool uses Auth0's device flow for secure authentication:

1. On first run, you'll be prompted to visit a URL
2. Open the URL in your browser
3. Complete the authentication process
4. The tool will automatically receive and store the token

Tokens are securely stored in your home directory and automatically refreshed when needed.

## Debugging

Set the `SMOOTHDEV_DEBUG` environment variable to `1` to enable detailed logging:

```bash
SMOOTHDEV_DEBUG=1 commit-message-cli
```

This will show:

- API request/response details
- Authentication flow information
- Configuration loading
- Error details

## Error Handling

The tool provides clear error messages for common issues:

- Invalid configuration
- Authentication failures
- API errors
- Invalid diff content

Error messages are displayed in stderr, while the commit message is output to stdout.

## License

MIT License - see LICENSE file for details
