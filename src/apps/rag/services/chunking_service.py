from langchain_text_splitters import RecursiveCharacterTextSplitter

from django.conf import settings


class ChunkingService:
    def __init__(self) -> None:
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.RAG_CHUNK_SIZE,
            chunk_overlap=settings.RAG_CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def split(self, content: str) -> list[str]:
        clean = (content or "").strip()
        if not clean:
            return []
        return self.splitter.split_text(clean)
