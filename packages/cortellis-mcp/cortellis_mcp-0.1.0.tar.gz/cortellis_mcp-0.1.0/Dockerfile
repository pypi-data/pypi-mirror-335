FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY pyproject.toml .
COPY README.md .
COPY LICENSE .
COPY cortellis_mcp ./cortellis_mcp

# Install dependencies
RUN pip install --no-cache-dir requests>=2.31.0 python-dotenv>=1.0.0 \
    && pip install --no-cache-dir -e .

# Create non-root user
RUN useradd -m -u 1000 mcp
USER mcp

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import cortellis_mcp; print('Health check passed')" || exit 1

# Run the MCP server
CMD ["python", "-m", "cortellis_mcp"] 