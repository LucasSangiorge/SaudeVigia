"""Padroniza a descrição das compras do PNCP com LLM (saída estruturada).

A regra por palavra-chave (dados.pncp.eh_saude) acha os candidatos; o LLM
confirma e classifica, porque o texto é livre e a regra erra
(ex.: "medicamentos veterinários" passa no filtro, mas não é saúde humana).
"""

from typing import Literal

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field

INSTRUCOES = (
    "Você classifica compras públicas brasileiras a partir da descrição do objeto. "
    "Responda só com base no texto. Não invente produtos que não estão escritos."
)


Categoria = Literal["medicamento", "equipamento", "material_medico", "outro"]


class ClassificacaoCompra(BaseModel):
    """O formulário que o LLM é obrigado a preencher."""

    categoria: Categoria = Field(
        description="Tipo principal do que está sendo comprado."
    )
    saude_humana: bool = Field(
        description="True se for para saúde humana; "
        "False se for veterinária ou não for de saúde."
    )
    produtos: list[str] = Field(
        description="Produtos citados no texto, lista vazia se não citar nenhum."
    )


def classificar_compra(llm: BaseChatModel, objeto: str) -> ClassificacaoCompra:
    """Pede ao LLM a classificação do texto da compra, já validada pelo Pydantic."""
    llm_estruturado = llm.with_structured_output(ClassificacaoCompra)
    resultado = llm_estruturado.invoke([("system", INSTRUCOES), ("human", objeto)])
    return ClassificacaoCompra.model_validate(resultado)
