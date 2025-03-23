"""Client module for downloading shards."""

import os
import time
import urllib.request
import urllib.error
import socket
import threading
from urllib.parse import urlparse, urljoin
from typing import List, Dict, Optional, Set
from concurrent.futures import ThreadPoolExecutor

from shardcast.constants import (
    HTTP_PORT,
    DISTRIBUTION_FILE,
    HTTP_TIMEOUT,
    MAX_CONCURRENT_DOWNLOADS,
    RETRY_ATTEMPTS,
    FAST_RETRY_ATTEMPTS,
    FAST_RETRY_INTERVAL,
    SLOW_RETRY_INTERVAL,
)
from shardcast.utils import logger, ensure_dir


class ShardDownloader:
    """Client for downloading shards from servers."""

    def __init__(self, servers: List[str], timeout: int = HTTP_TIMEOUT):
        """Initialize the shard downloader.

        Args:
            servers: List of server URLs or IP addresses
            timeout: Timeout for HTTP requests in seconds
        """
        self.servers = self._normalize_servers(servers)
        self.timeout = timeout

        # Server performance metrics
        self.server_metrics: Dict[str, Dict[str, float]] = {
            server: {"latency": 0.0, "speed": 0.0, "success_rate": 1.0} for server in self.servers
        }

        # Lock for thread-safe access to metrics
        self.metrics_lock = threading.Lock()

    def _normalize_servers(self, servers: List[str]) -> List[str]:
        """Normalize server URLs to include protocol and port if needed.

        Args:
            servers: List of server URLs or IP addresses

        Returns:
            List of normalized server URLs
        """
        normalized = []
        for server in servers:
            parsed = urlparse(server)

            if not parsed.scheme:
                # No scheme, assume HTTP
                server = f"http://{server}"
                parsed = urlparse(server)

            if not parsed.port:
                # No port, use default
                server = f"{parsed.scheme}://{parsed.netloc}:{HTTP_PORT}"
                if parsed.path:
                    server += parsed.path

            normalized.append(server)

        return normalized

    def _get_best_servers(self, num_servers: int = 3) -> List[str]:
        """Get the best servers based on performance metrics.

        Args:
            num_servers: Number of best servers to return

        Returns:
            List of best server URLs
        """
        with self.metrics_lock:
            # Sort servers by: success_rate (desc), speed (desc), latency (asc)
            sorted_servers = sorted(
                self.servers,
                key=lambda s: (
                    -self.server_metrics[s]["success_rate"],
                    -self.server_metrics[s]["speed"],
                    self.server_metrics[s]["latency"],
                ),
            )

            return sorted_servers[: min(num_servers, len(sorted_servers))]

    def _update_server_metrics(self, server: str, latency: float, speed: float, success: bool) -> None:
        """Update performance metrics for a server.

        Args:
            server: Server URL
            latency: Request latency in seconds
            speed: Download speed in bytes/second
            success: Whether the download was successful
        """
        with self.metrics_lock:
            metrics = self.server_metrics.get(server, {"latency": 0.0, "speed": 0.0, "success_rate": 1.0})

            # Update metrics with exponential moving average (alpha=0.3)
            alpha = 0.3
            metrics["latency"] = alpha * latency + (1 - alpha) * metrics["latency"]

            if speed > 0:
                metrics["speed"] = alpha * speed + (1 - alpha) * metrics["speed"]

            # Update success rate
            success_value = 1.0 if success else 0.0
            metrics["success_rate"] = alpha * success_value + (1 - alpha) * metrics["success_rate"]

            self.server_metrics[server] = metrics

    def download_file(self, url_path: str, output_path: str) -> bool:
        """Download a file from the best server.

        Args:
            url_path: Path component of the URL (e.g., "v1/shard_001.bin")
            output_path: Local path to save the file

        Returns:
            True if successful, False otherwise
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Try downloading from the best servers
        best_servers = self._get_best_servers()

        for retry in range(RETRY_ATTEMPTS):
            for server in best_servers:
                url = urljoin(server, url_path)

                try:
                    start_time = time.time()

                    # Send request and measure latency
                    req = urllib.request.Request(url)
                    with urllib.request.urlopen(req, timeout=self.timeout) as response:
                        latency = time.time() - start_time

                        # Start download and measure speed
                        download_start = time.time()
                        content = response.read()
                        download_time = time.time() - download_start

                        # Calculate speed in bytes/second
                        speed = len(content) / max(download_time, 0.001)

                        # Save the file
                        with open(output_path, "wb") as f:
                            f.write(content)

                        # Update metrics
                        self._update_server_metrics(server, latency, speed, True)

                        logger.debug(f"Downloaded {url_path} from {server} (latency: {latency:.3f}s, speed: {speed:.0f} B/s)")

                        return True

                except (urllib.error.URLError, socket.timeout) as e:
                    # Update metrics with failure
                    self._update_server_metrics(server, self.timeout, 0, False)
                    logger.debug(f"Failed to download {url_path} from {server}: {str(e)}")

            # If we get here, all servers failed
            if retry < RETRY_ATTEMPTS - 1:
                # Use fast retries for the first FAST_RETRY_ATTEMPTS attempts, then switch to slow retries, but never stop
                if retry < FAST_RETRY_ATTEMPTS:
                    wait_time = FAST_RETRY_INTERVAL
                    logger.info(f"Fast retrying download of {url_path} (attempt {retry + 1}/{RETRY_ATTEMPTS}, wait: {wait_time}s)")
                else:
                    wait_time = SLOW_RETRY_INTERVAL
                    logger.info(f"Slow retrying download of {url_path} (attempt {retry + 1}/{RETRY_ATTEMPTS}, wait: {wait_time}s)")
                
                # Wait before retrying
                time.sleep(wait_time)

        logger.error(f"Failed to download {url_path} after {RETRY_ATTEMPTS} attempts")
        return False

    def download_distribution_file(self) -> Optional[str]:
        """Download the distribution file.

        Returns:
            Content of the distribution file or None if failed
        """
        temp_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_distribution.txt")

        if self.download_file(DISTRIBUTION_FILE, temp_path):
            with open(temp_path, "r") as f:
                content = f.read()

            # Clean up
            os.unlink(temp_path)
            return content

        return None

    def download_shards(self, version: str, num_shards: int, output_dir: str) -> List[str]:
        """Download all shards for a version.

        Args:
            version: Version folder name (e.g., "v1")
            num_shards: Number of shards to download
            output_dir: Directory to save the shards

        Returns:
            List of successfully downloaded shard paths
        """
        ensure_dir(output_dir)

        # Track successfully downloaded shards
        successful_shards: List[str] = []
        failed_shards: Set[int] = set()

        # Use a thread pool for concurrent downloads
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_DOWNLOADS) as executor:
            futures = []

            for i in range(num_shards):
                shard_filename = f"shard_{i + 1:03d}.bin"
                url_path = f"{version}/{shard_filename}"
                output_path = os.path.join(output_dir, shard_filename)

                futures.append(executor.submit(self._download_shard_with_retry, url_path, output_path, i))

            # Wait for all downloads to complete
            for i, future in enumerate(futures):
                try:
                    result = future.result()
                    if result:
                        successful_shards.append(result)
                    else:
                        failed_shards.add(i)
                except Exception as e:
                    logger.error(f"Error downloading shard {i + 1}: {str(e)}")
                    failed_shards.add(i)

        # Report summary
        if failed_shards:
            logger.warning(f"Failed to download {len(failed_shards)} out of {num_shards} shards")
            logger.debug(f"Failed shard indices: {sorted(failed_shards)}")
        else:
            logger.info(f"Successfully downloaded all {num_shards} shards")

        return successful_shards

    def _download_shard_with_retry(self, url_path: str, output_path: str, shard_index: int) -> Optional[str]:
        """Download a shard with retries.

        Args:
            url_path: Path component of the URL
            output_path: Local path to save the shard
            shard_index: Index of the shard (for logging)

        Returns:
            Output path if successful, None otherwise
        """
        if self.download_file(url_path, output_path):
            return output_path
        return None
