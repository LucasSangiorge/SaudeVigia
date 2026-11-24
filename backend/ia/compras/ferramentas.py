"""Ferramentas (tools) do agente de compras: as "mãos" que o LLM pode pedir para usar.
O LLM não executa nada: ele pede a ferramenta, o nosso código executa
e devolve o resultado para ele ler.
"""

from datetime import date

import httpx
from langchain_core.tools import tool

from dados.pncp import buscar_compras_do_dia, filtrar_saude


def resumir_compras(compras: list[dict]) -> list[dict]:
    """Guarda só o que o llm precisa: menos texto, menos tokens e menos confusão."""
    return [
        {
            "orgao": compra["orgaoEntidade"]["razaoSocial"],
            "objeto": compra["objetoCompra"],
        }
        for compra in compras
    ]


@tool
def buscar_compras_de_saude(dia: date) -> list[dict] | str:
    """Busca as compras de saúde (pregão eletrônico de Belo Horizonte)
    publicadas no PNCP em um dia. Use quando o usuário perguntar o que foi
    comprado, ou se houver compra de saúde, numa data."""
    try:
        with httpx.Client(timeout=60) as cliente:
            compras = buscar_compras_do_dia(cliente, dia)
    except httpx.HTTPError:
        return "O PNCP não respondeu agora. Tente de novo em alguns minutos."

    return resumir_compras(filtrar_saude(compras))
