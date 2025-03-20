import os
import sys


def load_config():
    """
    Load API configuration from environment variables.

    - Requires users to `source ~/.auth_token` before execution.
    - Ensures that required environment variables exist.
    - Reads values directly from environment variables instead of a file.
    """

    # 1Required environment variables
    required_keys = ["USERNAME", "PASSWORD", "LOGIN_URL", "INHIBIT_URL"]

    # validate if all required variables are set
    missing_keys = [key for key in required_keys if key not in os.environ]
    if missing_keys:
        print(
            f"Error: Missing required environment variables: {missing_keys}. "
            f"Ensure you have sourced the `.auth_token` file properly."
        )
        sys.exit(1)

    # Read authentication details from environment variables
    config = {key.lower(): os.environ[key] for key in required_keys}
    return config
