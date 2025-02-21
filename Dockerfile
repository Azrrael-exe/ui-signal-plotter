# Stage de dependencias
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml poetry.lock* ./

ENV POETRY_VIRTUALENVS_IN_PROJECT=true
RUN poetry install --no-interaction --no-ansi --no-root

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD uvicorn src.infrastructure.app:app --host 0.0.0.0 --port $PORT --workers 1