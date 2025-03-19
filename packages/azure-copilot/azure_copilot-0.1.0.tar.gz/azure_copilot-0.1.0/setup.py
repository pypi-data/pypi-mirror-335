from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

AZURE_OPENAI_SERVICE_API = "https://oai-endpoint.developer.azure-api.net/api-details#api=aws&operation=ChatCompletions_Create"

setup(
    name="azure-copilot",
    version="0.1.0",
    author="CloudRoller",
    description="A package for creating chat completions with Azure OpenAI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
