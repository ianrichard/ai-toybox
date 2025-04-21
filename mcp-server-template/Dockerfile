FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock* ./
COPY README.md ./
COPY src ./src

RUN uv venv && \
    uv sync --frozen --no-install-project --no-dev && \
    uv pip install .

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-m", "custom_mcp_server", "--verbose"]