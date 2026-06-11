.PHONY: help start stop install install-frontend lint format typecheck test clean status docker-logs docker-build

# Default target
help:
	@echo "Tech Digest AI - Make Targets"
	@echo "=============================="
	@echo ""
	@echo "Running:"
	@echo "  make start            - Start with Docker Compose"
	@echo "  make stop             - Stop Docker services"
	@echo "  make docker-logs      - View Docker logs"
	@echo "  make docker-build     - Rebuild Docker images"
	@echo ""
	@echo "Setup:"
	@echo "  make install          - Install backend dependencies"
	@echo "  make install-frontend - Install frontend dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make lint             - Run linter (ruff check)"
	@echo "  make format           - Format code (ruff format)"
	@echo "  make typecheck        - Run type checker (mypy)"
	@echo "  make test             - Run tests"
	@echo "  make clean            - Clean generated files"


# Install backend dependencies
install:
	@echo "📦 Installing backend dependencies..."
	pip install -e .

# Install frontend dependencies
install-frontend:
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install

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

# Run tests
test:
	@echo "🧪 Running tests..."
	pytest

# Clean generated files
clean:
	@echo "🧹 Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	cd frontend && rm -rf .next node_modules/.cache 2>/dev/null || true
	@echo "✅ Clean complete"

# Docker commands
start:
	@echo "🐳 Starting Docker services..."
	@if [ ! -f .env ]; then \
		echo "⚠️  .env file not found. Copy .env.docker to .env and configure it."; \
		echo "   cp .env.docker .env"; \
		exit 1; \
	fi
	docker-compose up -d
	@echo ""
	@echo "✅ Services started!"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend:  http://localhost:8000"
	@echo ""
	@echo "View logs: make docker-logs"

stop:
	@echo "🛑 Stopping Docker services..."
	docker-compose down
	@echo "✅ Services stopped"

logs:
	@echo "📋 Docker logs (Ctrl+C to exit)..."
	docker-compose logs -f

build:
	@echo "🔨 Rebuilding Docker images..."
	docker-compose build --no-cache
	@echo "✅ Build complete"
	@echo "Start services: make start"
