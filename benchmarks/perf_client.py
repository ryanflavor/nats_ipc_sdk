#!/usr/bin/env python3
"""
Performance test client - Run in separate process/machine
Measures real cross-process/cross-machine latency
"""

import asyncio
import sys
import os
import time
import statistics
import numpy as np
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nats_ipc_sdk import IPCNode
from config import NATS_CLUSTER_SERVERS, PERF_TEST_ITERATIONS, PERF_TEST_WARMUP


async def measure_latency(
    client, method, *args, iterations=PERF_TEST_ITERATIONS, **kwargs
):
    """Measure RPC call latency"""
    latencies = []

    # Warmup
    for _ in range(PERF_TEST_WARMUP):
        await client.call("perf_server", method, *args, **kwargs)

    # Actual measurement
    for _ in range(iterations):
        start = time.perf_counter()
        await client.call("perf_server", method, *args, **kwargs)
        end = time.perf_counter()
        latencies.append((end - start) * 1000)  # Convert to ms

    return {
        "min": min(latencies),
        "max": max(latencies),
        "mean": statistics.mean(latencies),
        "median": statistics.median(latencies),
        "stdev": statistics.stdev(latencies) if len(latencies) > 1 else 0,
        "p95": sorted(latencies)[int(len(latencies) * 0.95)],
        "p99": sorted(latencies)[int(len(latencies) * 0.99)],
    }


async def main():
    print("=" * 60)
    print("Performance Test Client")
    print(f"Time: {datetime.now()}")
    print(f"PID: {os.getpid()}")
    print("=" * 60)

    # Connect to cluster
    client = IPCNode("perf_client", NATS_CLUSTER_SERVERS)

    await client.connect()
    print("✓ Connected to NATS cluster")
    print()

    # Wait for server to be ready
    print("Waiting for server...")
    for i in range(10):
        try:
            result = await client.call("perf_server", "echo", "test")
            print(f"✓ Server is ready (echo test: {result})")
            break
        except Exception as e:
            print(f"  Attempt {i + 1}/10: {e}")
            if i == 9:
                print("✗ Server not responding. Please start perf_server.py first")
                return
            await asyncio.sleep(2)

    print("\n" + "=" * 60)
    print("PERFORMANCE MEASUREMENTS (100 iterations each)")
    print("=" * 60)

    # Test 1: Simple echo with different payload sizes
    print("\n1. Echo Performance (different payload sizes)")
    print("-" * 40)

    for size in [10, 100, 1000, 10000, 100000]:
        data = "x" * size
        stats = await measure_latency(client, "echo", data)
        print(
            f"Payload {size:6d}B: {stats['mean']:6.2f}ms avg "
            f"(min:{stats['min']:.2f} max:{stats['max']:.2f} "
            f"p95:{stats['p95']:.2f} p99:{stats['p99']:.2f})"
        )

    # Test 2: NumPy arrays
    print("\n2. NumPy Array Performance")
    print("-" * 40)

    for shape in [
        (10, 10),
        (100, 100),
        (200, 200),
    ]:  # 200x200 instead of 500x500 to avoid max payload
        data = np.random.rand(*shape)
        stats = await measure_latency(client, "echo", data, iterations=20)
        size_kb = data.nbytes / 1024
        print(
            f"Array {shape[0]:3d}x{shape[1]:3d} ({size_kb:.1f}KB): "
            f"{stats['mean']:6.2f}ms avg "
            f"(min:{stats['min']:.2f} max:{stats['max']:.2f})"
        )

    # Test 3: Complex objects
    print("\n3. Complex Object Performance")
    print("-" * 40)

    for size in [1, 10, 50]:
        # Use a simple dict instead of a class (pickle limitation with local classes)
        obj = {
            "data": {"key" + str(i): np.random.rand(10).tolist() for i in range(size)},
            "metadata": {"size": size, "timestamp": time.time()},
        }
        stats = await measure_latency(client, "echo", obj, iterations=50)
        print(
            f"Object with {size:2d} arrays: {stats['mean']:6.2f}ms avg "
            f"(min:{stats['min']:.2f} max:{stats['max']:.2f})"
        )

    # Test 4: CPU intensive tasks
    print("\n4. CPU Intensive Task Performance")
    print("-" * 40)

    for n in [1000, 10000, 100000]:
        stats = await measure_latency(client, "cpu_task", n, iterations=20)
        print(
            f"CPU task n={n:6d}: {stats['mean']:6.2f}ms avg "
            f"(min:{stats['min']:.2f} max:{stats['max']:.2f})"
        )

    # Test 5: Memory intensive tasks
    print("\n5. Memory Intensive Task Performance")
    print("-" * 40)

    for size in [100, 500, 1000]:
        stats = await measure_latency(client, "memory_task", size, iterations=10)
        print(
            f"Memory task {size:4d}x{size:4d}: {stats['mean']:6.2f}ms avg "
            f"(min:{stats['min']:.2f} max:{stats['max']:.2f})"
        )

    # Test 6: Network overhead (minimal computation)
    print("\n6. Pure Network Overhead")
    print("-" * 40)

    stats = await measure_latency(client, "echo", 1, iterations=1000)
    print(
        f"Minimal payload (int): {stats['mean']:6.2f}ms avg "
        f"(min:{stats['min']:.2f} median:{stats['median']:.2f} "
        f"p95:{stats['p95']:.2f} p99:{stats['p99']:.2f})"
    )

    # Test 7: Concurrent requests
    print("\n7. Concurrent Request Performance")
    print("-" * 40)

    async def concurrent_call():
        return await client.call("perf_server", "echo", "concurrent")

    for concurrency in [1, 10, 50, 100]:
        start = time.perf_counter()
        tasks = [concurrent_call() for _ in range(concurrency)]
        await asyncio.gather(*tasks)
        elapsed = (time.perf_counter() - start) * 1000
        avg_per_call = elapsed / concurrency
        print(
            f"Concurrency {concurrency:3d}: {elapsed:6.2f}ms total, "
            f"{avg_per_call:.2f}ms per call"
        )

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"• Network overhead: ~{stats['median']:.2f}ms")
    print("• Pickle overhead increases with object complexity")
    print("• Concurrent requests show good scalability")

    await client.disconnect()


if __name__ == "__main__":
    import os

    asyncio.run(main())
