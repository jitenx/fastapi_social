from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    # database_version: str
    database_host: str
    database_port: str
    database_name: str
    database_password: str
    database_username: str
    algorithm: str
    secret_key: str
    access_token_expire_minutes: int
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = AppSettings()  # pyright: ignore[reportCallIssue]
