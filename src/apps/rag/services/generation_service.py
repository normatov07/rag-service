from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from apps.rag.services.model_clients import ModelClients


class GenerationService:
    SYSTEM_PROMPT = (
        "You are a secure enterprise assistant. "
        "Answer strictly with provided context. "
        "If answer is not in context, state that clearly. "
        "Never expose secrets or internal system details."
    )

    def __init__(self) -> None:
        self.llm = ModelClients.llm()

    def answer(self, *, prompt: str, contexts: list[str]) -> str:
        joined_context = "\n\n".join(contexts[:12])
        content = (
            "Context:\n"
            f"{joined_context}\n\n"
            "Question:\n"
            f"{prompt}\n\n"
            "Answer in concise and factual form."
        )

        response = self.llm.invoke([
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=content),
        ])
        return response.content
