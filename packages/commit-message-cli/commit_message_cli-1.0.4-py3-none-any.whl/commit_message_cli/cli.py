#!/usr/bin/env python3

import argparse
import base64
import json
import logging
import os
import platform
import subprocess
import sys
import time
import zlib
from pathlib import Path
from typing import Any, Dict, Union

import requests

# Configure logging
log_level = logging.DEBUG if os.getenv("SMOOTHDEV_DEBUG") == "1" else logging.INFO
logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Constants
DEFAULT_AUTH0_DOMAIN = "auth.smoothdev.io"
DEFAULT_AUTH0_CLIENT_ID = "8r7cnzhhVnW8Cvscl7Lm0i9PEROyHXMw"
DEFAULT_AUTH0_AUDIENCE = "https://auth.smoothdev.io/api"
DEFAULT_REDIRECT_URI = "http://app.smoothdev.io/auth/callback"
DEFAULT_API_DOMAIN = "rest.smoothdev.io"
DEFAULT_CONFIG_FILE = "~/.smoothdevio/config.json"
DEFAULT_SMOOTHDEVIO_DIR = "~/.smoothdevio"
DEFAULT_JWT_FILE = "~/.smoothdevio/jwt"
DEFAULT_JWT_EXPIRY_FILE = "~/.smoothdevio/jwt_expiry"

# Global configuration dictionary
_config: Dict[str, str] = {}


def get_config() -> Dict[str, str]:
    """Get configuration from config file or environment variables."""
    global _config

    if _config:
        return _config

    # Try to load from config file
    config_file = os.path.expanduser(DEFAULT_CONFIG_FILE)
    logger.debug(f"Looking for config file at: {config_file}")
    if Path(config_file).exists():
        logger.debug("Found config file, loading...")
        with open(config_file) as f:
            _config = json.load(f)
        masked_config = {
            k: "***" if "id" in k.lower() else v for k, v in _config.items()
        }
        logger.debug(f"Loaded config: {json.dumps(masked_config)}")
    else:
        logger.debug("No config file found")
        _config = {}

    # Load default values for missing keys
    defaults = {
        "api_domain": DEFAULT_API_DOMAIN,
        "auth0_domain": DEFAULT_AUTH0_DOMAIN,
        "auth0_client_id": DEFAULT_AUTH0_CLIENT_ID,
        "auth0_audience": DEFAULT_AUTH0_AUDIENCE,
        "redirect_uri": DEFAULT_REDIRECT_URI,
        "smoothdevio_dir": DEFAULT_SMOOTHDEVIO_DIR,
        "jwt_file": DEFAULT_JWT_FILE,
        "jwt_expiry_file": DEFAULT_JWT_EXPIRY_FILE,
    }
    for key, value in defaults.items():
        if key not in _config:
            logger.debug(f"Using default value for {key}")
            _config[key] = value

    # Load from environment variables, only if they are set
    env_vars = {
        "api_domain": "SMOOTHDEV_API_DOMAIN",
        "auth0_domain": "SMOOTHDEV_AUTH0_DOMAIN",
        "auth0_client_id": "SMOOTHDEV_AUTH0_CLIENT_ID",
        "auth0_audience": "SMOOTHDEV_AUTH0_AUDIENCE",
        "redirect_uri": "SMOOTHDEV_REDIRECT_URI",
        "smoothdevio_dir": "SMOOTHDEV_DIR",
        "jwt_file": "SMOOTHDEV_JWT_FILE",
        "jwt_expiry_file": "SMOOTHDEV_JWT_EXPIRY_FILE",
    }
    for key, env_var in env_vars.items():
        env_value = os.getenv(env_var)
        if env_value is not None:
            logger.debug(f"Using environment value for {key}")
            _config[key] = env_value

    # Ensure directory exists
    os.makedirs(os.path.expanduser(_config["smoothdevio_dir"]), exist_ok=True)

    return _config


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate commit message using AI")
    parser.add_argument("-d", "--diff", help="Git diff")
    parser.add_argument("-f", "--file", help="File containing git diff")
    parser.add_argument("-b", "--branch", help="Branch name")
    parser.add_argument("-i", "--issue", help="Issue number")
    parser.add_argument("-c", "--config", help="Config file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def get_diff_input(args: argparse.Namespace) -> str:
    """Get diff input from command line arguments or git."""
    if args.diff:
        return str(args.diff)
    elif args.file:
        with open(str(args.file)) as f:
            content: str = f.read()
            return content
    else:
        return get_diff_input_from_git()


def get_branch_name(args: argparse.Namespace) -> str:
    """Get branch name from command line arguments or git."""
    if args.branch:
        return str(args.branch)
    return get_branch_name_from_git()


def get_issue_key(args: argparse.Namespace) -> Union[str, None]:
    """Get issue key from command line arguments."""
    if args.issue:
        return str(args.issue)
    return None


def validate_diff_input(diff_input: str) -> None:
    """Validate diff input."""
    if not diff_input:
        logger.error("Error: diff input is required.")
        sys.exit(1)


def get_device_code() -> Dict[str, Any]:
    """Get device code from Auth0."""
    config = get_config()
    url = f"https://{config['auth0_domain']}/oauth/device/code"
    data = {
        "client_id": config["auth0_client_id"],
        "scope": "openid profile email",
        "audience": config["auth0_audience"],
    }
    logger.debug(f"Making device code request to: {url}")

    log_data = {k: "***" if k == "client_id" else v for k, v in data.items()}
    logger.debug(f"Request data: {json.dumps(log_data)}")

    try:
        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json=data,
        )

        if response.status_code != 200:
            logger.error(f"Error response: {response.status_code}")
            logger.error(f"Response body: {response.text}")
            logger.error(f"Request URL: {url}")
            logger.error(f"Request headers: {response.request.headers}")

        response.raise_for_status()
        return dict(response.json())
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        raise


def authenticate_user(device_code_data: Dict[str, Any]) -> None:
    """Authenticate user with Auth0."""
    verification_uri_complete = device_code_data["verification_uri_complete"]
    if platform.system() == "Darwin":
        subprocess.run(["open", verification_uri_complete])
    else:
        subprocess.run(["xdg-open", verification_uri_complete])

    print(f"1. Navigate to: {verification_uri_complete}")
    print(f"2. Enter code: {device_code_data['user_code']}")


def poll_for_token(device_code_data: Dict[str, Any]) -> Dict[str, Any]:
    """Poll for the access token."""
    config = get_config()
    token_url = f"https://{config['auth0_domain']}/oauth/token"
    while True:
        response = requests.post(
            token_url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": device_code_data["device_code"],
                "client_id": config["auth0_client_id"],
            },
        )
        response_data = dict(response.json())
        if response.status_code == 200:
            return response_data
        error = response_data.get("error", "")
        if error == "authorization_pending":
            time.sleep(device_code_data["interval"])
            continue
        raise Exception(response_data.get("error_description", "Unknown error"))


def get_jwt() -> str:
    """Get JWT token from Auth0."""
    device_code_data = get_device_code()

    # Open browser for user authentication
    if platform.system() == "Darwin":
        subprocess.run(["open", device_code_data["verification_uri_complete"]])
    else:
        subprocess.run(["xdg-open", device_code_data["verification_uri_complete"]])

    # Poll for token
    token_data = poll_for_token(device_code_data)
    jwt = str(token_data["access_token"])

    # Save token and expiry
    config = get_config()
    jwt_file = Path(config["jwt_file"]).expanduser()
    jwt_expiry_file = Path(config["jwt_expiry_file"]).expanduser()

    jwt_file.write_text(jwt)
    jwt_expiry_file.write_text(str(int(time.time()) + token_data["expires_in"]))

    return jwt


def is_jwt_valid() -> bool:
    """Check if JWT token is valid."""
    config = get_config()
    jwt_file = os.path.expanduser(config["jwt_file"])
    jwt_expiry_file = os.path.expanduser(config["jwt_expiry_file"])

    if not os.path.exists(jwt_file) or not os.path.exists(jwt_expiry_file):
        return False

    with open(jwt_expiry_file) as f:
        expiry = int(f.read().strip())
        return expiry > time.time()


def get_stored_jwt() -> str:
    """Get stored JWT token."""
    config = get_config()
    jwt_file = os.path.expanduser(config["jwt_file"])
    with open(jwt_file) as f:
        return f.read().strip()


def sanitize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize the payload to remove sensitive information."""
    sanitized_diff = payload["diff"].replace("169.254.169.254", "[REDACTED]")
    payload["diff"] = sanitized_diff
    return payload


def validate_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the payload for security concerns."""
    if "169.254.169.254" in payload["diff"]:
        raise ValueError("Invalid content in diff input")
    return payload


def encode_payload(payload: Dict[str, Any]) -> str:
    """Encode the payload for transmission."""
    payload_json = json.dumps(payload)
    compressed_payload = zlib.compress(payload_json.encode("utf-8"))
    encoded_bytes: bytes = base64.b64encode(compressed_payload)
    result: str = encoded_bytes.decode("utf-8")
    return result


def decode_commit_message(encoded_message: str) -> str:
    """Decode a base64 and zlib compressed commit message."""
    try:
        # Decode base64
        compressed_data = base64.b64decode(encoded_message)
        # Decompress with zlib
        decompressed_data = zlib.decompress(compressed_data)
        # Decode bytes to string
        return decompressed_data.decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to decode commit message: {str(e)}")
        raise


def get_branch_name_from_git() -> str:
    """Get branch name from git."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def get_diff_input_from_git() -> str:
    """Get diff input from git."""
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def main() -> None:
    """Main entry point for the CLI tool."""
    args = parse_arguments()

    # Get JWT token
    if not is_jwt_valid():
        jwt = get_jwt()
    jwt = get_stored_jwt()

    # Get diff input
    diff_input = get_diff_input(args)
    validate_diff_input(diff_input)

    # Create payload
    payload = {
        "diff": diff_input,
        "branch": get_branch_name(args),
        "issue": get_issue_key(args),
    }

    # Sanitize, validate and encode payload
    payload = sanitize_payload(payload)
    payload = validate_payload(payload)
    encoded_payload = encode_payload(payload)

    # Make API request
    config = get_config()
    api_url = f"https://{config['api_domain']}/commit_message_generator"
    headers = {"Authorization": f"Bearer {jwt}"}
    request_data = {"payload": encoded_payload}

    logger.debug(f"Making API request to: {api_url}")
    log_headers = {
        k: v[:10] + "..." if k.lower() == "authorization" else v
        for k, v in headers.items()
    }
    logger.debug(f"Request headers: {json.dumps(log_headers)}")
    logger.debug(f"Request data: {json.dumps(request_data)}")

    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=request_data,
        )

        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response headers: {dict(response.headers)}")
        logger.debug(f"Response body: {response.text}")

        if response.status_code != 200:
            logger.error(f"Error response: {response.status_code}")
            logger.error(f"Response body: {response.text}")
            error_msg = response.json().get("message", "Unknown error")
            logger.error(f"API Error: {error_msg}")
            print(f"Error: {error_msg}", file=sys.stderr)
            sys.exit(1)

        # Decode and output the commit message
        encoded_message = response.json()["commit_message"]
        commit_message = decode_commit_message(encoded_message)
        logger.debug("Successfully generated commit message")
        logger.debug(f"Generated commit message: {commit_message}")
        sys.stdout.write(commit_message + "\n")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
