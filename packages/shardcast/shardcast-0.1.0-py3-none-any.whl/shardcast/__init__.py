"""Shardcast: A package for distributing large files via HTTP."""

from shardcast.origin_server import OriginServer
from shardcast.middle_node import MiddleNode
from shardcast.client_node import ClientNode
from shardcast.constants import (
    SHARD_SIZE,
    MAX_DISTRIBUTION_FOLDERS,
    HTTP_PORT,
    MAX_MIDDLE_NODE_LAYERS,
    RETRY_ATTEMPTS,
    LOG_LEVEL,
)
from shardcast.utils import logger

# Create origin server instance
_origin_server = None


def initialize(data_dir: str = "./data", port: int = HTTP_PORT) -> None:
    """Initialize the shardcast package.

    Args:
        data_dir: Directory to store and serve shards from
        port: HTTP port to listen on
    """
    global _origin_server

    # Initialize the origin server
    if _origin_server is None:
        _origin_server = OriginServer(data_dir, port)
        logger.info(f"Shardcast initialized with data directory: {data_dir}")
    else:
        logger.warning("Shardcast already initialized")


def broadcast(file_path: str, shard_size: int = SHARD_SIZE) -> str:
    """Broadcast a file by sharding it and making it available for download.

    Args:
        file_path: Path to the file to broadcast
        shard_size: Size of each shard in bytes

    Returns:
        Version folder name
    """
    global _origin_server

    if _origin_server is None:
        raise RuntimeError("Shardcast not initialized. Call initialize() first.")

    return _origin_server.broadcast(file_path, shard_size)


def shutdown() -> None:
    """Shutdown the shardcast package."""
    global _origin_server

    if _origin_server is not None:
        _origin_server.shutdown()
        _origin_server = None
        logger.info("Shardcast shutdown complete")


__all__ = [
    "initialize",
    "broadcast",
    "shutdown",
    "OriginServer",
    "MiddleNode",
    "ClientNode",
    "SHARD_SIZE",
    "MAX_DISTRIBUTION_FOLDERS",
    "HTTP_PORT",
    "MAX_MIDDLE_NODE_LAYERS",
    "RETRY_ATTEMPTS",
    "LOG_LEVEL",
]
