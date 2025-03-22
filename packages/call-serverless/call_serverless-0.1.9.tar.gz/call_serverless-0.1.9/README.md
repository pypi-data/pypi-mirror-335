# Call Serverless
`call-serverless` is a Python library designed to remotely invoke AWS Lambda functions that have API Gateway integration. It simplifies the process of invoking Lambda functions with HTTP-like requests, providing easy-to-use methods to send requests and handle responses.

## Features
#### Invoke AWS Lambda Functions:
Call Lambda functions via their ARN using HTTP methods such as GET, POST, PUT, DELETE.
#### Simulate API Gateway Requests: 
Send requests with customizable paths, headers, stages, and body payloads.

#### Simple Setup:
Built on top of boto3, the library manages AWS Lambda client connections and simplifies API invocation.


## Installation
To install the library, use pip:
``` pip install call-serverless ```

## Requirements
- Python 3.6 or higher
- `boto3` for AWS SDK integration

## Usage
Basic Lambda Invocation

```
from call_serverless.apis import call_lambda

response = call_lambda(
    lambda_arn="arn:aws:lambda:us-west-2:123456789012:function:MyFunction",
    path="/users",
    method="POST",
    stage="prod",
    region="us-west-2",
    body={"username": "new_user"},
    headers={"Authorization": "Bearer token123"}
)

print(response)
# {'statusCode': 200, 'message': 'User created successfully'}
```

## Contributing
If you want to contribute to this project, please submit a pull request or open an issue on GitHub.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.