#!/usr/bin/env python3
"""
Test script for the Mesh SDK chat functionality.

This script tests the chat functionality by sending a simple message.
"""

import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mesh.test")

# Import Mesh SDK
import mesh_improved as mesh

def test_chat():
    """Test the chat functionality"""
    print("Testing chat functionality...")
    
    try:
        # Try to send a message
        response = mesh.chat("Write a short poem about programming.")
        
        if response:
            print("Chat successful!")
            print("\nResponse:")
            print(response)
            return True
        else:
            print("Chat failed - no response.")
            return False
    except Exception as e:
        print(f"Chat failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    test_chat()