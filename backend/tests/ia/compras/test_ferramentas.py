"""Testes das ferramentas do agente de compras, com o PNCP falso (sem internet)."""

from datetime import date

import httpx

from ia.compras import ferramentas

COMPRA_DE_ESCRITORIO = {
    "orgaoEntidade": {"razaoSocial": "SECRETARIA DA FAZENDA"},
    "objetoCompra": "MATERIAL DE ESCRITÓRIO",
}


def test_resumir_compras_guarda_so_orgao_e_objeto(monkeypatch, compra_de_saude):
    assert ferramentas.resumir_compras([compra_de_saude]) == [
        {"orgao": "PREFEITURA DE BELO HORIZONTE", "objeto": "Aquisição de medicamentos"}
    ]


def test_buscar_compras_de_saude_devolve_so_as_de_saude(monkeypatch, compra_de_saude):
    def busca_falsa(cliente, dia):
        assert dia == date(2026, 11, 18)
        return [compra_de_saude, COMPRA_DE_ESCRITORIO]

    monkeypatch.setattr(ferramentas, "buscar_compras_do_dia", busca_falsa)

    resultado = ferramentas.buscar_compras_de_saude.invoke({"dia": "2026-11-18"})

    assert resultado == [
        {"orgao": "PREFEITURA DE BELO HORIZONTE", "objeto": "Aquisição de medicamentos"}
    ]


def test_buscar_compras_de_saude_avisa_quando_o_pncp_falha(monkeypatch):
    def busca_com_erro(cliente, dia):
        raise httpx.ConnectError("PNCP fora do ar")

    monkeypatch.setattr(ferramentas, "buscar_compras_do_dia", busca_com_erro)

    resultado = ferramentas.buscar_compras_de_saude.invoke({"dia": "2026-11-18"})

    assert resultado == "O PNCP não respondeu agora. Tente de novo em alguns minutos."
