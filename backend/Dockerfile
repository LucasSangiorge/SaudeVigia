# Multi-stage: um Dockerfile com 3 etapas (stages).
#   base -> o que dev e prod têm em comum (Python + pacotes da API)
#   dev  -> base + pytest/Ruff, para rodar os testes dentro do contêiner
#   prod -> base + código, sem ferramentas de teste (imagem que vai pro ar)
# Sem --target, o Docker monta a ÚLTIMA etapa (prod). É o que o Compose usa.

# ---------- base ----------
# Imagem oficial do Python, versão enxuta (sem compiladores e extras)
FROM python:3.14-slim AS base

# Não gera arquivos .pyc e mostra os logs na hora (sem buffer)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Primeiro só o requirements: enquanto ele não mudar, o Docker reaproveita
# a camada do pip install do cache e o build fica rápido
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- dev ----------
# docker build --target dev -t saudevigia-api:dev backend
# docker run --rm saudevigia-api:dev
FROM base AS dev

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

CMD ["pytest"]

# ---------- prod ----------
FROM base AS prod

# O código (o .dockerignore tira .venv, .env e caches)
COPY . .

# Roda sem ser root: se alguém invadir a API, não manda no contêiner
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# Ao ligar: aplica as migrations pendentes e só então sobe a API.
# ${PORT:-8000}: o Render escolhe a porta pela variável PORT; local usa 8000.
# exec: o uvicorn assume o lugar do sh e recebe o sinal de desligar do Docker.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
