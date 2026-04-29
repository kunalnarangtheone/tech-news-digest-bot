#!/bin/bash
# Tech Digest Bot Launcher

set -e

echo "🤖 Tech Digest Bot"
echo "=================="
echo ""

# Stop any existing instances
pkill -f "python -m tech_digest_bot" 2>/dev/null || true
sleep 1

# Run the bot (Python will load .env and validate)
echo "🚀 Starting Tech Digest Bot..."
echo ""
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
.venv/bin/python3 -m tech_digest_bot
