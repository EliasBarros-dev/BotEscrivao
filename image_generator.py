import os
import io
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

    def _wrap_text(self, text, font, max_width):
        lines = []

        for paragraph in text.split("\n"):
            words = paragraph.split(" ")
            current_line = ""

            for word in words:
                test_line = word if not current_line else current_line + " " + word
                width = font.getlength(test_line)

                if width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)

                    # 🔥 quebra palavra grande se necessário
                    while font.getlength(word) > max_width:
                        for i in range(len(word), 0, -1):
                            if font.getlength(word[:i]) <= max_width:
                                lines.append(word[:i])
                                word = word[i:]
                                break

                    current_line = word

            if current_line:
                lines.append(current_line)

            lines.append("")

        if lines and lines[-1] == "":
            lines.pop()

        return lines

    def _draw_centered_text(
        self,
        base_img: Image.Image,
        draw: ImageDraw.ImageDraw,
        text: str,
        box: tuple[int, int, int, int],
        font: ImageFont.FreeTypeFont,
        color: str | tuple,
        valign: str = "center",
        halign: str = "center",
        line_spacing: int = 4,
        style: dict | None = None
    ) -> None:
        """Desenha o texto alinhado dentro de uma caixa, com suporte a line_spacing e estilo simples (bold/italic emulação)."""
        x1, y1, x2, y2 = box
        box_width = x2 - x1
        box_height = y2 - y1

        lines = self._wrap_text(text, font, box_width)

        ascent, descent = font.getmetrics()
        line_height = ascent + descent

        total_text_height = (len(lines) * line_height) + ((len(lines) - 1) * line_spacing)

        if valign == "center":
            current_y = y1 + (box_height - total_text_height) // 2
        elif valign == "bottom":
            current_y = y2 - total_text_height
        else:
            current_y = y1

        # estilo
        bold = bool(style and style.get("bold"))
        italic = bool(style and style.get("italic"))
        # valor de cisalhamento para itálico (negativo inclina à esquerda; ajuste conforme desejado)
        shear = style.get("italic_shear", -0.25) if style else -0.25

        for line in lines:
            if line == "":
                current_y += line_height + line_spacing
                continue

            line_width = int(font.getlength(line))

            if halign == "left":
                current_x = x1
            elif halign == "right":
                current_x = x2 - line_width
            else:
                current_x = x1 + (box_width - line_width) // 2

            # Se não precisar de itálico customizado, desenha diretamente (com 'bold' emulação se pedido)
            if not italic:
                if bold:
                    # desenha duas vezes com offset para "engrossar" visualmente
                    draw.text((current_x, current_y), line, font=font, fill=color)
                    draw.text((current_x + 1, current_y), line, font=font, fill=color)
                else:
                    draw.text((current_x, current_y), line, font=font, fill=color)
            else:
                # emulação de itálico: desenha a linha em imagem temporária e aplica affine shear
                # cria imagem do tamanho da linha
                tmp_w = max(1, int(line_width + abs(shear) * (line_height)))
                tmp_h = line_height + 4
                tmp = Image.new("RGBA", (tmp_w, tmp_h), (0, 0, 0, 0))
                tmp_draw = ImageDraw.Draw(tmp)
                # desenha (com ou sem bold emulação)
                if bold:
                    tmp_draw.text((0, 0), line, font=font, fill=color)
                    tmp_draw.text((1, 0), line, font=font, fill=color)
                else:
                    tmp_draw.text((0, 0), line, font=font, fill=color)

                # aplica shear (affine). Matriz = (a, b, c, d, e, f) -> x' = a*x + b*y + c ; y' = d*x + e*y + f
                # usamos b = shear para inclinar horizontalmente
                try:
                    sheared = tmp.transform(
                        (tmp_w + int(abs(shear) * tmp_h) + 8, tmp_h),
                        Image.AFFINE,
                        (1, shear, 0, 0, 1, 0),
                        resample=Image.BICUBIC,
                    )
                except Exception:
                    # fallback se transform falhar
                    sheared = tmp

                # colar a imagem resultante em base_img
                base_img.paste(sheared, (int(current_x), int(current_y)), sheared)

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
                if box:
                    line_spacing = config.get("line_spacing", 4)
                    style_cfg = config.get("style", None)
                    self._draw_centered_text(base_img, draw, text, box, font, color,
                                             valign=valign, halign=halign,
                                             line_spacing=line_spacing, style=style_cfg)
            else:
                # Caso o usuario mande apenas 'pos' (x, y) fixo em vez de caixa limitadora
                pos = config.get("pos", (0, 0))
                draw.text(pos, text, font=font, fill=color)

        # Salva o arquivo em RGB se for .jpg, ou com canal Alpha se for .png
        if output_path.lower().endswith(".jpg"):
            base_img = base_img.convert("RGB")
        base_img.save(output_path)
        print(f"Imagem gerada com sucesso e salva em '{output_path}'!")

    def render_bytes(self, data: dict, layout: dict, fmt: str = "PNG") -> bytes:
        """
        Renderiza a imagem na memória e retorna os bytes (PNG por padrão).
        """
        # Reutiliza a lógica de abertura e desenho do método render:
        base_img = Image.open(self.template_path).convert("RGBA")
        draw = ImageDraw.Draw(base_img)

        for key, config in layout.items():
            if key not in data:
                continue

            text = str(data[key])
            box = config.get("box")
            color = config.get("color", "black")
            font_path = config.get("font_path", "arial.ttf")
            font_size = config.get("size", 20)
            valign = config.get("valign", "center")
            halign = config.get("halign", "center")

            try:
                font = ImageFont.truetype(font_path, font_size)
            except Exception:
                font = ImageFont.load_default()

            if self.debug and box:
                draw.rectangle(box, outline="red", width=2)

            if box:
                if box:
                    line_spacing = config.get("line_spacing", 4)
                    style_cfg = config.get("style", None)
                    self._draw_centered_text(base_img, draw, text, box, font, color,
                                             valign=valign, halign=halign,
                                             line_spacing=line_spacing, style=style_cfg)
            else:
                pos = config.get("pos", (0, 0))
                draw.text(pos, text, font=font, fill=color)

        # salvar em BytesIO e retornar bytes
        buffer = io.BytesIO()
        save_fmt = fmt.upper()
        if save_fmt == "JPG":
            rgb = base_img.convert("RGB")
            rgb.save(buffer, format="JPEG")
        else:
            base_img.save(buffer, format=save_fmt)
        buffer.seek(0)
        return buffer.read()


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


