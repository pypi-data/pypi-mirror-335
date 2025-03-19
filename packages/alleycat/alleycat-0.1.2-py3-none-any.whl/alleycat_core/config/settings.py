"""Configuration settings for AlleyCat."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """AlleyCat configuration settings."""

    # LLM Provider settings
    provider: Literal["openai"] = "openai"
    openai_api_key: str = Field(default="", description="OpenAI API key")
    model: str = Field(default="gpt-4o-mini", description="Model to use")
    temperature: float = Field(
        default=0.7,
        description="Sampling temperature",
        ge=0.0,
        le=2.0
    )
    max_tokens: int | None = Field(
        default=None,
        description="Maximum number of tokens to generate"
    )

    # Chat settings
    history_file: Path = Field(
        default=Path.home() / ".alleycat" / "history.json",
        description="Path to chat history file"
    )
    max_history: int = Field(
        default=100,
        description="Maximum number of messages to keep in history"
    )

    # Output settings
    output_format: Literal["text", "markdown", "json"] = Field(
        default="text",
        description="Output format for responses"
    )

    model_config = SettingsConfigDict(
        env_prefix="ALLEYCAT_",
        env_file=".env",
        env_file_encoding="utf-8"
    )
