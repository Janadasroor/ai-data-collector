#!/bin/bash

echo "🚀 Starting AI Data Collector Dashboard..."
echo ""

# Activate virtual environment
source .venv/bin/activate

# Start the dashboard server
echo "📊 Dashboard will be available at: http://localhost:8000"
echo "🔌 WebSocket endpoint: ws://localhost:8000/ws"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

python dashboard_server.py
