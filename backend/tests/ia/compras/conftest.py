"""Dados de exemplo compartilhados pelos testes de ia/compras."""

import pytest


@pytest.fixture
def compra_de_saude() -> dict:
    """Uma compra no formato que a API do PNCP devolve (só os campos usados)."""
    return {
        "orgaoEntidade": {"razaoSocial": "PREFEITURA DE BELO HORIZONTE"},
        "objetoCompra": "Aquisição de medicamentos",
    }
