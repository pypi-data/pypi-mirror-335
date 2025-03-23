import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-mwaa",
    "version": "0.0.13",
    "description": "cdk-mwaa",
    "license": "MIT",
    "url": "https://github.com/hupe1980/cdk-mwaa.git",
    "long_description_content_type": "text/markdown",
    "author": "hupe1980<frankhuebner1980@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/hupe1980/cdk-mwaa.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_mwaa",
        "cdk_mwaa._jsii"
    ],
    "package_data": {
        "cdk_mwaa._jsii": [
            "cdk-mwaa@0.0.13.jsii.tgz"
        ],
        "cdk_mwaa": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.182.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.109.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
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
