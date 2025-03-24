from enum import Enum


class ErrorType(str, Enum):
    VALIDATION_ERROR = "validation_error"
    PROCESS_ERROR = "process_error"
    INTEGRATION_ERROR = "integration_error"


class IntegrationError(Exception):
    """Custom exception for integration errors, allowing errors to be passed as a list."""

    def __init__(self, error_type: ErrorType, message: str, errors=None):
        self.errors = errors
        self.message = message
        self.error_type = error_type
        super().__init__(f"Integration failed with errors")

    def __str__(self):
        if self.errors is None:
            return f"ErrorType: {self.error_type}, Message: {self.message}"
        return f"ErrorType: {self.error_type}, Message: {self.message}, Errors: {self.errors}"
