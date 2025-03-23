#!/usr/bin/env python3
"""Example script demonstrating the usage of the shardcast package."""

import os
import sys
import time
import random
import argparse
import re
from typing import List

import shardcast
from shardcast.utils import logger


def create_dummy_file(file_path: str, size_mb: int = 100) -> None:
    """Create a dummy file of the specified size using random.randbytes."""
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

    print(f"Creating dummy file: {file_path} ({size_mb} MB)")
    with open(file_path, "wb") as f:
        for _ in range(size_mb):
            f.write(random.randbytes(1024 * 1024))  # 1MB of random data

    print(f"Created dummy file: {file_path} ({os.path.getsize(file_path) / (1024 * 1024):.2f} MB)")


def run_origin_server(data_dir: str, port: int, file_path: str) -> None:
    """Run an origin server and broadcast a file.

    Args:
        data_dir: Directory to store and serve shards from
        port: HTTP port to listen on
        file_path: Path to the file to broadcast
    """
    print(f"Starting origin server on port {port}")

    # Initialize the package
    shardcast.initialize(data_dir=data_dir, port=port)

    try:
        # Broadcast the file
        version = shardcast.broadcast(file_path)
        print(f"File broadcast as version {version}")

        # Keep the server running
        print("Origin server running. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        # Shut down when done
        shardcast.shutdown()


def run_middle_node(upstream_servers: List[str], data_dir: str, port: int) -> None:
    """Run a middle node.

    Args:
        upstream_servers: List of upstream server URLs or IP addresses
        data_dir: Directory to store and serve shards from
        port: HTTP port to listen on
    """
    print(f"Starting middle node on port {port}")
    print(f"Upstream servers: {', '.join(upstream_servers)}")

    # Create the middle node
    node = shardcast.MiddleNode(upstream_servers=upstream_servers, data_dir=data_dir, port=port)

    try:
        # Keep the server running
        print("Middle node running. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        # Shut down when done
        node.shutdown()


def run_client_node(servers: List[str], output_dir: str, version: str = None) -> None:
    """Run a client node.

    Args:
        servers: List of server URLs or IP addresses
        output_dir: Directory to save downloaded files
        version: Version to download, or None to download the latest version
    """
    print("Starting client node")
    print(f"Servers: {', '.join(servers)}")

    # Create the client node
    client = shardcast.ClientNode(servers, output_dir)

    # Get available versions
    print("Listing available versions")
    versions = client.list_available_versions()
    if not versions:
        print("No versions available or failed to retrieve distribution file")
        return

    # Display available versions
    print("Available versions:")
    for v, checksum in sorted(versions.items()):
        print(f"  {v} - Checksum: {checksum}")

    # If no version specified, use the latest one
    if not version:
        # Get the latest version by sorting numerically
        latest_version = sorted(versions.keys(), key=lambda v: int(v[1:]) if v.startswith("v") and v[1:].isdigit() else 0)[-1]
        print(f"No version specified, using latest version: {latest_version}")
        version = latest_version

    # Download the version
    print(f"Downloading version {version}")
    output_file = client.download_version(version)
    if output_file:
        print(f"Successfully downloaded and reassembled: {output_file}")
    else:
        print(f"Failed to download and reassemble version {version}")


def parse_ip_addr_list():
    """Parse IP_ADDR_LIST environment variable.

    Returns:
        List of IP addresses
    """
    ip_addr_list = os.environ.get("IP_ADDR_LIST")
    if not ip_addr_list:
        return []

    # Remove parentheses if present
    ip_addr_list = ip_addr_list.strip()
    if ip_addr_list.startswith("(") and ip_addr_list.endswith(")"):
        ip_addr_list = ip_addr_list[1:-1].strip()

    # Extract IPs within quotes
    quoted_ips = re.findall(r'"([^"]+)"', ip_addr_list)
    if quoted_ips:
        return quoted_ips

    # If no quoted IPs found, try space-separated format
    return [s.strip() for s in ip_addr_list.split() if s.strip()]


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Shardcast Example")
    parser.add_argument(
        "--mode",
        required=True,
        choices=["origin", "middle", "client"],
        help="Mode to run (origin, middle, or client)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=shardcast.HTTP_PORT,
        help=f"HTTP port to listen on (default: {shardcast.HTTP_PORT})",
    )
    parser.add_argument("--data-dir", default="./example_data", help="Directory to store data")
    parser.add_argument(
        "--upstream",
        help="Comma-separated list of upstream server URLs or IP addresses (optional if IP_ADDR_LIST env var is set)",
    )
    parser.add_argument(
        "--servers",
        help="Comma-separated list of server URLs or IP addresses (optional if IP_ADDR_LIST env var is set)",
    )
    parser.add_argument("--file-path", help="Path to the file to broadcast")
    parser.add_argument("--create-dummy", action="store_true", help="Create a dummy file for testing")
    parser.add_argument(
        "--dummy-size",
        type=int,
        default=100,
        help="Size of the dummy file in megabytes (default: 100)",
    )
    parser.add_argument("--version", help="Version to download (client mode only, defaults to latest version if not specified)")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )

    args = parser.parse_args()

    # Set log level
    logger.setLevel(args.log_level)

    if args.mode == "origin":
        # Run origin server
        if args.create_dummy:
            # Create a dummy file if requested
            dummy_path = args.file_path or os.path.join(args.data_dir, "dummy.bin")
            create_dummy_file(dummy_path, args.dummy_size)
            args.file_path = dummy_path

        if not args.file_path:
            print("Error: --file-path is required for origin mode")
            return 1

        run_origin_server(args.data_dir, args.port, args.file_path)

    elif args.mode == "middle":
        # Run middle node
        upstream_servers = []

        if args.upstream:
            # Parse from command-line argument
            upstream_servers = [s.strip() for s in args.upstream.split(",") if s.strip()]
        else:
            # Try to get from environment variable
            upstream_servers = parse_ip_addr_list()
            if not upstream_servers:
                print("Error: IP_ADDR_LIST environment variable not set and --upstream not provided")
                print("Set IP_ADDR_LIST='ip1 ip2 ip3' or use --upstream parameter")
                return 1

        if not upstream_servers:
            print("Error: No upstream servers specified")
            return 1

        print(f"Using upstream servers: {upstream_servers}")
        run_middle_node(upstream_servers, args.data_dir, args.port)

    elif args.mode == "client":
        # Run client node
        servers = []

        if args.servers:
            # Parse from command-line argument
            servers = [s.strip() for s in args.servers.split(",") if s.strip()]
        else:
            # Try to get from environment variable
            servers = parse_ip_addr_list()
            if not servers:
                print("Error: IP_ADDR_LIST environment variable not set and --servers not provided")
                print("Set IP_ADDR_LIST='ip1 ip2 ip3' or use --servers parameter")
                return 1

        if not servers:
            print("Error: No servers specified")
            return 1

        print(f"Using servers: {servers}")
        run_client_node(servers, args.data_dir, args.version)

    return 0


if __name__ == "__main__":
    sys.exit(main())
