"""
Benchmarks package for NATS IPC SDK.

This package contains performance testing tools:
- perf_server.py: Performance test server with various test methods
- perf_client.py: Performance test client for measuring latency and throughput
"""

# Make the parent package importable when running benchmarks
import sys
from pathlib import Path

# Add parent directory to path for benchmarks
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))
