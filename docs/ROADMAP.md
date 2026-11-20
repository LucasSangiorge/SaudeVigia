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

### Sprint 3 (08/12 a 21/12/2026): coleta mínima para alimentar a IA
Objetivo: ter itens de saúde com preço real no banco, o suficiente para a Fase 2.
- [x] SV-14 Explorar a API de consulta do PNCP e documentar os endpoints.
- [x] SV-15 Adicionar Airflow ao Docker Compose
- [ ] SV-16 Criar DAG que coleta compras de saúde do PNCP (com retries; absorve a SV-18)
- [ ] SV-17 Gravar os dados coletados no PostgreSQL
- [ ] Coletar os itens e os resultados (preço homologado) de cada compra de saúde
- [ ] SV-19 Testar o carregamento das DAGs no pytest e no CI
- ~~SV-18 Configurar retries e analisar logs de uma falha proposital~~ (retries entram na SV-16)
- ~~SV-20 Documentar no README como subir o ambiente~~ (vai para a documentação final)

## Fase 2 — IA aplicada aos dados (foco do projeto)
Decisão de 18/11/2026: o projeto passa a focar em IA generativa sobre os dados coletados (embeddings, RAG, agentes e MCP).
Cada etapa começa pelo conceito, termina com teste e entra em produção pelo mesmo fluxo de PR e CI.

- **Sprint 4: padronização com LLM e embeddings.** Primeiro, o LLM lê a descrição bagunçada e devolve JSON validado com Pydantic (saída estruturada: `princípio_ativo`, `dosagem`, `forma`, `unidade`). Depois, gerar embeddings das descrições, guardar no PostgreSQL com pgvector e agrupar o mesmo produto escrito de formas diferentes (ex.: "DIPIRONA SÓDICA 500MG COMP" e "dipirona 500 mg comprimido").
- **Sprint 5: comparação de preços.** Preço mínimo, médio e máximo por produto padronizado e por órgão, calculados com SQL/pandas (o LLM não faz conta), preços fora do padrão e rotas na API (`/precos`, `/comparar`).
- **Sprint 6: RAG sobre os editais.** Explorar os arquivos de edital no PNCP, quebrar em trechos, busca híbrida (palavra + vetor) e respostas citando a fonte.
- **Sprint 7: agente com LangGraph e tool calling.** Pergunta em linguagem natural (rota `/perguntar`); o LLM escolhe as ferramentas (buscar preços, comparar órgãos, buscar no edital). Os números vêm do banco, nunca do LLM. Conjunto de avaliação com perguntas e respostas esperadas.
- **Sprint 8: servidor MCP e entrega.** Expor as ferramentas via MCP, README com como subir o ambiente, diagrama e demonstração.

### Fora do escopo (cortado para focar na IA)
- Frontend próprio (a demonstração é pela API, pelo MCP e pelo Swagger)
- Alertas automáticos e análise de fornecedores
- Coleta de outras cidades e modalidades além de pregão eletrônico em BH

### Decisões tomadas
- 19/11/2026: o agente usa **LangGraph** com tool calling (é o framework pedido nas vagas de IA generativa). O MeuAnalista já tem orquestração feita à mão; aqui o objetivo é aprender o framework.

### Decisões em aberto
- Modelo de embedding: local e gratuito (ex.: sentence-transformers multilíngue) ou por API. O PC tem 4 núcleos e 16 GB.
- Imagem do banco com pgvector (a imagem `postgres` oficial não traz a extensão).
