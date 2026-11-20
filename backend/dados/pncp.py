"""Coleta de contratações de saúde na API de consulta do PNCP.

As funções recebem o cliente HTTP como parâmetro (injeção de dependência):
na DAG ele acessa o PNCP de verdade; nos testes é um cliente falso, sem internet.
"""

from datetime import date

import httpx

URL_CONSULTA = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"

PREGAO_ELETRONICO = 6
BELO_HORIZONTE = "3106200"  # código IBGE do município
TAMANHO_PAGINA = 50  # máximo aceito pelo PNCP
PALAVRAS_SAUDE = ("medicamento",)


def buscar_pagina(
    cliente: httpx.Client,
    dia: date,
    pagina: int,
) -> dict | None:
    """Busca uma página de pregões publicados no dia.

    Devolve None quando o dia não tem compras (o PNCP responde 204, sem corpo).
    Lança httpx.HTTPStatusError se o PNCP responder com erro (ex.: 500).
    """
    params = {
        "dataInicial": dia.strftime("%Y%m%d"),
        "dataFinal": dia.strftime("%Y%m%d"),
        "codigoModalidadeContratacao": PREGAO_ELETRONICO,
        "codigoMunicipioIbge": BELO_HORIZONTE,
        "pagina": pagina,
        "tamanhoPagina": TAMANHO_PAGINA,
    }
    resposta = cliente.get(URL_CONSULTA, params=params)

    # Dia sem compras: o PNCP responde 204 sem corpo e o .json() quebraria
    if resposta.status_code == 204:
        return None

    resposta.raise_for_status()
    return resposta.json()


def buscar_compras_do_dia(cliente: httpx.Client, dia: date) -> list[dict]:
    """Percorre todas as páginas do dia e junta os pregões numa lista só."""
    compras = []
    pagina = 1

    while True:
        resultado = buscar_pagina(cliente, dia, pagina)

        if resultado is None:
            break

        compras.extend(resultado["data"])

        if resultado["paginasRestantes"] == 0:
            break

        pagina += 1

    return compras


def eh_saude(objeto: str) -> bool:
    """Diz se o objeto da compra é de saúde, procurando palavras-chave no texto."""
    texto = objeto.lower()
    return any(palavra in texto for palavra in PALAVRAS_SAUDE)


def filtrar_saude(compras: list[dict]) -> list[dict]:
    """Mantém só as compras de saúde."""
    return [compra for compra in compras if eh_saude(compra["objetoCompra"])]
