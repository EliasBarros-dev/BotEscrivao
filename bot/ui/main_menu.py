import discord

from bot.ui.action_select import ActionSelectView


class StartButton(discord.ui.Button):
    def __init__(self) -> None:
        super().__init__(label="Iniciar", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(
            content="Selecione uma opcao:",
            view=ActionSelectView(),
        )


class MainMenuView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(StartButton())

