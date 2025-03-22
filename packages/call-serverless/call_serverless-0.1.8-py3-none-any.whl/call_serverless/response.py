import json
from typing import Union

from .exceptions import ErrorResponse


class CLResponse:
    def __init__(self, status_code: int, body: Union[dict, str]):
        self.status_code = status_code
        try:
            self.body = json.loads(body)  # type: ignore
        except json.JSONDecodeError:
            self.body = body

    def __str__(self):
        return f"<CLResponse {self.status_code}>"

    @classmethod
    def from_response(cls, response: str):
        try:
            response_json = json.loads(response)
            instance = cls(response_json["statusCode"], response_json["body"])
        except json.JSONDecodeError:
            raise
        return instance

    def raise_for_status(self):
        if self.status_code >= 400:
            raise ErrorResponse(self.body)
