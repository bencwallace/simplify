class InvalidPythonPathError(Exception):
    def __init__(self, python_path: str, message=""):
        message = f"Invalid Python path: {python_path}. {message}"
        super().__init__(message)


class InvalidBindingError(Exception):
    def __init__(self, binding: str):
        message = f"Invalid binding: {binding}"
        super().__init__(message)


class InvalidExpressionError(Exception):
    def __init__(self, expr):
        message = f"Invalid expression: {expr}"
        super().__init__(message)
