import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
GHOST = ROOT / "ghosttown"
TEMPLATES = ROOT / "templates"
INDEX = DATA / "index.json"
STATE = DATA / "state.json"


def _resolve_env_file() -> str:
    """Busca los secretos primero en el folder de prod (fuera del repo),
    luego en el .env local. Asi las credenciales viven fuera de git/OneDrive.

    Prioridad:
      1) GMAILBOT_ENV_FILE  (ruta explicita por variable de entorno)
      2) %USERPROFILE%/.gmailbot/.env  (folder de prod)
      3) <repo>/.env  (fallback local, ignorado por git)
    """
    explicit = os.environ.get("GMAILBOT_ENV_FILE")
    if explicit and Path(explicit).is_file():
        return explicit

    prod = Path.home() / ".gmailbot" / ".env"
    if prod.is_file():
        return str(prod)

    return str(ROOT / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_resolve_env_file(), env_file_encoding="utf-8", extra="ignore")

    imap_host: str = "imap.gmail.com"
    imap_user: str = ""
    imap_password: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    port: int = 8765


def get_settings() -> Settings:
    return Settings()
