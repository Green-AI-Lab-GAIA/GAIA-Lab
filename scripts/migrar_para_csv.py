#!/usr/bin/env python3
"""Extrai o conteudo que ja existe no site para as tres tabelas em dados/.

Roda uma vez, para a migracao. Depois disso a fonte da verdade sao os CSV (que
vem das planilhas do Google Sheets) e este script nao e mais usado.

Uso:  python3 scripts/migrar_para_csv.py
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"

PESSOAS = ["slug", "grupo", "nome", "primeiro", "ultimo", "imagem", "cargo_pt", "cargo_en",
           "formacao_pt", "formacao_en", "linkedin", "email", "bio_pt", "bio_en",
           "formacao_detalhe_pt", "formacao_detalhe_en", "interesses_pt", "interesses_en"]

PUBLICACOES = ["slug", "data", "imagem", "titulo", "titulo_en", "autores", "veiculo",
               "local_pt", "local_en",
               "publicado_pt", "publicado_en", "resumo_pt", "resumo_en",
               "botao1_pt", "botao1_en", "botao1_url", "botao2_pt", "botao2_en", "botao2_url",
               "texto_pt", "texto_en"]

NOTICIAS = ["slug", "data", "imagem", "titulo_pt", "titulo_en", "fonte_pt", "fonte_en",
            "data_texto_pt", "data_texto_en", "url_pt", "url_en", "resumo_pt", "resumo_en"]


def front_e_corpo(texto: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", texto, re.S)
    if not m:
        raise ValueError("arquivo sem front matter")
    escalares = {}
    for linha in m.group(1).split("\n"):
        chave = re.match(r"^([a-zA-Z_][\w-]*):[ ]*(.*)$", linha)
        if chave and chave.group(2).strip():
            escalares[chave.group(1)] = chave.group(2).strip().strip('"')
    return escalares, m.group(2)


def links_do_about(fm_bruto: str) -> dict:
    """Devolve {'linkedin': url, 'email': url} a partir do bloco about.links."""
    achados = {}
    for m in re.finditer(r"-\s*icon:\s*(\S+)\s*\n\s*text:\s*.+?\n\s*href:\s*\"?([^\"\n]+)\"?", fm_bruto):
        icone, href = m.group(1), m.group(2).strip()
        if icone == "envelope":
            achados["email"] = href.replace("mailto:", "")
        else:
            achados[icone] = href
    return achados


def secoes_do_corpo(corpo: str) -> tuple[str, list[tuple[str, str]]]:
    """Devolve (bio, [(titulo da secao, conteudo)])."""
    dentro = re.search(r"::: \{#perfil\}\n(.*?)\n:::", corpo, re.S)
    bloco = dentro.group(1).strip() if dentro else ""
    partes = re.split(r"^## (.+)$", bloco, flags=re.M)
    bio = partes[0].strip()
    secoes = [(partes[i].strip(), partes[i + 1].strip()) for i in range(1, len(partes) - 1, 2)]
    return bio, secoes


def itens_de_lista(texto: str) -> str:
    """Converte '- a\\n- b' em 'a|b', que e como a planilha guarda listas."""
    itens = [re.sub(r"^-\s*", "", l).strip() for l in texto.split("\n") if l.strip().startswith("-")]
    return "|".join(itens)


def migrar_pessoas() -> list[dict]:
    linhas = {}
    pastas = sorted(p for p in (RAIZ / "people").iterdir() if p.is_dir())
    for pasta in pastas:
        for lang in ("pt", "en"):
            arq = pasta / f"{pasta.name}.{lang}.qmd"
            if not arq.exists():
                continue
            bruto = arq.read_text(encoding="utf-8")
            fm, corpo = front_e_corpo(bruto)
            bio, secoes = secoes_do_corpo(corpo)
            formacao = itens_de_lista(secoes[0][1]) if secoes else ""
            interesses = secoes[1][1] if len(secoes) > 1 else ""
            registo = linhas.setdefault(pasta.name, {"slug": pasta.name})
            registo["grupo"] = fm.get("people_group", "")
            registo["nome"] = fm.get("title", "")
            registo["primeiro"] = fm.get("first", "")
            registo["ultimo"] = fm.get("last", "")
            registo["imagem"] = fm.get("image", "")
            registo[f"cargo_{lang}"] = fm.get("subtitle", "")
            registo[f"formacao_{lang}"] = fm.get("education", "")
            registo[f"bio_{lang}"] = bio
            registo[f"formacao_detalhe_{lang}"] = formacao
            registo[f"interesses_{lang}"] = interesses
            if lang == "pt":
                registo.update({k: v for k, v in links_do_about(bruto).items()
                                if k in ("linkedin", "email")})
    return [{c: r.get(c, "") for c in PESSOAS} for r in linhas.values()]


def migrar_publicacoes() -> list[dict]:
    linhas = {}
    for pasta in sorted(p for p in (RAIZ / "publications").iterdir() if p.is_dir()):
        for lang in ("pt", "en"):
            arq = pasta / f"{pasta.name}.{lang}.qmd"
            if not arq.exists():
                continue
            bruto = arq.read_text(encoding="utf-8")
            fm, corpo = front_e_corpo(bruto)
            registo = linhas.setdefault(pasta.name, {"slug": pasta.name})
            registo["data"] = fm.get("date", "")
            registo["imagem"] = fm.get("image", "")
            registo["autores"] = fm.get("paper-authors", "")
            registo["veiculo"] = fm.get("venue", "")
            registo["titulo" if lang == "pt" else "titulo_en"] = fm.get("title", "")
            registo[f"publicado_{lang}"] = fm.get("pub-date", "")
            registo[f"resumo_{lang}"] = fm.get("snippet", "")
            meta = re.search(r"\{\.pub-detail-meta\}\n(.*?)\n:::", corpo, re.S)
            if meta:
                for m in re.finditer(r"\[(.+?)\]\((.+?)\)\{\.pub-btn\}", meta.group(1)):
                    rotulo, url = m.group(1).strip(), m.group(2).strip()
                    papel = "botao1" if not registo.get(f"botao1_{lang}") else "botao2"
                    registo[f"{papel}_{lang}"] = rotulo
                    registo[f"{papel}_url"] = url
                publicado = re.search(r"\*\*(?:Publicação|Publication|Published):\*\*\s*(.+?)(?:\n|$)",
                                      meta.group(1))
                if publicado:
                    # o complemento do veiculo e localizado: v./n./p. em pt, vol./no./pp. em en
                    partes = publicado.group(1).split("—", 1)
                    registo[f"local_{lang}"] = partes[1].strip() if len(partes) > 1 else ""
            # O texto longo vai para a celula com as quebras de linha: e o que
            # separa paragrafo de titulo, de figura e de bloco de citacao. Colapsar
            # isso em uma linha transforma secao em texto solto na pagina.
            texto = re.search(r"^## (?:Resumo|Abstract)\n\n(.*?)\n```\{=html\}", corpo, re.S | re.M)
            if texto:
                registo[f"texto_{lang}"] = texto.group(1).rstrip()
    return [{c: r.get(c, "") for c in PUBLICACOES} for r in linhas.values()]


def migrar_noticias() -> list[dict]:
    linhas = {}
    for lang in ("pt", "en"):
        arq = RAIZ / "publications" / f"index.{lang}.qmd"
        linhas[lang] = arq.read_text(encoding="utf-8")
    itens = {}
    for lang, texto in linhas.items():
        bloco = texto[texto.index("  - id: news"):]
        for m in re.finditer(
            r'- title:\s*"(.*?)"\s*\n\s*path:\s*"?(.*?)"?\s*\n\s*date:\s*([\d-]+)\s*\n'
            r'\s*news-source:\s*"?(.*?)"?\s*\n\s*news-date:\s*"?(.*?)"?\s*\n'
            r'\s*image:\s*"?(.*?)"?\s*\n\s*summary:\s*"(.*?)"\s*$',
            bloco, re.S | re.M,
        ):
            titulo, url, data, fonte, data_texto, imagem, resumo = (g.strip() for g in m.groups())
            # a mesma noticia tem URL e fonte diferentes em pt e em en, entao a
            # chave que junta os dois idiomas e a data
            registo = itens.setdefault(data, {"slug": "", "data": data, "imagem": imagem})
            registo[f"titulo_{lang}"] = re.sub(r"\s*\n\s*", " ", titulo)
            registo[f"resumo_{lang}"] = re.sub(r"\s*\n\s*", " ", resumo)
            registo[f"fonte_{lang}"] = fonte
            registo[f"data_texto_{lang}"] = data_texto
            registo[f"url_{lang}"] = url
            if lang == "pt":
                registo["slug"] = _slug(titulo)
    return [{c: r.get(c, "") for c in NOTICIAS} for r in itens.values()]


def _slug(titulo: str) -> str:
    import unicodedata
    base = unicodedata.normalize("NFKD", titulo.lower())
    base = "".join(c for c in base if not unicodedata.combining(c))
    base = re.sub(r"[^a-z0-9\s-]", "", base)
    palavras, tamanho = [], 0
    for palavra in re.sub(r"[\s_-]+", "-", base).strip("-").split("-"):
        if tamanho + len(palavra) > 40:
            break
        palavras.append(palavra)
        tamanho += len(palavra) + 1
    return "-".join(palavras) or "noticia"


def escrever(nome: str, colunas: list[str], linhas: list[dict]) -> None:
    DADOS.mkdir(exist_ok=True)
    destino = DADOS / nome
    with destino.open("w", encoding="utf-8", newline="") as fh:
        escritor = csv.DictWriter(fh, fieldnames=colunas, extrasaction="ignore")
        escritor.writeheader()
        escritor.writerows(linhas)
    print(f"{destino.relative_to(RAIZ)}: {len(linhas)} linhas, {len(colunas)} colunas")


if __name__ == "__main__":
    escrever("pessoas.csv", PESSOAS, migrar_pessoas())
    escrever("publicacoes.csv", PUBLICACOES, migrar_publicacoes())
    escrever("noticias.csv", NOTICIAS, migrar_noticias())
