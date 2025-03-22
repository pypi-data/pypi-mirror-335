import json
from typing import Union


def base_template():
    with open("./template.json", "r") as file:
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
    template = base_template()
    template["resource"] = path
    template["path"] = path
    template["headers"] = headers
    template["requestContext"]["resourcePath"] = path
    template["requestContext"]["path"] = f"/{stage}/{path}"
    template["requestContext"]["stage"] = stage
    template["body"] = body
    template["httpMethod"] = method
    template["requestContext"]["httpMethod"] = method
    return template
