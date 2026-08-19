"""Saphira AI validated environment settings."""
from __future__ import annotations

from functools import lru_cache
from typing import List, Literal, Optional
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=('.env', '.env.local'), env_file_encoding='utf-8', extra='ignore', case_sensitive=False)

    port: int = Field(default=8000, ge=1, le=65535)
    environment: Literal['development', 'staging', 'production', 'test'] = Field(default='development', validation_alias='ENVIRONMENT')
    saphira_env: Optional[str] = Field(default=None, validation_alias='SAPHIRA_ENV')
    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = Field(default='INFO', validation_alias='LOG_LEVEL')
    saphira_allowed_origins: str = Field(default='http://localhost:3000,http://127.0.0.1:3000', validation_alias='SAPHIRA_ALLOWED_ORIGINS')

    database_url: Optional[str] = Field(default=None, validation_alias='DATABASE_URL')
    redis_url: Optional[str] = Field(default='redis://localhost:6379/0', validation_alias='REDIS_URL')
    celery_broker_url: Optional[str] = Field(default=None, validation_alias='CELERY_BROKER_URL')
    celery_result_backend: Optional[str] = Field(default=None, validation_alias='CELERY_RESULT_BACKEND')

    openai_api_key: Optional[str] = Field(default=None, validation_alias='OPENAI_API_KEY')
    gemini_api_key: Optional[str] = Field(default=None, validation_alias='GEMINI_API_KEY')
    xai_api_key: Optional[str] = Field(default=None, validation_alias='XAI_API_KEY')
    saphira_model: Optional[str] = Field(default=None, validation_alias='SAPHIRA_MODEL')

    elevenlabs_api_key: Optional[str] = Field(default=None, validation_alias='ELEVENLABS_API_KEY')
    elevenlabs_voice_id: Optional[str] = Field(default=None, validation_alias='ELEVENLABS_VOICE_ID')
    saphira_tts_provider: Optional[str] = Field(default=None, validation_alias='SAPHIRA_TTS_PROVIDER')

    stripe_secret_key: Optional[str] = Field(default=None, validation_alias='STRIPE_SECRET_KEY')
    stripe_webhook_secret: Optional[str] = Field(default=None, validation_alias='STRIPE_WEBHOOK_SECRET')
    stripe_price_monthly: Optional[str] = Field(default=None, validation_alias='STRIPE_PRICE_MONTHLY')
    resend_api_key: Optional[str] = Field(default=None, validation_alias='RESEND_API_KEY')
    resend_from: Optional[str] = Field(default=None, validation_alias='RESEND_FROM')
    telegram_bot_token: Optional[str] = Field(default=None, validation_alias='TELEGRAM_BOT_TOKEN')
    telegram_chat_id: Optional[str] = Field(default=None, validation_alias='TELEGRAM_CHAT_ID')

    saphira_jwt_secret: Optional[str] = Field(default=None, validation_alias='SAPHIRA_JWT_SECRET')
    saphira_encryption_key: Optional[str] = Field(default=None, validation_alias='SAPHIRA_ENCRYPTION_KEY')
    saphira_admin_audit_key: Optional[str] = Field(default=None, validation_alias='SAPHIRA_ADMIN_AUDIT_KEY')

    @field_validator('log_level', mode='before')
    @classmethod
    def normalize_log_level(cls, v: object) -> object:
        return v.upper() if isinstance(v, str) else v

    @field_validator('environment', mode='before')
    @classmethod
    def normalize_environment(cls, v: object) -> object:
        return v.lower() if isinstance(v, str) else v

    @model_validator(mode='after')
    def production_requires_core_secrets(self) -> 'Settings':
        if self.environment == 'production' and self.saphira_jwt_secret is not None and not self.saphira_jwt_secret.strip():
            raise ValueError('Invalid production configuration: SAPHIRA_JWT_SECRET is empty')
        return self

    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.saphira_allowed_origins.split(',') if o.strip()]

    def has_any_llm_provider(self) -> bool:
        return any(bool(v and v.strip()) for v in (self.openai_api_key, self.gemini_api_key, self.xai_api_key))

    def validation_report(self) -> dict:
        return {
            'environment': self.environment,
            'port': self.port,
            'log_level': self.log_level,
            'allowed_origins_count': len(self.allowed_origins_list()),
            'database_configured': bool(self.database_url),
            'redis_configured': bool(self.redis_url),
            'llm_provider_configured': self.has_any_llm_provider(),
            'tts_configured': bool(self.elevenlabs_api_key and self.elevenlabs_voice_id),
            'stripe_configured': bool(self.stripe_secret_key),
            'stripe_webhook_configured': bool(self.stripe_webhook_secret),
            'stripe_price_configured': bool(self.stripe_price_monthly),
            'email_configured': bool(self.resend_api_key and self.resend_from),
            'phone_alert_configured': bool(self.telegram_bot_token and self.telegram_chat_id),
            'jwt_secret_set': bool(self.saphira_jwt_secret and self.saphira_jwt_secret.strip()),
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()


def validate_environment(*, strict: bool = False) -> Settings:
    settings = Settings()
    if strict and not settings.has_any_llm_provider():
        raise ValueError('Strict validation failed: set OPENAI_API_KEY, GEMINI_API_KEY, or XAI_API_KEY')
    return settings
