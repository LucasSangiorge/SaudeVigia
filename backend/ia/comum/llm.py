from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings

MODELO = "gemini-4-hydrogen"


def criar_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=MODELO,
        api_key=settings.google_api_key,
    )
