# Imagem oficial do Python, versão enxuta (sem compiladores e extras)
FROM python:3.14-slim

# Não gera arquivos .pyc e mostra os logs na hora (sem buffer)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Primeiro só o requirements: enquanto ele não mudar, o Docker reaproveita
# a camada do pip install do cache e o build fica rápido
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Depois o código (o .dockerignore tira .venv, .env e caches)
COPY . .

# Roda sem ser root: se alguém invadir a API, não manda no contêiner
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
