"""
Configuration file for NATS IPC SDK
"""

import os
from typing import List, Union

# NATS Connection Settings
NATS_SERVERS: Union[str, List[str]] = os.getenv(
    "NATS_SERVERS",
    "nats://localhost:4222"
).split(",") if "," in os.getenv("NATS_SERVERS", "") else os.getenv("NATS_SERVERS", "nats://localhost:4222")

# Cluster servers for testing (can be overridden by environment variables)
NATS_CLUSTER_SERVERS: List[str] = os.getenv(
    "NATS_CLUSTER_SERVERS",
    "nats://192.168.10.68:4222,nats://192.168.10.238:4222"
).split(",")

# Timeout settings (in seconds)
DEFAULT_TIMEOUT: float = float(os.getenv("NATS_TIMEOUT", "30"))

# Performance test settings
PERF_TEST_ITERATIONS: int = int(os.getenv("PERF_TEST_ITERATIONS", "100"))
PERF_TEST_WARMUP: int = int(os.getenv("PERF_TEST_WARMUP", "10"))

# Test settings
TEST_DELAY: float = float(os.getenv("TEST_DELAY", "0.5"))