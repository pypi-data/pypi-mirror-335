from setuptools import setup, find_packages
import os


def read_readme():
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    return ""

setup(
    name="fastapi-autodoc",
    version="1.0.2",
    description="A FastAPI library for generating and managing project documentation",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Yemi Ogunrinde",
    author_email="ogunrinde_olayemi@yahoo.com",
    url="https://github.com/BisiOlaYemi/fastapi-autodoc",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "click",
        "pydantic",
        "jinja2",
        "python-dotenv",
        "pydantic-settings",
        "watchdog",
        "typing-extensions",
        "httpx",
        "ast-comments",
        "astroid",
    ],
    entry_points={
        "console_scripts": [
            "fastapi-autodoc=app.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: FastAPI",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
        ],
    },
)