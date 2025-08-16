"""Configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="VRM_",
    )

    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")
    site_id: str = Field(..., description="ID of the site")
    token_name: str = Field(description="Name of the token", default="vrm-cloud-mqtt")
    revoke_duplicate_token: bool = Field(description="Revoke duplicate token", default=False)
    mqtt_host: str = Field(description="MQTT host")
    mqtt_port: int = Field(description="MQTT port", default=1883)
    mqtt_topic: str = Field(description="MQTT topic", default="vrm/cloud")
    mqtt_username: str | None = Field(description="MQTT username", default=None)
    mqtt_password: str | None = Field(description="MQTT password", default=None)
    poll_interval: int = Field(description="Poll interval", default=60)
    debug: bool = Field(description="Enable debug logging", default=False)


# Create a global settings instance
settings = Settings()
