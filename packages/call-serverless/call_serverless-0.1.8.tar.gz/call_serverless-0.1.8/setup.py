from setuptools import find_packages, setup

setup(
    name="call-serverless",
    version="0.1.8",
    description="Remote call AWS Lambda functions directly that have API Gateway integration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/er-nabin-bhusal/call-serverless",
    author="Nabin Bhusal",
    author_email="nabinbhusal80@gmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "boto3",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data={"call_serverless": ["template.json"]},
    python_requires=">=3.8",
)
