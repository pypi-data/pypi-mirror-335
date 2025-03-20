from json import JSONDecodeError
from typing import Type, TypeVar

import pydantic
import requests

from .exceptions import InvalidResponseSchema, RequestError


def format_pydantic_error(error: pydantic.ValidationError):
    message = "Invalid data structure\n"
    for e in error.errors():
        variable_path = ".".join(str(value) for value in e["loc"])
        message += f"{variable_path} - {e['msg']}\n"

    return message


ExtendsBaseModel = TypeVar("ExtendsBaseModel", bound=pydantic.BaseModel)


def try_parse_response(
    response: requests.Response, output_model: Type[ExtendsBaseModel]
) -> ExtendsBaseModel:
    try:
        response_json = response.json()
    except JSONDecodeError:
        raise InvalidResponseSchema("Response is not a valid json")

    try:
        parsed_response = output_model(**response_json)
    except pydantic.ValidationError as e:
        raise InvalidResponseSchema(format_pydantic_error(e))
    return parsed_response


def raise_if_response_not_ok(response: requests.Response, error_message: str):
    if not response.ok:
        raise RequestError(
            f"({response.status_code}) - {error_message}\n{response.text}"
        )
