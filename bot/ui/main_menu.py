import discord

from bot.ui.action_select import ActionSelectView


class StartButton(discord.ui.Button):
    def __init__(self) -> None:
        # custom_id obrigatorio para Views persistentes
        super().__init__(label="Iniciar", style=discord.ButtonStyle.success, custom_id="persistent_start_button")

    async def callback(self, interaction: discord.Interaction) -> None:
        # ephemeral=True garante que as proximas opcoes so aparecam para quem clicou!
        await interaction.response.send_message(
            content="Selecione uma opcao:",
            view=ActionSelectView(),
            ephemeral=True
        )


class MainMenuView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(StartButton())

