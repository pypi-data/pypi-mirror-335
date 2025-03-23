"""Origin server for the shardcast package."""

import os
import time
import shutil
import argparse
import threading

import shardcast.server as server
from shardcast.constants import (
    SHARD_SIZE,
    MAX_DISTRIBUTION_FOLDERS,
    HTTP_PORT,
    DISTRIBUTION_FILE,
)
from shardcast.utils import (
    compute_checksum,
    get_next_version,
    update_distribution_file,
    get_shard_count,
    get_shard_filename,
    ensure_dir,
    logger,
)


class OriginServer:
    """Origin server for sharding and distributing files."""

    def __init__(self, data_dir: str, port: int = HTTP_PORT):
        """Initialize the origin server.

        Args:
            data_dir: Directory to store and serve shards from
            port: HTTP port to listen on
        """
        self.data_dir = os.path.abspath(data_dir)
        self.port = port
        self.shutdown_event = threading.Event()

        # Ensure data directory exists
        ensure_dir(self.data_dir)

        # Start HTTP server
        self.http_server, self.server_thread = server.run_server(self.data_dir, self.port, self.shutdown_event)

        # Create distribution file if it doesn't exist
        dist_file = os.path.join(self.data_dir, DISTRIBUTION_FILE)
        if not os.path.exists(dist_file):
            with open(dist_file, "w") as f:  # noqa: F841
                pass

    def broadcast(self, file_path: str, shard_size: int = SHARD_SIZE) -> str:
        """Broadcast a file by sharding it and making it available for download.

        Args:
            file_path: Path to the file to broadcast
            shard_size: Size of each shard in bytes

        Returns:
            Version folder name
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get file size and compute checksum
        file_size = os.path.getsize(file_path)
        checksum = compute_checksum(file_path)

        # Get next version
        version = get_next_version(self.data_dir)
        version_dir = os.path.join(self.data_dir, version)

        # Create version directory
        ensure_dir(version_dir)

        # Shard the file
        num_shards = get_shard_count(file_size, shard_size)

        logger.info(f"Broadcasting file {os.path.basename(file_path)} ({file_size} bytes) as {version}")
        logger.info(f"Sharding into {num_shards} shards of {shard_size} bytes each")

        with open(file_path, "rb") as f_in:
            for i in range(num_shards):
                shard_path = os.path.join(version_dir, get_shard_filename(i))

                # Read a chunk of the file
                chunk = f_in.read(shard_size)

                # Write the chunk to a shard file
                with open(shard_path, "wb") as f_out:
                    f_out.write(chunk)

                logger.debug(f"Created shard {i + 1}/{num_shards}: {shard_path}")

        # Update distribution file with number of shards
        dist_file = os.path.join(self.data_dir, DISTRIBUTION_FILE)
        versions_to_remove = update_distribution_file(dist_file, version, checksum, MAX_DISTRIBUTION_FOLDERS, num_shards)

        # Remove old versions if necessary
        for v in versions_to_remove:
            old_dir = os.path.join(self.data_dir, v)
            if os.path.exists(old_dir):
                shutil.rmtree(old_dir)
                logger.info(f"Removed old version: {v}")

        logger.info(f"file was chunked, version={version} ({num_shards} shards)")
        return version

    def shutdown(self) -> None:
        """Shutdown the server."""
        logger.info("Shutting down origin server...")
        self.shutdown_event.set()
        # Give the server thread a chance to exit cleanly
        time.sleep(0.5)

        if self.server_thread.is_alive():
            # Force shutdown if thread is still alive
            logger.warning("Server thread did not exit cleanly, forcing shutdown")


def main():
    """Run the origin server as a standalone script."""
    parser = argparse.ArgumentParser(description="Shardcast Origin Server")
    parser.add_argument("--data-dir", default="./data", help="Directory to store and serve shards from")
    parser.add_argument(
        "--port",
        type=int,
        default=HTTP_PORT,
        help=f"HTTP port to listen on (default: {HTTP_PORT})",
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

    # Start the origin server
    origin = OriginServer(args.data_dir, args.port)

    try:
        logger.info(f"Origin server running at http://{server.get_local_ip()}:{args.port}")
        logger.info(f"Serving files from {os.path.abspath(args.data_dir)}")
        logger.info("Press Ctrl+C to exit")

        # Keep the main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        origin.shutdown()


if __name__ == "__main__":
    main()
