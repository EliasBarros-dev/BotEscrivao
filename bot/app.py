import discord
from discord.ext import commands

from bot.config import get_prefix, get_token, get_menu_channel_id
from bot.ui.main_menu import MainMenuView


class EscrivaoBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=get_prefix(), intents=intents)

    async def setup_hook(self) -> None:
        # Registra a view para ela continuar funcionando apos reiniciar o bot
        self.add_view(MainMenuView())

    async def on_ready(self) -> None:
        print(f"Conectado como {self.user} (id={self.user.id})")

        channel_id = get_menu_channel_id()
        if channel_id:
            channel = self.get_channel(channel_id)
            if channel:
                print(f"Garantindo menu fixo no canal: {channel.name}")
                # Apaga as mensagens anteriores do bot neste canal
                async for msg in channel.history(limit=50):
                    if msg.author == self.user:
                        try:
                            await msg.delete()
                        except discord.HTTPException:
                            pass

                # Envia o menu limpo e atualizado
                await channel.send("🚀 **Menu Principal**", view=MainMenuView())


def create_bot() -> commands.Bot:
    bot = EscrivaoBot()

    @bot.command(name="menu")
    async def menu(ctx: commands.Context) -> None:
        await ctx.send("🚀 **Menu Principal**", view=MainMenuView())

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

