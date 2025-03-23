"""Middle node for the shardcast package."""

import os
import time
import argparse
import threading
import sys
from typing import List, Dict, Set

import shardcast.server as server
from shardcast.client import ShardDownloader
from shardcast.constants import (
    HTTP_PORT,
    DISTRIBUTION_FILE,
    HTTP_TIMEOUT,
)
from shardcast.utils import (
    ensure_dir,
    logger,
)


class MiddleNode:
    """Middle node for downloading and re-serving shards."""

    def __init__(
        self,
        upstream_servers: List[str],
        data_dir: str,
        port: int = HTTP_PORT,
        check_interval: int = 30,
    ):
        """Initialize the middle node.

        Args:
            upstream_servers: List of upstream server URLs or IP addresses
            data_dir: Directory to store and serve shards from
            port: HTTP port to listen on
            check_interval: Interval in seconds to check for new versions
        """
        self.upstream_servers = upstream_servers
        self.data_dir = os.path.abspath(data_dir)
        self.port = port
        self.check_interval = check_interval

        # Create downloader for fetching from upstream servers
        self.downloader = ShardDownloader(upstream_servers, HTTP_TIMEOUT)

        # Track which versions we have already processed
        self.processed_versions: Set[str] = set()

        # Track known shards per version
        self.known_shards: Dict[str, int] = {}

        # Processing lock
        self.lock = threading.Lock()

        # Shutdown event
        self.shutdown_event = threading.Event()

        # Ensure data directory exists
        ensure_dir(self.data_dir)

        # Start HTTP server
        self.http_server, self.server_thread = server.run_server(self.data_dir, self.port, self.shutdown_event)

        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_upstream)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def _monitor_upstream(self) -> None:
        """Monitor upstream servers for new versions."""
        while not self.shutdown_event.is_set():
            try:
                # Download and parse distribution file
                distribution_content = self.downloader.download_distribution_file()

                if distribution_content:
                    # Parse the distribution file into a dictionary
                    distribution = {}
                    for line in distribution_content.strip().split("\n"):
                        if line and ":" in line:
                            version, info = line.strip().split(":", 1)
                            distribution[version.strip()] = info.strip()

                    # Process each version
                    for version, info in distribution.items():
                        self._process_version(version, info)

                # Create local distribution file for clients
                local_dist_path = os.path.join(self.data_dir, DISTRIBUTION_FILE)

                # Copy the discovered versions to our own distribution file
                with open(local_dist_path, "w") as f:
                    for version, info in sorted(distribution.items()):
                        # Only list versions that we have actually processed
                        if version in self.processed_versions:
                            # If we have discovered a different shard count, update the info
                            if version in self.known_shards:
                                from shardcast.utils import extract_checksum_from_info

                                checksum = extract_checksum_from_info(info)
                                known_shard_count = self.known_shards[version]
                                f.write(f"{version}: {checksum}|{known_shard_count}\n")
                            else:
                                f.write(f"{version}: {info}\n")

            except Exception as e:
                logger.error(f"Error monitoring upstream servers: {str(e)}")

            # Wait before checking again
            time.sleep(self.check_interval)

    def _process_version(self, version: str, info: str) -> None:
        """Process a version by downloading and serving its shards.

        Args:
            version: Version folder name (e.g., "v1")
            info: Information string with checksum and optionally shard count
        """
        with self.lock:
            # Skip if we've already processed this version
            if version in self.processed_versions:
                return

            # Extract checksum and possibly shard count from info
            from shardcast.utils import extract_checksum_from_info, extract_shard_count_from_info

            checksum = extract_checksum_from_info(info)
            shard_count = extract_shard_count_from_info(info)

            version_dir = os.path.join(self.data_dir, version)
            ensure_dir(version_dir)

            # If we know the exact number of shards, download them directly
            if shard_count is not None:
                logger.info(f"Distribution file indicates {shard_count} shards for version {version}")

                # Start timer for total file download
                start_time = time.time()
                total_size = 0

                # Download all shards in sequence
                for i in range(1, shard_count + 1):
                    shard_filename = f"shard_{i:03d}.bin"
                    shard_path = os.path.join(version_dir, shard_filename)
                    url_path = f"{version}/{shard_filename}"

                    if self.downloader.download_file(url_path, shard_path):
                        # Add shard size to total
                        total_size += os.path.getsize(shard_path)
                        logger.debug(f"Downloaded shard {i}/{shard_count} for version {version}")
                    else:
                        logger.warning(f"Failed to download shard {i}/{shard_count} for version {version}")

                # Calculate download time and speed
                download_time = time.time() - start_time
                download_speed_bps = total_size / max(download_time, 0.001)
                download_speed_mbps = download_speed_bps / (1024 * 1024)

                logger.info(f"Downloaded {total_size / (1024 * 1024):.2f} MB in {download_time:.2f} seconds")
                logger.info(f"Average download speed: {download_speed_mbps:.2f} MB/s")

                # Set as processed and store shard count
                self.known_shards[version] = shard_count
                self.processed_versions.add(version)
                logger.info(f"Finished downloading all {shard_count} shards for version {version}")
                return

            # If shard count unknown, use discovery method
            logger.info(f"Discovering shards for version {version} (count unknown)")

            shard_index = 1
            found_shards = 0

            # Try downloading the first few shards to determine total count
            while shard_index <= 10:  # Try up to 10 shards to start
                shard_filename = f"shard_{shard_index:03d}.bin"
                shard_path = os.path.join(version_dir, shard_filename)
                url_path = f"{version}/{shard_filename}"

                if self.downloader.download_file(url_path, shard_path):
                    found_shards = shard_index
                    shard_index += 1
                else:
                    break

            if found_shards == 0:
                logger.warning(f"No shards found for version {version}")
                return

            # Continue downloading shards in the background
            self.known_shards[version] = found_shards
            self.processed_versions.add(version)

            # Start a thread to continue downloading more shards if they exist
            threading.Thread(
                target=self._continue_downloading_shards,
                args=(version, found_shards),
                daemon=True,
            ).start()

    def _continue_downloading_shards(self, version: str, start_index: int) -> None:
        """Continue downloading additional shards for a version.

        Args:
            version: Version folder name (e.g., "v1")
            start_index: 1-based index to start from
        """
        version_dir = os.path.join(self.data_dir, version)

        logger.info(f"Continuing to download shards for {version} starting from {start_index + 1}")

        # Start timer for total file download
        start_time = time.time()
        total_size = 0

        # Calculate size of already downloaded shards
        for i in range(1, start_index + 1):
            shard_path = os.path.join(version_dir, f"shard_{i:03d}.bin")
            if os.path.exists(shard_path):
                total_size += os.path.getsize(shard_path)

        shard_index = start_index + 1
        consecutive_failures = 0
        max_consecutive_failures = 3

        while consecutive_failures < max_consecutive_failures:
            shard_filename = f"shard_{shard_index:03d}.bin"
            shard_path = os.path.join(version_dir, shard_filename)
            url_path = f"{version}/{shard_filename}"

            if self.downloader.download_file(url_path, shard_path):
                # Add shard size to total
                total_size += os.path.getsize(shard_path)
                logger.debug(f"Downloaded shard {shard_index} for version {version}")
                consecutive_failures = 0

                # Update known shards count
                with self.lock:
                    self.known_shards[version] = shard_index

                shard_index += 1
            else:
                consecutive_failures += 1
                logger.debug(
                    f"Failed to download shard {shard_index} for version {version} "
                    f"(failure {consecutive_failures}/{max_consecutive_failures})"
                )

        # Calculate download time and speed
        download_time = time.time() - start_time
        download_speed_bps = total_size / max(download_time, 0.001)
        download_speed_mbps = download_speed_bps / (1024 * 1024)

        logger.info(f"Downloaded {total_size / (1024 * 1024):.2f} MB in {download_time:.2f} seconds")
        logger.info(f"Average download speed: {download_speed_mbps:.2f} MB/s")

        logger.info(f"Finished downloading shards for version {version}, found {self.known_shards.get(version, 0)} shards")

    def shutdown(self) -> None:
        """Shutdown the middle node."""
        logger.info("Shutting down middle node...")
        self.shutdown_event.set()

        # Give threads a chance to exit cleanly
        time.sleep(0.5)

        if self.monitor_thread.is_alive():
            logger.warning("Monitor thread did not exit cleanly")

        if self.server_thread.is_alive():
            logger.warning("Server thread did not exit cleanly")


def main():
    """Run the middle node as a standalone script."""
    parser = argparse.ArgumentParser(description="Shardcast Middle Node")
    parser.add_argument(
        "--upstream",
        help="Comma-separated list of upstream server URLs or IP addresses (optional if IP_ADDR_LIST env var is set)",
    )
    parser.add_argument(
        "--data-dir",
        default="./middle_data",
        help="Directory to store and serve shards from",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=HTTP_PORT,
        help=f"HTTP port to listen on (default: {HTTP_PORT})",
    )
    parser.add_argument(
        "--check-interval",
        type=int,
        default=30,
        help="Interval in seconds to check for new versions (default: 30)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )

    args = parser.parse_args()

    # Set log level
    logger.setLevel(args.log_level)

    # Check if IP_ADDR_LIST environment variable is set
    import os
    import re

    upstream_servers = []

    if args.upstream:
        # Parse from command-line argument
        upstream_servers = [s.strip() for s in args.upstream.split(",") if s.strip()]
    else:
        # Try to get from environment variable
        ip_addr_list = os.environ.get("IP_ADDR_LIST")
        if not ip_addr_list:
            logger.error("IP_ADDR_LIST environment variable not set and --upstream not provided")
            logger.error("Set IP_ADDR_LIST='ip1 ip2 ip3' or use --upstream parameter")
            return 1

        # Parse the environment variable - expected format: ("ip1" "ip2" "ip3")
        # Remove parentheses if present
        ip_addr_list = ip_addr_list.strip()
        if ip_addr_list.startswith("(") and ip_addr_list.endswith(")"):
            ip_addr_list = ip_addr_list[1:-1].strip()

        # Extract IPs within quotes
        quoted_ips = re.findall(r'"([^"]+)"', ip_addr_list)
        if quoted_ips:
            upstream_servers = quoted_ips
        else:
            # If no quoted IPs found, try space-separated format
            upstream_servers = [s.strip() for s in ip_addr_list.split() if s.strip()]

    if not upstream_servers:
        logger.error("No upstream servers specified")
        return 1

    logger.info(f"Using upstream servers: {upstream_servers}")

    # Start the middle node
    node = MiddleNode(
        upstream_servers=upstream_servers,
        data_dir=args.data_dir,
        port=args.port,
        check_interval=args.check_interval,
    )

    try:
        logger.info(f"Middle node running at http://{server.get_local_ip()}:{args.port}")
        logger.info(f"Serving files from {os.path.abspath(args.data_dir)}")
        logger.info(f"Monitoring upstream servers: {', '.join(upstream_servers)}")
        logger.info("Press Ctrl+C to exit")

        # Keep the main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        node.shutdown()

    return 0


if __name__ == "__main__":
    sys.exit(main())
