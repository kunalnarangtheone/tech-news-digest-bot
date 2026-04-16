#!/bin/bash
# Setup script for OpenClaw integration

set -e

echo "🦞 Setting up OpenClaw Integration"
echo "===================================="

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install Node.js first."
    exit 1
fi

# Install OpenClaw if not already installed
if ! command -v openclaw &> /dev/null; then
    echo "📦 Installing OpenClaw..."
    npm install -g openclaw
else
    echo "✅ OpenClaw is already installed"
fi

# Create skills directory
echo "📁 Creating skills directory..."
mkdir -p ~/.openclaw/skills
mkdir -p ~/.openclaw/workflows

# Copy skills
echo "📋 Copying JavaScript skills..."
cp openclaw/skills/*.js ~/.openclaw/skills/
echo "✅ Copied $(ls openclaw/skills/*.js | wc -l | xargs) skills"

# Copy workflows
echo "📋 Copying workflows..."
cp openclaw/workflows/*.js ~/.openclaw/workflows/
echo "✅ Copied $(ls openclaw/workflows/*.js | wc -l | xargs) workflows"

# Start OpenClaw
echo ""
echo "🚀 Starting OpenClaw Gateway..."
openclaw start

# Wait a bit for startup
sleep 2

# Test connection
echo ""
echo "🧪 Testing connection..."
if curl -s http://localhost:3000/health > /dev/null; then
    echo "✅ OpenClaw Gateway is running!"
else
    echo "⚠️  Gateway may not be ready yet. Check with: openclaw status"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Test integration: python scripts/test_integration.py"
echo "  2. Update .env: OPENCLAW_ENABLED=true"
echo "  3. Run bot: tech-digest-bot"
