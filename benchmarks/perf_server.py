#!/usr/bin/env python3
"""
Performance test server - Run in separate process/machine

This server provides various methods for benchmarking:
- Echo service for latency testing
- Large data transfer testing
- Concurrent request handling
"""

import asyncio
import os
import time
import numpy as np
from datetime import datetime

# Clean import approach with fallback
try:
    # When running as module: python -m benchmarks.perf_server
    from nats_ipc_sdk import IPCNode
    from config import NATS_CLUSTER_SERVERS
except ImportError:
    # Fallback for direct execution: python benchmarks/perf_server.py
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from nats_ipc_sdk import IPCNode
    from config import NATS_CLUSTER_SERVERS


async def main():
    print("=" * 60)
    print("Performance Test Server")
    print(f"Time: {datetime.now()}")
    print(f"PID: {os.getpid()}")
    print("=" * 60)

    # Connect to cluster
    server = IPCNode("perf_server", NATS_CLUSTER_SERVERS)

    await server.connect()
    print("✓ Connected to NATS cluster")

    # Register test methods
    await server.register("echo", lambda x: x)
    await server.register(
        "echo_with_delay", lambda x, delay=0: (time.sleep(delay), x)[1]
    )

    # CPU intensive task
    def cpu_task(n):
        result = 0
        for i in range(n):
            result += i * i
        return result

    await server.register("cpu_task", cpu_task)

    # Memory intensive task
    def memory_task(size):
        data = np.random.rand(size, size)
        return data.sum()

    await server.register("memory_task", memory_task)

    # IO simulation
    async def io_task(duration):
        await asyncio.sleep(duration)
        return {"completed": True, "duration": duration}

    await server.register("io_task", io_task)

    print("✓ Registered 5 test methods:")
    print("  - echo: Simple echo")
    print("  - echo_with_delay: Echo with optional delay")
    print("  - cpu_task: CPU intensive calculation")
    print("  - memory_task: Memory intensive numpy operation")
    print("  - io_task: Async IO simulation")
    print()
    print("Server ready, waiting for requests...")
    print("Press Ctrl+C to stop")

    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        await server.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
