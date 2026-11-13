# Roadmap — SaudeVigia

Organização: Jira (espaço SV, Scrum, sprints de 2 semanas). Uma branch e um Pull Request por tarefa, com CI verde antes do merge.

## Fase 1 — Infraestrutura (walking skeleton)

### Sprint 1 (10/11 a 23/11/2026): código versionado e protegido por CI
- [x] SV-1 Configurar Git no WSL e criar repositório no GitHub
- [x] SV-4 Criar esqueleto do projeto (venv, requirements, .gitignore, .env.example)
- [x] SV-5 Configurar Ruff com pyproject.toml e format on save
- [x] SV-6 Criar API mínima com rota /health e primeiro teste
- [x] SV-7 Criar pipeline de CI no GitHub Actions (Ruff + pytest)
- [x] SV-8 Proteger a branch main (PR obrigatório com CI verde)

### Sprint 2 (24/11 a 07/12/2026): ambiente em Docker e API no ar
- [x] SV-9 Configurar Docker Compose com PostgreSQL, settings e Alembic
- [x] SV-10 Criar Dockerfile da API e adicionar a API ao Docker Compose
- [x] SV-11 Configurar settings, conexão com o banco e Alembic (entregue junto com a SV-9)
- [x] SV-12 Rodar testes no container e validar build do Docker no CI
- [x] SV-13 Configurar deploy automático (CD) no Render com banco no Neon
- [x] SV-21 Usar 127.0.0.1 no DATABASE_URL do .env.example

### Sprint 3 (08/12 a 21/12/2026): Airflow coletando dados do PNCP
- [x] SV-14 Explorar a API de consulta do PNCP e documentar os endpoints.
- [ ] SV-15 Adicionar Airflow ao Docker Compose
- [ ] SV-16 Criar DAG que coleta compras de saúde do PNCP
- [ ] SV-17 Gravar os dados coletados no PostgreSQL
- [ ] SV-18 Configurar retries e analisar logs de uma falha proposital
- [ ] SV-19 Testar o carregamento das DAGs no pytest e no CI
- [ ] SV-20 Documentar no README como subir o ambiente

## Fase 2 — Produto (planejamento inicial, sujeito a ajustes)
- Sprint 4: coleta completa e incremental (bronze para silver)
- Sprint 5: padronização de produtos (avaliar o catálogo CATMAT)
- Sprint 6: comparação de preços entre órgãos e rotas da API
- Sprint 7: alertas de preços fora do padrão e análise de fornecedores
- Sprint 8: polimento e documentação final
