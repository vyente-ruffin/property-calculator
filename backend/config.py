from pathlib import Path

from pydantic_settings import BaseSettings

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-4o"
    RENTCAST_API_KEY: str = ""
    GOOGLE_SERVICE_ACCOUNT: str = "{}"
    GOOGLE_SHEET_ID: str = "1dVf1UShQry4nDvM3HbqM9ts0ltbKnruEDKd6lZ_xAMg"

    model_config = {"env_file": str(_ENV_FILE), "extra": "ignore"}


settings = Settings()
