"""
Utility functions for NATS IPC SDK.

This module provides helper functions for logging, metrics, and debugging.
"""

import asyncio
import functools
import logging
import time
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from datetime import datetime

# Set up logging
logger = logging.getLogger("nats_ipc_sdk")

# Type variables
F = TypeVar("F", bound=Callable[..., Any])


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure logging for the NATS IPC SDK.

    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO)
    """
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)


def timing_decorator(func: F) -> F:
    """
    Decorator to measure and log execution time of functions.

    Args:
        func: Function to decorate

    Returns:
        Decorated function that logs execution time
    """

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            logger.debug(f"{func.__name__} took {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start
            logger.error(f"{func.__name__} failed after {elapsed:.3f}s: {e}")
            raise

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            logger.debug(f"{func.__name__} took {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start
            logger.error(f"{func.__name__} failed after {elapsed:.3f}s: {e}")
            raise

    if asyncio.iscoroutinefunction(func):
        return async_wrapper  # type: ignore
    else:
        return sync_wrapper  # type: ignore


def retry_decorator(
    max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0
) -> Callable[[F], F]:
    """
    Decorator to retry failed operations with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for each retry

    Returns:
        Decorator function
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}"
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_retries + 1} attempts"
                        )

            raise last_exception  # type: ignore

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_retries + 1} attempts"
                        )

            raise last_exception  # type: ignore

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore

    return decorator


class Metrics:
    """Simple metrics collector for monitoring IPC operations."""

    def __init__(self) -> None:
        self.call_count: Dict[str, int] = {}
        self.call_times: Dict[str, List[float]] = {}
        self.error_count: Dict[str, int] = {}
        self.start_time = datetime.now()

    def record_call(self, method: str, duration: float, success: bool = True) -> None:
        """
        Record metrics for a method call.

        Args:
            method: Method name
            duration: Call duration in seconds
            success: Whether the call succeeded
        """
        if method not in self.call_count:
            self.call_count[method] = 0
            self.call_times[method] = []
            self.error_count[method] = 0

        self.call_count[method] += 1
        self.call_times[method].append(duration)

        if not success:
            self.error_count[method] += 1

    def get_stats(self, method: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for method calls.

        Args:
            method: Specific method to get stats for, or None for all methods

        Returns:
            Dictionary containing call statistics
        """
        if method:
            if method not in self.call_count:
                return {"error": f"No data for method {method}"}

            times = self.call_times[method]
            return {
                "method": method,
                "calls": self.call_count[method],
                "errors": self.error_count[method],
                "avg_time": sum(times) / len(times) if times else 0,
                "min_time": min(times) if times else 0,
                "max_time": max(times) if times else 0,
            }

        # Return stats for all methods
        uptime = (datetime.now() - self.start_time).total_seconds()
        total_calls = sum(self.call_count.values())
        total_errors = sum(self.error_count.values())

        return {
            "uptime_seconds": uptime,
            "total_calls": total_calls,
            "total_errors": total_errors,
            "methods": {m: self.get_stats(m) for m in self.call_count.keys()},
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.call_count.clear()
        self.call_times.clear()
        self.error_count.clear()
        self.start_time = datetime.now()


def validate_node_id(node_id: str) -> bool:
    """
    Validate a node ID format.

    Args:
        node_id: Node ID to validate

    Returns:
        True if valid, False otherwise
    """
    if not node_id or not isinstance(node_id, str):
        return False

    # Node ID should be alphanumeric with underscores/hyphens
    # and not contain spaces or special characters
    import re

    return bool(re.match(r"^[a-zA-Z0-9_-]+$", node_id))


def format_bytes(num_bytes: Union[int, float]) -> str:
    """
    Format bytes into human-readable string.

    Args:
        num_bytes: Number of bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"
