from __future__ import annotations

import io

from docx import Document
from pypdf import PdfReader


class ContentExtractionService:
    @staticmethod
    def extract_from_upload(file_obj, source_type: str, video_transcript: str | None = None) -> str:
        if source_type == "text":
            return file_obj.read().decode("utf-8")

        name = (getattr(file_obj, "name", "") or "").lower()

        if name.endswith(".txt"):
            return file_obj.read().decode("utf-8")
        if name.endswith(".pdf"):
            reader = PdfReader(file_obj)
            return "\n".join((page.extract_text() or "") for page in reader.pages)
        if name.endswith(".docx"):
            content = file_obj.read()
            doc = Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)
        if name.endswith(".mp4") or name.endswith(".mp3") or source_type == "video":
            return (video_transcript or "").strip()

        return ""
