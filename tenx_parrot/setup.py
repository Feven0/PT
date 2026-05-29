"""Package setup configuration."""
from setuptools import setup, find_packages

setup(
    name="tenx_ipersona",
    version="1.0.0",
    description="TenX iPersona Backend",
    author="TenX Team",
    packages=find_packages(include=["*"]),
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn>=0.25.0",
        "pydantic>=2.5.3",
        "pydantic[email]>=2.5.3",
        "pydantic-settings>=2.1.0",
        "dependency-injector>=4.41.0",
        "starlette>=0.27.0",
        "PyYAML>=6.0.1",
        "redis>=5.0.1",
        "weaviate-client>=3.25.3",
        "httpx>=0.26.0",
        "aiohttp>=3.9.1",
        "boto3>=1.34.15",
        "botocore>=1.34.15",
        "aiosmtplib>=3.0.1",
        "python-jose>=3.3.0",
        "prometheus-client>=0.19.0",
        "opentelemetry-api>=1.21.0",
        "opentelemetry-sdk>=1.21.0",
        "opentelemetry-instrumentation-fastapi>=0.42b0",
        "psutil>=5.9.7",
        "passlib>=1.7.4",
        "jwt>=1.3.1",
        "python-multipart>=0.0.6",
        "google-auth>=2.25.2",
        "google-auth-oauthlib>=1.2.0",
        "google-api-python-client>=2.111.0",
        "aiortc>=1.5.0",
        "websockets>=12.0",
        "structlog>=23.2.0",
        "wasabi>=0.10.1",
        "python-dotenv>=1.0.0",
        "tenacity>=8.2.3",
        "python-dateutil>=2.8.2",
        "pytz>=2023.3.post1"
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.23.2",
            "pytest-cov>=4.1.0",
            "black>=23.12.1",
            "isort>=5.13.2",
            "mypy>=1.8.0",
            "pylint>=3.0.3",
            "flake8>=7.0.0"
        ]
    }
)
