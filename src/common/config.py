import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.environ["DATABASE_URL"]
    JWT_KEY: str = os.environ["JWT_KEY"]
    API_VERSION: str = os.environ["API_VERSION"]
    TOKEN_EXPIRES: int = os.environ["TOKEN_EXPIRES"]
    EMAIL_FROM: str = os.environ["EMAIL_FROM"]
    SMTP_HOST: str = os.environ["SMTP_HOST"]
    SMTP_PORT: int = int(os.environ["SMTP_PORT"])
    SMTP_USER: str = os.environ["SMTP_USER"]
    SMTP_PASSWORD: str = os.environ["SMTP_PASSWORD"]
    GROQ_API_KEY: str = os.environ["GROQ_API_KEY"]

settings = Settings()