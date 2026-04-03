from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from django.conf import settings


class ModelClients:
    @staticmethod
    def embeddings(model: str | None = None) -> GoogleGenerativeAIEmbeddings:
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required for RAG embeddings.")

        model_name = (model or settings.RAG_EMBEDDING_MODEL or "").strip()
        if model_name.startswith("models/"):
            model_name = model_name.split("/", 1)[1]

        return GoogleGenerativeAIEmbeddings(
            google_api_key=settings.GOOGLE_API_KEY,
            model=model_name,
        )

    @staticmethod
    def llm() -> ChatGoogleGenerativeAI:
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required for RAG generation.")

        model_name = (settings.RAG_LLM_MODEL or "").strip()
        if model_name.startswith("models/"):
            model_name = model_name.split("/", 1)[1]

        return ChatGoogleGenerativeAI(
            google_api_key=settings.GOOGLE_API_KEY,
            model=model_name,
            temperature=settings.RAG_LLM_TEMPERATURE,
            timeout=settings.RAG_MODEL_TIMEOUT_SECONDS,
            max_tokens=settings.RAG_LLM_MAX_TOKENS,
        )
