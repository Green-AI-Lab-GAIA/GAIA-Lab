#!/usr/bin/env python3
"""Gera a galeria da página Sobre a partir da pasta about/images/galeria.

Qualquer imagem colocada nessa pasta entra na galeria no próximo build, em
ordem alfabética de nome de arquivo. As legendas (pt e en) vêm do arquivo
legendas.txt na mesma pasta; fotos sem legenda usam o nome do arquivo.
Executado pelo scripts/build.sh antes do Quarto; gera um fragmento de
miniaturas por idioma (about/_galeria.pt.qmd e about/_galeria.en.qmd).
"""

import html
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # sem Pillow o build continua, só publica as fotos originais
    Image = None

PASTA = Path("about/images/galeria")
LEGENDAS = PASTA / "legendas.txt"
EXTENSOES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".avif"}

# As fotos originais são pesadas e a galeria carrega todas de uma vez: a versão
# leve de cada uma vai para galeria/web/, e essa pasta fica fora da varredura
# porque o nome dela não tem extensão de imagem.
WEB = PASTA / "web"
LARGURA_MAXIMA = 1600
QUALIDADE = 78


def caminho_da_miniatura(arquivo):
    """Caminho relativo usado no src, em WebP quando dá para converter."""
    if Image is None or arquivo.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
        return f"images/galeria/{arquivo.name}"
    WEB.mkdir(parents=True, exist_ok=True)
    destino = WEB / f"{arquivo.stem}.webp"
    if not destino.exists() or destino.stat().st_mtime < arquivo.stat().st_mtime:
        with Image.open(arquivo) as imagem:
            imagem = imagem.convert("RGB")
            if imagem.width > LARGURA_MAXIMA:
                altura = round(imagem.height * LARGURA_MAXIMA / imagem.width)
                imagem = imagem.resize((LARGURA_MAXIMA, altura), Image.LANCZOS)
            imagem.save(destino, "WEBP", quality=QUALIDADE, method=6)
    return f"images/galeria/web/{destino.name}"

PASTA.mkdir(parents=True, exist_ok=True)


def ler_legendas():
    mapa = {}
    if not LEGENDAS.exists():
        return mapa
    for linha in LEGENDAS.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        partes = [p.strip() for p in linha.split("|")]
        if len(partes) >= 3:
            mapa[partes[0]] = (partes[1], partes[2])
    return mapa


legendas = ler_legendas()

for lang in ("pt", "en"):
    linhas = ["```{=html}"]
    for arquivo in sorted(PASTA.iterdir()):
        if arquivo.suffix.lower() not in EXTENSOES:
            continue
        padrao = arquivo.stem.replace("-", " ").replace("_", " ")
        par = legendas.get(arquivo.name, (padrao, padrao))
        legenda = html.escape(par[0] if lang == "pt" else par[1])
        linhas.append(
            f'<button class="gallery-thumb" type="button" data-caption="{legenda}">'
            f'<img src="{caminho_da_miniatura(arquivo)}" alt="{legenda}" loading="lazy">'
            f"</button>"
        )
    linhas.append("```")
    conteudo = "\n".join(linhas) + "\n"

    destino = Path(f"about/_galeria.{lang}.qmd")
    # só regrava quando o conteúdo muda, para não invalidar o cache do Quarto
    if not destino.exists() or destino.read_text(encoding="utf-8") != conteudo:
        destino.write_text(conteudo, encoding="utf-8")
