from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from django.conf import settings


class ModelClients:
    @staticmethod
    def embeddings() -> OpenAIEmbeddings:
        return OpenAIEmbeddings(
            base_url=settings.RAG_EMBEDDING_BASE_URL,
            api_key=settings.RAG_LLM_API_KEY,
            model=settings.RAG_EMBEDDING_MODEL,
            timeout=settings.RAG_MODEL_TIMEOUT_SECONDS,
        )

    @staticmethod
    def llm() -> ChatOpenAI:
        return ChatOpenAI(
            base_url=settings.RAG_LLM_BASE_URL,
            api_key=settings.RAG_LLM_API_KEY,
            model=settings.RAG_LLM_MODEL,
            temperature=settings.RAG_LLM_TEMPERATURE,
            timeout=settings.RAG_MODEL_TIMEOUT_SECONDS,
            max_tokens=settings.RAG_LLM_MAX_TOKENS,
        )
