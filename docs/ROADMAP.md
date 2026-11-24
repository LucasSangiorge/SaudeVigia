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
- [x] SV-16 Criar DAG que coleta compras de saúde do PNCP (com retries; absorve a SV-18)
- ~~SV-18 Configurar retries e analisar logs de uma falha proposital~~ (retries entram na SV-16)
- ~~SV-20 Documentar no README como subir o ambiente~~ (vai para a documentação final)

**Pausado em 24/11/2026** (ver "Decisões tomadas"): a coleta continua funcionando, mas ainda não grava no banco. A DAG fica pausada no Airflow até a retomada.
- [ ] SV-17 Gravar os dados coletados no PostgreSQL
- [ ] Coletar os itens e os resultados (preço homologado) de cada compra de saúde
- [ ] SV-19 Testar o carregamento das DAGs no pytest e no CI

## Fase 2 — Camada de IA (foco atual)
Decisão de 18/11/2026: o projeto passa a focar em IA generativa. Em 24/11/2026, a ordem mudou: a camada de IA vem antes de gravar os dados, e os agentes consultam a API do PNCP diretamente.
Cada etapa começa pelo conceito, termina com teste (LLM falso: sem internet, sem chave, sem custo) e entra pelo mesmo fluxo de PR e CI.

- [ ] SV-22 Padronizar a descrição das compras com LLM (LangChain + saída estruturada). O LLM classifica o `objetoCompra` em categoria, saúde humana (sim/não) e produtos citados, validado com Pydantic. A regra por palavra-chave acha os candidatos e o LLM confirma: ela deixava passar compras de "medicamentos veterinários".
- [ ] SV-23 Agente de compras com tool calling e LangGraph: a ferramenta busca as compras de saúde do dia no PNCP.
- [ ] SV-24 Segundo agente (valores, com as contas em Python), roteador entre os dois e memória da conversa (estado do LangGraph).
- [ ] SV-25 RAG sobre as descrições das compras: trechos, embeddings e busca por similaridade num vector store em memória (pgvector depois).
- [ ] SV-26 Rota `POST /perguntar` na API.
- [ ] SV-27 Tela de chat para as perguntas.

### Depois (sujeito a ajustes)
- Gravar os dados (SV-17) e trocar as ferramentas dos agentes para ler do banco.
- Comparação de preços: mínimo, médio e máximo por produto e por órgão, calculados com SQL/pandas (o LLM não faz conta).
- pgvector no PostgreSQL e RAG sobre os arquivos de edital, com respostas citando a fonte.
- Conjunto de avaliação (evals) com perguntas e respostas esperadas.
- Servidor MCP expondo as ferramentas.

### Fora do escopo
- Alertas automáticos e análise de fornecedores
- Coleta de outras cidades e modalidades além de pregão eletrônico em BH

### Decisões tomadas
- 19/11/2026: o agente usa **LangGraph** com tool calling (é o framework pedido nas vagas de IA generativa). O MeuAnalista já tem orquestração feita à mão; aqui o objetivo é aprender o framework.
- 19/11/2026: LLM **Gemini** (plano gratuito do Google AI Studio) via LangChain; trocar de modelo muda só `ia/comum/llm.py`. No plano gratuito o Google pode usar os textos enviados, então só vão dados públicos do PNCP.
- 24/11/2026: a SV-22 classifica a compra em vez de extrair princípio ativo e dosagem, porque o `objetoCompra` descreve a compra inteira ("aquisição de medicamentos para a secretaria"). Princípio ativo e dosagem ficam para quando os itens forem coletados.
- 24/11/2026: a camada de IA vem antes de gravar os dados; a coleta no banco (SV-17) e a DAG ficam pausadas. Uma tela de chat simples volta ao escopo, para usar o agente.

### Decisões em aberto
- Modelo de embedding: o do Gemini, por API, ou um local e gratuito (ex.: sentence-transformers multilíngue). O PC tem 4 núcleos e 16 GB.
- Tecnologia da tela de chat (SV-27).
- Onde o Airflow roda quando a coleta voltar: no notebook gravando no Neon, ou num servidor na nuvem.
- Imagem do banco com pgvector (a imagem `postgres` oficial não traz a extensão).
