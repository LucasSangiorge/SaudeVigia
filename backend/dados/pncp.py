from datetime import date

import httpx

URL_CONSULTA = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"


PREGAO_ELETRONICO = 6
BELO_HORIZONTE = "3106200"
TAMANHO_PAGINA = 50
PALAVRAS_SAUDE = ("medicamento",)


def buscar_pagina(
    cliente: httpx.Client,
    dia: date,
    pagina: int,
) -> dict | None:

    params = {
        "dataInicial": dia.strftime("%Y%m%d"),
        "dataFinal": dia.strftime("%Y%m%d"),
        "codigoModalidadeContratacao": PREGAO_ELETRONICO,
        "codigoMunicipioIbge": BELO_HORIZONTE,
        "pagina": pagina,
        "tamanhoPagina": TAMANHO_PAGINA,
    }
    resposta = cliente.get(URL_CONSULTA, params=params)

    if resposta.status_code == 204:
        return None

    resposta.raise_for_status()
    return resposta.json()


def buscar_compras_do_dia(cliente: httpx.Client, dia: date) -> list[dict]:
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
    texto = objeto.lower()
    return any(palavra in texto for palavra in PALAVRAS_SAUDE)


def filtrar_saude(compras: list[dict]) -> list[dict]:
    return [
        compra
        for compra in compras
        if eh_saude(compra["objetoCompra"])
    ]
