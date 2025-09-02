"""
Ultra-minimal usage example
"""

import asyncio
import os
import sys
import numpy as np

# Add parent directory to path if running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nats_ipc_sdk import IPCNode


# Example: Any Python object/function return type
class CustomData:
    def __init__(self, value):
        self.value = value
        self.timestamp = asyncio.get_event_loop().time()


async def main():
    # Server node
    async with IPCNode("server") as server:
        # Register functions with ANY return type
        def add(a, b):
            return a + b

        def get_array(size):
            return np.random.rand(size)

        def get_object():
            return CustomData("test")

        # Example: Return a multiplier function
        def create_multiplier(factor):
            """Creates a multiplier function with the given factor"""
            return factor * 2

        # Async function
        async def async_task(duration):
            await asyncio.sleep(duration)
            return {"status": "completed", "duration": duration}

        await server.register("add", add)
        await server.register("get_array", get_array)
        await server.register("get_object", get_object)
        await server.register("multiply_by_two", create_multiplier)
        await server.register("async_task", async_task)

        # Client node
        async with IPCNode("client") as client:  # Will use environment or default
            # Call different return types
            result = await client.call("server", "add", 10, 20)
            print(f"Add: {result}")  # 30

            arr = await client.call("server", "get_array", 5)
            print(f"Array: {arr}")  # numpy array

            obj = await client.call("server", "get_object")
            print(f"Object value: {obj.value}")  # CustomData object

            # Call the multiplier function
            result = await client.call("server", "multiply_by_two", 5)
            print(f"Multiply by two: 5 * 2 = {result}")

            async_result = await client.call("server", "async_task", 0.1)
            print(f"Async: {async_result}")

        # Broadcast example
        async with IPCNode("pub") as pub:
            async with IPCNode("sub") as sub:
                messages = []
                await sub.subscribe("test", messages.append)
                await asyncio.sleep(0.1)

                await pub.broadcast(
                    "test", {"any": "data", "numpy": np.array([1, 2, 3])}
                )
                await asyncio.sleep(0.1)

                print(f"Broadcast received: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
