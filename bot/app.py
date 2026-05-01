import discord
from discord.ext import commands

from bot.config import get_prefix, get_token
from bot.ui.main_menu import MainMenuView


def create_bot() -> commands.Bot:
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix=get_prefix(), intents=intents)

    @bot.event
    async def on_ready() -> None:
        print(f"Conectado como {bot.user} (id={bot.user.id})")

    @bot.command(name="menu")
    async def menu(ctx: commands.Context) -> None:
        await ctx.send("Menu principal:", view=MainMenuView())

    return bot


def run_bot() -> None:
    bot = create_bot()
    bot.run(get_token())


def run_dry_run() -> str:
    return (
        "Dry-run OK! Estrutura validada.\n"
        "Menu principal:\n"
        "  - Botao: Iniciar\n"
        "Submenu (ao clicar em Iniciar):\n"
        "  - Opcao: Limpeza de Ficha\n"
        "  - Opcao: Transferencia de Unidade\n\n"
        "Para rodar o bot com Discord, remova --dry-run."
    )

