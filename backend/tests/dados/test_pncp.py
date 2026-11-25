"""Testes da coleta do PNCP, sem acessar a internet (respostas simuladas)."""

from datetime import date

import httpx
import pytest

from dados.pncp import (
    buscar_compras_do_dia,
    buscar_pagina,
    eh_saude,
    filtrar_saude,
)

DIA = date(2026, 11, 12)


def criar_cliente(responder):
    """Cliente httpx que não acessa a internet: cada requisição chama `responder`.

    `responder` recebe a requisição e devolve uma resposta inventada,
    simulando o PNCP.
    """
    return httpx.Client(transport=httpx.MockTransport(responder))


def test_buscar_pagina_devolve_none_quando_dia_sem_compra():
    # Arrange: o "PNCP falso" responde 204, sem corpo
    def responder(requisicao: httpx.Request) -> httpx.Response:
        return httpx.Response(204)

    cliente = criar_cliente(responder)

    # Act + Assert
    assert buscar_pagina(cliente, DIA, 1) is None


def test_buscar_pagina_envia_os_filtros_certos():
    # O "PNCP falso" confere os parâmetros da URL antes de responder.
    # Na URL tudo vira texto: por isso "50" e não 50.
    def responder(requisicao: httpx.Request) -> httpx.Response:
        params = requisicao.url.params
        assert params["dataInicial"] == "20261112"
        assert params["dataFinal"] == "20261112"
        assert params["codigoModalidadeContratacao"] == "6"
        assert params["codigoMunicipioIbge"] == "3106200"
        assert params["pagina"] == "1"
        assert params["tamanhoPagina"] == "50"
        return httpx.Response(200, json={"data": [], "paginasRestantes": 0})

    cliente = criar_cliente(responder)

    resultado = buscar_pagina(cliente, DIA, 1)

    assert resultado == {"data": [], "paginasRestantes": 0}


def test_buscar_pagina_lanca_erro_quando_pncp_falha():
    # Se o PNCP falhar, a coleta precisa falhar também (e o Airflow tenta de
    # novo). Engolir o erro faria um dia com dados parecer um dia sem compras.
    def responder(requisicao: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    cliente = criar_cliente(responder)

    with pytest.raises(httpx.HTTPStatusError):
        buscar_pagina(cliente, DIA, 1)


def test_buscar_compras_do_dia_junta_todas_as_paginas():
    # Dia com 2 páginas: a primeira diz que falta 1, a segunda que não falta nenhuma
    def responder(requisicao: httpx.Request) -> httpx.Response:
        if requisicao.url.params["pagina"] == "1":
            return httpx.Response(
                200, json={"data": [{"id": "A"}], "paginasRestantes": 1}
            )
        return httpx.Response(200, json={"data": [{"id": "B"}], "paginasRestantes": 0})

    cliente = criar_cliente(responder)

    compras = buscar_compras_do_dia(cliente, DIA)

    assert compras == [{"id": "A"}, {"id": "B"}]


def test_buscar_compras_do_dia_sem_compras_devolve_lista_vazia():
    def responder(requisicao: httpx.Request) -> httpx.Response:
        return httpx.Response(204)

    cliente = criar_cliente(responder)

    assert buscar_compras_do_dia(cliente, DIA) == []


@pytest.mark.parametrize(
    ("objeto", "esperado"),
    [
        ("Aquisição de medicamentos", True),
        ("MEDICAMENTOS - COMPRA CENTRAL", True),  # maiúsculas
        ("Material de escritório", False),
        ("Saúde e Segurança do Trabalho", False),  # o falso positivo da SV-14
    ],
)
def test_eh_saude(objeto, esperado):
    # parametrize: o mesmo teste roda uma vez para cada linha da lista acima
    assert eh_saude(objeto) is esperado


def test_filtrar_saude_mantem_so_compras_de_saude():
    compras = [
        {"objetoCompra": "Medicamentos diversos"},
        {"objetoCompra": "Papel A4"},
    ]

    assert filtrar_saude(compras) == [{"objetoCompra": "Medicamentos diversos"}]
