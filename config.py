from functools import lru_cache
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="JARVIS", description="Application name")
    app_env: str = Field(default="development", description="Running environment")
    log_level: str = Field(default="INFO", description="Logging level")

    openai_api_key: SecretStr | None = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model")
    openrouter_api_key: SecretStr | None = Field(default=None, description="OpenRouter API key")
    openrouter_model: str = Field(default="anthropic/claude-3.5-sonnet", description="OpenRouter model")

    twilio_account_sid: SecretStr | None = Field(default=None)
    twilio_auth_token: SecretStr | None = Field(default=None)
    twilio_phone_number: str | None = Field(default=None)

    sms_owner_number: str | None = Field(default=None, description="Owner phone number for summaries")

    google_calendar_api_key: SecretStr | None = Field(default=None)
    google_calendar_id: str | None = Field(default=None)

    notes_db_path: str = Field(default="data/notes.db")

    @property
    def has_openai(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key.get_secret_value())

    @property
    def has_openrouter(self) -> bool:
        return bool(self.openrouter_api_key and self.openrouter_api_key.get_secret_value())

    @property
    def has_twilio(self) -> bool:
        return bool(
            self.twilio_account_sid and self.twilio_auth_token and self.twilio_account_sid.get_secret_value()
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
