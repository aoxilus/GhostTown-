from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
GHOST = ROOT / "ghosttown"
TEMPLATES = ROOT / "templates"
INDEX = DATA / "index.json"
STATE = DATA / "state.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ROOT / ".env"), env_file_encoding="utf-8", extra="ignore")

    imap_host: str = "imap.gmail.com"
    imap_user: str = ""
    imap_password: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    port: int = 8765


def get_settings() -> Settings:
    return Settings()
