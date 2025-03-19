from enum import Enum
from pydantic import BaseModel, Field

from contentgrid_extension_helpers import exceptions


class DenyReason(Enum):
    NOT_RELATED = "not_related"
    MISSING_INPUT = "missing_input"
    MALFORMED_INPUT = "malformed_input"
    ILLEGAL_ACTIVITY = "illegal_activity"
    SENSITIVE_INFORMATION = "sensitive_information"
    SECURITY_ERROR = "security_error"
    INJECTION_ATTEMPT = "injection_attempt"

    def to_exception(self) -> type[exceptions.LLMDenyException]:
        """Maps a DenyReason to its corresponding exception class."""
        match self:
            case DenyReason.NOT_RELATED:
                return exceptions.NotRelatedError
            case DenyReason.MISSING_INPUT:
                return exceptions.MissingInputError
            case DenyReason.MALFORMED_INPUT:
                return exceptions.MalformedInputError
            case DenyReason.ILLEGAL_ACTIVITY:
                return exceptions.IllegalActivityError
            case DenyReason.SENSITIVE_INFORMATION:
                return exceptions.SensitiveInformationError
            case DenyReason.SECURITY_ERROR:
                return exceptions.SecurityError
            case DenyReason.INJECTION_ATTEMPT:
                return exceptions.InjectionError


class ModelDeny(BaseModel):
    deny_type: DenyReason = Field(description="Type of denial")
    reason: str = Field(
        description="Reason for denying the request. Should be a short sentence that can be shown to the user. Not longer than two lines"
    )

    def __init__(self, **data):
        super().__init__(**data)
        # Raise the corresponding exception immediately
        exception_class = self.deny_type.to_exception()
        raise exception_class(self.reason)