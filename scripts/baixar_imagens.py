#!/usr/bin/env python3
"""Baixa para o repositorio as imagens que o formulario guardou no Google Drive.

O formulario de upload grava na celula o endereco do arquivo no Drive. Este script
pega esse endereco, baixa o arquivo e salva na pasta do item, com o nome que o site
espera (people/<pessoa>/avatar.jpg, publications/<artigo>/miniatura.png,
news/<noticia>/imagem.jpg). Quem escreveu a planilha nao precisa saber nome de
arquivo nem caminho.

Para o download funcionar sem senha, a pasta de respostas precisa estar
compartilhada como "qualquer pessoa com o link". Se nao estiver, o Google devolve
a pagina de login em vez da imagem, e o script para com essa explicacao em vez de
gravar a pagina de login no lugar da foto.

O que ja foi baixado fica anotado em dados/imagens.json, entao a rodada seguinte
nao baixa de novo.

Uso:  python3 scripts/baixar_imagens.py [--seco]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

from tabelas import ErroDeConteudo, eh_endereco, ler_tabela

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"
REGISTRO = DADOS / "imagens.json"

# onde cada imagem de cada tabela mora, e com que nome
DESTINOS = {
    "pessoas": [("people", "avatar", "foto")],
    "publicacoes": [("publications", "miniatura", "imagem"),
                    ("publications", "figura1", "figura1"),
                    ("publications", "figura2", "figura2")],
    "noticias": [("news", "imagem", "imagem")],
}

EXTENSAO = {
    "image/jpeg": ".jpg", "image/jpg": ".jpg", "image/png": ".png",
    "image/webp": ".webp", "image/gif": ".gif", "image/svg+xml": ".svg",
    "image/avif": ".avif", "image/tiff": ".tiff", "image/bmp": ".bmp",
}

ENDERECO_DRIVE = re.compile(r"drive\.google\.com|docs\.google\.com", re.I)
ID_DRIVE = re.compile(r"(?:[?&]id=|/d/)([A-Za-z0-9_-]{10,})")


class ErroDeImagem(Exception):
    """Falha ao trazer uma imagem, dizendo qual item e o que houve."""


def aviso(texto: str) -> None:
    print(texto, file=sys.stderr)


def endereco_de_download(url: str, item: str) -> str:
    """No Drive, o endereco da celula e uma pagina de visualizacao. O arquivo em si
    sai pelo uc?export=download. Fora do Drive, o proprio endereco serve."""
    if not ENDERECO_DRIVE.search(url):
        return url
    achado = ID_DRIVE.search(url)
    if not achado:
        raise ErroDeImagem(f"{item}: nao achei o identificador do arquivo em {url}")
    return f"https://drive.google.com/uc?export=download&id={achado.group(1)}"


def extensao(tipo: str, dados: bytes) -> str:
    """Extensao pelo que o servidor disse e, se ele nao disse, pelo conteudo."""
    tipo = (tipo or "").split(";")[0].strip().lower()
    if tipo in EXTENSAO:
        return EXTENSAO[tipo]
    if dados[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if dados[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if dados[:4] == b"RIFF" and dados[8:12] == b"WEBP":
        return ".webp"
    if dados[:4] in (b"GIF8",):
        return ".gif"
    if dados.lstrip()[:4] == b"<svg":
        return ".svg"
    raise ErroDeImagem(f"o que chegou nao parece imagem (tipo {tipo or 'desconhecido'})")


def baixar(url: str, item: str) -> tuple[bytes, str]:
    pedido = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; gaia-lab-sincronizador)"})
    try:
        with urllib.request.urlopen(pedido, timeout=120) as resposta:
            dados = resposta.read()
            tipo = resposta.headers.get("Content-Type", "")
    except urllib.error.HTTPError as erro:
        raise ErroDeImagem(f"{item}: o servidor respondeu {erro.code}") from erro
    except urllib.error.URLError as erro:
        raise ErroDeImagem(f"{item}: nao consegui alcancar o endereco ({erro.reason})") from erro
    if dados.lstrip()[:1] == b"<" or "text/html" in tipo:
        raise ErroDeImagem(
            f"{item}: o Drive devolveu uma pagina em vez da imagem, sinal de que o "
            "arquivo nao esta publico. Compartilhe a pasta de respostas do formulario "
            "como 'qualquer pessoa com o link'.")
    return dados, tipo


def ler_registro() -> dict:
    if REGISTRO.exists():
        return json.loads(REGISTRO.read_text(encoding="utf-8"))
    return {}


def gravar_registro(registro: dict) -> None:
    REGISTRO.write_text(json.dumps(registro, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                        encoding="utf-8")


def versionados(registro: dict, prefixo: str) -> list[str]:
    return [p for p in registro if p.startswith(prefixo + ".")]


def baixar_tabela(tabela: str, seco: bool, registro: dict) -> tuple[int, int, bool]:
    """Devolve (baixadas, puladas, registro_mudou)."""
    linhas = ler_tabela(tabela, DADOS / f"{tabela}.csv")
    baixadas = puladas = 0
    mudou = False
    for linha in linhas:
        for pasta, base, coluna in DESTINOS[tabela]:
            valor = (linha.get(coluna) or "").strip()
            if not valor:
                continue
            prefixo = f"{pasta}/{linha['slug']}/{base}"
            item = f"{tabela}/{linha['slug']}/{base}"
            if not eh_endereco(valor):
                if not (RAIZ / f"{prefixo}{Path(valor).suffix}").exists() and \
                        not list((RAIZ / f"{pasta}/{linha['slug']}").glob(f"{base}.*")):
                    aviso(f"aviso: {item}: a planilha cita {valor!r} e o arquivo nao esta na pasta")
                continue
            antigos = versionados(registro, prefixo)
            if antigos and registro[antigos[0]]["url"] == valor and (RAIZ / antigos[0]).exists():
                puladas += 1
                continue
            if seco:
                aviso(f"{item}: baixaria {valor}")
                baixadas += 1
                continue
            dados, tipo = baixar(endereco_de_download(valor, item), item)
            sufixo = extensao(tipo, dados)
            destino = RAIZ / f"{prefixo}{sufixo}"
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(dados)
            for antigo in antigos:
                if antigo != f"{prefixo}{sufixo}" and (RAIZ / antigo).exists():
                    (RAIZ / antigo).unlink()
                    registro.pop(antigo, None)
            registro[f"{prefixo}{sufixo}"] = {"url": valor, "bytes": len(dados)}
            mudou = True
            baixadas += 1
            aviso(f"{item}: {len(dados) // 1024} KB em {pasta}/{linha['slug']}/{base}{sufixo}")
    return baixadas, puladas, mudou


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seco", action="store_true", help="so mostra o que faria")
    ap.add_argument("--tabela", choices=sorted(DESTINOS), default=None)
    args = ap.parse_args()

    registro = ler_registro()
    tabelas = [args.tabela] if args.tabela else sorted(DESTINOS)
    total_baixadas = total_puladas = 0
    mudou = False
    try:
        for tabela in tabelas:
            baixadas, puladas, mexeu = baixar_tabela(tabela, args.seco, registro)
            total_baixadas += baixadas
            total_puladas += puladas
            mudou = mudou or mexeu
    except (ErroDeConteudo, ErroDeImagem) as erro:
        aviso(f"erro: {erro}")
        return 1

    if mudou and not args.seco:
        gravar_registro(registro)
    print(f"imagens: {total_baixadas} baixadas, {total_puladas} ja estavam")
    return 0


if __name__ == "__main__":
    sys.exit(main())
