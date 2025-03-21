from setuptools import setup, find_packages

# Read README with explicit UTF-8 encoding
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="agentrix",
    version="0.1.0",
    author="Sanjeev",
    author_email="sanjeevsaritha03@gmail.com",
    description="A framework for creating AI agents, agent managers and Memory stores(buffer memory and Redis memory store).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sanjeev-0407/Agentic.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "beautifulsoup4",
        "requests"
    ],
)