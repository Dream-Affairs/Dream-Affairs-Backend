"""Test cases for custom responses and exceptions."""
import pytest

from app.api.responses.custom_responses import (
    CustomException,
    CustomResponse,
    custom_http_exception_handler,
)


def test_custom_response() -> None:
    """Test the custom response class."""
    response = CustomResponse(
        status_code=200, message="Success", data={"status": "Healthy"}
    )
    assert response.status_code == 200
    assert (
        response.body == b'{"message":"Success","data":{"status":"Healthy"}}'
    )


def test_custom_response_with_headers() -> None:
    """Test the custom response class with headers."""
    response = CustomResponse(
        status_code=200,
        message="Success",
        data={"status": "Healthy"},
        headers={"X-Custom": "test"},
    )
    assert response.status_code == 200
    assert (
        response.body == b'{"message":"Success","data":{"status":"Healthy"}}'
    )
    assert response.headers.get("X-Custom") == "test"


def test_custom_exception() -> None:
    """Test the custom exception class."""
    with pytest.raises(CustomException) as exc:
        raise CustomException(
            status_code=400,
            message="Bad Request",
            data={"status": "Bad Request"},
        )
    assert exc.value.status_code == 400
    assert exc.value.detail == {
        "message": "Bad Request",
        "data": {"status": "Bad Request"},
    }


def test_custom_exception_with_headers() -> None:
    """Test the custom exception class with headers."""
    with pytest.raises(CustomException) as exc:
        raise CustomException(
            status_code=400,
            message="Bad Request",
            data={"status": "Bad Request"},
            headers={"X-Custom": "test"},
        )
    assert exc.value.status_code == 400
    assert exc.value.detail == {
        "message": "Bad Request",
        "data": {"status": "Bad Request"},
    }
    assert exc.value.headers == {"X-Custom": "test"}


@pytest.mark.asyncio
async def test_custom_http_exception_handler() -> None:
    """Test the custom http exception handler."""
    response = await custom_http_exception_handler(
        _=None,
        exc=CustomException(
            status_code=400,
            message="Bad Request",
            data={"status": "Bad Request"},
        ),
    )
    assert response.status_code == 400
    assert (
        response.body
        == b'{"message":"Bad Request","data":{"status":"Bad Request"}}'
    )
