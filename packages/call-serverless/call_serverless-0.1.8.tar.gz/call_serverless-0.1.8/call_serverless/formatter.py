import json
import os
from typing import Union
from urllib.parse import parse_qs, urlparse


def base_template():
    with open(os.path.join(os.path.dirname(__file__), "template.json"), "r") as file:
        request = json.load(file)
    return request


def format_request(
    stage: str,
    path: str,
    method: str,
    body: Union[dict, None] = None,
    headers: Union[dict, None] = None,
):
    """
    @param headers: dict
    @param path: str - the path of the resource and it starts with a forward slash
    """
    if not path.startswith("/"):
        path = f"/{path}"

    parsed = urlparse(path)
    params = (
        {k: v[0] for k, v in parse_qs(parsed.query).items()} if parsed.query else None
    )
    path = parsed.path

    template = base_template()
    template["resource"] = path
    template["path"] = path
    template["headers"] = headers
    template["queryStringParameters"] = params
    template["requestContext"]["resourcePath"] = path
    template["requestContext"]["path"] = f"/{stage}{path}"
    template["requestContext"]["stage"] = stage
    template["body"] = body
    template["httpMethod"] = method
    template["requestContext"]["httpMethod"] = method
    return template
