import discord
import asyncio

from bot.ui.action_select import ActionSelectView
from bot.config import get_menu_channel_id

class StartButton(discord.ui.Button):
    def __init__(self) -> None:
        # custom_id obrigatorio para Views persistentes
        super().__init__(label="Iniciar", style=discord.ButtonStyle.success, custom_id="persistent_start_button")

    async def _clean_fixed_channel(self, interaction: discord.Interaction, keep_message_id: int | None = None) -> None:
        """
        Remove mensagens do bot no canal do menu (obtido via config),
        preservando a mensagem cujo id for `keep_message_id` (a mensagem do menu).
        """
        try:
            channel_id = get_menu_channel_id()
            if not channel_id:
                return
            channel = interaction.client.get_channel(channel_id)
            if channel is None:
                return

            # Percorre histórico e apaga mensagens do bot (exceto a do menu)
            async for msg in channel.history(limit=200):
                # apaga apenas as mensagens do próprio bot
                if msg.author == interaction.client.user:
                    if keep_message_id and msg.id == keep_message_id:
                        continue
                    try:
                        await msg.delete()
                    except Exception:
                        # ignore failures (perms, race conditions)
                        pass
        except Exception:
            # proteger contra qualquer exceção para não quebrar a interação
            return

    async def callback(self, interaction: discord.Interaction) -> None:
        # ephemeral=True garante que as proximas opcoes so aparecam para quem clicou!
        await interaction.response.send_message(
            content="Selecione uma opcao:",
            view=ActionSelectView(),
            ephemeral=True
        )

        # Pequeno atraso para que outras callbacks que postem no canal o façam antes da limpeza
        await asyncio.sleep(0.5)

        # Ao clicar o `interaction.message` é a própria mensagem do menu (onde o botão está).
        # Vamos limpar outras mensagens do bot no canal do menu, preservando essa.
        keep_id = None
        try:
            keep_id = interaction.message.id
        except Exception:
            keep_id = None

        await self._clean_fixed_channel(interaction, keep_message_id=keep_id)


class MainMenuView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(StartButton())