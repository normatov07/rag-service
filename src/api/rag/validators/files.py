from api.common.validators.file_validators import FileValidator


RAG_UPLOAD_VALIDATOR = FileValidator(
    max_size=50 * 1024 * 1024,
    allowed_extensions=["txt", "pdf", "docx", "mp4"],
)
