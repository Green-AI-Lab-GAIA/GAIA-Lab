#!/usr/bin/env python3
"""Gera as paginas de pessoas, publicacoes e noticias a partir das tabelas em dados/.

As tabelas sao a fonte da verdade: elas chegam das planilhas do Google pelo
scripts/sincronizar.py. Toda pagina .pt.qmd e .en.qmd escrita aqui e arquivo
gerado, entao editar a pagina nao adianta, ela e sobrescrita na rodada seguinte.

O que o formulario pergunta esta em scripts/tabelas.py. O formulario manda texto
corrido, sem sintaxe: quem monta os blocos (ficha, figuras, como citar) e este
script.

Uso:  python3 scripts/gerar_conteudo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from tabelas import (COLUNAS, ErroDeConteudo, eh_endereco, itens, ler_tabela,
                     por_extenso, sem_travessao, texto)

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"

AVISO = ("# Arquivo gerado por scripts/gerar_conteudo.py a partir de {tabela}.\n"
         "# Nao edite aqui: edite a planilha e rode o script.")

# quando o formulario nao manda imagem, a pagina usa o desenho padrao do site
PADRAO = {"people": "avatar-default.svg", "publications": "paper-default.svg", "news": None}


# ----------------------------------------------------------------- utilidades

def aspas(valor: str) -> str:
    """Valor pronto para entrar como string YAML entre aspas duplas."""
    return '"' + valor.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").strip() + '"'


def escrever(relativo: str, texto_saida: str) -> None:
    destino = RAIZ / relativo
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto_saida.rstrip() + "\n", encoding="utf-8")


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


def imagem_local(pasta: str, base: str, valor: str) -> str | None:
    """Resolve a imagem de uma linha.

    A planilha pode trazer o nome do arquivo (quem edita a mao) ou o endereco que
    o formulario gravou. No segundo caso o arquivo ja foi baixado para a pasta do
    item por scripts/baixar_imagens.py, e aqui so procuramos por ele. O nome tem
    extensao desconhecida, entao procuramos por pasta/base.*.
    """
    valor = (valor or "").strip()
    if valor and not eh_endereco(valor):
        return valor
    achados = sorted(p.name for p in (RAIZ / pasta).glob(f"{base}.*") if p.is_file())
    return achados[0] if achados else None


def padrao(pasta: str) -> str | None:
    """Caminho relativo ate a imagem padrao, visto de dentro da pasta do item."""
    nome = PADRAO[pasta]
    if not nome:
        return None
    return f"../../images/{nome}"


def resolver(pasta: str, slug: str, base: str, valor: str) -> str | None:
    pasta_item = f"{pasta}/{slug}"
    encontrada = imagem_local(pasta_item, base, valor)
    if encontrada:
        return encontrada
    if valor:
        print(f"aviso: {pasta_item}: {base} nao encontrada, a pagina usa o padrao",
              file=sys.stderr)
    return padrao(pasta)


def limpo(valor: str) -> str:
    """Texto que vai para o site, ja sem travessao (regra do site)."""
    return sem_travessao((valor or "").strip())


def primeira_frase(resumo_longo: str, limite: int = 220) -> str:
    """O cartao da listagem precisa de uma frase curta. Quem escreve o artigo pode
    mandar so o resumo longo: aqui sai a primeira frase dele."""
    resumo_longo = resumo_longo.strip()
    if len(resumo_longo) <= limite:
        return resumo_longo
    corte = resumo_longo[:limite]
    fim = max(corte.rfind(". "), corte.rfind("! "), corte.rfind("? "))
    if fim > 80:
        return corte[:fim + 1]
    return corte.rsplit(" ", 1)[0] + "..."


# --------------------------------------------------------------------- pessoas

ROTULOS = {
    "pt": {"secao_formacao": "Formação", "secao_interesses": "Interesses",
           "voltar": "Voltar para a equipe"},
    "en": {"secao_formacao": "Education", "secao_interesses": "Interests",
           "voltar": "Back to the team"},
}


def pagina_de_pessoa(linha: dict, lang: str) -> str:
    r = ROTULOS[lang]
    nome = limpo(linha["nome"])
    cargo = limpo(texto(linha, "cargo", lang))
    formacao = limpo(texto(linha, "formacao", lang))
    apresentacao = limpo(texto(linha, "apresentacao", lang))
    interesses = limpo(texto(linha, "interesses", lang))
    curso = [limpo(i) for i in itens(texto(linha, "formacao_detalhe", lang))]
    imagem = resolver("people", linha["slug"], "avatar", linha["foto"]) or padrao("people")
    links = []
    if linha.get("linkedin"):
        links.append(f'    - icon: linkedin\n      text: LinkedIn\n      href: {aspas(linha["linkedin"])}')
    if linha.get("email"):
        links.append(f'    - icon: envelope\n      text: Email\n      href: "mailto:{linha["email"]}"')
    secoes = []
    if curso:
        secoes.append(f"## {r['secao_formacao']}\n\n" + "\n".join(f"- {i}" for i in curso))
    if interesses:
        secoes.append(f"## {r['secao_interesses']}\n\n{interesses}")
    corpo = "\n\n".join(secoes)
    return f"""---
title: {aspas(nome)}
last: {aspas(linha['ultimo'])}
first: {aspas(linha['primeiro'])}
people_group: {aspas(linha['grupo'])}
subtitle: {aspas(cargo)}
education: {aspas(formacao)}
image: {imagem}
page-layout: full
toc: false
about:
  id: perfil
  template: trestles
  image-shape: round
  image: {imagem}
  links:
{chr(10).join(links) if links else '    []'}
---

```{{=html}}
<div class="page-shell">
<div class="page-main">
```

::: {{#perfil}}

{apresentacao}

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
    linhas = ler_tabela("pessoas", DADOS / "pessoas.csv")
    for linha in linhas:
        for lang in ("pt", "en"):
            escrever(f"people/{linha['slug']}/{linha['slug']}.{lang}.qmd",
                     pagina_de_pessoa(linha, lang))
    apagados = limpar_antigos("people", {linha["slug"] for linha in linhas})
    print(f"people: {len(linhas)} pessoas, {len(linhas) * 2} paginas"
          + (f", {len(apagados)} paginas removidas" if apagados else ""))


# ----------------------------------------------------------------- publicacoes

ROTULOS_PUB = {
    "pt": {"autores": "Autores", "publicacao": "Publicação", "resumo": "Resumo",
           "citacao": "Como citar", "botao": "Acessar o artigo",
           "voltar": "Voltar para as publicações"},
    "en": {"autores": "Authors", "publicacao": "Published", "resumo": "Abstract",
           "citacao": "How to cite", "botao": "Read the article",
           "voltar": "Back to publications"},
}


def bloco_de_figuras(linha: dict, lang: str, pasta: str) -> str:
    partes = []
    for numero in (1, 2):
        figura = resolver(pasta, linha["slug"], f"figura{numero}", linha.get(f"figura{numero}", ""))
        if not linha.get(f"figura{numero}") or not figura:
            continue
        legenda = limpo(texto(linha, f"legenda{numero}", lang))
        partes.append(f"![{legenda}]({figura})")
    if not partes:
        return ""
    return ":::: {.pub-figures}\n" + "\n\n".join(partes) + "\n::::"


def bloco_de_citacao(linha: dict, lang: str) -> str:
    r = ROTULOS_PUB[lang]
    citacao = (linha.get("citacao") or "").strip()
    if not citacao:
        return ""
    # a citacao e o unico campo com sintaxe, e vem em LaTeX ou BibTeX: nao passa
    # pelo corretor de travessao, senao estraga o codigo
    linguagem = "bibtex" if citacao.lstrip().startswith("@") else "latex"
    return f"## {r['citacao']}\n\n```{linguagem}\n{citacao}\n```"


def pagina_de_publicacao(linha: dict, lang: str) -> str:
    r = ROTULOS_PUB[lang]
    titulo = limpo(texto(linha, "titulo", lang))
    resumo = limpo(texto(linha, "resumo", lang))
    curto = limpo(texto(linha, "resumo_curto", lang)) or primeira_frase(resumo)
    corpo = limpo(texto(linha, "texto", lang))
    local = limpo(texto(linha, "local", lang))
    veiculo = limpo(texto(linha, "veiculo", lang))
    autores = limpo(linha["autores"])
    publicado = por_extenso(linha["data"], lang, com_dia=False)
    imagem = resolver("publications", linha["slug"], "miniatura", linha.get("imagem", "")) \
        or padrao("publications")
    meta = ", ".join(p for p in (publicado, local) if p)
    figuras = bloco_de_figuras(linha, lang, "publications")
    citacao = bloco_de_citacao(linha, lang)
    pedacos = [f"## {r['resumo']}\n\n{resumo}"]
    if corpo:
        pedacos.append(corpo)
    if figuras:
        pedacos.append(figuras)
    if citacao:
        pedacos.append(citacao)
    corpo_final = "\n\n".join(pedacos)
    return f"""---
title: {aspas(titulo)}
paper-authors: {aspas(autores)}
venue: {aspas(veiculo)}
pub-date: {aspas(publicado)}
date: {linha['data']}
image: {imagem}
snippet: {aspas(curto)}
page-layout: full
toc: false
---

```{{=html}}
<div class="page-shell">
<div class="page-main">
```

:::: {{.pub-detail}}

::: {{.pub-detail-thumb}}
[![]({imagem})]({linha['url']})
:::

::: {{.pub-detail-meta}}
**{r['autores']}:** {autores}

**{r['publicacao']}:** {meta}

[{r['botao']}]({linha['url']}){{.pub-btn}}
:::

::::

{corpo_final}

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
    linhas = ler_tabela("publicacoes", DADOS / "publicacoes.csv")
    for linha in linhas:
        for lang in ("pt", "en"):
            escrever(f"publications/{linha['slug']}/{linha['slug']}.{lang}.qmd",
                     pagina_de_publicacao(linha, lang))
    apagados = limpar_antigos("publications", {linha["slug"] for linha in linhas})
    print(f"publications: {len(linhas)} artigos, {len(linhas) * 2} paginas"
          + (f", {len(apagados)} paginas removidas" if apagados else ""))


# -------------------------------------------------------------------- noticias

ROTULOS_NOTICIA = {"pt": "Voltar para as notícias", "en": "Back to the news"}


def pagina_de_noticia(linha: dict, lang: str) -> str:
    titulo = limpo(texto(linha, "titulo", lang))
    resumo = limpo(texto(linha, "resumo", lang))
    veiculo = limpo(texto(linha, "veiculo", lang))
    url = texto(linha, "url", lang)
    imagem = resolver("news", linha["slug"], "imagem", linha.get("imagem", ""))
    data_texto = por_extenso(linha["data"], lang, com_dia=True)
    imagem_yml = aspas(imagem) if imagem else '""'
    return f"""---
title: {aspas(titulo)}
date: {linha['data']}
news-source: {aspas(veiculo)}
news-date: {aspas(data_texto)}
news-url: {aspas(url)}
image: {imagem_yml}
summary: {aspas(resumo)}
---

```{{=html}}
<div class="page-shell">
<div class="page-main">
```

::: {{#noticia}}

{resumo}

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
    linhas = ler_tabela("noticias", DADOS / "noticias.csv")
    for linha in linhas:
        for lang in ("pt", "en"):
            escrever(f"news/{linha['slug']}/{linha['slug']}.{lang}.qmd",
                     pagina_de_noticia(linha, lang))
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
