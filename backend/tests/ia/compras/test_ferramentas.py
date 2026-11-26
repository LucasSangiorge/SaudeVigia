"""Testes das ferramentas do agente de compras, com PNCP e LLM falsos."""

from datetime import date

import httpx
import pytest

from ia.compras import ferramentas

COMPRA_DE_ESCRITORIO = {
    "orgaoEntidade": {"razaoSocial": "SECRETARIA DE FAZENDA"},
    "objetoCompra": "Material de escritório",
}


def test_resumir_compras_guarda_so_orgao_e_objeto(compra_de_saude):
    assert ferramentas.resumir_compras([compra_de_saude]) == [
        {"orgao": "PREFEITURA DE BELO HORIZONTE", "objeto": "Aquisição de medicamentos"}
    ]


@pytest.mark.usefixtures("classificacao_falsa")
def test_manter_saude_humana_descarta_veterinaria(
    llm_sem_uso, compra_de_saude, compra_veterinaria
):
    resultado = ferramentas.manter_saude_humana(
        llm_sem_uso, [compra_de_saude, compra_veterinaria]
    )

    assert resultado == [compra_de_saude]


@pytest.mark.usefixtures("classificacao_falsa")
def test_buscar_compras_de_saude_devolve_so_saude_humana(
    monkeypatch, llm_sem_uso, compra_de_saude, compra_veterinaria
):
    def busca_falsa(cliente, dia):
        assert dia == date(2026, 11, 18)
        return [compra_de_saude, compra_veterinaria, COMPRA_DE_ESCRITORIO]

    monkeypatch.setattr(ferramentas, "buscar_compras_do_dia", busca_falsa)
    [buscar_compras_de_saude] = ferramentas.criar_ferramentas(llm_sem_uso)

    resultado = buscar_compras_de_saude.invoke({"dia": "2026-11-18"})

    assert resultado == [
        {"orgao": "PREFEITURA DE BELO HORIZONTE", "objeto": "Aquisição de medicamentos"}
    ]


def test_buscar_compras_de_saude_avisa_quando_o_pncp_falha(monkeypatch, llm_sem_uso):
    def busca_com_erro(cliente, dia):
        raise httpx.ConnectError("PNCP fora do ar")

    monkeypatch.setattr(ferramentas, "buscar_compras_do_dia", busca_com_erro)
    [buscar_compras_de_saude] = ferramentas.criar_ferramentas(llm_sem_uso)

    resultado = buscar_compras_de_saude.invoke({"dia": "2026-11-18"})

    assert resultado == ferramentas.AVISO_PNCP_FORA


def test_buscar_compras_de_saude_avisa_quando_o_llm_falha(
    monkeypatch, llm_sem_uso, compra_de_saude
):
    def classificar_com_erro(llm, objeto):
        raise RuntimeError("503: modelo sobrecarregado")

    monkeypatch.setattr(
        ferramentas, "buscar_compras_do_dia", lambda cliente, dia: [compra_de_saude]
    )
    monkeypatch.setattr(ferramentas, "classificar_compra", classificar_com_erro)
    [buscar_compras_de_saude] = ferramentas.criar_ferramentas(llm_sem_uso)

    resultado = buscar_compras_de_saude.invoke({"dia": "2026-11-18"})

    assert resultado == ferramentas.AVISO_LLM_FORA


@pytest.mark.usefixtures("classificacao_falsa")
def test_buscar_compras_de_saude_avisa_quando_nao_ha_compra_humana(
    monkeypatch, llm_sem_uso, compra_veterinaria
):
    monkeypatch.setattr(
        ferramentas, "buscar_compras_do_dia", lambda cliente, dia: [compra_veterinaria]
    )
    [buscar_compras_de_saude] = ferramentas.criar_ferramentas(llm_sem_uso)

    resultado = buscar_compras_de_saude.invoke({"dia": "2026-11-18"})

    assert resultado == ferramentas.AVISO_NENHUMA_COMPRA
