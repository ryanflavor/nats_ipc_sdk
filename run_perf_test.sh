#!/bin/bash
# Run cross-process performance test

echo "Starting performance test..."
echo "Starting server in background..."

# Start server
uv run python perf_server.py &
SERVER_PID=$!

# Wait for server to start
sleep 2

# Run client
echo "Running client tests..."
uv run python perf_client.py

# Kill server
echo "Stopping server..."
kill $SERVER_PID 2>/dev/null

echo "Test complete!"