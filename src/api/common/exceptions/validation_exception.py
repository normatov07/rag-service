

class ValidationException(Exception):
    """
    Custom exception for validation errors
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)