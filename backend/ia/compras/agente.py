"""Agente de compras (LangGraph): o LLM decide, a ferramenta executa, em loop.

Fluxo START -> llm -> (pediu ferramenta?) -> ferramentas -> llm -> ... -> END

"""

from datetime import date

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from ia.compras.ferramentas import buscar_compras_de_saude

FERRAMENTAS = [buscar_compras_de_saude]


def criar_agente(llm: BaseChatModel):
    """Monta o grafo do agente com o LLM recebido (o Gemini ou o falso dos testes)."""
    llm_com_ferramentas = llm.bind_tools(FERRAMENTAS)

    def chamar_llm(state: MessagesState) -> dict:
        """NÓ "llm": lê as mensagens e decide (responder ou pedir ferramentas)."""
        instrucoes = SystemMessage(
            "Você responde perguntas sobre compras públicas de saúde. "
            f"Hoje é {date.today().isoformat()}. "
            "Use as ferramentas para buscar os dados e não invente compras."
        )
        resposta = llm_com_ferramentas.invoke([instrucoes, *state["messages"]])
        return {"messages": [resposta]}

    grafo = StateGraph(MessagesState)
    grafo.add_node("llm", chamar_llm)
    grafo.add_node("ferramentas", ToolNode(FERRAMENTAS))
    grafo.add_edge(START, "llm")
    grafo.add_conditional_edges(
        "llm", tools_condition, {"tools": "ferramentas", END: END}
    )
    grafo.add_edge("ferramentas", "llm")
    return grafo.compile()
