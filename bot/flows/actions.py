import os
import json
import discord
from discord import Interaction
from discord.ui import Modal, TextInput, View, Select

from image_generator import ImageTemplateRenderer

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
        await interaction.response.defer(ephemeral=False, thinking=True)

        # Junta todos os crimes separados por virgula/ponto
        crimes_texto = "; ".join(self.crimes_selecionados) if self.crimes_selecionados else "Nenhum crime selecionado."

        dados = {
            "Nome completo": self.nome.value,
            "passaporte": self.passaporte.value,
            "motivo da limpeza": self.motivo.value,
            "crimes cometidos": crimes_texto,
            "Quantidade de Prisoes Anteriores": self.prisoes.value
        }

        MEU_LAYOUT = {
            "Nome completo": {"box": (205, 310, 647, 327), "size": 15, "color": "black", "valign": "center", "halign": "left"},
            "passaporte": {"box": (171, 333, 295, 345), "size": 15, "color": "black", "valign": "center", "halign": "left"},
            "motivo da limpeza": {"box": (83, 370, 615, 410), "size": 15, "color": "black", "valign": "top", "halign": "left"},
            "crimes cometidos": {"box": (85, 440, 632, 465), "size": 15, "color": "black", "valign": "top", "halign": "left"},
            "Quantidade de Prisoes Anteriores": {"box": (327, 475, 381, 485), "size": 15, "color": "black", "valign": "center", "halign": "left"}
        }

        template_path = "img/base.png"
        if not os.path.exists(template_path):
            os.makedirs("img", exist_ok=True)
            from PIL import Image, ImageDraw, ImageFont
            blank = Image.new("RGBA", (800, 600), (240, 240, 240, 255))
            d = ImageDraw.Draw(blank)
            d.text((300, 20), "TEMPLATE BASE AUTOMATICO", fill="black", font=ImageFont.load_default())
            blank.save(template_path)

        renderer = ImageTemplateRenderer(template_path, debug=False)
        output_file = f"resultado_{interaction.user.id}.png"
        renderer.render(output_file, dados, MEU_LAYOUT)

        arquivo_discord = discord.File(output_file, filename="ficha.png")
        await interaction.followup.send(
            content=f"Ficha de **{self.nome.value}** gerada com sucesso!",
            file=arquivo_discord
        )

        if os.path.exists(output_file):
            os.remove(output_file)

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


async def handle_limpeza_ficha(interaction: Interaction) -> None:
    artigos = carregar_artigos()
    if not artigos:
        await interaction.response.send_message("Arquivo artigos.json ausente ou invalido.", ephemeral=True)
        return

    # Mostra a view com os Selects de Crimes antes do Modal
    view = CrimeSelectView(artigos)
    await interaction.response.send_message(
        "Selecione todos os crimes correspondentes ao individuo (pode escolher em varias listas se precisar):",
        view=view,
        ephemeral=True
    )


async def handle_transferencia_unidade(interaction: Interaction) -> None:
    await interaction.response.send_message(
        "Fluxo **Transferencia de Unidade** iniciado. (placeholder)",
        ephemeral=True,
    )

