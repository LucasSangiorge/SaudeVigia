"""Faz uma pergunta ao agente de compras pelo terminal.

Uso (dentro da pasta backend, com o venv ativado):
    python -m ia.perguntar "Teve compra de saúde em BH no dia 18/11/2026?"
"""

import sys

from langchain_core.messages import HumanMessage

from ia.compras.agente import criar_agente
from ia.comum.llm import criar_llm


def mostrar_mensagens(mensagens: list) -> None:
    """Mostra cada passo do agente: pergunta, pedido de ferramenta,
    resultado e resposta."""
    for numero, mensagem in enumerate(mensagens, start=1):
        print(f"\n[{numero}] {type(mensagem).__name__}")
        if getattr(mensagem, "tool_calls", None):
            for pedido in mensagem.tool_calls:
                print(f"    pediu a ferramenta: {pedido['name']} {pedido['args']}")
        else:
            print("   ", mensagem.text[:300])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Uso: python -m ia.perguntar "sua pergunta"')

    pergunta = sys.argv[1]
    agente = criar_agente(criar_llm())
    resultado = agente.invoke({"messages": [HumanMessage(pergunta)]})
    mostrar_mensagens(resultado["messages"])
