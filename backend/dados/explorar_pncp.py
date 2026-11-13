"""Exploração da API de consulta do PNCP (SV-14).

Busca os pregões publicados em um dia e mostra os que parecem ser de saúde.
Rodar a partir de backend/:  python -m dados.explorar_pncp
"""

from datetime import date, timedelta

import httpx

URL_CONSULTA = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
DIAS_PARA_TRAS = 10
PREGAO_ELETRONICO = 6
BELO_HORIZONTE = "3106200"  # código IBGE do município
PALAVRAS_SAUDE = ["medicamento"]


def buscar_contratacoes(data_inicial: str, data_final: str, pagina: int = 1) -> dict:
    params = {
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "codigoModalidadeContratacao": PREGAO_ELETRONICO,
        "codigoMunicipioIbge": BELO_HORIZONTE,
        "pagina": pagina,
        "tamanhoPagina": 50,
    }
    resposta = httpx.get(URL_CONSULTA, params=params, timeout=60)
    resposta.raise_for_status()
    return resposta.json()


def eh_saude(objeto: str) -> bool:
    texto = objeto.lower()
    return any(palavra in texto for palavra in PALAVRAS_SAUDE)


def main() -> None:
    hoje = date.today()
    inicio = hoje - timedelta(days=DIAS_PARA_TRAS)

    data_inicial = inicio.strftime("%Y%m%d")
    data_final = hoje.strftime("%Y%m%d")
    print(f"Período: {data_inicial} a {data_final}")

    resultado = buscar_contratacoes(data_inicial, data_final)
    print(f"Pregões em BH: {resultado['totalRegistros']}")
    print(f"Páginas de 50: {resultado['totalPaginas']}\n")

    for compra in resultado["data"]:
        if eh_saude(compra["objetoCompra"]):
            orgao = compra["orgaoEntidade"]["razaoSocial"]
            print(f"- {orgao}: {compra['objetoCompra'][:100]}")


if __name__ == "__main__":
    main()
