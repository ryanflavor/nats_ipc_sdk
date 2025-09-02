"""
Examples package for NATS IPC SDK.

This package contains various examples demonstrating the usage of NATS IPC SDK:
- basic_usage.py: Basic RPC and broadcast examples
- More examples can be added here
"""

# Make the parent package importable when running examples
import sys
from pathlib import Path

# Add parent directory to path for examples
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))
