from pydantic import BaseSettings, Field, AnyHttpUrl

class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SELLER_WEBHOOK_URL: AnyHttpUrl = Field(..., env="SELLER_WEBHOOK_URL")
    API_KEY: str = Field(..., env="API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
