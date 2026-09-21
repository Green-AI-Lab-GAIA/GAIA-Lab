#!/usr/bin/env python3
"""Gera as paginas de pessoas, publicacoes e noticias a partir das tabelas em dados/.

As tabelas sao a fonte da verdade: elas vem das planilhas do Google Sheets pelo
scripts/sincronizar.sh. Toda pagina .pt.qmd e .en.qmd escrita aqui e arquivo
gerado, entao editar a pagina nao adianta, ela e sobrescrita na proxima rodada.

Uso:  python3 scripts/gerar_conteudo.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"

AVISO = ("# Arquivo gerado por scripts/gerar_conteudo.py a partir de {tabela}.\n"
         "# Nao edite aqui: edite a planilha e rode o script.")


class ErroDeConteudo(Exception):
    """Falha de validacao numa tabela, com a linha e a coluna do problema."""


# ----------------------------------------------------------------- utilidades

def ler(tabela: str, obrigatorias: list[str]) -> list[dict]:
    caminho = DADOS / tabela
    if not caminho.exists():
        raise ErroDeConteudo(f"{tabela} nao existe em dados/")
    with caminho.open(encoding="utf-8", newline="") as fh:
        linhas = [{k: (v or "").strip() for k, v in linha.items()}
                  for linha in csv.DictReader(fh)]
    vistas = set()
    for numero, linha in enumerate(linhas, start=2):
        for coluna in obrigatorias:
            if not linha.get(coluna):
                raise ErroDeConteudo(f"{tabela}, linha {numero}: coluna obrigatoria vazia: {coluna}")
        chave = linha["slug"]
        if chave in vistas:
            raise ErroDeConteudo(f"{tabela}, linha {numero}: slug repetido: {chave}")
        if not chave.replace("-", "").isalnum() or chave != chave.lower():
            raise ErroDeConteudo(f"{tabela}, linha {numero}: slug deve ser minusculo e sem espaco: {chave}")
        vistas.add(chave)
    return linhas


def aspas(valor: str) -> str:
    """Valor pronto para entrar como string YAML entre aspas duplas."""
    return '"' + valor.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").strip() + '"'


def itens(valor: str) -> list[str]:
    """Lista guardada na planilha como 'a|b|c'."""
    return [p.strip() for p in valor.split("|") if p.strip()]


def escrever(relativo: str, texto: str) -> None:
    destino = RAIZ / relativo
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto.rstrip() + "\n", encoding="utf-8")


def limpar_antigos(pasta: str, gerados: set[str]) -> list[str]:
    """Remove paginas de itens que sairam da planilha. Devolve o que apagou."""
    apagados = []
    raiz = RAIZ / pasta
    if not raiz.exists():
        return apagados
    for item in sorted(raiz.iterdir()):
        if item.is_dir() and item.name not in gerados:
            for arq in sorted(item.glob("*.qmd")):
                arq.unlink()
                apagados.append(str(arq.relative_to(RAIZ)))
            if not any(item.iterdir()):
                item.rmdir()
    return apagados


# --------------------------------------------------------------------- pessoas

PESSOAS_OBRIGATORIAS = ["slug", "grupo", "nome", "primeiro", "ultimo", "imagem",
                        "cargo_pt", "cargo_en", "formacao_pt", "formacao_en",
                        "bio_pt", "bio_en", "linkedin"]

GRUPOS = {"professor", "postdoc", "phd", "masters", "undergrad", "alumni"}

ROTULOS = {
    "pt": {"secao_formacao": "Formação", "secao_interesses": "Interesses", "voltar": "Voltar para a equipe"},
    "en": {"secao_formacao": "Education", "secao_interesses": "Interests", "voltar": "Back to the team"},
}


def pagina_de_pessoa(linha: dict, lang: str) -> str:
    r = ROTULOS[lang]
    formacao = "\n".join(f"- {item}" for item in itens(linha[f"formacao_detalhe_{lang}"]))
    interesses = linha[f"interesses_{lang}"].strip()
    links = [f'    - icon: linkedin\n      text: LinkedIn\n      href: "{linha["linkedin"]}"']
    if linha["email"]:
        links.append(f'    - icon: envelope\n      text: Email\n      href: "mailto:{linha["email"]}"')
    secoes = []
    if formacao:
        secoes.append(f"## {r['secao_formacao']}\n\n{formacao}")
    if interesses:
        secoes.append(f"## {r['secao_interesses']}\n\n{interesses}")
    corpo = "\n\n".join(secoes)
    return f"""---
title: {aspas(linha['nome'])}
last: {aspas(linha['ultimo'])}
first: {aspas(linha['primeiro'])}
people_group: {aspas(linha['grupo'])}
subtitle: {aspas(linha[f'cargo_{lang}'])}
education: {aspas(linha[f'formacao_{lang}'])}
image: {linha['imagem']}
page-layout: full
toc: false
about:
  id: perfil
  template: trestles
  image-shape: round
  image: {linha['imagem']}
  links:
{chr(10).join(links)}
---

```{{=html}}
<div class="page-shell">
<div class="page-main">
```

::: {{#perfil}}

{linha[f'bio_{lang}']}

{corpo}

:::

```{{=html}}
<a class="back-link" href="/people/">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M15 5l-7 7 7 7"/></svg>
  <span>{r['voltar']}</span>
</a>
```

```{{=html}}
</div>
</div>
```"""


def gerar_pessoas() -> None:
    linhas = ler("pessoas.csv", PESSOAS_OBRIGATORIAS)
    for linha in linhas:
        if linha["grupo"] not in GRUPOS:
            raise ErroDeConteudo(f"pessoas.csv, {linha['slug']}: grupo desconhecido: {linha['grupo']}")
        for lang in ("pt", "en"):
            escrever(f"people/{linha['slug']}/{linha['slug']}.{lang}.qmd", pagina_de_pessoa(linha, lang))
    apagados = limpar_antigos("people", {linha["slug"] for linha in linhas})
    print(f"people: {len(linhas)} pessoas, {len(linhas) * 2} paginas"
          + (f", {len(apagados)} paginas removidas" if apagados else ""))


# ----------------------------------------------------------------- publicacoes

PUBLICACOES_OBRIGATORIAS = ["slug", "data", "imagem", "titulo", "autores", "veiculo",
                            "publicado_pt", "publicado_en", "resumo_pt", "resumo_en",
                            "botao1_pt", "botao1_en", "botao1_url"]

ROTULOS_PUB = {
    "pt": {"autores": "Autores", "publicacao": "Publicação", "resumo": "Resumo",
           "voltar": "Voltar para as publicações"},
    "en": {"autores": "Authors", "publicacao": "Published", "resumo": "Abstract",
           "voltar": "Back to publications"},
}


def pagina_de_publicacao(linha: dict, lang: str) -> str:
    r = ROTULOS_PUB[lang]
    titulo = linha["titulo"] if lang == "pt" else (linha["titulo_en"] or linha["titulo"])
    local_veiculo = linha.get(f"local_{lang}", "")
    local = f" — {local_veiculo}" if local_veiculo else ""
    botoes = [f"[{linha[f'botao1_{lang}']}]({linha['botao1_url']}){{.pub-btn}}"]
    if linha.get("botao2_url"):
        botoes.append(f"[{linha[f'botao2_{lang}']}]({linha['botao2_url']}){{.pub-btn}}")
    texto = linha[f"texto_{lang}"] or linha[f"resumo_{lang}"]
    return f"""---
title: {aspas(titulo)}
paper-authors: {aspas(linha['autores'])}
venue: {aspas(linha['veiculo'])}
pub-date: {aspas(linha[f'publicado_{lang}'])}
date: {linha['data']}
image: {linha['imagem']}
snippet: {aspas(linha[f'resumo_{lang}'])}
page-layout: full
toc: false
---

```{{=html}}
<div class="page-shell">
<div class="page-main">
```

:::: {{.pub-detail}}

::: {{.pub-detail-thumb}}
[![]({linha['imagem']})]({linha['botao1_url']})
:::

::: {{.pub-detail-meta}}
**{r['autores']}:** {linha['autores']}

**{r['publicacao']}:** {linha[f'publicado_{lang}']}{local}

{chr(10).join(botoes)}
:::

::::

## {r['resumo']}

{texto}

```{{=html}}
<a class="back-link" href="/publications/">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M15 5l-7 7 7 7"/></svg>
  <span>{r['voltar']}</span>
</a>
```

```{{=html}}
</div>
</div>
```"""


def gerar_publicacoes() -> None:
    linhas = ler("publicacoes.csv", PUBLICACOES_OBRIGATORIAS)
    for linha in linhas:
        for lang in ("pt", "en"):
            escrever(f"publications/{linha['slug']}/{linha['slug']}.{lang}.qmd",
                     pagina_de_publicacao(linha, lang))
    apagados = limpar_antigos("publications", {linha["slug"] for linha in linhas})
    print(f"publications: {len(linhas)} artigos, {len(linhas) * 2} paginas"
          + (f", {len(apagados)} paginas removidas" if apagados else ""))


# -------------------------------------------------------------------- noticias

NOTICIAS_OBRIGATORIAS = ["slug", "data", "titulo_pt", "titulo_en", "fonte_pt", "fonte_en",
                         "data_texto_pt", "data_texto_en", "url_pt", "url_en",
                         "resumo_pt", "resumo_en"]

ROTULOS_NOTICIA = {"pt": "Voltar para as notícias", "en": "Back to the news"}


def pagina_de_noticia(linha: dict, lang: str) -> str:
    titulo = linha[f"titulo_{lang}"]
    url = linha[f"url_{lang}"]
    return f"""---
title: {aspas(titulo)}
date: {linha['data']}
news-source: {aspas(linha[f'fonte_{lang}'])}
news-date: {aspas(linha[f'data_texto_{lang}'])}
news-url: {aspas(url)}
image: {aspas(linha['imagem'])}
summary: {aspas(linha[f'resumo_{lang}'])}
---

```{{=html}}
<div class="page-shell">
<div class="page-main">
```

::: {{#noticia}}

{linha[f'resumo_{lang}']}

[{'Ler a notícia na íntegra' if lang == 'pt' else 'Read the full story'}]({url}){{.pub-btn}}

:::

```{{=html}}
<a class="back-link" href="/publications/#news">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M15 5l-7 7 7 7"/></svg>
  <span>{ROTULOS_NOTICIA[lang]}</span>
</a>
```

```{{=html}}
</div>
</div>
```"""


def gerar_noticias() -> None:
    linhas = ler("noticias.csv", NOTICIAS_OBRIGATORIAS)
    for linha in linhas:
        for lang in ("pt", "en"):
            escrever(f"news/{linha['slug']}/{linha['slug']}.{lang}.qmd", pagina_de_noticia(linha, lang))
    apagados = limpar_antigos("news", {linha["slug"] for linha in linhas})
    print(f"news: {len(linhas)} noticias, {len(linhas) * 2} paginas"
          + (f", {len(apagados)} paginas removidas" if apagados else ""))


def main() -> int:
    try:
        gerar_pessoas()
        gerar_publicacoes()
        gerar_noticias()
    except ErroDeConteudo as erro:
        print(f"conteudo invalido: {erro}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
