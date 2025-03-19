from fastapi import FastAPI, Request, status
from fastapi.testclient import TestClient
import pytest
from unittest.mock import MagicMock

from contentgrid_extension_helpers.middleware.exception_middleware import (
    catch_exceptions_middleware,
)
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
from contentgrid_extension_helpers.problem_response import ProblemResponse


@pytest.fixture
def app():
    """Creates a FastAPI app with the exception middleware."""
    app = FastAPI()

    @app.middleware("http")
    async def add_exception_middleware(request: Request, call_next):
        return await catch_exceptions_middleware(request, call_next, "https://test.example.com")

    return app


@pytest.fixture
def client(app):
    """Provides a TestClient for the test app."""
    return TestClient(app)


def test_no_exception(client: TestClient):
    """Tests the middleware when no exception is raised."""

    @client.app.get("/no-error")
    async def no_error():
        return {"message": "OK"}

    response = client.get("/no-error")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}


def test_no_exception_with_origin(client: TestClient):
    """Tests the middleware when no exception is raised and origin is present."""

    @client.app.get("/no-error")
    async def no_error():
        return {"message": "OK"}

    response = client.get("/no-error", headers={"Origin": "https://example.com"})
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}


def test_not_found_exception(client: TestClient):
    """Tests the NotFound exception handling."""

    @client.app.get("/not-found")
    async def not_found():
        raise NotFound()

    response = client.get("/not-found")
    assert response.status_code == 404
    problem = response.json()
    assert problem["title"] == "Not found"
    assert problem["type"] == "https://test.example.com/not-found"


def test_unauthorized_exception(client: TestClient):
    """Tests the Unauthorized exception handling."""

    @client.app.get("/unauthorized")
    async def unauthorized():
        raise Unauthorized()

    response = client.get("/unauthorized", headers={"Origin": "https://example.com"})
    assert response.status_code == 401
    problem = response.json()
    assert problem["title"] == "Unauthorized"
    assert problem["type"] == "https://test.example.com/unauthorized"


def test_bad_request_exception(client: TestClient):
    """Tests the BadRequest exception handling."""

    @client.app.get("/bad-request")
    async def bad_request():
        raise BadRequest()

    response = client.get("/bad-request")
    assert response.status_code == 400
    problem = response.json()
    assert problem["title"] == "Bad Request"
    assert problem["type"] == "https://test.example.com/bad-request"


def test_incorrect_attribute_type_exception(client: TestClient):
    """Tests the IncorrectAttributeType exception handling."""

    @client.app.get("/incorrect-attribute")
    async def incorrect_attribute():
        raise IncorrectAttributeType("Incorrect type")

    response = client.get("/incorrect-attribute", headers={"Origin": "https://different.com"})
    assert response.status_code == 400
    problem = response.json()
    assert problem["title"] == "Incorrect Attribute Type"
    assert problem["type"] == "https://test.example.com/incorrect-attribute-type"
    assert problem["detail"] == "Incorrect type"


def test_non_existent_attribute_exception(client: TestClient):
    """Tests the NonExistantAttribute exception handling."""

    @client.app.get("/non-existent-attribute")
    async def non_existent_attribute():
        raise NonExistantAttribute("Attribute does not exist")

    response = client.get("/non-existent-attribute")
    assert response.status_code == 404
    problem = response.json()
    assert problem["title"] == "Non-Existent Attribute"
    assert problem["type"] == "https://test.example.com/non-existent-attribute"
    assert problem["detail"] == "Attribute does not exist"


def test_missing_required_attribute_exception(client: TestClient):
    """Tests the MissingRequiredAttribute exception handling."""

    @client.app.get("/missing-required-attribute")
    async def missing_required_attribute():
        raise MissingRequiredAttribute("Missing attribute")

    response = client.get("/missing-required-attribute")
    assert response.status_code == 400
    problem = response.json()
    assert problem["title"] == "Missing Required Attribute"
    assert problem["type"] == "https://test.example.com/missing-required-attribute"
    assert problem["detail"] == "Missing attribute"


def test_missing_hal_template_exception(client: TestClient):
    """Tests the MissingHALTemplate exception handling."""

    @client.app.get("/missing-hal-template")
    async def missing_hal_template():
        raise MissingHALTemplate("HAL template missing")

    response = client.get("/missing-hal-template")
    assert response.status_code == 404
    problem = response.json()
    assert problem["title"] == "Missing HAL Template"
    assert problem["type"] == "https://test.example.com/missing-hal-template"
    assert problem["detail"] == "HAL template missing"


def test_http_error_exception(client: TestClient):
    """Tests the HTTPError exception handling."""

    @client.app.get("/http-error")
    async def http_error():
        response = MagicMock()
        response.status_code = 418  # I'm a teapot!
        raise HTTPError("Teapot error", response=response)

    response = client.get("/http-error")
    assert response.status_code == 418
    problem = response.json()
    assert problem["title"] == "HTTP Error"
    assert problem["type"] == "https://test.example.com/http-error"
    assert problem["detail"] == "An HTTP error occurred: Teapot error"


def test_llm_deny_exception(client: TestClient):
    """Tests the LLMDenyException exception handling."""

    @client.app.get("/llm-deny")
    async def llm_deny():
        raise LLMDenyException("LLM denied")

    response = client.get("/llm-deny")
    assert response.status_code == 400
    problem = response.json()
    assert problem["title"] == "Request Denied"
    assert problem["type"] == "https://test.example.com/request-denied"
    assert problem["detail"] == "LLM denied"


def test_generic_exception(client: TestClient):
    """Tests the generic Exception handling."""

    @client.app.get("/generic-exception")
    async def generic_exception():
        raise Exception("Something went wrong")

    response = client.get("/generic-exception")
    assert response.status_code == 500
    problem = response.json()
    assert problem["title"] == "Internal server error"
    assert problem["type"] == "https://test.example.com/unknown"
    assert problem["detail"] == "An unexpected error occurred: Something went wrong"


def test_http_error_no_response(client: TestClient):
    """Tests HTTPError when e.response is None"""
    @client.app.get("/http-error-no-response")
    async def http_error_no_response():
        raise HTTPError("Generic HTTP Error")

    response = client.get("/http-error-no-response")
    assert response.status_code == 500
    problem = response.json()
    assert problem["title"] == "HTTP Error"
    assert problem["type"] == "https://test.example.com/http-error"

