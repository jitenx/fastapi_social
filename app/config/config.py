from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "mydb"
    database_username: str = "user"
    database_password: str = "pass"
    algorithm: str = "HS256"
    secret_key: str = "supersecret"
    access_token_expire_minutes: int = 60
    database_com: str = "default"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = AppSettings()
