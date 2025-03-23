"""Client node for downloading and reassembling shards."""

import os
import sys
import time
import argparse
from typing import List, Dict, Optional

from shardcast.client import ShardDownloader
from shardcast.utils import (
    ensure_dir,
    get_shard_filename,
    verify_checksum,
    logger,
)


class ClientNode:
    """Client node for downloading and reassembling shards."""

    def __init__(self, servers: List[str], output_dir: str = "./downloads"):
        """Initialize the client node.

        Args:
            servers: List of server URLs or IP addresses
            output_dir: Directory to save downloaded files
        """
        self.servers = servers
        self.output_dir = os.path.abspath(output_dir)

        # Create downloader
        self.downloader = ShardDownloader(servers)

        # Ensure output directory exists
        ensure_dir(self.output_dir)

    def list_available_versions(self) -> Dict[str, str]:
        """List available versions from the distribution file.

        Returns:
            Dictionary mapping version names to file checksums
        """
        # Download distribution file
        distribution_content = self.downloader.download_distribution_file()
        if not distribution_content:
            logger.error("Failed to download distribution file")
            return {}

        # Parse the distribution file
        distribution = {}
        for line in distribution_content.strip().split("\n"):
            if line and ":" in line:
                version, info = line.strip().split(":", 1)
                distribution[version.strip()] = info.strip()

        return distribution

    def download_version(self, version: str, output_file: Optional[str] = None) -> Optional[str]:
        """Download a specific version and reassemble the original file.

        Args:
            version: Version to download (e.g., "v1")
            output_file: Path to save the reassembled file, or None to use default

        Returns:
            Path to the reassembled file, or None if failed
        """
        # Get information about available versions
        available_versions = self.list_available_versions()
        if not available_versions:
            logger.error("No versions available for download")
            return None

        if version not in available_versions:
            logger.error(f"Version {version} not found in distribution")
            logger.info(f"Available versions: {', '.join(sorted(available_versions.keys()))}")
            return None

        version_info = available_versions[version]
        from shardcast.utils import extract_checksum_from_info, extract_shard_count_from_info

        checksum = extract_checksum_from_info(version_info)
        shard_count = extract_shard_count_from_info(version_info)

        if shard_count is not None:
            logger.info(f"Downloading version {version} (checksum: {checksum}, shards: {shard_count})")
        else:
            logger.info(f"Downloading version {version} (checksum: {checksum}, unknown shard count)")

        # Create temporary directory for shards
        temp_dir = os.path.join(self.output_dir, f"temp_{version}")
        ensure_dir(temp_dir)

        try:
            # Discover and download shards
            shard_paths = self._discover_and_download_shards(version, temp_dir)

            if not shard_paths:
                logger.error(f"Failed to download any shards for version {version}")
                return None

            # Sort shards by index
            sorted_shards = sorted(shard_paths)

            # Determine output file path
            if output_file is None:
                output_file = os.path.join(self.output_dir, f"download_{version}.bin")
            else:
                output_file = os.path.abspath(output_file)
                # Ensure output directory exists
                ensure_dir(os.path.dirname(output_file))

            # Reassemble file
            logger.info(f"Reassembling file from {len(sorted_shards)} shards")

            # Start timer for total file download
            start_time = time.time()
            total_size = 0

            with open(output_file, "wb") as out_file:
                for shard_path in sorted_shards:
                    with open(shard_path, "rb") as shard_file:
                        shard_data = shard_file.read()
                        total_size += len(shard_data)
                        out_file.write(shard_data)

            # Calculate download time and speed
            download_time = time.time() - start_time
            download_speed_bps = total_size / max(download_time, 0.001)
            download_speed_mbps = download_speed_bps / (1024 * 1024)

            logger.info(f"Downloaded {total_size / (1024 * 1024):.2f} MB in {download_time:.2f} seconds")
            logger.info(f"Average download speed: {download_speed_mbps:.2f} MB/s")

            # Verify checksum
            logger.info("Verifying file integrity...")
            if verify_checksum(output_file, checksum):
                logger.info(f"Checksum verification passed for {output_file}")
            else:
                logger.error(f"Checksum verification failed for {output_file}")
                return None

            return output_file

        finally:
            # Clean up temporary directory
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)

    def _discover_and_download_shards(self, version: str, output_dir: str) -> List[str]:
        """Discover and download all shards for a version.

        Args:
            version: Version to download (e.g., "v1")
            output_dir: Directory to save shards

        Returns:
            List of paths to downloaded shards
        """
        # Start timer for download process
        start_time = time.time()

        # Get version info from distribution file to check for known shard count
        available_versions = self.list_available_versions()
        known_shard_count = None

        if version in available_versions:
            from shardcast.utils import extract_shard_count_from_info

            known_shard_count = extract_shard_count_from_info(available_versions[version])

        if known_shard_count is not None:
            logger.info(f"Distribution file indicates {known_shard_count} shards for version {version}")
            # Download all shards at once since we know how many there are
            shards = self.downloader.download_shards(version, known_shard_count, output_dir)

            # Calculate total downloaded size
            total_size = sum(os.path.getsize(shard) for shard in shards if os.path.exists(shard))

            # Calculate download speed
            download_time = time.time() - start_time
            download_speed_bps = total_size / max(download_time, 0.001)
            download_speed_mbps = download_speed_bps / (1024 * 1024)

            logger.info(f"Downloaded {total_size / (1024 * 1024):.2f} MB in {download_time:.2f} seconds")
            logger.info(f"Average download speed: {download_speed_mbps:.2f} MB/s")

            return shards

        # If shard count is unknown, use discovery mode
        logger.info(f"Discovering shards for version {version} (count unknown)")

        # Start with a reasonable number of shards to try
        initial_shard_count = 10

        # Download the first batch of shards
        initial_shards = self.downloader.download_shards(version, initial_shard_count, output_dir)

        if not initial_shards:
            return []

        # If we got all the initial shards, try to find more
        if len(initial_shards) == initial_shard_count:
            logger.info(f"Found at least {initial_shard_count} shards, searching for more")

            # Continue looking for more shards until we get a failure
            max_shard_index = initial_shard_count
            consecutive_failures = 0
            max_consecutive_failures = 3

            while consecutive_failures < max_consecutive_failures:
                max_shard_index += 1
                shard_filename = get_shard_filename(max_shard_index - 1)
                shard_path = os.path.join(output_dir, shard_filename)
                url_path = f"{version}/{shard_filename}"

                if self.downloader.download_file(url_path, shard_path):
                    initial_shards.append(shard_path)
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    logger.debug(f"Failed to find shard {max_shard_index} (failure {consecutive_failures}/{max_consecutive_failures})")

            # Calculate total downloaded size
            total_size = sum(os.path.getsize(shard) for shard in initial_shards if os.path.exists(shard))

            # Calculate download speed
            download_time = time.time() - start_time
            download_speed_bps = total_size / max(download_time, 0.001)
            download_speed_mbps = download_speed_bps / (1024 * 1024)

            logger.info(f"Downloaded {total_size / (1024 * 1024):.2f} MB in {download_time:.2f} seconds")
            logger.info(f"Average download speed: {download_speed_mbps:.2f} MB/s")

            logger.info(f"Found {len(initial_shards)} total shards")

        return initial_shards


def main():
    """Run the client node as a standalone script."""
    parser = argparse.ArgumentParser(description="Shardcast Client Node")
    parser.add_argument(
        "--servers",
        help="Comma-separated list of server URLs or IP addresses (optional if IP_ADDR_LIST env var is set)",
    )
    parser.add_argument("--output-dir", default="./downloads", help="Directory to save downloaded files")
    parser.add_argument("--list", action="store_true", help="List available versions and exit")
    parser.add_argument("--version", help="Version to download (e.g., 'v1')")
    parser.add_argument("--output-file", help="Output file path for the reassembled file")
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

    servers = []

    if args.servers:
        # Parse from command-line argument
        servers = [s.strip() for s in args.servers.split(",") if s.strip()]
    else:
        # Try to get from environment variable
        ip_addr_list = os.environ.get("IP_ADDR_LIST")
        if not ip_addr_list:
            logger.error("IP_ADDR_LIST environment variable not set and --servers not provided")
            logger.error("Set IP_ADDR_LIST='ip1 ip2 ip3' or use --servers parameter")
            return 1

        # Parse the environment variable - expected format: ("ip1" "ip2" "ip3")
        # Remove parentheses if present
        ip_addr_list = ip_addr_list.strip()
        if ip_addr_list.startswith("(") and ip_addr_list.endswith(")"):
            ip_addr_list = ip_addr_list[1:-1].strip()

        # Extract IPs within quotes
        quoted_ips = re.findall(r'"([^"]+)"', ip_addr_list)
        if quoted_ips:
            servers = quoted_ips
        else:
            # If no quoted IPs found, try space-separated format
            servers = [s.strip() for s in ip_addr_list.split() if s.strip()]

    if not servers:
        logger.error("No servers specified")
        return 1

    logger.info(f"Using servers: {servers}")

    # Create client
    client = ClientNode(servers, args.output_dir)

    if args.list:
        # List available versions
        versions = client.list_available_versions()
        if versions:
            logger.info("Available versions:")
            for version, checksum in sorted(versions.items()):
                logger.info(f"  {version} - Checksum: {checksum}")
        else:
            logger.error("No versions available or failed to retrieve distribution file")
            return 1
    elif args.version:
        # Download specific version
        output_file = client.download_version(args.version, args.output_file)
        if output_file:
            logger.info(f"Successfully downloaded and reassembled: {output_file}")
        else:
            logger.error(f"Failed to download and reassemble version {args.version}")
            return 1
    else:
        logger.error("Either --list or --version must be specified")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
