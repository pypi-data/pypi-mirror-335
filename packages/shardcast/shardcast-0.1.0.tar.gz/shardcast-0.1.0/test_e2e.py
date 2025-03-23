#!/usr/bin/env python3
"""End-to-end test script for Shardcast."""

import os
import time
import shutil
import hashlib
import subprocess
import tempfile
import atexit
import signal
import random

# Test configuration
TEST_FILE_SIZE_MB = 10
ORIGIN_PORT = 8001
MIDDLE_PORT_1 = 8002
MIDDLE_PORT_2 = 8003
PROCESSES = []


def cleanup():
    """Clean up all processes and temporary directories."""
    print("Cleaning up...")
    for process in PROCESSES:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

    for dir_path in [ORIGIN_DATA_DIR, MIDDLE_NODE_1_DIR, MIDDLE_NODE_2_DIR, CLIENT_DATA_DIR]:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)

    if os.path.exists(TEST_FILE_PATH):
        os.remove(TEST_FILE_PATH)


# Register cleanup on exit
atexit.register(cleanup)


# Handle keyboard interrupt
def signal_handler(sig, frame):
    print("Test interrupted")
    cleanup()
    exit(1)


signal.signal(signal.SIGINT, signal_handler)

# Create temporary directories
TEMP_DIR = tempfile.gettempdir()
TEST_DIR = os.path.join(TEMP_DIR, f"shardcast_test_{int(time.time())}")
os.makedirs(TEST_DIR, exist_ok=True)

ORIGIN_DATA_DIR = os.path.join(TEST_DIR, "origin_data")
MIDDLE_NODE_1_DIR = os.path.join(TEST_DIR, "middle_node_1")
MIDDLE_NODE_2_DIR = os.path.join(TEST_DIR, "middle_node_2")
CLIENT_DATA_DIR = os.path.join(TEST_DIR, "client_data")
TEST_FILE_PATH = os.path.join(TEST_DIR, "test_file.bin")

os.makedirs(ORIGIN_DATA_DIR, exist_ok=True)
os.makedirs(MIDDLE_NODE_1_DIR, exist_ok=True)
os.makedirs(MIDDLE_NODE_2_DIR, exist_ok=True)
os.makedirs(CLIENT_DATA_DIR, exist_ok=True)


def create_test_file():
    """Create a test file with random data."""
    print(f"Creating test file: {TEST_FILE_PATH} ({TEST_FILE_SIZE_MB} MB)")
    with open(TEST_FILE_PATH, "wb") as f:
        # Create random data in 1MB chunks
        for _ in range(TEST_FILE_SIZE_MB):
            # Generate 1MB of random data
            data = bytearray(random.getrandbits(8) for _ in range(1024 * 1024))
            f.write(data)

    # Calculate file hash for verification
    with open(TEST_FILE_PATH, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    print(f"Created test file with hash: {file_hash}")
    return file_hash


def start_origin_server():
    """Start the origin server and broadcast the test file."""
    print("Starting origin server...")

    # Use the example_usage.py script with origin mode
    cmd = [
        "python3",
        "examples/example_usage.py",
        "--mode",
        "origin",
        "--data-dir",
        ORIGIN_DATA_DIR,
        "--port",
        str(ORIGIN_PORT),
        "--file-path",
        TEST_FILE_PATH,
        "--log-level",
        "DEBUG",
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    PROCESSES.append(process)
    cmd_str = " ".join(cmd)
    print(f"Executing command: {cmd_str}")

    # Wait for the server to start
    error_output = []
    for _ in range(30):
        output = process.stdout.readline().strip()
        print(f"Origin: {output}")
        error_output.append(output)
        if "Origin server running" in output:
            break
        if process.poll() is not None:
            # Process exited, capture all remaining output
            for line in process.stdout:
                error_line = line.strip()
                print(f"Origin Error: {error_line}")
                error_output.append(error_line)

            # Raise exception with detailed error
            full_error = "\n".join(error_output)
            raise Exception(f"Origin server failed to start:\n{full_error}")
        time.sleep(0.1)

    # Extract version number from logs
    version = None
    for _ in range(10):
        output = process.stdout.readline().strip()
        print(f"Origin: {output}")
        if "File broadcast as version" in output:
            version = output.split("version ")[-1]
            break

    if not version:
        raise Exception("Failed to get version from origin server")

    print(f"Origin server started, broadcasting version: {version}")
    return version


def start_middle_node(port, data_dir, node_name="Middle"):
    """Start a middle node."""
    print(f"Starting {node_name} node on port {port}...")

    # Use the example_usage.py script with middle mode
    cmd = [
        "python3",
        "examples/example_usage.py",
        "--mode",
        "middle",
        "--data-dir",
        data_dir,
        "--port",
        str(port),
        "--upstream",
        f"localhost:{ORIGIN_PORT}",
        "--log-level",
        "DEBUG",
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    PROCESSES.append(process)

    # Wait for the server to start
    error_output = []
    for _ in range(30):
        output = process.stdout.readline().strip()
        print(f"{node_name}: {output}")
        error_output.append(output)
        if "Middle node running" in output:
            break
        if process.poll() is not None:
            # Process exited, capture all remaining output
            for line in process.stdout:
                error_line = line.strip()
                print(f"{node_name} Error: {error_line}")
                error_output.append(error_line)

            # Raise exception with detailed error
            full_error = "\n".join(error_output)
            raise Exception(f"{node_name} node failed to start:\n{full_error}")
        time.sleep(0.1)

    print(f"{node_name} node started on port {port}")
    return process


def verify_client_download(version, original_hash):
    """Run a client to download the file and verify its integrity."""
    print(f"Testing client download for version {version}...")

    # Create a temporary download directory
    download_dir = os.path.join(CLIENT_DATA_DIR, "downloads")
    os.makedirs(download_dir, exist_ok=True)

    # Run client in list mode first to verify version is available
    list_cmd = [
        "python3",
        "examples/example_usage.py",
        "--mode",
        "client",
        "--data-dir",
        download_dir,
        "--servers",
        f"localhost:{MIDDLE_PORT_1},localhost:{MIDDLE_PORT_2}",
        "--log-level",
        "DEBUG",
    ]

    print("Listing available versions...")
    list_result = subprocess.run(list_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    print(list_result.stdout)

    if version not in list_result.stdout:
        raise Exception(f"Version {version} not found in available versions")

    # Download the file
    download_cmd = [
        "python",
        "examples/example_usage.py",
        "--mode",
        "client",
        "--data-dir",
        download_dir,
        "--servers",
        f"localhost:{MIDDLE_PORT_1},localhost:{MIDDLE_PORT_2}",
        "--version",
        version,
        "--log-level",
        "DEBUG",
    ]

    print(f"Downloading version {version}...")
    download_result = subprocess.run(download_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    print(download_result.stdout)

    if "Successfully downloaded and reassembled" not in download_result.stdout:
        raise Exception(f"Failed to download version {version}")

    # Extract the downloaded file path
    output_lines = download_result.stdout.split("\n")
    downloaded_file = None
    for line in output_lines:
        if "Successfully downloaded and reassembled" in line:
            downloaded_file = line.split(": ")[-1]
            break

    if not downloaded_file:
        raise Exception("Could not find downloaded file path in output")

    # Verify file hash
    print(f"Verifying downloaded file: {downloaded_file}")
    with open(downloaded_file, "rb") as f:
        downloaded_hash = hashlib.sha256(f.read()).hexdigest()

    if downloaded_hash != original_hash:
        raise Exception(f"Hash mismatch! Original: {original_hash}, Downloaded: {downloaded_hash}")

    print("✅ Hash verification successful! Downloaded file matches original")
    return True


def main():
    """Run the end-to-end test."""
    try:
        print("=== SHARDCAST END-TO-END TEST ===")
        print(f"Test directory: {TEST_DIR}")

        # Step 1: Create a test file
        original_hash = create_test_file()

        # Step 2: Start the origin server
        version = start_origin_server()
        time.sleep(2)  # Wait for server to fully initialize

        # Step 3: Start the middle nodes
        middle_node1 = start_middle_node(MIDDLE_PORT_1, MIDDLE_NODE_1_DIR, "Middle Node 1")  # noqa: F841
        middle_node2 = start_middle_node(MIDDLE_PORT_2, MIDDLE_NODE_2_DIR, "Middle Node 2")  # noqa: F841
        time.sleep(5)  # Wait for nodes to sync with origin server

        # Step 4: Run client to download and verify
        success = verify_client_download(version, original_hash)

        # Test completed
        if success:
            print("\n✅ END-TO-END TEST PASSED!")
            return 0
        else:
            print("\n❌ END-TO-END TEST FAILED!")
            return 1

    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        return 1
    finally:
        cleanup()


if __name__ == "__main__":
    exit(main())
