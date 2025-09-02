"""
Custom exceptions for NATS IPC SDK.

This module defines specific exception types for better error handling
and debugging in distributed systems.
"""

from typing import Optional


class NATSIPCError(Exception):
    """Base exception for all NATS IPC SDK errors."""

    pass


class ConnectionError(NATSIPCError):
    """Raised when connection to NATS fails or is lost."""

    def __init__(self, message: str, url: Optional[str] = None):
        self.url = url
        super().__init__(f"Connection error{f' to {url}' if url else ''}: {message}")


class TimeoutError(NATSIPCError):
    """Raised when an RPC call times out."""

    def __init__(self, target: str, method: str, timeout: float):
        self.target = target
        self.method = method
        self.timeout = timeout
        super().__init__(f"Call to {target}.{method} timed out after {timeout} seconds")


class RemoteError(NATSIPCError):
    """Raised when a remote method raises an exception."""

    def __init__(self, target: str, method: str, error: str):
        self.target = target
        self.method = method
        self.error = error
        super().__init__(f"Remote error in {target}.{method}: {error}")


class SerializationError(NATSIPCError):
    """Raised when data cannot be serialized or deserialized."""

    def __init__(self, message: str, data_type: Optional[str] = None):
        self.data_type = data_type
        super().__init__(
            f"Serialization error{f' for type {data_type}' if data_type else ''}: {message}"
        )


class MethodNotFoundError(NATSIPCError):
    """Raised when a requested method is not registered."""

    def __init__(self, method: str, node_id: Optional[str] = None):
        self.method = method
        self.node_id = node_id
        super().__init__(
            f"Method '{method}' not found{f' on node {node_id}' if node_id else ''}"
        )


class InvalidRequestError(NATSIPCError):
    """Raised when an RPC request has invalid format."""

    def __init__(self, message: str):
        super().__init__(f"Invalid request format: {message}")
