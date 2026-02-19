from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    database_host: str
    database_port: int  # Use int for ports
    database_name: str
    database_username: str
    database_password: str

    algorithm: str
    secret_key: str
    access_token_expire_minutes: int
    database_com: str
    # Config for reading .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = AppSettings()
