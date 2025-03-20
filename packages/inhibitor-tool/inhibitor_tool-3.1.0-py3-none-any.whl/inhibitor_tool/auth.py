"""
Author: mmwei3
Email: mmwei3@iflytek.com
Date: 2025-03-19
Description: Authentication module for obtaining API token.
"""

import requests
import sys


def get_token(username: str, password: str, login_url: str) -> str:
    """
    Retrieve authentication token from the login API.

    Args:
        username (str): API username.
        password (str): API password.
        login_url (str): Authentication endpoint.

    Returns:
        str: Authentication token if successful, otherwise an empty string.
    """
    headers = {"Content-Type": "application/json"}
    data = {"username": username, "password": password}

    try:
        response = requests.post(login_url, json=data, headers=headers, timeout=5)

        if response.status_code == 200:
            response_json = response.json()
            token = response_json.get("data", {}).get("token", "")

            if token:
                return token
            else:
                print(
                    "Error: Authentication response is missing 'token' field.",
                    file=sys.stderr,
                )
                return ""
        else:
            print(
                f"Error: Failed to authenticate. Status code: {response.status_code}",
                file=sys.stderr,
            )
            print(f"Response: {response.text}", file=sys.stderr)
            return ""

    except requests.exceptions.Timeout:
        print("Error: Authentication request timed out.", file=sys.stderr)
    except requests.exceptions.RequestException as e:
        print(f"Error: An error occurred during authentication: {e}", file=sys.stderr)

    return ""
