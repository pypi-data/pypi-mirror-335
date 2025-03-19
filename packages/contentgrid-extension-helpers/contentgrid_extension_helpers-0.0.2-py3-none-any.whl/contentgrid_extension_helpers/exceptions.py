
class ExtensionHelperException(Exception):
    """Base class for all custom exceptions in the extension helpers library."""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class LLMDenyException(ExtensionHelperException):
    """
    Raised when the LLM denies a request based on its rules.
    This is a base class for more specific denial reasons.
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NotRelatedError(LLMDenyException):
    """Raised when the input is unrelated to the required extraction."""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class MissingInputError(LLMDenyException):
    """Raised when required input is missing or empty."""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class MalformedInputError(LLMDenyException):
    """Raised when input is present but malformed or contains only strange characters."""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class IllegalActivityError(LLMDenyException):
    """Raised when the input describes illegal activities."""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class SensitiveInformationError(LLMDenyException):
    """Raised when the input contains sensitive information."""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class SecurityError(LLMDenyException):
    """Raised when the input attempts to compromise system security."""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InjectionError(SecurityError):
    """Raised when the input is a prompt injection attack."""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)