import os
import json
import discord
import io
import asyncio
import random
import string
from discord import Interaction, PermissionOverwrite
from discord.ui import Modal, TextInput, View, Select
from image_generator import ImageTemplateRenderer

scheduled_deletes: dict[int, asyncio.Task] = {}

def carregar_artigos():
    try:
        with open("artigos.json", "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception:
        return []

class LimpezaFichaModal(Modal, title='Formulario: Limpeza de Ficha'):
    nome = TextInput(
        label='Nome Completo',
        placeholder='Ex: Joao da Silva',
        required=True,
        max_length=100
    )
    passaporte = TextInput(
        label='Passaporte',
        placeholder='Ex: 12345',
        required=True,
        max_length=10
    )
    motivo = TextInput(
        label='Motivo da Limpeza',
        style=discord.TextStyle.paragraph,
        placeholder='Ex: Cumpriu servico comunitario...',
        required=True,
        max_length=130
    )
    prisoes = TextInput(
        label='Quant. de Prisoes Anteriores',
        placeholder='Ex: 2',
        required=True,
        max_length=10
    )

    def __init__(self, crimes_selecionados: list[str]):
        super().__init__()
        self.crimes_selecionados = crimes_selecionados

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        crimes_texto = "; ".join(self.crimes_selecionados) if self.crimes_selecionados else "Nenhum crime selecionado."

        dados = {
            "Nome completo": self.nome.value,
            "passaporte": self.passaporte.value,
            "motivo da limpeza": self.motivo.value,
            "crimes cometidos": crimes_texto,
            "Quantidade de Prisoes Anteriores": self.prisoes.value
        }

        # 👉 agora chama o segundo passo
        await interaction.followup.send(
            content="Agora informe os dados do responsável:",
            view=ContinuarView(dados),
            ephemeral=True
        )

class ContinuarView(View):
    def __init__(self, dados):
        super().__init__(timeout=120)
        self.dados = dados

    @discord.ui.button(label="Preencher Responsavel e Oficio", style=discord.ButtonStyle.success)
    async def abrir_modal(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ResponsavelOficioModal(self.dados))

class ResponsavelOficioModal(Modal, title='Dados do Responsavel'):
    responsavel = TextInput(
        label='Nome do Responsavel pela Limpeza',
        placeholder='Ex: Sgt. Oliveira',
        required=True,
        max_length=100
    )

    oficio = TextInput(
        label='Numero do Oficio',
        placeholder='Ex: 123/2025',
        required=True,
        max_length=50
    )

    def __init__(self, dados_base: dict):
        super().__init__()
        self.dados_base = dados_base

    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)

        # junta os dados
        self.dados_base["responsavel"] = self.responsavel.value
        self.dados_base["oficio"] = self.oficio.value

        MEU_LAYOUT = {
            "Nome completo": {"box": (205, 310, 647, 327), "size": 15, "color": "black", "valign": "center", "halign": "left"},
            "passaporte": {"box": (171, 333, 295, 345), "size": 15, "color": "black", "valign": "center", "halign": "left"},
            "motivo da limpeza": {"box": (83, 370, 615, 410), "size": 15, "color": "black", "valign": "top", "halign": "left"},
            "crimes cometidos": {"box": (85, 440, 632, 465), "size": 15, "color": "black", "valign": "top", "halign": "left"},
            "Quantidade de Prisoes Anteriores": {"box": (327, 510, 381, 518), "size": 15, "color": "black", "valign": "center", "halign": "left"},
            "responsavel": {"box": (86, 800, 649, 820), "size": 15, "color": "black", "halign": "center"},
            "oficio": {"box": (368, 80, 438, 87), "size": 15, "color": "black", "halign": "left"},
        }

        template_path = "img/base.png"
        renderer = ImageTemplateRenderer(template_path, debug=False)

        image_bytes = renderer.render_bytes(self.dados_base, MEU_LAYOUT, fmt="PNG")
        file_obj = io.BytesIO(image_bytes)
        file_obj.seek(0)
        discord_file = discord.File(file_obj, filename="ficha.png")

        channel = interaction.channel  # canal onde a modal foi invocada (deveria ser o canal temporário)
        delete_view = DeleteChannelView(channel, owner_id=interaction.user.id)

        # aqui respondemos com a imagem e adicionamos o botão ao mesmo tempo
        await interaction.followup.send(
            content="Ficha gerada com sucesso! Use o botão abaixo para encerrar este canal antes de 2 minutos, se desejar.",
            file=discord_file,
            view=delete_view
        )

        # agendar exclusão do canal em 120s (2 minutos) e armazenar a task para poder cancelar
        if channel is not None:
            task = asyncio.create_task(schedule_delete_channel(channel, delay_seconds=120))
            scheduled_deletes[channel.id] = task

class CrimeSelectView(View):
    def __init__(self, artigos: list):
        super().__init__(timeout=None)
        self.crimes_selecionados = {}

        # Como o Discord so permite 25 items por Select, dividimos em varios
        chunk_size = 25
        for i in range(0, len(artigos), chunk_size):
            chunk = artigos[i:i+chunk_size]

            options = []
            for art in chunk:
                # Cada item do Select vai usar o titulo.
                lbl = art.get("titulo", "Crime")[:100]
                # Modificado para usar o codigo em vez da descricao
                codigo = art.get("codigo", "")
                desc = f"Artigo {codigo}" if codigo else ""
                val = art.get("titulo", "Crime")[:100]
                options.append(discord.SelectOption(label=lbl, description=desc, value=val))

            select = Select(
                placeholder=f"Selecione os crimes (P. {(i//chunk_size)+1})",
                min_values=0,
                max_values=len(options),
                options=options
            )
            # Ao definir callback dinamicamente pegamos as chaves selecionadas
            select.callback = self.make_callback(select)
            self.add_item(select)

        # Botão para avancar pro formulario de texto
        continuar_btn = discord.ui.Button(label="Continuar e Preencher Formulario", style=discord.ButtonStyle.primary, row=4)
        continuar_btn.callback = self.continuar_callback
        self.add_item(continuar_btn)

    def make_callback(self, select):
        async def select_callback(interaction: Interaction):
            self.crimes_selecionados[select.placeholder] = select.values
            await interaction.response.defer(ephemeral=True)
        return select_callback

    async def continuar_callback(self, interaction: Interaction):
        # Achata a lista de listas que o usuario escolheu nos multiplos selects
        todos_crimes = []
        for lst in self.crimes_selecionados.values():
            todos_crimes.extend(lst)

        if not todos_crimes:
            await interaction.response.send_message("Voce previsa selecionar ao menos um crime!", ephemeral=True)
            return

        # Agora sim avanca pro Modal de texto passando os crimes escolhidos
        await interaction.response.send_modal(LimpezaFichaModal(todos_crimes))

class DeleteChannelView(View):
    def __init__(self, channel: discord.TextChannel, owner_id: int):
        super().__init__(timeout=None)
        self.channel = channel
        self.owner_id = owner_id

    @discord.ui.button(label="Fechar canal agora", style=discord.ButtonStyle.danger)
    async def close_now(self, interaction: Interaction, button: discord.ui.Button):
        author_id = interaction.user.id
        # Permitir se for dono do canal ou moderador com manage_channels
        if author_id != self.owner_id and not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("Apenas o dono do canal ou um moderador pode fechar o canal.", ephemeral=True)
            return

        # responder antes de deletar (ephemeral para não poluir o canal)
        await interaction.response.send_message("Fechando o canal...", ephemeral=True)

        # cancelar a task agendada, se houver
        task = scheduled_deletes.pop(self.channel.id, None)
        if task and not task.done():
            task.cancel()

        try:
            await self.channel.delete(reason=f"Canal fechado por {interaction.user}")
        except Exception as e:
            # se nao for possivel deletar, informe o usuário
            try:
                await interaction.followup.send(f"Erro ao deletar canal: {e}", ephemeral=True)
            except Exception:
                print(f"Erro ao notificar usuario sobre falha ao deletar canal: {e}")


async def handle_limpeza_ficha(interaction: Interaction) -> None:
    artigos = carregar_artigos()
    if not artigos:
        await interaction.response.send_message("Arquivo artigos.json ausente ou invalido.", ephemeral=True)
        return

    if interaction.guild is None:
        await interaction.response.send_message("Este comando precisa ser usado dentro de um servidor (não em DMs).", ephemeral=True)
        return

    # cria a view com os Selects de Crimes
    view = CrimeSelectView(artigos)

    # cria canal temporario privado
    try:
        canal = await create_temp_private_channel(interaction.guild, interaction.user, name_prefix="anon", duration=120)
    except Exception as e:
        await interaction.response.send_message(f"Falha ao criar canal temporario: {e}", ephemeral=True)
        return

    # informar ao usuário que o canal foi criado (ephemeral)
    await interaction.response.send_message(f"Canal temporário criado: {canal.mention} — ele será fechado em 2 minutos.", ephemeral=True)

    # enviar a mensagem com a view dentro do canal privado
    await canal.send(f"{interaction.user.mention} — aqui está seu canal temporário. Use os controles abaixo para gerar a ficha:", view=view)


async def handle_transferencia_unidade(interaction: Interaction) -> None:
    await interaction.response.send_message(
        "Fluxo **Transferencia de Unidade** iniciado. (placeholder)",
        ephemeral=True,
    )

async def create_temp_private_channel(guild: discord.Guild, user: discord.Member, *,
                                      name_prefix: str = "anon", duration: int = 120) -> discord.TextChannel:
    """
    Cria um canal de texto que apenas 'user' e o bot podem ver.
    Retorna o canal criado. O canal NÃO é excluído aqui — crie uma task para remover.
    """
    # gerar nome aleatorio para anonimato
    rand = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=6))
    channel_name = f"{name_prefix}-{rand}"

    # permissões: negar view a @everyone, permitir ao user e ao bot
    overwrites = {
        guild.default_role: PermissionOverwrite(view_channel=False),
        user: PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        guild.me: PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True)
    }

    # cria o canal no topo (ou especifique category)
    channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites, reason="Canal temporario anonimo")
    return channel

async def schedule_delete_channel(channel: discord.TextChannel, delay_seconds: int = 120):
    try:
        await asyncio.sleep(delay_seconds)
        await channel.delete(reason="Canal temporario expirado")
    except asyncio.CancelledError:
        # tarefa cancelada (usuário fechou manualmente)
        return
    except Exception as e:
        print(f"Erro ao deletar canal temporario {getattr(channel, 'id', 'unknown')}: {e}")
    finally:
        # garantir que, se existir, a referência da task seja removida do dicionário
        try:
            scheduled_deletes.pop(channel.id, None)
        except Exception:
            pass

