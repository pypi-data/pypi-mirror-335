from fastapi import Request, status
import logging
from contentgrid_extension_helpers.problem_response import ProblemResponse
from contentgrid_hal_client.exceptions import (
    NotFound,
    Unauthorized,
    BadRequest,
    IncorrectAttributeType,
    NonExistantAttribute,
    MissingRequiredAttribute,
    MissingHALTemplate,
)
from requests.exceptions import HTTPError
from contentgrid_extension_helpers.exceptions import LLMDenyException

async def catch_exceptions_middleware(request: Request, call_next, problem_base_url: str = "https://docs.contentgrid.com"):
    """
    Catches exceptions and returns ProblemResponse objects.

    Args:
        request: The incoming request.
        call_next: The next middleware or route handler.
        problem_base_url: The base URL for problem type URIs.
    """

    def format_type(type_name: str) -> str:
        """Formats problem type URIs."""
        return f"{problem_base_url}/{type_name}"
    
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*, Authorization",
    }
    
    try:
        return await call_next(request)
    except LLMDenyException as e:
        logging.error(f"LLM denied request: {e}")
        return ProblemResponse(
            title="Request Denied",
            problem_type=format_type("request-denied"),
            detail=str(e),
            status=status.HTTP_400_BAD_REQUEST,
            headers=cors_headers,
        )
    except NotFound:
        return ProblemResponse(
            title="Not found",
            problem_type=format_type("not-found"),
            detail="Resource not found",
            status=status.HTTP_404_NOT_FOUND,
            headers=cors_headers,
        )
    except Unauthorized:
        return ProblemResponse(
            title="Unauthorized",
            problem_type=format_type("unauthorized"),
            detail="user is not authorized for requested resource",
            status=status.HTTP_401_UNAUTHORIZED,
            headers=cors_headers,
        )
    except BadRequest:
        return ProblemResponse(
            title="Bad Request",
            problem_type=format_type("bad-request"),
            detail="The request was malformed or invalid.",
            status=status.HTTP_400_BAD_REQUEST,
            headers=cors_headers,
        )
    except IncorrectAttributeType as e:
        return ProblemResponse(
            title="Incorrect Attribute Type",
            problem_type=format_type("incorrect-attribute-type"),
            detail=str(e),
            status=status.HTTP_400_BAD_REQUEST,
            headers=cors_headers,
        )
    except NonExistantAttribute as e:
        return ProblemResponse(
            title="Non-Existent Attribute",
            problem_type=format_type("non-existent-attribute"),
            detail=str(e),
            status=status.HTTP_404_NOT_FOUND,
            headers=cors_headers,
        )
    except MissingRequiredAttribute as e:
        return ProblemResponse(
            title="Missing Required Attribute",
            problem_type=format_type("missing-required-attribute"),
            detail=str(e),
            status=status.HTTP_400_BAD_REQUEST,
            headers=cors_headers,
        )
    except MissingHALTemplate as e:
        return ProblemResponse(
            title="Missing HAL Template",
            problem_type=format_type("missing-hal-template"),
            detail=str(e),
            status=status.HTTP_404_NOT_FOUND,
            headers=cors_headers,
        )
    except HTTPError as e:
        logging.exception(f"HTTP Error: {str(e)}", exc_info=True)
        return ProblemResponse(
            title="HTTP Error",
            problem_type=format_type("http-error"),
            detail=f"An HTTP error occurred: {str(e)}",
            status=e.response.status_code if e.response else status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers=cors_headers,
        )
    except Exception as e:
        logging.exception(
            f"Untyped exception caught in backend request...: {str(e)}",
            exc_info=True,
            stack_info=True,
        )
        return ProblemResponse(
            title="Internal server error",
            problem_type=format_type("unknown"),
            detail=f"An unexpected error occurred: {str(e)}",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers=cors_headers,
        )
