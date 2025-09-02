"""
Ultra-thin NATS IPC SDK - Single file, minimal dependencies
"""

import asyncio
import pickle
import uuid
import os
from typing import Any, Callable, Optional, List, Union

import nats
from nats.aio.msg import Msg

# Default timeout from environment or 30 seconds
DEFAULT_TIMEOUT = float(os.getenv("NATS_TIMEOUT", "30"))


class IPCNode:
    """Minimal IPC node for NATS communication"""
    
    def __init__(
        self,
        node_id: Optional[str] = None,
        nats_url: Union[str, List[str]] = None,
        timeout: Optional[float] = None
    ):
        self.node_id = node_id or f"node_{uuid.uuid4().hex[:8]}"
        # Use provided URL or get from environment or default to localhost
        if nats_url is None:
            nats_url = os.getenv("NATS_SERVERS", "nats://localhost:4222")
            if "," in nats_url:
                nats_url = nats_url.split(",")
        self.nats_url = nats_url
        self.timeout = timeout or DEFAULT_TIMEOUT
        self.nc = None
        self.methods = {}
        self.subscriptions = []
    
    async def connect(self):
        """Connect to NATS"""
        if isinstance(self.nats_url, str):
            self.nc = await nats.connect(self.nats_url)
        else:
            self.nc = await nats.connect(servers=self.nats_url)
        
        # Setup existing method subscriptions
        for method_name in self.methods:
            await self._subscribe_method(method_name)
    
    async def disconnect(self):
        """Disconnect from NATS"""
        for sub in self.subscriptions:
            await sub.unsubscribe()
        if self.nc:
            await self.nc.close()
    
    async def register(self, name: str, handler: Callable):
        """Register a method for RPC"""
        self.methods[name] = handler
        if self.nc and self.nc.is_connected:
            await self._subscribe_method(name)
    
    async def call(self, target: str, method: str, *args, **kwargs) -> Any:
        """Call remote method"""
        subject = f"ipc.{target}.{method}"
        request = pickle.dumps({
            "args": args,
            "kwargs": kwargs
        })
        
        try:
            response = await self.nc.request(subject, request, timeout=self.timeout)
            result = pickle.loads(response.data)
            if "error" in result:
                raise Exception(result["error"])
            return result.get("result")
        except asyncio.TimeoutError:
            raise TimeoutError(f"Call to {target}.{method} timed out")
    
    async def broadcast(self, channel: str, data: Any):
        """Broadcast data to channel"""
        await self.nc.publish(f"broadcast.{channel}", pickle.dumps(data))
    
    async def subscribe(self, channel: str, handler: Callable):
        """Subscribe to broadcast channel"""
        async def wrapper(msg: Msg):
            data = pickle.loads(msg.data)
            if asyncio.iscoroutinefunction(handler):
                await handler(data)
            else:
                handler(data)
        
        sub = await self.nc.subscribe(f"broadcast.{channel}", cb=wrapper)
        self.subscriptions.append(sub)
    
    async def _subscribe_method(self, method_name: str):
        """Setup subscription for a method"""
        subject = f"ipc.{self.node_id}.{method_name}"
        
        async def handler(msg: Msg):
            try:
                request = pickle.loads(msg.data)
                method = self.methods[method_name]
                
                # Execute method
                if asyncio.iscoroutinefunction(method):
                    result = await method(*request["args"], **request["kwargs"])
                else:
                    result = method(*request["args"], **request["kwargs"])
                
                # Send response
                response = {"result": result}
            except Exception as e:
                response = {"error": str(e)}
            
            await msg.respond(pickle.dumps(response))
        
        sub = await self.nc.subscribe(subject, cb=handler)
        self.subscriptions.append(sub)
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()