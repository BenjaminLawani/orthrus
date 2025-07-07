import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.environ["DATABASE_URL"]
    JWT_KEY: str = os.environ["JWT_KEY"]
    API_VERSION: str = os.environ["API_VERSION"]
    TOKEN_EXPIRES: int = os.environ["TOKEN_EXPIRES"]
    EMAIL_FROM: str = os.getenv("EMAIL_FROM")
    SMTP_HOST: str = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT"))
    SMTP_TLS: bool = os.getenv("SMTP_TLS")
    SMTP_USER: str = os.getenv("SMTP_USER")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")

settings = Settings()