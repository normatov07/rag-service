FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_ENVIRONMENT=/opt/.venv

# Install system dependencies
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends supervisor gettext && \
    mkdir -p /app/src/logs

COPY --from=ghcr.io/astral-sh/uv:0.10.2 /uv /uvx /bin/

WORKDIR /app

COPY ./src/pyproject.toml ./src/pyproject.toml

# Install dependencies (including dev) without the project
WORKDIR /app/src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project

COPY ./src/ ./
COPY ./docker/ ./docker/

# Install project in editable mode with all dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync && \
    /opt/.venv/bin/python manage.py collectstatic --noinput --clear

COPY ./docker/supervisord/supervisord-local.conf /etc/supervisor/conf.d/supervisord.conf

ENV PATH="/opt/.venv/bin:$PATH"

EXPOSE 8000

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]