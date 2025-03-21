from setuptools import setup, find_packages

setup(
    name="cli-social",
    version="0.0.2.dev0",
    author="Andrew Polykandriotis",
    author_email="andrew@minakilabs.com",
    description="A CLI interface for interacting with the MinakiLabs Social API",
    long_description="Private development CLI project for internal testing by MinakiLabs.",
    long_description_content_type="text/markdown",
    url="https://minakilabs.dev",
    project_urls={
        "Source": "https://github.com/minakilabs/cli-social",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    install_requires=[
        "click",
        "requests",
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "asyncpg"
    ],
    entry_points={
        "console_scripts": [
            "social=cli.cli:cli"
        ]
    },
    python_requires=">=3.7",
)
