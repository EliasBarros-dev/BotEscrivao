from discord import Interaction


async def handle_limpeza_ficha(interaction: Interaction) -> None:
    await interaction.response.send_message(
        "Fluxo **Limpeza de Ficha** iniciado. (placeholder)",
        ephemeral=True,
    )


async def handle_transferencia_unidade(interaction: Interaction) -> None:
    await interaction.response.send_message(
        "Fluxo **Transferencia de Unidade** iniciado. (placeholder)",
        ephemeral=True,
    )

