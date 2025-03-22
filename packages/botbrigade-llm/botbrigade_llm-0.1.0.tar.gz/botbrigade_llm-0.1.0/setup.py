from setuptools import setup, find_packages

setup(
    name="botbrigade-llm",
    version="0.1.0",
    author="Lantip",
    author_email="lantip@gmail.com",
    description="A Python SDK for interacting with the BotBrigade LLM API.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/bot-brigade-studio/botbrigade-llm",
    packages=find_packages(),
    install_requires=[
        "httpx",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)