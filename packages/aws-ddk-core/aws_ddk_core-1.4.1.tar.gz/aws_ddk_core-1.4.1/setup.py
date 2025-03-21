import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "aws-ddk-core",
    "version": "1.4.1",
    "description": "The AWS DataOps Development Kit is an open source development framework for customers that build data workflows and modern data architecture on AWS.",
    "license": "Apache-2.0",
    "url": "https://github.com/awslabs/aws-ddk/tree/main",
    "long_description_content_type": "text/markdown",
    "author": "AWS Professional Services<aws-proserve-orion-dev@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/awslabs/aws-ddk/tree/main"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "aws_ddk_core",
        "aws_ddk_core._jsii"
    ],
    "package_data": {
        "aws_ddk_core._jsii": [
            "aws-ddk-core@1.4.1.jsii.tgz"
        ],
        "aws_ddk_core": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.8",
    "install_requires": [
        "aws-cdk-lib>=2.177.0, <3.0.0",
        "aws-cdk.aws-glue-alpha>=2.177.0.a0, <3.0.0",
        "aws-cdk.aws-kinesisfirehose-alpha>=2.177.0.a0, <3.0.0",
        "aws-cdk.aws-kinesisfirehose-destinations-alpha>=2.177.0.a0, <3.0.0",
        "aws-cdk.integ-tests-alpha>=2.177.0.a0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.105.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
