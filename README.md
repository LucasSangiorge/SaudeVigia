# SaudeVigia

Monitor de compras públicas de saúde (medicamentos, equipamentos e materiais médicos) a partir de dados do PNCP.

## Rodando localmente

Pré-requisitos: Python 3.14, Docker (no WSL, com o Docker Desktop aberto).

Primeira vez:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env          # depois troque a senha no .env
```

Rotina do dia:

```bash
docker compose up -d          # sobe o PostgreSQL
alembic upgrade head          # aplica as migrations pendentes
uvicorn app.main:app --reload # API em http://localhost:8000/docs
pytest                        # testes
ruff check . && ruff format . # lint e formatação
docker compose down           # desliga o banco (os dados ficam salvos)
```
