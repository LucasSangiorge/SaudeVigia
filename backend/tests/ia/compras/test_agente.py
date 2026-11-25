"""Testes do agente de compras com LLM e PNCP falsos: sem internet e sem custo."""

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from ia.compras import ferramentas
from ia.compras.agente import criar_agente


class LLMFalso(GenericFakeChatModel):
    """Finge ser o Gemini: devolve as mensagens combinadas no teste, em ordem."""

    def bind_tools(self, tools, **kwargs):
        # O LLM falso não precisa "ver" as ferramentas: as respostas já estão prontas.
        return self


def test_agente_chama_a_ferramenta_e_responde(monkeypatch, compra_de_saude):
    monkeypatch.setattr(
        ferramentas, "buscar_compras_do_dia", lambda cliente, dia: [compra_de_saude]
    )
    llm = LLMFalso(
        messages=iter(
            [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "buscar_compras_de_saude",
                            "args": {"dia": "2026-11-18"},
                            "id": "pedido-1",
                        }
                    ],
                ),
                AIMessage(content="Sim, a Prefeitura de BH comprou medicamentos."),
            ]
        )
    )

    resultado = criar_agente(llm).invoke(
        {"messages": [HumanMessage("Teve compra de saúde no dia 18/11/2026?")]}
    )
    mensagens = resultado["messages"]

    assert len(mensagens) == 4
    assert isinstance(mensagens[2], ToolMessage)
    assert "PREFEITURA DE BELO HORIZONTE" in mensagens[2].text
    assert mensagens[-1].text == "Sim, a Prefeitura de BH comprou medicamentos."


def test_agente_responde_direto_quando_nao_precisa_de_ferramenta():
    llm = LLMFalso(messages=iter([AIMessage(content="Olá! Pergunte sobre compras.")]))

    resultado = criar_agente(llm).invoke({"messages": [HumanMessage("Oi")]})
    mensagens = resultado["messages"]

    assert len(mensagens) == 2
    assert mensagens[-1].text == "Olá! Pergunte sobre compras."
