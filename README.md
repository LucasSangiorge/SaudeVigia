# SaudeVigia

Monitor de compras públicas de saúde (medicamentos, equipamentos e materiais médicos) a partir de dados do PNCP.

## Estrutura

```
SaudeVigia/
├── backend/        # API FastAPI, banco, migrations e testes (Python)
├── frontend/       # páginas com os gráficos (planejado)
├── docs/           # roadmap e arquitetura
└── compose.yaml    # sobe os serviços (PostgreSQL) com um comando
```

## Rodando localmente

Pré-requisitos: Python 3.14, Docker (no WSL, com o Docker Desktop aberto).

Primeira vez:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env          # depois troque a senha no .env
```

No Windows (Git Bash), use `python` no lugar de `python3` e ative com `source .venv/Scripts/activate`.

Rotina do dia (a partir da pasta `backend/`):

```bash
docker compose up -d db       # sobe só o PostgreSQL
alembic upgrade head          # aplica as migrations pendentes
uvicorn app.main:app --reload # API em http://127.0.0.1:8000/docs (recarrega ao salvar)
pytest                        # testes
ruff check . && ruff format . # lint e formatação
docker compose down           # desliga tudo (os dados do banco ficam salvos)
```

Para rodar a API dentro do Docker, do jeito que vai para produção:

```bash
docker compose up -d --build  # monta a imagem da API e sobe API + banco
docker compose logs -f api    # acompanha os logs (Ctrl+C para sair)
```

A API do contêiner e o `uvicorn` do venv usam a mesma porta 8000: rode um de cada vez.

Para rodar os testes dentro da imagem (o mesmo que o CI faz), a partir da raiz:

```bash
docker build --target dev -t saudevigia-api:dev backend
docker run --rm saudevigia-api:dev
```

O `docker compose` funciona de dentro de `backend/`: ele sobe as pastas até achar o `compose.yaml` da raiz.
