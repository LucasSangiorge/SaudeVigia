"""Testes do padronizar.py com um LLM falso: sem internet, sem chave, sem custo."""

from typing import Any

import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.runnables import RunnableLambda
from pydantic import ValidationError

from ia.padronizar import ClassificacaoCompra, classificar_compra


class LLMFalso(FakeListChatModel):
    """Finge ser o Gemini: devolve sempre a resposta combinada no teste."""

    resposta: Any = None

    def with_structured_output(self, schema, *, include_raw=False, **kwargs):
        return RunnableLambda(lambda mensagens: self.resposta)


def test_classificar_compra_devolve_a_classificacao_do_llm():
    esperado = ClassificacaoCompra(
        categoria="medicamento", saude_humana=False, produtos=[]
    )
    llm = LLMFalso(responses=[], resposta=esperado)

    resultado = classificar_compra(llm, "Aquisição de medicamentos veterinários")

    assert resultado == esperado


def test_classificar_compra_rejeita_resposta_fora_do_formato():
    # O LLM "inventou" uma categoria que não está no Literal
    llm = LLMFalso(
        responses=[],
        resposta={"categoria": "remédio", "saude_humana": True, "produtos": []},
    )

    with pytest.raises(ValidationError):
        classificar_compra(llm, "Aquisição de dipirona")
