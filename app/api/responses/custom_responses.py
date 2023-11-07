"""Custom responses function for api it contains all custom responses for api.

the return type of all functions is a tuple of
(status_code, response)

status_code: int
response: dict
"""

from typing import Any, Optional

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


async def custom_http_exception_handler(
    _: Any, exc: HTTPException
) -> JSONResponse:
    """Custom HTTP exception handler.

    This function is used to handle all HTTP exceptions
    and return a custom response.

    Args:
        request (Request): The request object
        exc (HTTPException): The exception object

        Returns:
            JSONResponse: The custom response
    """
    if isinstance(exc.detail, str):
        detail = {"message": exc.detail}
    else:
        detail = exc.detail

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": detail.get("message", "Bad Request"),
            "data": detail.get("data", None),
        },
    )


class CustomResponse(JSONResponse):  # type: ignore
    """Custom response class.

    This class is used to return custom responses for the api.
    It takes in any other keyword or parameter that
    the JSONResponse class supports.

    Args:
      status_code (int): The status code of the response
      message (str): The message to be returned
      data (dict): The data to be returned
      kwargs (Any): Any other keyword arguments

      Example:
          ```python
          from fastapi import FastAPI
          from app.api.responses.custom_responses import CustomResponse

          @app.get("/health")
          def health() -> dict[str, str]:
              return CustomResponse(
                  status_code=200,
                  message="Healthy",
                  data={"status": "Healthy"}
              )

          ```
      Example:
          ```python
          from fastapi import FastAPI
          from app.api.responses.custom_responses import CustomResponse

          @app.get("/health")
          def health() -> dict[str, str]:
              return CustomResponse(
                  status_code=200,
                  message="Healthy",
                  data={"status": "Healthy"}
                  headers={"X-Custom": "test"}
              )

          ```
    """

    def __init__(
        self,
        status_code: int = status.HTTP_200_OK,
        message: str = "Success",
        data: Optional[Any] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(
            status_code=status_code,
            content={"message": message, "data": data},
            **kwargs
        )


class CustomException(HTTPException):  # type: ignore
    """Custom exception class.

    This class is used to return custom exceptions for the api.
    The custom exception is as a reult of the `custom_http_exception_handler`
    function. It takes in any other keyword or parameter that
    the HTTPException class supports.

    Args:
      status_code (int): The status code of the response
      message (str): The message to be returned
      data (dict): The data to be returned
      kwargs (Any): Any other keyword arguments

      Example:
          ```python
          from fastapi import FastAPI
          from app.api.responses.custom_responses import CustomException

          @app.get("/health")
          def health() -> dict[str, str]:
              return CustomException(
                  status_code=200,
                  message="Healthy",
                  data={"status": "Healthy"}
              )

          ```
      Example:
          ```python
          from fastapi import FastAPI
          from app.api.responses.custom_responses import CustomException

          @app.get("/health")
          def health() -> dict[str, str]:
              return CustomException(
                  status_code=200,
                  message="Healthy",
                  data={"status": "Healthy"}
                  headers={"X-Custom": "test"}
              )

          ```
    """

    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        message: str = "Bad Request",
        data: Optional[Any] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail={"message": message, "data": data},
            **kwargs
        )
