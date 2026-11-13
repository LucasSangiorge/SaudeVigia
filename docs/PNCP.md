# API do PNCP: o que descobrimos (SV-14)

Fonte: API pública de consulta do PNCP (Portal Nacional de Contratações Públicas), sem login nem chave.
Swagger: https://pncp.gov.br/api/consulta/swagger-ui/index.html

Script de exploração: `backend/dados/explorar_pncp.py` (rodar de dentro de `backend/` com `python -m dados.explorar_pncp`).

## Como os dados se organizam

```
CONTRATAÇÃO (a licitação)   ex.: pregão de medicamentos da Fhemig
  └── ITENS                 ex.: palbociclibe, 5.796 unidades
        └── RESULTADO       vencedor e preço homologado (só depois que a licitação termina)
```

## Endpoints

| Endpoint | Para que serve |
|---|---|
| `GET /api/consulta/v1/contratacoes/publicacao` | Contratações publicadas num período |
| `GET /api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens` | Itens de uma contratação |
| `GET /api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens/{numero}/resultados` | Vencedor e preço homologado de um item |

## Parâmetros usados

- `dataInicial` / `dataFinal`: formato `AAAAMMDD`
- `codigoModalidadeContratacao=6`: pregão eletrônico
- `codigoMunicipioIbge=3106200`: Belo Horizonte (cidade do órgão comprador, inclui órgãos estaduais e federais com sede em BH)
- `pagina` / `tamanhoPagina`: até 50 por página; a resposta traz `totalRegistros`, `totalPaginas` e `paginasRestantes`

## Descobertas

- **Volume:** 145 pregões em BH em 10 dias (1.826 no Brasil num único dia).
- **Lentidão:** até 20 s por página. A coleta automática vai precisar de retries.
- **Sem filtro de saúde:** a API não filtra por assunto; filtramos pelo texto `objetoCompra`.
- **Filtro por palavra erra:** buscando "saúde", veio "Saúde e Segurança do Trabalho" de uma empresa agropecuária. Com "medicamento" o erro sumiu, mas perdemos textos como "fármacos" ou "soro fisiológico". O código de catálogo (CATMAT) dos itens deve ser mais preciso.
- **Paginação é obrigatória:** 3 das 4 compras de medicamento estavam nas páginas 2 e 3.
- **Orçamento sigiloso:** as compras de medicamento vieram com valor estimado R$ 0, e os itens com preço unitário R$ 0 (permitido pela Lei 14.133). O preço real só aparece no resultado, depois da licitação. Para comparar preços, o projeto precisa coletar os resultados.
- **Código de catálogo vazio:** nos itens testados, `catalogoCodigoItem` veio `null`. Verificar em mais compras antes de depender dele.
- **Resultado de item em andamento:** HTTP 204 (sem corpo). Um período sem compras também pode responder 204, o que quebra o `resposta.json()`; tratar isso na DAG.
