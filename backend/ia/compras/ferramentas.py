"""Ferramentas (tools) do agente de compras: as "mãos" que o LLM pode pedir para usar.
O LLM não executa nada: ele pede a ferramenta, o nosso código executa
e devolve o resultado para ele ler.
"""

from datetime import date

import httpx
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool, tool

from dados.pncp import buscar_compras_do_dia, filtrar_saude
from ia.padronizar import classificar_compra

AVISO_PNCP_FORA = "O PNCP não respondeu agora. Tente de novo em alguns minutos."
AVISO_LLM_FORA = "Não consegui confirmar as compras agora. Tente de novo em instantes."


def resumir_compras(compras: list[dict]) -> list[dict]:
    """Guarda só o que o llm precisa: menos texto, menos tokens e menos confusão."""
    return [
        {
            "orgao": compra["orgaoEntidade"]["razaoSocial"],
            "objeto": compra["objetoCompra"],
        }
        for compra in compras
    ]


def manter_saude_humana(llm: BaseChatModel, compras: list[dict]) -> list[dict]:
    """Confirma cada candidata com o LLM e mantém só as de saúde humana."""
    return [
        compra
        for compra in compras
        if classificar_compra(llm, compra["objetoCompra"]).saude_humana
    ]


def criar_ferramentas(llm: BaseChatModel) -> list[BaseTool]:
    """Monta as ferramentas com o LLM recebido (o Gemini ou o falso dos testes)."""

    @tool
    def buscar_compras_de_saude(dia: date) -> list[dict] | str:
        """Busca as compras de saúde (pregão eletrônico de Belo Horizonte)
        publicadas no PNCP em um dia. Use quando o usuário perguntar o que foi
        comprado, ou se houver compra de saúde, numa data."""
        try:
            with httpx.Client(timeout=60) as cliente:
                compras = buscar_compras_do_dia(cliente, dia)
        except httpx.HTTPError:
            return AVISO_PNCP_FORA

        try:
            humanas = manter_saude_humana(llm, filtrar_saude(compras))
        except Exception:  # LLM fora do ar ou cota esgotada: avisa em vez de quebrar
            return AVISO_LLM_FORA

        return resumir_compras(humanas)

    return [buscar_compras_de_saude]
