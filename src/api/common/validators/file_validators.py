import os
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat


class FileValidator:
    """
    Validator for uploaded files
    """
    error_messages = {
        'max_size': "File size must not exceed %(max_size)s. Current file size is %(size)s.",
        'min_size': "File size must be at least %(min_size)s. Current file size is %(size)s.",
        'content_type': "File type '%(content_type)s' is not supported. Allowed types: %(allowed_types)s.",
        'extension': "File extension '%(extension)s' is not allowed. Allowed extensions: %(allowed_extensions)s.",
        'mime_mismatch': "File content does not match its extension. Detected type: %(detected)s.",
    }

    def __init__(self, max_size=None, min_size=None, allowed_extensions=None, allowed_mimetypes=None):
        """
        Args:
            max_size: Maximum file size in bytes (e.g., 5242880 for 5MB)
            min_size: Minimum file size in bytes
            allowed_extensions: List of allowed file extensions (e.g., ['pdf', 'jpg', 'png'])
            allowed_mimetypes: List of allowed MIME types (e.g., ['application/pdf', 'image/jpeg'])
        """
        self.max_size = max_size
        self.min_size = min_size
        self.allowed_extensions = [ext.lower().lstrip('.') for ext in (allowed_extensions or [])]
        self.allowed_mimetypes = [mt.lower() for mt in (allowed_mimetypes or [])]

    def __call__(self, file):
        """
        Validate the uploaded file
        """
        # Validate file size
        if self.max_size is not None and file.size > self.max_size:
            raise ValidationError(
                self.error_messages['max_size'],
                code='max_size',
                params={
                    'max_size': filesizeformat(self.max_size),
                    'size': filesizeformat(file.size),
                }
            )

        if self.min_size is not None and file.size < self.min_size:
            raise ValidationError(
                self.error_messages['min_size'],
                code='min_size',
                params={
                    'min_size': filesizeformat(self.min_size),
                    'size': filesizeformat(file.size),
                }
            )

        # Validate file extension
        if self.allowed_extensions:
            filename = str(file.name)
            ext = os.path.splitext(filename)[1][1:].lower()
            
            if ext not in self.allowed_extensions:
                raise ValidationError(
                    self.error_messages['extension'],
                    code='extension',
                    params={
                        'extension': ext,
                        'allowed_extensions': ', '.join(self.allowed_extensions),
                    }
                )


class PDFValidator(FileValidator):
    """
    Validator specifically for PDF files
    """
    def __init__(self, max_size=10485760):  # 10MB default
        super().__init__(
            max_size=max_size,
            allowed_extensions=['pdf'],
            allowed_mimetypes=['application/pdf']
        )


class ImageValidator(FileValidator):
    """
    Validator for image files
    """
    def __init__(self, max_size=5242880):  # 5MB default
        super().__init__(
            max_size=max_size,
            allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp'],
            allowed_mimetypes=['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        )


class DocumentValidator(FileValidator):
    """
    Validator for document files (PDF, Word, Excel)
    """
    def __init__(self, max_size=20971520):  # 20MB default
        super().__init__(
            max_size=max_size,
            allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'jpg', 'jpeg', 'png'],
            allowed_mimetypes=[
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'text/plain',
            ]
        )


def validate_file_list(files, validator):
    """
    Validate a list of files with the given validator
    
    Args:
        files: List of uploaded files
        validator: FileValidator instance
    
    Raises:
        ValidationError: If any file fails validation
    """
    errors = []
    for idx, file in enumerate(files):
        try:
            validator(file)
        except ValidationError as e:
            for msg in e.messages:
                errors.append(f"File {idx + 1} ({file.name}): {msg}")
    
    if errors:
        raise ValidationError(errors)
