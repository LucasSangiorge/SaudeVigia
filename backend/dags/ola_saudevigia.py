"""DAG de teste (SV-15): só prova que o Airflow está lendo a pasta backend/dags.

Será substituída pela DAG de coleta do PNCP na SV-16.
"""

from datetime import datetime

from airflow.sdk import dag, task


# schedule=None: não roda sozinha, só quando você clica em "Trigger" na tela
@dag(
    schedule=None,
    start_date=datetime(2026, 11, 1),
    catchup=False,
    tags=["teste"],
)
def ola_saudevigia():
    @task
    def dizer_ola():
        print("Airflow está lendo a pasta backend/dags")

    dizer_ola()


ola_saudevigia()
