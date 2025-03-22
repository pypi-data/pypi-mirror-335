import json
from typing import Union

import boto3

from .formatter import format_request

_client = None


def _get_lambda_client(region: str):
    global _client

    if not _client:
        _client = boto3.client("lambda", region_name=region)
    return _client


def call_lambda(
    lambda_arn: str,
    path: str,
    method: str,
    stage: str,
    region: str,
    body: Union[dict, None] = None,
    headers: Union[dict, None] = None,
):
    """
    Invokes an AWS Lambda function by sending an HTTP-like request with the specified method, path, and headers.

    Args:
        lambda_arn (str): The Amazon Resource Name (ARN) of the Lambda function to invoke.
        path (str): The API Gateway path to invoke on the Lambda function (e.g., `/users`, `/items`).
        method (str): The HTTP method to use for the request (e.g., 'GET', 'POST', 'PUT', 'DELETE').
        stage (str): The deployment stage of the API (e.g., 'dev', 'prod').
        region (str): The AWS region where the Lambda function is hosted.
        body (Union[dict, None], optional): The request body to send in the Lambda invocation. Defaults to None.
        headers (Union[dict, None], optional): Additional headers to send in the request. Defaults to None.

    Returns:
        dict: The JSON response body from the Lambda function.

    Raises:
        botocore.exceptions.BotoCoreError: If there is an error in the Lambda client during the invocation.
        json.JSONDecodeError: If the response from the Lambda is not valid JSON or cannot be decoded.

    Example:
        >>> response = call_lambda(
                lambda_arn="arn:aws:lambda:us-west-2:123456789012:function:MyFunction",
                path="/users",
                method="POST",
                stage="prod",
                region="us-west-2",
                body={"username": "new_user"},
                headers={"Authorization": "Bearer token123"}
            )
        >>> print(response)
        {'statusCode': 200, 'message': 'User created successfully'}

    This function formats a request payload and uses the AWS SDK to invoke a Lambda function via its ARN.
    It simulates an API Gateway request to the Lambda, including HTTP methods and headers,
    and parses the response body into a dictionary.
    """

    payload = format_request(stage, path, method, body, headers)

    client = _get_lambda_client(region)

    response = client.invoke(
        FunctionName=lambda_arn,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload),
    )

    response_str = response["Payload"].read().decode("utf-8")
    response_json = json.loads(response_str)

    return response_json["body"]
