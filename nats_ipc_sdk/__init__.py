"""
NATS IPC SDK - Enterprise-grade Inter-Process Communication SDK for NATS

A powerful yet minimal SDK for building distributed systems with NATS messaging.
Supports RPC, pub-sub patterns, and handles any Python object through pickle serialization.

Key Features:
    - Minimal dependencies (only nats-py required)
    - Support for any Python object type
    - Full async/await support
    - Automatic cluster failover
    - Comprehensive error handling
    - Built-in metrics and logging
    - Type-safe with full type hints

Quick Start:
    >>> from nats_ipc_sdk import IPCNode
    >>> async with IPCNode("my_service") as node:
    ...     await node.register("hello", lambda name: f"Hello {name}!")
    ...     result = await node.call("other_service", "greet", "World")
"""

from .core import IPCNode
from .exceptions import (
    NATSIPCError,
    ConnectionError,
    TimeoutError,
    RemoteError,
    SerializationError,
    MethodNotFoundError,
    InvalidRequestError,
)
from .utils import (
    setup_logging,
    timing_decorator,
    retry_decorator,
    Metrics,
    validate_node_id,
    format_bytes,
)

__version__ = "1.1.0"
__author__ = "Ryan"
__license__ = "MIT"
__email__ = "ryan@example.com"

__all__ = [
    # Core
    "IPCNode",
    # Exceptions
    "NATSIPCError",
    "ConnectionError",
    "TimeoutError",
    "RemoteError",
    "SerializationError",
    "MethodNotFoundError",
    "InvalidRequestError",
    # Utils
    "setup_logging",
    "timing_decorator",
    "retry_decorator",
    "Metrics",
    "validate_node_id",
    "format_bytes",
]

# Configure default logging
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
