#!/usr/bin/env python3
"""Script to set up folder structure and create a test file for Shardcast."""

import os
import time
import hashlib
import tempfile
import random

# Test configuration
TEST_FILE_SIZE_MB = 15

# Create a unique temporary directory for the test
TEMP_DIR = tempfile.gettempdir()
TEST_DIR = os.path.join(TEMP_DIR, f"shardcast_test_{int(time.time())}")
os.makedirs(TEST_DIR, exist_ok=True)

# Define the required subdirectories
ORIGIN_DATA_DIR = os.path.join(TEST_DIR, "origin_data")
MIDDLE_NODE_1_DIR = os.path.join(TEST_DIR, "middle_node_1")
MIDDLE_NODE_2_DIR = os.path.join(TEST_DIR, "middle_node_2")
CLIENT_DATA_DIR = os.path.join(TEST_DIR, "client_data")
TEST_FILE_PATH = os.path.join(TEST_DIR, "test_file.bin")

# Create the subdirectories
os.makedirs(ORIGIN_DATA_DIR, exist_ok=True)
os.makedirs(MIDDLE_NODE_1_DIR, exist_ok=True)
os.makedirs(MIDDLE_NODE_2_DIR, exist_ok=True)
os.makedirs(CLIENT_DATA_DIR, exist_ok=True)


def create_test_file():
    """Create a test file with random data and print its hash."""
    print(f"Creating test file: {TEST_FILE_PATH} ({TEST_FILE_SIZE_MB * 100} MB)")
    with open(TEST_FILE_PATH, "wb") as f:
        # Write random data in 1MB chunks
        for _ in range(TEST_FILE_SIZE_MB):
            data = bytearray(random.getrandbits(8) for _ in range(1024 * 1024 * 100))
            f.write(data)

    # Calculate file hash for verification
    with open(TEST_FILE_PATH, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    print(f"Created test file with hash: {file_hash}")
    return file_hash


def main():
    print("Setting up folder structure for Shardcast test...")
    print(f"Test directory created at: {TEST_DIR}")
    create_test_file()
    print("Folder structure and test file setup completed.")


if __name__ == "__main__":
    main()
