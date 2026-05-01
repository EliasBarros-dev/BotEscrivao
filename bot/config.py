import os
from pathlib import Path

from dotenv import load_dotenv

# Carrega variaveis do arquivo .env se existir
_env_file = Path(__file__).parent.parent / ".env"
if _env_file.exists():
    load_dotenv(dotenv_path=_env_file, override=True)
    # Fallback caso o python-dotenv falhe por algum motivo de codificacao
    with open(_env_file, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()

def get_token() -> str:
    token = os.getenv("DISCORD_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Defina a variavel de ambiente DISCORD_TOKEN com o token do bot.")
    return token


def get_prefix() -> str:
    return os.getenv("BOT_PREFIX", "!")


def get_menu_channel_id() -> int | None:
    val = os.getenv("MENU_CHANNEL_ID", "").strip()
    return int(val) if val.isdigit() else None
