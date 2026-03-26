# Estágio 1: Builder
FROM python:3.13-slim AS builder

RUN pip install poetry
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

# Instalamos tudo (incluindo dev) para garantir que ferramentas de auxílio funcionem
RUN poetry install --no-interaction --no-ansi --no-root

# Estágio 2: Development
FROM python:3.13-slim AS development

# Instalamos o curl para o healthcheck do Docker funcionar
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN useradd -m appuser
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copia todo o projeto para dentro do container
COPY . .

# Garante que o usuário tenha permissão na pasta (importante para o banco local)
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Ajustado o caminho para src/apisisbro/app.py
CMD ["fastapi", "dev", "src/apisisbro/app.py", "--host", "0.0.0.0", "--port", "8000"]