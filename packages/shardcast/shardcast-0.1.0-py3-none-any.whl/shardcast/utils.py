"""Utility functions for the shardcast package."""

import os
import hashlib
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional

from shardcast.constants import VERSION_PREFIX

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def compute_checksum(file_path: str) -> str:
    """Compute the SHA-256 checksum of a file.

    Args:
        file_path: Path to the file

    Returns:
        SHA-256 checksum as a hex string
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def verify_checksum(file_path: str, expected_checksum: str) -> bool:
    """Verify the checksum of a file.

    Args:
        file_path: Path to the file
        expected_checksum: Expected SHA-256 checksum

    Returns:
        True if the checksum matches, False otherwise
    """
    actual_checksum = compute_checksum(file_path)
    return actual_checksum == expected_checksum


def get_next_version(base_dir: str) -> str:
    """Get the next version folder name.

    Args:
        base_dir: Base directory for version folders

    Returns:
        Next version folder name (e.g., 'v1', 'v2', etc.)
    """
    version_pattern = re.compile(f"^{VERSION_PREFIX}(\\d+)$")
    version = 0

    if os.path.exists(base_dir):
        for item in os.listdir(base_dir):
            if os.path.isdir(os.path.join(base_dir, item)):
                match = version_pattern.match(item)
                if match:
                    current_version = int(match.group(1))
                    version = max(version, current_version)

    return f"{VERSION_PREFIX}{version + 1}"


def get_all_versions(base_dir: str) -> List[str]:
    """Get all version folders sorted by version number.

    Args:
        base_dir: Base directory for version folders

    Returns:
        List of version folder names sorted by version number
    """
    version_pattern = re.compile(f"^{VERSION_PREFIX}(\\d+)$")
    versions = []

    if os.path.exists(base_dir):
        for item in os.listdir(base_dir):
            if os.path.isdir(os.path.join(base_dir, item)):
                match = version_pattern.match(item)
                if match:
                    versions.append((int(match.group(1)), item))

    # Sort by version number
    versions.sort()
    return [v[1] for v in versions]


def parse_distribution_file(file_path: str) -> Dict[str, str]:
    """Parse the distribution file.

    Args:
        file_path: Path to the distribution file

    Returns:
        Dictionary mapping version folder names to info string (checksum|num_shards or just checksum for backward compatibility)
    """
    result = {}
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and ":" in line:
                    version, info = line.split(":", 1)
                    result[version.strip()] = info.strip()
    return result


def update_distribution_file(file_path: str, version: str, checksum: str, max_versions: int, num_shards: int) -> List[str]:
    """Update the distribution file with a new version.

    Args:
        file_path: Path to the distribution file
        version: Version folder name
        checksum: Checksum of the original file
        max_versions: Maximum number of versions to keep
        num_shards: Number of shards for this version

    Returns:
        List of versions to remove (if any)
    """
    versions_to_remove = []

    # Read existing distribution file
    distribution = parse_distribution_file(file_path)

    # Add or update the new version with checksum and number of shards
    distribution[version] = f"{checksum}|{num_shards}"

    # Remove oldest versions if exceeding max_versions
    if len(distribution) > max_versions:
        # Get versions sorted by number
        sorted_versions = sorted(
            distribution.keys(),
            key=lambda v: int(v[len(VERSION_PREFIX) :]) if v.startswith(VERSION_PREFIX) else 0,
        )

        # Determine versions to remove
        versions_to_remove = sorted_versions[: len(distribution) - max_versions]

        # Remove from distribution dictionary
        for v in versions_to_remove:
            del distribution[v]

    # Write updated distribution file
    with open(file_path, "w") as f:
        for v, info in sorted(
            distribution.items(),
            key=lambda item: int(item[0][len(VERSION_PREFIX) :]) if item[0].startswith(VERSION_PREFIX) else 0,
        ):
            f.write(f"{v}: {info}\n")

    return versions_to_remove


def get_shard_count(file_size: int, shard_size: int) -> int:
    """Calculate the number of shards for a file.

    Args:
        file_size: Size of the file in bytes
        shard_size: Size of each shard in bytes

    Returns:
        Number of shards required
    """
    return (file_size + shard_size - 1) // shard_size


def extract_checksum_from_info(info: str) -> str:
    """Extract checksum from distribution file info string.

    Args:
        info: Information string from distribution file (checksum|num_shards or just checksum)

    Returns:
        Checksum string
    """
    if "|" in info:
        return info.split("|")[0]
    return info


def extract_shard_count_from_info(info: str) -> Optional[int]:
    """Extract shard count from distribution file info string.

    Args:
        info: Information string from distribution file (checksum|num_shards or just checksum)

    Returns:
        Number of shards if available, None otherwise
    """
    if "|" in info:
        try:
            return int(info.split("|")[1])
        except (IndexError, ValueError):
            return None
    return None


def get_shard_filename(shard_index: int) -> str:
    """Get the filename for a shard.

    Args:
        shard_index: Index of the shard (0-based)

    Returns:
        Shard filename (e.g., 'shard_001.bin')
    """
    return f"shard_{shard_index + 1:03d}.bin"


def ensure_dir(directory: str) -> None:
    """Ensure a directory exists.

    Args:
        directory: Directory path
    """
    Path(directory).mkdir(parents=True, exist_ok=True)
