# Shardcast

A Python package for distributing large files via an HTTP-based peer-to-peer network.

## Overview

Shardcast is designed to distribute large binary files through a multi-tier network, making it efficient to transfer large files to many clients:

1. **Origin Server**: The root node that shards a large file and serves the shards via HTTP
2. **Middle Nodes**: Intermediate servers that download shards from upstream servers and re-serve them
3. **Client Nodes**: End nodes that download and reassemble shards into the original file

## Features

- Automatically shards large files into configurable chunks (default: 50MB)
- Versioned distribution with auto-cleanup of old versions
- SHA-256 integrity verification for reassembled files
- Dynamic server performance tracking for optimal downloads
- Concurrent downloads with automatic retries
- Support for multiple distribution layers
- Simple API for broadcasting files

## Installation

```bash
# Install from source
git clone https://github.com/PrimeIntellect-ai/shardcast.git
cd shardcast
pip install -e .
```

## Usage

### Origin Server

Run as a standalone server:

```bash
# Start an origin server on port 8000
shardcast-origin --data-dir ./data --port 8000
```

Use as a library:

```python
import shardcast

# Initialize the package
shardcast.initialize(data_dir="./data", port=8000)

# Broadcast a file
version = shardcast.broadcast("/path/to/large_file.bin")
print(f"File broadcast as version {version}")

# Shut down when done
shardcast.shutdown()
```

### Middle Node

```bash
# Start a middle node that connects to an origin server
shardcast-middle --upstream 192.168.1.100 --data-dir ./middle_data --port 8001

# Connect to multiple upstream servers (comma-separated)
shardcast-middle --upstream 192.168.1.100,192.168.1.101 --data-dir ./middle_data --port 8001

# Using the IP_ADDR_LIST environment variable instead of --upstream
export IP_ADDR_LIST="192.168.1.100 192.168.1.101"
# or in bash array format
export IP_ADDR_LIST=("192.168.1.100" "192.168.1.101")
shardcast-middle --data-dir ./middle_data --port 8001
```

### Client Node

```bash
# List available versions
shardcast-client --servers 192.168.1.100,192.168.1.101 --list

# Download a specific version
shardcast-client --servers 192.168.1.100,192.168.1.101 --version v1 --output-file ./downloaded_file.bin

# Using the IP_ADDR_LIST environment variable instead of --servers
export IP_ADDR_LIST="192.168.1.100 192.168.1.101"
# or in bash array format
export IP_ADDR_LIST=("192.168.1.100" "192.168.1.101")
shardcast-client --list
```

## Configuration

Key constants are defined in `shardcast/constants.py`:

- `SHARD_SIZE`: Size of each shard in bytes (default: 50MB)
- `MAX_DISTRIBUTION_FOLDERS`: Maximum number of version folders to keep (default: 15)
- `HTTP_PORT`: Default HTTP port for servers (default: 8000)
- `RETRY_ATTEMPTS`: Number of retry attempts for failed downloads (default: 5)
- `MAX_CONCURRENT_DOWNLOADS`: Number of concurrent download threads (default: 10)

## Architecture

- **File Sharding**: The origin server splits files into shards named `shard_001.bin`, `shard_002.bin`, etc.
- **Distribution**: Shards are served via HTTP from the origin server and middle nodes.
- **Folder Versioning**: Each broadcast creates a new folder (e.g., `v1`, `v2`), with a maximum of 15 folders.
- **Discovery**: A `distribution.txt` file lists active shard folders and their SHA-256 checksums.
- **Download Optimization**: Clients download concurrently and prefer faster middle nodes based on runtime performance.
- **Integrity**: Clients verify the reassembled file using the SHA-256 checksum from `distribution.txt`.

```bash
cat distribution.txt
> v1: 4d1d960b53356285f45ea2e27c89a1a11d10a9601d3ba2a90851f9f227dd9295
```