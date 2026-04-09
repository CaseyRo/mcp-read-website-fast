"""Configuration loaded from environment variables."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Server transport
    transport: Literal["stdio", "http"] = "stdio"
    host: str = "127.0.0.1"
    port: int = 8000

    # Authentication
    mcp_api_key: SecretStr | None = None

    # Cache
    cache_dir: Path = Path.home() / ".cache" / "mcp-read-website-fast"

    model_config = {"env_prefix": "", "case_sensitive": False}


settings = Settings()
