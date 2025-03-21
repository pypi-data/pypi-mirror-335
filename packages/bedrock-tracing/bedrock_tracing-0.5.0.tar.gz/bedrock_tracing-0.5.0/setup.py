from setuptools import setup, find_packages

setup(
    name="bedrock_tracing",
    version="0.5.0",
    author="Agi K Thomas",
    author_email="agikthomas@hotmail.com",
    description="A Python library for tracing Bedrock agent responses with OpenTelemetry.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/agithomas/bedrock-tracing",
    packages=find_packages(),
    install_requires=[
        "opentelemetry-api",
        "opentelemetry-sdk"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

