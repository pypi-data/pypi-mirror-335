"""HTTP server module for serving shards."""

import socket
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Optional, Tuple

from shardcast.constants import HTTP_PORT
from shardcast.utils import logger


class ShardcastRequestHandler(SimpleHTTPRequestHandler):
    """HTTP request handler for serving shards."""

    def __init__(self, *args, **kwargs):
        # Disable logging of requests to stdout
        self.server = args[2]  # server is passed as the third argument
        super().__init__(*args, **kwargs, directory=self.server.directory)

    def log_message(self, format: str, *args) -> None:
        """Override to use our logger instead of printing to stderr."""
        logger.debug(
            "%s - - [%s] %s",
            self.address_string(),
            self.log_date_time_string(),
            format % args,
        )

    def end_headers(self) -> None:
        """Add CORS headers to all responses."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type")
        super().end_headers()


class ShardcastServer(HTTPServer):
    """HTTP server for serving shards."""

    def __init__(
        self,
        server_address: Tuple[str, int],
        directory: str,
        shutdown_event: Optional[threading.Event] = None,
    ):
        """Initialize the server.

        Args:
            server_address: (host, port) tuple
            directory: Directory to serve files from
            shutdown_event: Event to signal server shutdown
        """
        super().__init__(server_address, ShardcastRequestHandler)
        self.directory = directory
        self.shutdown_event = shutdown_event or threading.Event()


def get_local_ip() -> str:
    """Get the local IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to be reachable
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def run_server(
    directory: str,
    port: int = HTTP_PORT,
    shutdown_event: Optional[threading.Event] = None,
) -> Tuple[HTTPServer, threading.Thread]:
    """Run an HTTP server in a background thread.

    Args:
        directory: Directory to serve files from
        port: Port to listen on
        shutdown_event: Event to signal server shutdown

    Returns:
        Tuple of (server, thread)
    """
    shutdown_event = shutdown_event or threading.Event()
    server = ShardcastServer(("0.0.0.0", port), directory, shutdown_event)

    server_thread = threading.Thread(target=_server_thread, args=(server, shutdown_event))
    server_thread.daemon = True
    server_thread.start()

    local_ip = get_local_ip()
    logger.info(f"Server running at http://{local_ip}:{port}")

    return server, server_thread


def _server_thread(server: HTTPServer, shutdown_event: threading.Event) -> None:
    """Thread function for running the HTTP server.

    Args:
        server: HTTP server instance
        shutdown_event: Event to signal server shutdown
    """
    try:
        while not shutdown_event.is_set():
            server.handle_request()
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        server.server_close()
        logger.info("Server stopped")
