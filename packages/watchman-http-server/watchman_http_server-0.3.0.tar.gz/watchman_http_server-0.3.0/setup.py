# Setup script for packaging
from setuptools import setup, find_packages

setup(
    name="watchman_http_server",
    version="0.3.0",
    packages=find_packages(),
    install_requires=["fastapi", "uvicorn", "django-environ"],
    entry_points={
        "console_scripts": [
            "watchman-http-server=watchman_http_server.main:cli",
        ],
    },
    author="Watchman",
    author_email="support@watchman.bj",
    description="Un serveur HTTP FastAPI pour récupérer les applications installées",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: FastAPI",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
