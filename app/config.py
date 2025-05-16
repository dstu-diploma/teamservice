from pydantic_settings import BaseSettings, SettingsConfigDict


class TeamServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    DATABASE_URL: str

    USER_SERVICE_URL: str
    USER_SERVICE_API_KEY: str

    HACKATHON_SERVICE_URL: str
    HACKATHON_SERVICE_API_KEY: str

    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str

    JWT_SECRET: str = "dstu"
    ROOT_PATH: str = ""
    INTERNAL_API_KEY: str = "apikey"


Settings = TeamServiceSettings()
