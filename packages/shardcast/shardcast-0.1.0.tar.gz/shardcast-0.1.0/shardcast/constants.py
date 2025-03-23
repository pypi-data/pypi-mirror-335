"""Constants for the shardcast package."""

# Default shard size: 5MB in bytes
SHARD_SIZE = 50_000_000

# Maximum number of distribution folders to keep
MAX_DISTRIBUTION_FOLDERS = 15

# Default HTTP port for servers
HTTP_PORT = 8000

# Maximum number of middle node layers (informational)
MAX_MIDDLE_NODE_LAYERS = 2

# Number of retry attempts for failed downloads
RETRY_ATTEMPTS = 5

# Number of fast retries before switching to slow retries
FAST_RETRY_ATTEMPTS = 3

# Fast retry interval in seconds
FAST_RETRY_INTERVAL = 2

# Slow retry interval in seconds
SLOW_RETRY_INTERVAL = 15

# Default logging level
LOG_LEVEL = "INFO"

# Distribution file name
DISTRIBUTION_FILE = "distribution.txt"

# Default timeout for HTTP requests (in seconds)
HTTP_TIMEOUT = 30

# Number of concurrent download threads
MAX_CONCURRENT_DOWNLOADS = 10

# Folder prefix for distribution versions
VERSION_PREFIX = "v"
