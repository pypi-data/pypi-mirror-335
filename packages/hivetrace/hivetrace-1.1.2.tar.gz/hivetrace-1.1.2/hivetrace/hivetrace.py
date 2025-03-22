import httpx
import os
import uuid
from typing import Dict, Any, Optional, Union
from dotenv import load_dotenv


class MissingConfigError(Exception):
    def __init__(self, param: str):
        super().__init__(f"Config parameter '{param}' is missing")


class InvalidParameterError(Exception):
    pass


class UnauthorizedError(Exception):
    def __init__(self, message="Invalid or expired access token"):
        super().__init__(message)


class HivetraceSDK:
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        load_dotenv()
        self.config = config or self._load_config_from_env()
        self.hivetrace_url = self._get_required_config("HIVETRACE_URL")
        self.hivetrace_access_token = self._get_required_config(
            "HIVETRACE_ACCESS_TOKEN"
        )
        self.session = httpx.Client()
        self._verify_token()

    def _verify_token(self):
        url = f"{self.hivetrace_url}/api-tokens/validate"
        token = self.hivetrace_access_token
        payload = {
            "token": token,
        }
        try:
            verify = self.session.post(url, json=payload)
            verify.raise_for_status()
        except httpx.RequestError as e:
            raise UnauthorizedError(f"Token validation failed: {e}")

    def _load_config_from_env(self) -> Dict[str, Any]:
        return {
            "HIVETRACE_URL": os.getenv("HIVETRACE_URL"),
            "HIVETRACE_ACCESS_TOKEN": os.getenv("HIVETRACE_ACCESS_TOKEN"),
        }

    def _get_required_config(self, key: str) -> str:
        value = self.config.get(key)
        if not value:
            raise MissingConfigError(key)
        return value.rstrip("/")

    @staticmethod
    def _validate_application_id(application_id: str) -> str:
        try:
            return str(uuid.UUID(application_id))
        except ValueError as e:
            raise InvalidParameterError("Invalid application_id format") from e

    @staticmethod
    def _validate_message(message: str) -> None:
        if not isinstance(message, str) or not message.strip():
            raise InvalidParameterError("Message must be non-empty")

    @staticmethod
    def _validate_additional_parameters(
        additional_parameters: Optional[Dict[str, Any]],
    ) -> None:
        if additional_parameters is not None and not isinstance(
            additional_parameters, dict
        ):
            raise InvalidParameterError(
                "Additional parameters must be a dict or None"
            )

    def _send_request(
        self,
        endpoint: str,
        application_id: str,
        message: str,
        additional_parameters: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        try:
            application_id = self._validate_application_id(application_id)
            self._validate_message(message)
            self._validate_additional_parameters(additional_parameters)

            url = f"{self.hivetrace_url.rstrip('/')}/{endpoint.lstrip('/')}"
            payload = {
                "application_id": application_id,
                "message": message,
                "additional_parameters": additional_parameters or {},
            }

            headers = {
                "Authorization": f"Bearer {self.hivetrace_access_token}"
            }

            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as e:
            print(f"HTTP Error {e.response.status_code}")

            safe_messages = {
                400: "Invalid request.",
                401: "Unauthorized access.",
                403: "Access forbidden.",
                404: "Resource not found.",
                500: "Internal server error.",
            }

            return {
                "error": "HTTP error",
                "status_code": e.response.status_code,
                "details": safe_messages.get(
                    e.response.status_code, "An unexpected error occurred."
                ),
            }

        except httpx.RequestError as e:
            print(f"Request Error: {e}")

            return {
                "error": "Request failed",
                "details": "Failed to connect to the service.",
                "application_id": application_id,
            }

    def _send_tool_call(
        self,
        endpoint: str,
        application_id: str,
        tool_call_id: str,
        func_name: str,
        func_args: str,
        func_result: Optional[Union[Dict, str]] = None,
        additional_parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        try:
            application_id = self._validate_application_id(application_id)
            self._validate_additional_parameters(additional_parameters)

            url = f"{self.hivetrace_url.rstrip('/')}/{endpoint.lstrip('/')}"
            payload = {
                "application_id": application_id,
                "tool_call_id": tool_call_id,
                "func_name": func_name,
                "func_args": func_args,
                "func_result": func_result,
                "additional_parameters": additional_parameters or {},
            }

            headers = {
                "Authorization": f"Bearer {self.hivetrace_access_token}"
            }

            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as e:
            print(f"HTTP Error {e.response.status_code}")

            safe_messages = {
                400: "Invalid request.",
                401: "Unauthorized access.",
                403: "Access forbidden.",
                404: "Resource not found.",
                500: "Internal server error.",
            }

            return {
                "error": "HTTP error",
                "status_code": e.response.status_code,
                "details": safe_messages.get(
                    e.response.status_code, "An unexpected error occurred."
                ),
            }

        except httpx.RequestError as e:
            print(f"Request Error: {e}")

            return {
                "error": "Request failed",
                "details": "Failed to connect to the service.",
                "application_id": application_id,
            }

    def input(
        self,
        application_id: str,
        message: str,
        additional_parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self._send_request(
            "/process_request/", application_id, message, additional_parameters
        )

    def output(
        self,
        application_id: str,
        message: str,
        additional_parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self._send_request(
            "/process_response/",
            application_id,
            message,
            additional_parameters,
        )

    def function_call(
        self,
        application_id: str,
        tool_call_id: str,
        func_name: str,
        func_args: str,
        func_result: Optional[Union[Dict, str]] = None,
        additional_parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self._send_tool_call(
            "/process_response/",
            application_id,
            tool_call_id,
            func_name,
            func_args,
            func_result,
            additional_parameters,
        )

    def __del__(self) -> None:
        if hasattr(self, "session"):
            self.session.close()
