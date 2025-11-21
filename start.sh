#!/bin/bash

# Enhanced AI Data Collector - Quick Start Guide

echo "🚀 Enhanced AI Data Collector"
echo "=============================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt -q

echo ""
echo "✅ Setup complete!"
echo ""
echo "Available commands:"
echo "  1. Start 24-hour collection:  .venv/bin/python app.py"
echo "  2. Test run (5 minutes):      .venv/bin/python app.py --duration 0.083"
echo "  3. Resume from checkpoint:    .venv/bin/python app.py --resume"
echo "  4. Custom duration (hours):   .venv/bin/python app.py --duration 12"
echo ""
echo "📊 Monitor progress:"
echo "  - Live logs: tail -f crawler.log"
echo "  - Data collected: wc -l training_data.jsonl"
echo "  - Statistics: cat crawler_stats.json"
echo ""
echo "Press Ctrl+C to stop gracefully (saves checkpoint)"
echo ""
