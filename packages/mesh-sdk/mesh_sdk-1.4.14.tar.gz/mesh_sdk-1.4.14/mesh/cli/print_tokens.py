#!/usr/bin/env python
"""
Mesh Token Utility Script

This script provides a simple way to print your current Mesh tokens
in a format suitable for setting environment variables in Render or
other deployment platforms.

Usage:
    python -m mesh.cli.print_tokens

This will print instructions for setting environment variables with your
current authentication tokens.
"""

import sys
from mesh.token_manager import print_token_env_instructions


def main():
    # Print header
    print("\nMesh Token Utility")
    print("=================")
    print("This utility will print your current authentication tokens")
    print("for use in headless environments like Render.\n")
    
    # Print token information
    print_token_env_instructions()


if __name__ == "__main__":
    main()
