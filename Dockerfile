FROM ghcr.io/astral-sh/uv:python3.11-bookworm

WORKDIR /app

COPY pyproject.toml uv.lock /app/
RUN uv sync --frozen --no-dev --no-install-project

COPY src/ /app/src/

ENV PYTHONPATH=/app/src:/app \
    PYTHONUNBUFFERED=1

ENTRYPOINT ["uv", "run"]
CMD ["python3", "src/evaluation/runner.py"]