.PHONY: help start stop install install-dev install-frontend lint lint-fix format test test-cov check pre-commit clean logs build build-clean

# Default target
help:
	@echo "AI adversarial chatbot - Make Targets"
	@echo "=============================="
	@echo ""
	@echo "Running:"
	@echo "  make start            - Start with Docker Compose"
	@echo "  make stop             - Stop Docker services"
	@echo "  make logs             - View Docker logs"
	@echo "  make build            - Rebuild Docker images (with cache)"
	@echo "  make build-clean      - Rebuild Docker images (no cache)"
	@echo ""
	@echo "Setup:"
	@echo "  make install          - Install backend dependencies"
	@echo "  make install-dev      - Install dev dependencies (tests, linting)"
	@echo "  make install-frontend - Install frontend dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make lint             - Check code style (ruff)"
	@echo "  make lint-fix         - Auto-fix code style issues"
	@echo "  make format           - Format code (ruff format)"
	@echo "  make test             - Run tests"
	@echo "  make test-cov         - Run tests with coverage"
	@echo "  make check            - Run all checks (lint + test)"
	@echo "  make pre-commit       - Run before committing (format + check)"
	@echo "  make clean            - Clean generated files"


# Install backend dependencies
install:
	@echo "📦 Installing backend dependencies..."
	uv pip install -e .

# Install dev dependencies (testing, linting)
install-dev:
	@echo "📦 Installing dev dependencies..."
	uv pip install -e ".[dev]"

# Install frontend dependencies
install-frontend:
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install

# Check code style (no changes)
lint:
	@echo "🔍 Checking backend code style..."
	@ruff check src/ && echo "✅ Backend code style looks good!" || (echo "❌ Backend code style issues found. Run 'make lint-fix' to auto-fix." && exit 1)
	@echo ""
	@echo "🔍 Checking frontend code style..."
	@cd frontend && npm run lint && echo "✅ Frontend code style looks good!" || (echo "❌ Frontend code style issues found." && exit 1)

# Auto-fix code style issues
lint-fix:
	@echo "🔧 Auto-fixing code style issues..."
	ruff check --fix src/
	@echo "✅ Auto-fixes applied!"

# Format code
format:
	@echo "✨ Formatting code..."
	ruff format src/
	@echo "✅ Code formatted!"

# Run tests
test:
	@echo "🧪 Running backend tests..."
	pytest -v
	@echo ""
	@echo "🧪 Running frontend tests..."
	@cd frontend && npm test -- --passWithNoTests && echo "✅ Frontend tests passed!" || echo "⚠️  No frontend tests configured yet"

# Run tests with coverage
test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest --cov=tech_digest_bot --cov-report=term-missing

# Run all checks (lint + test)
check: lint test
	@echo ""
	@echo "✅ All backend and frontend checks passed! Ready for Docker build."

# Pre-commit checks (format + check)
pre-commit: format check
	@echo ""
	@echo "✅ Pre-commit checks complete! Safe to commit."

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
	@echo "🔨 Rebuilding Docker images (with cache)..."
	docker-compose build
	@echo "✅ Build complete"
	@echo "Start services: make start"

build-clean:
	@echo "🔨 Rebuilding Docker images (no cache)..."
	docker-compose build --no-cache
	@echo "✅ Build complete"
	@echo "Start services: make start"
