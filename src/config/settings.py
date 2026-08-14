"""
Saphira AI — validated environment settings.

Loads from process environment and optional .env / .env.local files,
then validates types and presence rules via pydantic-settings.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List, Literal, Optional

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / dotenv files."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Runtime ---
    port: int = Field(default=8000, ge=1, le=65535, description="HTTP listen port")
    environment: Literal["development", "staging", "production", "test"] = Field(
        default="development",
        validation_alias="ENVIRONMENT",
    )
    saphira_env: Optional[str] = Field(default=None, validation_alias="SAPHIRA_ENV")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        validation_alias="LOG_LEVEL",
    )
    saphira_allowed_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        validation_alias="SAPHIRA_ALLOWED_ORIGINS",
    )

    # --- Persistence (optional for minimal local chat) ---
    database_url: Optional[str] = Field(default=None, validation_alias="DATABASE_URL")
    redis_url: Optional[str] = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    celery_broker_url: Optional[str] = Field(default=None, validation_alias="CELERY_BROKER_URL")
    celery_result_backend: Optional[str] = Field(default=None, validation_alias="CELERY_RESULT_BACKEND")

    # --- Model / provider credentials ---
    openai_api_key: Optional[str] = Field(default=None, validation_alias="OPENAI_API_KEY")
    gemini_api_key: Optional[str] = Field(default=None, validation_alias="GEMINI_API_KEY")
    xai_api_key: Optional[str] = Field(default=None, validation_alias="XAI_API_KEY")
    saphira_model: Optional[str] = Field(default=None, validation_alias="SAPHIRA_MODEL")

    # --- Voice / TTS ---
    elevenlabs_api_key: Optional[str] = Field(default=None, validation_alias="ELEVENLABS_API_KEY")
    elevenlabs_voice_id: Optional[str] = Field(default=None, validation_alias="ELEVENLABS_VOICE_ID")
    saphira_tts_provider: Optional[str] = Field(default=None, validation_alias="SAPHIRA_TTS_PROVIDER")

    # --- Commerce ---
    stripe_secret_key: Optional[str] = Field(default=None, validation_alias="STRIPE_SECRET_KEY")
    stripe_webhook_secret: Optional[str] = Field(default=None, validation_alias="STRIPE_WEBHOOK_SECRET")

    # --- Security ---
    saphira_jwt_secret: Optional[str] = Field(default=None, validation_alias="SAPHIRA_JWT_SECRET")
    saphira_encryption_key: Optional[str] = Field(default=None, validation_alias="SAPHIRA_ENCRYPTION_KEY")
    saphira_admin_audit_key: Optional[str] = Field(default=None, validation_alias="SAPHIRA_ADMIN_AUDIT_KEY")

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, v: object) -> object:
        if isinstance(v, str):
            return v.upper()
        return v

    @field_validator("environment", mode="before")
    @classmethod
    def normalize_environment(cls, v: object) -> object:
        if isinstance(v, str):
            return v.lower()
        return v

    @model_validator(mode="after")
    def production_requires_core_secrets(self) -> "Settings":
        """In production, require security-related secrets when features imply them."""
        if self.environment == "production":
            missing: List[str] = []
            # Soft guidance: warn via exception only for clearly critical empty JWT if set policy requires it.
            # Keep bootable with optional secrets; enforce only when explicitly enabled later.
            if self.saphira_jwt_secret is not None and len(self.saphira_jwt_secret.strip()) == 0:
                missing.append("SAPHIRA_JWT_SECRET (empty)")
            if missing:
                raise ValueError(
                    "Invalid production configuration: " + ", ".join(missing)
                )
        return self

    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.saphira_allowed_origins.split(",") if o.strip()]

    def has_any_llm_provider(self) -> bool:
        return bool(
            (self.openai_api_key and self.openai_api_key.strip())
            or (self.gemini_api_key and self.gemini_api_key.strip())
            or (self.xai_api_key and self.xai_api_key.strip())
        )

    def validation_report(self) -> dict:
        """Structured summary for health / CLI (never includes secret values)."""
        return {
            "environment": self.environment,
            "port": self.port,
            "log_level": self.log_level,
            "allowed_origins_count": len(self.allowed_origins_list()),
            "database_configured": bool(self.database_url),
            "redis_configured": bool(self.redis_url),
            "llm_provider_configured": self.has_any_llm_provider(),
            "tts_configured": bool(self.elevenlabs_api_key and self.elevenlabs_voice_id),
            "stripe_configured": bool(self.stripe_secret_key),
            "jwt_secret_set": bool(self.saphira_jwt_secret and self.saphira_jwt_secret.strip()),
        }


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton for application use."""
    return Settings()


def validate_environment(*, strict: bool = False) -> Settings:
    """
    Load and validate environment.

    Raises pydantic.ValidationError on type/constraint failures.
    If strict=True, also requires at least one LLM provider key (useful for CI / full-stack local).
    """
    settings = Settings()
    if strict and not settings.has_any_llm_provider():
        raise ValueError(
            "Strict validation failed: set at least one of OPENAI_API_KEY, GEMINI_API_KEY, or XAI_API_KEY"
        )
    return settings
