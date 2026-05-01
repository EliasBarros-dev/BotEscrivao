import os
from PIL import Image, ImageDraw, ImageFont

class ImageTemplateRenderer:
    def __init__(self, template_path: str, debug: bool = False):
        """
        Inicializa o renderizador de imagens.

        :param template_path: Caminho para a imagem base (ex: 'img/base.png').
        :param debug: Se True, desenha os retangulos das caixas de texto para facilitar o layout.
        """
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template nao encontrado: {template_path}")

        self.template_path = template_path
        self.debug = debug

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
        """Quebra texto respeitando largura e quebras de linha (\n)."""

        final_lines = []

        # separa por ENTER (parágrafos)
        paragraphs = text.split("\n")

        for paragraph in paragraphs:
            words = paragraph.split(" ")
            current_line = []

            for word in words:
                test_line = " ".join(current_line + [word])
                line_w = int(font.getlength(test_line))

                if line_w <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        final_lines.append(" ".join(current_line))
                    current_line = [word]

            if current_line:
                final_lines.append(" ".join(current_line))

            # adiciona linha vazia entre parágrafos
            final_lines.append("")

        # remove última linha vazia extra
        if final_lines and final_lines[-1] == "":
            final_lines.pop()

        return final_lines

    def _draw_centered_text(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        box: tuple[int, int, int, int],
        font: ImageFont.FreeTypeFont,
        color: str | tuple,
        valign: str = "center",
        halign: str = "center",
        line_spacing: int = 4
    ) -> None:
        """Desenha o texto alinhado horizontalmente e verticalmente dentro de uma caixa."""
        x1, y1, x2, y2 = box
        box_width = x2 - x1
        box_height = y2 - y1

        # Quebra de linha automatica (Word Wrap)
        lines = self._wrap_text(text, font, box_width)

        # Usando as caixas de contorno da fonte para determinar as alturas (ascent/descent evitam cortes)
        ascent, descent = font.getmetrics()
        line_height = ascent + descent

        total_text_height = (len(lines) * line_height) + ((len(lines) - 1) * line_spacing)

        # Alinhamento vertical (valign)
        if valign == "center":
            current_y = y1 + (box_height - total_text_height) // 2
        elif valign == "bottom":
            current_y = y2 - total_text_height
        else: # top
            current_y = y1

        # Desenhar cada linha
        for line in lines:
            line_width = int(font.getlength(line))

            # Alinhamento horizontal (halign)
            if halign == "left":
                current_x = x1
            elif halign == "right":
                current_x = x2 - line_width
            else: # center padrao
                current_x = x1 + (box_width - line_width) // 2

            draw.text((current_x, current_y), line, font=font, fill=color)
            current_y += line_height + line_spacing

    def render(self, output_path: str, data: dict, layout: dict) -> None:
        """
        Gera a imagem final de acordo com o layour e os dados.

        :param output_path: Caminho para savar o resultado.
        :param data: Dicionario com os textos dinamicos. ex: {"nome": "Fulaninho"}
        :param layout: Dicionario com as configuracoes de posicao, fontes e cores.
        """
        # Abrir imagem e converter para suporte RGBA se necessario
        base_img = Image.open(self.template_path).convert("RGBA")
        draw = ImageDraw.Draw(base_img)

        for key, config in layout.items():
            if key not in data:
                continue

            text = str(data[key])
            box = config.get("box")  # tuple (x1, y1, x2, y2)
            color = config.get("color", "black")
            font_path = config.get("font_path", "arial.ttf")
            font_size = config.get("size", 20)
            valign = config.get("valign", "center")
            halign = config.get("halign", "center")

            # Carregar a fonte. Se nao achar o arquivo, carrega a padrao (sem suporte a mudanca de tamanho ideal)
            try:
                font = ImageFont.truetype(font_path, font_size)
            except Exception:
                print(f"[Aviso] Fonte customizada '{font_path}' nao encontrada. Usando fonte padrao do sistema.")
                font = ImageFont.load_default()

            if self.debug and box:
                # Desenhar um retangulo vermelho ao redor da caixa de texto para ajudar no alinhamento
                draw.rectangle(box, outline="red", width=2)

            if box:
                self._draw_centered_text(draw, text, box, font, color, valign=valign, halign=halign)
            else:
                # Caso o usuario mande apenas 'pos' (x, y) fixo em vez de caixa limitadora
                pos = config.get("pos", (0, 0))
                draw.text(pos, text, font=font, fill=color)

        # Salva o arquivo em RGB se for .jpg, ou com canal Alpha se for .png
        if output_path.lower().endswith(".jpg"):
            base_img = base_img.convert("RGB")
        base_img.save(output_path)
        print(f"Imagem gerada com sucesso e salva em '{output_path}'!")


# =========================================================
# EXEMPLO COMPLETO DE USO
# =========================================================
if __name__ == "__main__":
    # Criar uma imagem 'base.png' em branco apenas para este exemplo funcionar se o user nao tiver um.
    if not os.path.exists("img/base.png"):
        print("Criando um template base dinamico (img/base.png) para teste...")
        blank_template = Image.new("RGBA", (800, 600), (240, 240, 240, 255))
        blank_draw = ImageDraw.Draw(blank_template)
        blank_draw.text((300, 20), "FICHA POLICIAL TEMPLATE", fill="black", font=ImageFont.load_default())
        blank_template.save("img/base.png")

    # 1. Instanciamos a classe de renderizacao apontando pro background base
    # Troque debug=True para ver os limites onde os textos e imagens irao se alinhar
    renderer = ImageTemplateRenderer("img/base.png", debug=True)

    # 2. Fonte padrao para testes (no Windows arialttf eh comum, em Linux seria /usr/share/fonts...)
    # Use caminhos relativos na sua aplicacao real: "fonts/SuaFonte.ttf"
    font_arial = "arial.ttf"

    # 3. Mapeamento do Layout (Box = (Esquerda, Cima, Direita, Baixo))
    MEU_LAYOUT = {
        "Nome completo": {
            "box": (50, 100, 380, 150),
            "font_path": font_arial,
            "size": 28,
            "color": (20, 20, 20),
            "valign": "center"
        },
        "passaporte": {
            "box": (420, 100, 750, 150),
            "font_path": font_arial,
            "size": 24,
            "color": "darkblue",
            "valign": "center"
        },
        "motivo da limpeza": {
            "box": (50, 200, 750, 300),
            "font_path": font_arial,
            "size": 20,
            "color": "black",
            "valign": "top"
        },
        "crimes cometidos": {
            "box": (50, 330, 750, 430),
            "font_path": font_arial,
            "size": 18,
            "color": "darkred",
            "valign": "top"
        },
        "Quantidade de Prisoes Anteriores": {
            "box": (300, 480, 500, 550),
            "font_path": font_arial,
            "size": 36,
            "color": "purple",
            "valign": "center"
        }
    }

    # 4. Dados de Teste dinamicos oriundos do Bot/Usuario
    dados_dinamicos = {
        "Nome completo": "Elias Barros",
        "passaporte": "ID-987654321",
        "motivo da limpeza": "O individuo apresentou bom comportamento durante os servicos comunitarios e solicitou encerramento dos registros menores para emissao de CNH.",
        "crimes cometidos": "Desacato leve a autoridade; Conducao de veiculo sem licenciamento; Invasao de propriedade (Nivel 1).",
        "Quantidade de Prisoes Anteriores": "03"
    }

    # 5. Renderizando e salvando
    saida = "resultado.png"
    renderer.render(saida, dados_dinamicos, MEU_LAYOUT)


