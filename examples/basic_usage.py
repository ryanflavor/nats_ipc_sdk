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
        await server.register("add", lambda a, b: a + b)
        await server.register("get_array", lambda size: np.random.rand(size))
        await server.register("get_object", lambda: CustomData("test"))
        # Note: Can't return nested lambdas due to pickle limitation
        # await server.register("get_function", lambda: lambda x: x * 2)
        
        # Async function
        async def async_task(duration):
            await asyncio.sleep(duration)
            return {"status": "completed", "duration": duration}
        
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
            
            # Function test removed due to pickle limitation
            # func = await client.call("server", "get_function")
            # print(f"Function result: {func(5)}")  # 10
            
            async_result = await client.call("server", "async_task", 0.1)
            print(f"Async: {async_result}")
            
        # Broadcast example
        async with IPCNode("pub") as pub:
            async with IPCNode("sub") as sub:
                
                messages = []
                await sub.subscribe("test", messages.append)
                await asyncio.sleep(0.1)
                
                await pub.broadcast("test", {"any": "data", "numpy": np.array([1,2,3])})
                await asyncio.sleep(0.1)
                
                print(f"Broadcast received: {messages}")


if __name__ == "__main__":
    asyncio.run(main())