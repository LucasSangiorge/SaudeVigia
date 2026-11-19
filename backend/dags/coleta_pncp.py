"""DAG de coleta diária das compras de saúde no PNCP (SV-16).

A DAG só orquestra: toda a lógica fica em dados/pncp.py, que é testada no pytest
sem precisar do Airflow. Gravar no banco é a SV-17; por enquanto, a coleta
registra no log o que encontrou.
"""

import logging
from datetime import datetime, timedelta

import httpx
from airflow.sdk import dag, task

from dados.pncp import buscar_compras_do_dia, filtrar_saude

log = logging.getLogger(__name__)


@dag(
    # Todo dia às 06h UTC (03h em Brasília), quando o dia anterior já fechou
    schedule="0 6 * * *",
    start_date=datetime(2026, 11, 1),
    catchup=False,
    # Se o PNCP falhar (ele chega a levar 20 s por página), tenta de novo
    default_args={"retries": 3, "retry_delay": timedelta(minutes=5)},
    tags=["pncp", "coleta"],
)
def coleta_pncp():
    @task
    def coletar_compras_de_saude(logical_date=None, dag_run=None) -> dict:
        # Data lógica: a data de referência da execução. Coletamos o dia
        # anterior a ela, assim rodar de novo uma execução antiga busca o
        # mesmo dia (coleta reproduzível). Em execução manual sem data
        # lógica, usa o momento em que a execução foi pedida.
        referencia = logical_date or dag_run.run_after
        dia = referencia.date() - timedelta(days=1)

        with httpx.Client(timeout=60) as cliente:
            compras = buscar_compras_do_dia(cliente, dia)

        de_saude = filtrar_saude(compras)

        log.info("Dia %s: %d pregões, %d de saúde", dia, len(compras), len(de_saude))
        for compra in de_saude:
            log.info("- %s", compra["objetoCompra"][:100])

        # Só um resumo pequeno vai para o XCom (o banco de metadados do Airflow);
        # a lista completa vai para o PostgreSQL na SV-17
        return {"dia": dia.isoformat(), "pregoes": len(compras), "saude": len(de_saude)}

    coletar_compras_de_saude()


coleta_pncp()
