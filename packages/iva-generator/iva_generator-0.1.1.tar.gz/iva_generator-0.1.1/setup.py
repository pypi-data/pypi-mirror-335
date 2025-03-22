from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="iva-generator",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "langchain",
        "langchain-community",
        "langchain-groq",
        "python-dotenv",
        "pydantic",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "iva=src.cli:main",
        ],
    },
    author="ItzCyzmiX",
    author_email="itzmedigamingx@gmail.com",
    description="AI Code Assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ItzCyzmiX/Iva",
    project_urls={
        "Bug Tracker": "https://github.com/ItzCyzmiX/Iva/issues",
        "Documentation": "https://github.com/ItzCyzmiX/Iva#readme",
        "Source Code": "https://github.com/ItzCyzmiX/Iva",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="ai, code generator, assistant, development",
    python_requires=">=3.8",
)