# """This module contains the LoggingMiddleware class which is a middleware."""
# import json
# import logging
# import logging.config
# import time
# from typing import Callable
# from uuid import uuid4

# from fastapi import FastAPI, HTTPException, Request, Response
# from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.types import Message

# IGNORED_PATHS = ["health", "logs"]


# class AsyncIteratorWrapper:
#    """The following is a utility class that transforms a regular iterable to
#    an asynchronous one.

#    link: https://www.python.org/dev/peps/pep-0492/#xample-2
#    """

#    def __init__(self, obj):
#        self._it = iter(obj)

#    def __aiter__(self):
#        return self

#    async def __anext__(self):
#        try:
#            value = next(self._it)
#        except StopIteration as e:
#            raise StopAsyncIteration from e
#        return value


# class LoggingMiddleware(BaseHTTPMiddleware):
#    """LoggingMiddleware class is a middleware that logs the request and
#    response.

#    Attributes:
#    - app: FastAPI
#    - logger: logging.Logger

#    Methods:
#    - dispatch: Logs the request and response
#    - set_body: Sets the request body
#    - _log_request: Logs the request
#    - _log_response: Logs the response
#    - _execute_request: Executes the request
#    - write_json_to_file: Writes the json to a file
#    """

#    def __init__(self, app: FastAPI, logger: logging.Logger) -> None:
#        super().__init__(app)
#        self.logger = logger

#    async def dispatch(
#        self, request: Request, call_next: Callable[[Request], Response]
#    ) -> Response:
#        """Logs the request and response.

#        Arguments:
#        - request: Request
#        - call_next: Callable[[Request], Response]
#        Returns:
#        - response: Response
#        """
#        #Ignore health and logs path from logging
#        path = request.url.path.split("/")[-1]
#        if path in IGNORED_PATHS:
#            return await call_next(request)

#        request_id = str(uuid4())
#        logging_dict = {"X-API-Request-ID": request_id}
#        await self.set_body(request)

#        response, response_dict = await self._log_response(
#            call_next, request, request_id
#        )
#        request_dict = await self._log_request(request)
#        logging_dict["request"] = request_dict
#        logging_dict["response"] = response_dict
#        #self.write_json_to_file(settings.LOG_FILE, logging_dict)
#        self.logger.info(logging_dict)
#        #write to file added to the config dict

#        return response

#    async def set_body(self, request: Request) -> None:
#        """Sets the request body.

#        Arguments:
#        - request: Request
#        """
#        #pylint: disable=protected-access
#        receive_ = await request._receive()

#        async def receive() -> Message:
#            return receive_

#        request._receive = receive
#        #pylint: enable=protected-access

#    async def _log_request(self, request: Request) -> str:
#        """Logs the request.

#        Arguments:
#        - request: Request
#        Returns:
#        - request_logging: str
#        """
#        path = request.url.path
#        if request.query_params:
#            path += f"?{request.query_params}"

#        request_logging = {
#            "method": request.method,
#            "path": path,
#            "ip": request.client.host,
#        }

#        try:
#            body = await request.json()
#            request_logging["body"] = body
#        except json.JSONDecodeError as e:
#            print(e)
#            body = None

#        return request_logging

#    async def _log_response(
#        self, call_next: Callable, request: Request, request_id: str
#    ) -> Response:
#        """Logs response part.

#        Arguments:
#        - call_next: Callable (To execute the actual path
#            function and get response back)
#        - request: Request
#        - request_id: str (uuid)
#        Returns:
#        - response: Response
#        - response_logging: str
#        """

#        start_time = time.perf_counter()
#        response = await self._execute_request(call_next, request, request_id)
#        finish_time = time.perf_counter()

#        overall_status = (
#            "successful" if response.status_code < 400 else "failed"
#        )

#        execution_time = finish_time - start_time
#        response_logging = {
#            "status": overall_status,
#            "status_code": response.status_code,
#            "time_taken": f"{execution_time:0.4f}s",
#        }

#        # convert the response body from asnychronous data to a list
#        resp_body = [
#            section async for section in response.__dict__["body_iterator"]
#        ]

#        #Set the resp_body as an attribute of the response object
#        setattr(response, "body_iterator", AsyncIteratorWrapper(resp_body))

#        try:
#            resp_body = json.loads(resp_body[0].decode())
#        except json.JSONDecodeError as e:
#            print(e)
#            resp_body = str(resp_body)

#        response_logging["body"] = resp_body

#        return response, response_logging

#    async def _execute_request(
#        self, call_next: Callable, request: Request, request_id: str
#    ) -> Response:
#        """Executes the actual path function using call_next. It also injects
#        "X-API-Request-ID" header to the response.

#        Arguments:
#        - call_next: Callable (To execute the actual path function
#                    and get response back)
#        - request: Request
#        - request_id: str (uuid)
#        Returns:
#        - response: Response
#        """
#        try:
#            response: Response = await call_next(request)

#            #Kickback X-Request-ID
#            response.headers["X-API-Request-ID"] = request_id
#            return response

#        except HTTPException as e:
#            self.logger.exception(
#                {
#                    "path": request.url.path,
#                    "method": request.method,
#                    "reason": e,
#                }
#            )

#    def write_json_to_file(self, filename: str, data: json) -> None:
#        """Writes the json to a file.

#        Arguments:
#        - filename: str
#        - data: dict
#        """
#        #Read existing data
#        try:
#            with open(file=filename, mode="r", encoding="UTF-8") as file:
#                existing_data = json.load(file)
#        except (FileNotFoundError, json.JSONDecodeError):
#            existing_data = []

#        #Append new data
#        existing_data.append(data)

#        #Write everything back to the file
#        with open(file=filename, mode="w", encoding="UTF-8") as file:
#            json.dump(existing_data, file, indent=4)
