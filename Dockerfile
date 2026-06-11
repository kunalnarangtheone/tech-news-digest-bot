# Backend Dockerfile for Tech Digest API

FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* && \
    curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files
COPY pyproject.toml uv.lock ./
COPY README.md ./

# Install Python dependencies using uv
RUN uv sync --frozen --no-dev

# Copy source code
COPY src/ ./src/

# Copy scripts
COPY scripts/ ./scripts/

# Create data directory for SQLite
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application using uv run
CMD ["uv", "run", "uvicorn", "tech_digest_bot.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
