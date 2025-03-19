"""
Author: mmwei3
Email: mmwei@iflytek.com
Contact: 178555350258
Date: 2025-03-19
Description: A CLI tool for sending inhibition requests via API.
"""

import requests
import datetime
import sys
import os
from inhibitor_tool.auth import get_token
from inhibitor_tool.utils import validate_content
from inhibitor_tool.constants import MAX_TTL


def inhibit(content: str, ttl: int, remark: str):
    """
    Send an inhibition request with the given content and TTL.

    - Validates content length and formatting.
    - Ensures TTL does not exceed the maximum allowed duration.
    - Retrieves authentication token before making API request.
    - Constructs inhibition request payload and sends it.
    """

    #  Validate inhibition content
    if not validate_content(content):
        print(
            "Error: Inhibition content must be at least 10 characters and cannot contain spaces."
        )
        sys.exit(1)

    # Validate TTL duration
    if ttl > MAX_TTL:
        print(f"Error: TTL cannot exceed {MAX_TTL} hours.")
        sys.exit(1)

    # Read required environment variables
    try:
        username = os.environ["USERNAME"]
        password = os.environ["PASSWORD"]
        login_url = os.environ["LOGIN_URL"]
        inhibit_url = os.environ["INHIBIT_URL"]
    except KeyError as e:
        print(
            f"Error: Missing required environment variable: {e}. Please run `source ~/.auth_token` first."
        )
        sys.exit(1)

    # Get authentication token
    token = get_token(username, password, login_url)
    if not token:
        print("Error: Unable to retrieve authentication token.")
        sys.exit(1)

    # Generate request metadata
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    name = f"cli_{username}_{timestamp}"

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "type": 1,
        "state": 0,
        "maskAlarmType": "content",
        "policyStartTime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "durationUnit": "h",
        "name": name,
        "maskContent": content,
        "duration": str(ttl),
        "remark": f"Inhibition request via CLI: {remark}",
    }

    # Send API request
    response = requests.post(inhibit_url, headers=headers, json=data, verify=False)

    # Handle response
    if response.status_code == 200:
        print("Success: Inhibition request sent.")
    else:
        print(
            f"Error: Failed to send inhibition request. Status: {response.status_code}, Response: {response.text}"
        )
