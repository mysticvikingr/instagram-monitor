from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_HOST: str
    REDIS_PORT: int
    TIKHUB_API_BASE_URL: str = "https://api.tikhub.io/api/v1/instagram/web_app"
    TIKHUB_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
