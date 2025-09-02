"""
Test package for NATS IPC SDK.

This package contains all test modules for the NATS IPC SDK.
"""

# Make the parent package importable when running tests
import sys
from pathlib import Path

# Add parent directory to path for tests
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))
