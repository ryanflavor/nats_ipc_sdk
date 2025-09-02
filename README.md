# NATS IPC SDK

**Ultra-lightweight Inter-Process Communication SDK for NATS**

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org)
[![NATS](https://img.shields.io/badge/NATS-2.0-green)](https://nats.io)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 特性

- ✅ **单文件** - 整个SDK只有1个文件
- ✅ **任意类型** - Pickle序列化支持所有Python对象
- ✅ **极简API** - 4个核心方法
- ✅ **零配置** - 开箱即用

## 安装

```bash
pip install nats-py
```

## 快速开始

```python
import asyncio
from nats_ipc import IPCNode

async def main():
    # 服务端
    async with IPCNode("server") as server:
        server.register("hello", lambda name: f"Hello {name}!")
        
        # 客户端
        async with IPCNode("client") as client:
            result = await client.call("server", "hello", "World")
            print(result)  # Hello World!

asyncio.run(main())
```

## 核心API

```python
node = IPCNode(node_id, nats_url)  # 创建节点
await node.connect()                # 连接NATS
node.register(name, func)           # 注册方法
await node.call(target, method, *args, **kwargs)  # RPC调用
await node.broadcast(channel, data) # 广播
await node.subscribe(channel, handler)  # 订阅
await node.disconnect()             # 断开
```

## 支持的返回类型

```python
# 基础类型
server.register("get_int", lambda: 42)
server.register("get_dict", lambda: {"key": "value"})

# NumPy数组
server.register("get_array", lambda: np.array([1,2,3]))

# 自定义类
class MyClass:
    def __init__(self, data):
        self.data = data

server.register("get_object", lambda: MyClass("test"))

# 函数
server.register("get_function", lambda: lambda x: x * 2)

# 任何可pickle的对象都支持！
```

## 集群部署

```python
# 连接到多个NATS节点（自动故障转移）
node = IPCNode("mynode", [
    "nats://192.168.10.68:4222",
    "nats://192.168.10.238:4222"
])
```

## 为什么选择Pickle？

| 序列化 | 支持类型 | 性能 | 依赖 |
|--------|---------|------|------|
| JSON | 基础类型 | 中 | 无 |
| Pickle | **所有Python类型** | **快** | **无** |
| MsgPack | 基础类型 | 快 | msgpack |
| Protobuf | 需定义schema | 最快 | protobuf |

**Pickle是RPC的最佳选择**：无需定义schema，支持所有Python类型，内置库无依赖。

## 完整示例

```python
import asyncio
from nats_ipc import IPCNode

async def main():
    # 启动服务
    server = IPCNode("math_service")
    await server.connect()
    
    # 注册任意复杂度的函数
    server.register("calculate", lambda x, y, op="+": eval(f"{x}{op}{y}"))
    
    # 客户端调用
    client = IPCNode("client")
    await client.connect()
    
    result = await client.call("math_service", "calculate", 10, 20)  # 30
    result = await client.call("math_service", "calculate", 10, 20, op="*")  # 200
    
    await client.disconnect()
    await server.disconnect()

asyncio.run(main())
```

## 优势

1. **代码量极少** - 核心代码仅100行
2. **功能完整** - RPC、广播、订阅全支持
3. **类型自由** - 任何Python对象都能传输
4. **易于理解** - 代码简单，容易修改

## License

MIT