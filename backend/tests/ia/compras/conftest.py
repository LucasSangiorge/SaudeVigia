"""Dados e dublês compartilhados pelos testes de ia/compras."""

import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from ia.compras import ferramentas
from ia.padronizar import ClassificacaoCompra


@pytest.fixture
def compra_de_saude() -> dict:
    """Uma compra no formato que a API do PNCP devolve (só os campos usados)."""
    return {
        "orgaoEntidade": {"razaoSocial": "PREFEITURA DE BELO HORIZONTE"},
        "objetoCompra": "Aquisição de medicamentos",
    }


@pytest.fixture
def compra_veterinaria() -> dict:
    """Passa no filtro por palavra-chave, mas não é saúde humana."""
    return {
        "orgaoEntidade": {"razaoSocial": "POLICIA CIVIL DE MINAS GERAIS"},
        "objetoCompra": "Aquisição de medicamentos veterinários",
    }


@pytest.fixture
def llm_sem_uso() -> FakeListChatModel:
    """LLM falso para quando a classificação também é falsa (não é chamado)."""
    return FakeListChatModel(responses=[])


@pytest.fixture
def classificacao_falsa(monkeypatch) -> None:
    """Troca o classificar_compra (testado na SV-22) por uma regra simples:
    é saúde humana se o texto não falar em veterinária."""

    def classificar_falso(llm, objeto: str) -> ClassificacaoCompra:
        return ClassificacaoCompra(
            categoria="medicamento",
            saude_humana="veterin" not in objeto.lower(),
            produtos=[],
        )

    monkeypatch.setattr(ferramentas, "classificar_compra", classificar_falso)
