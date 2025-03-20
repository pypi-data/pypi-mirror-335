"""
Author: mmwei3
Email: mmwei@iflytek.com
Contact: 178555350258
Date: 2025-03-19
Description: CLI entry point for sending inhibition requests.
"""

import argparse
from inhibitor_tool.inhibitor import inhibit


def main():
    """
    Parse command-line arguments and send an inhibition request.
    """

    parser = argparse.ArgumentParser(description="Send an inhibition request.")

    # Content argument (Required)
    parser.add_argument(
        "--content",
        type=str,
        required=True,
        help="Content to inhibit (at least 10 characters, no spaces).",
    )

    # TTL argument (Optional, Default = 3)
    parser.add_argument(
        "--ttl",
        type=int,
        default=3,
        help="TTL in hours (default: 3, max: 720).",
    )

    # Remark argument (Optional, Default = 'tmp_inhibitor')
    parser.add_argument(
        "--remark",
        type=str,
        default="tmp_inhibitor",
        help="Optional remark for the inhibition request (default: 'tmp_inhibitor').",
    )

    args = parser.parse_args()

    # Call the inhibition function with parsed arguments
    inhibit(args.content, args.ttl, args.remark)


if __name__ == "__main__":
    main()
