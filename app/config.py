from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    groq_api_key: str
    mem0_api_key: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
