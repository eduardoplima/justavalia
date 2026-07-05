# Imagem única compartilhada por web/worker/beat. ffmpeg já baked (pronto p/ Fase 5).
FROM python:3.12-slim AS base

# O venv fica FORA de /app: em dev, o bind-mount `.:/app` clobbaria um venv em /app/.venv
# (e o venv do host é de outra plataforma). Em /opt/venv ele sobrevive ao bind-mount.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# ffmpeg (extração de frames — Fase 5); curl p/ healthchecks; ca-certificates.
RUN apt-get update \
    && apt-get install --no-install-recommends -y ffmpeg curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# uv (gerenciador de dependências) a partir da imagem oficial.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Camada de dependências (cache): copia apenas os manifestos primeiro.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Código da aplicação (em dev é sobreposto por bind-mount).
COPY . .
RUN uv sync --frozen

# Usuário não-root; dono do código e do venv.
RUN useradd --create-home --uid 1000 app \
    && chown -R app:app /app /opt/venv
USER app

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
