.PHONY: help run stop install lint format typecheck clean status

# Default target
help:
	@echo "Tech Digest Bot - Make Targets"
	@echo "==============================="
	@echo ""
	@echo "Running:"
	@echo "  make run              - Run the bot"
	@echo "  make stop             - Stop the bot"
	@echo "  make status           - Check if bot is running"
	@echo ""
	@echo "Setup:"
	@echo "  make install          - Install dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make lint             - Run linter (ruff check)"
	@echo "  make format           - Format code (ruff format)"
	@echo "  make typecheck        - Run type checker (mypy)"
	@echo "  make clean            - Clean generated files"

# Run the bot
run: stop
	@echo ""
	@echo "🤖 Starting Tech Digest Bot..."
	@echo ""
	@sleep 1
	@bash run_bot.sh

# Stop the bot
stop:
	@echo "🛑 Stopping Tech Digest Bot..."
	@pkill -f "tech_digest_bot" 2>/dev/null && echo "✅ Bot stopped" || echo "ℹ️  Bot not running"

# Check bot status
status:
	@if pgrep -f "tech_digest_bot" > /dev/null; then \
		echo "✅ Bot is running (PID: $$(pgrep -f 'tech_digest_bot'))"; \
	else \
		echo "❌ Bot is not running"; \
	fi

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	.venv/bin/python3 -m pip install -e .

# Run linter
lint:
	@echo "🔍 Running linter..."
	ruff check src/

# Format code
format:
	@echo "✨ Formatting code..."
	ruff format src/

# Type checking
typecheck:
	@echo "🔎 Running type checker..."
	mypy src/

# Clean generated files
clean:
	@echo "🧹 Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Clean complete"
