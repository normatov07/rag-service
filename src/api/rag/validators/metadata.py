from apps.rag.security.metadata_filter import MetadataSecurityFilter


def validate_metadata(metadata: dict | None) -> dict:
    return MetadataSecurityFilter.sanitize(metadata)
