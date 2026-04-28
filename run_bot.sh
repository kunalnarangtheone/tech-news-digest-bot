#!/bin/bash
# Tech Digest Bot Launcher

set -e

echo "🤖 Tech Digest Bot"
echo "=================="
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "❌ Ollama is not running!"
    echo "   Start it with: brew services start ollama"
    exit 1
fi

echo "✅ Ollama is running"
echo ""

# Stop any existing instances
pkill -f "python -m tech_digest_bot" 2>/dev/null || true
sleep 1

# Run the bot
echo "🚀 Starting Tech Digest Bot..."
echo ""
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
.venv/bin/python3 -m tech_digest_bot
