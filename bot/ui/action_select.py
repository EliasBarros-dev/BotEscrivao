import discord

from bot.flows.actions import handle_limpeza_ficha, handle_transferencia_unidade


class ActionSelect(discord.ui.Select):
    def __init__(self) -> None:
        options = [
            discord.SelectOption(
                label="Limpeza de Ficha",
                value="limpeza_ficha",
                description="Inicia o fluxo de limpeza de ficha.",
            ),
            discord.SelectOption(
                label="Transferencia de Unidade",
                value="transferencia_unidade",
                description="Inicia o fluxo de transferencia de unidade.",
            ),
        ]

        super().__init__(
            placeholder="Escolha uma opcao...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        selected = self.values[0]

        if selected == "limpeza_ficha":
            await handle_limpeza_ficha(interaction)
            return

        if selected == "transferencia_unidade":
            await handle_transferencia_unidade(interaction)
            return

        await interaction.response.send_message("Opcao invalida.", ephemeral=True)


class ActionSelectView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(ActionSelect())

