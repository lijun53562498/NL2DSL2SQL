class NL2SQLError(Exception):
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class PreprocessError(NL2SQLError):
    def __init__(self, message: str):
        super().__init__(message, 'PREPROCESS_ERROR')


class LLMError(NL2SQLError):
    def __init__(self, message: str):
        super().__init__(message, 'LLM_ERROR')


class DSLError(NL2SQLError):
    def __init__(self, message: str):
        super().__init__(message, 'DSL_ERROR')


class SQLError(NL2SQLError):
    def __init__(self, message: str):
        super().__init__(message, 'SQL_ERROR')


class SecurityError(NL2SQLError):
    def __init__(self, message: str):
        super().__init__(message, 'SECURITY_ERROR')


class ValidationError(NL2SQLError):
    def __init__(self, message: str):
        super().__init__(message, 'VALIDATION_ERROR')


class SchemaError(NL2SQLError):
    def __init__(self, message: str):
        super().__init__(message, 'SCHEMA_ERROR')
