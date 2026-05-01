import os
from pathlib import Path

from dotenv import load_dotenv

# Carrega variaveis do arquivo .env se existir
_env_file = Path(__file__).parent.parent / ".env"
if _env_file.exists():
    load_dotenv(_env_file)


def get_token() -> str:
    token = os.getenv("DISCORD_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Defina a variavel de ambiente DISCORD_TOKEN com o token do bot.")
    return token


def get_prefix() -> str:
    return os.getenv("BOT_PREFIX", "!")

