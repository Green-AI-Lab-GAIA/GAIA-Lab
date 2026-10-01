#!/usr/bin/env python3
"""Gera as paginas de pessoas, publicacoes, noticias e cursos a partir das tabelas em dados/.

As tabelas sao a fonte da verdade: elas chegam das planilhas do Google pelo
scripts/sincronizar.py. Toda pagina .pt.qmd e .en.qmd escrita aqui e arquivo
gerado, entao editar a pagina nao adianta, ela e sobrescrita na rodada seguinte.

O que o formulario pergunta esta em scripts/tabelas.py. O formulario manda texto
corrido, sem sintaxe: quem monta os blocos (ficha, figuras, como citar) e este
script.

Uso:  python3 scripts/gerar_conteudo.py
"""
from __future__ import annotations

import html
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

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
    """Remove a pasta de itens que sairam da planilha, com a pagina e as imagens
    que vieram junto. Devolve o que apagou.

    A pasta nao fica para tras: ela e o endereco do item, e pasta antiga ocupando o
    nome de quem entrou depois faz a pagina nova cair dentro dela, com a imagem do
    outro."""
    apagados = []
    raiz = RAIZ / pasta
    if not raiz.exists():
        return apagados
    for item in sorted(raiz.iterdir()):
        if not item.is_dir() or item.name in gerados:
            continue
        for arq in sorted(item.rglob("*")):
            if arq.is_file():
                arq.unlink()
                apagados.append(str(arq.relative_to(RAIZ)))
        for sobra in sorted((d for d in item.rglob("*") if d.is_dir()), reverse=True):
            sobra.rmdir()
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
        # Legenda e obrigatoria quando existe figura: o formulario nao sabe
        # exigir uma pergunta em funcao de outra, entao quem cobra e este ponto.
        legenda = limpo(texto(linha, f"legenda{numero}", lang))
        if not legenda:
            raise ErroDeConteudo(
                f"figura {numero} sem legenda: {linha['slug']}. "
                f"Preencha a coluna 'Legenda da figura {numero}' na planilha, "
                "ou apague a figura")
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


# --------------------------------------------------------------------- cursos

ROTULOS_CURSOS = {
    "pt": {
        "title": "Cursos",
        "desc_top": "Disciplinas ministradas por integrantes do laboratório na FGV EMAp.",
        "professor": "Professor:",
        "carga_horaria": "Carga horária:",
        "aulas": "Aulas:",
        "oferta": "Oferta:",
        "botao": "Página do curso",
    },
    "en": {
        "title": "Courses",
        "desc_top": "Courses taught by lab members at FGV EMAp.",
        "professor": "Professor:",
        "carga_horaria": "Course load:",
        "aulas": "Classes:",
        "oferta": "Offered:",
        "botao": "Course page",
    },
}


def resolver_imagem_curso(linha: dict) -> str:
    slug = linha.get("slug", "")
    img = (linha.get("imagem") or "").strip()
    if img:
        if img.startswith("images/") or img.startswith("http://") or img.startswith("https://"):
            return img
        if (RAIZ / "courses" / "images" / img).is_file():
            return f"images/{img}"
    if slug:
        achados = sorted(p.name for p in (RAIZ / "courses" / "images").glob(f"{slug}.*") if p.is_file())
        if achados:
            return f"images/{achados[0]}"
    if "aprendizado-profundo" in slug:
        return "images/aprendizado-profundo.svg"
    return "images/redes-neurais.svg"


def cartao_de_curso(linha: dict, lang: str) -> str:
    r = ROTULOS_CURSOS[lang]
    titulo = limpo(texto(linha, "titulo", lang))
    nivel = limpo(texto(linha, "nivel", lang))
    prof = limpo(linha.get("professor", ""))
    ch = limpo(linha.get("carga_horaria", ""))
    aulas = limpo(texto(linha, "aulas", lang))
    oferta = limpo(texto(linha, "oferta", lang))
    url = (texto(linha, "url", lang) or linha.get("url", "")).strip()
    imagem = resolver_imagem_curso(linha)

    detalhes = []
    if prof:
        detalhes.append(f"        <li><strong>{r['professor']}</strong> {prof}</li>")
    if ch:
        detalhes.append(f"        <li><strong>{r['carga_horaria']}</strong> {ch}</li>")
    if aulas:
        detalhes.append(f"        <li><strong>{r['aulas']}</strong> {aulas}</li>")
    if oferta:
        detalhes.append(f"        <li><strong>{r['oferta']}</strong> {oferta}</li>")
    detalhes_html = "\n".join(detalhes)

    btn_html = f'\n      <a class="pub-btn" href="{url}">{r["botao"]}</a>' if url else ""

    return f"""  <div class="course-card">
    <img class="course-image" src="{imagem}"
         alt="{aspas(titulo).strip('"')}">
    <div class="course-info">
      <span class="course-level">{nivel}</span>
      <div class="course-title">{titulo}</div>
      <ul class="course-details">
{detalhes_html}
      </ul>{btn_html}
    </div>
  </div>"""


def pagina_de_cursos(linhas: list[dict], lang: str) -> str:
    r = ROTULOS_CURSOS[lang]
    cartoes = "\n\n".join(cartao_de_curso(linha, lang) for linha in linhas)
    return f"""---
title: {aspas(r['title'])}
# {r['desc_top']}
resources:
  - "images/"
page-layout: full
toc: false
---

```{{=html}}
<div class="page-shell">
<div class="page-main">
```

```{{=html}}
<div class="course-list">

{cartoes}

</div>
```

```{{=html}}
</div>
</div>
```"""


def gerar_cursos() -> None:
    caminho_csv = DADOS / "cursos.csv"
    caminho_xlsx = DADOS / "cursos.xlsx"
    if not caminho_csv.exists() and not caminho_xlsx.exists():
        return
    caminho = caminho_csv if caminho_csv.exists() else caminho_xlsx
    linhas = ler_tabela("cursos", caminho)
    for lang in ("pt", "en"):
        escrever(f"courses/index.{lang}.qmd", pagina_de_cursos(linhas, lang))
    print(f"courses: {len(linhas)} cursos, 2 paginas compiladas")


# ----------------------------------------------------------------- galeria

PASTA_GALERIA = RAIZ / "about/images/galeria"
LEGENDAS_GALERIA = PASTA_GALERIA / "legendas.txt"
EXTENSOES_GALERIA = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".avif"}
WEB_GALERIA = PASTA_GALERIA / "web"
LARGURA_MAXIMA_GALERIA = 1600
QUALIDADE_GALERIA = 78


def caminho_miniatura_galeria(arquivo: Path) -> str:
    """Caminho relativo usado no src, em WebP quando dá para converter."""
    if Image is None or arquivo.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
        return f"images/galeria/{arquivo.name}"
    WEB_GALERIA.mkdir(parents=True, exist_ok=True)
    destino = WEB_GALERIA / f"{arquivo.stem}.webp"
    if not destino.exists() or destino.stat().st_mtime < arquivo.stat().st_mtime:
        with Image.open(arquivo) as imagem:
            imagem = imagem.convert("RGB")
            if imagem.width > LARGURA_MAXIMA_GALERIA:
                altura = round(imagem.height * LARGURA_MAXIMA_GALERIA / imagem.width)
                imagem = imagem.resize((LARGURA_MAXIMA_GALERIA, altura), Image.LANCZOS)
            imagem.save(destino, "WEBP", quality=QUALIDADE_GALERIA, method=6)
    return f"images/galeria/web/{destino.name}"


def ler_legendas_galeria() -> dict[str, tuple[str, str]]:
    mapa = {}
    if not LEGENDAS_GALERIA.exists():
        return mapa
    for linha in LEGENDAS_GALERIA.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        partes = [p.strip() for p in linha.split("|")]
        if len(partes) >= 3:
            mapa[partes[0]] = (partes[1], partes[2])
    return mapa


def gerar_galeria() -> None:
    if not PASTA_GALERIA.exists():
        return
    legendas = ler_legendas_galeria()
    total_fotos = 0
    for lang in ("pt", "en"):
        linhas = ["```{=html}"]
        for arquivo in sorted(PASTA_GALERIA.iterdir()):
            if arquivo.suffix.lower() not in EXTENSOES_GALERIA:
                continue
            if lang == "pt":
                total_fotos += 1
            padrao = arquivo.stem.replace("-", " ").replace("_", " ")
            par = legendas.get(arquivo.name, (padrao, padrao))
            legenda = html.escape(par[0] if lang == "pt" else par[1])
            linhas.append(
                f'<button class="gallery-thumb" type="button" data-caption="{legenda}">'
                f'<img src="{caminho_miniatura_galeria(arquivo)}" alt="{legenda}" loading="lazy">'
                f"</button>"
            )
        linhas.append("```")
        conteudo = "\n".join(linhas) + "\n"
        destino = RAIZ / f"about/_galeria.{lang}.qmd"
        if not destino.exists() or destino.read_text(encoding="utf-8") != conteudo:
            destino.write_text(conteudo, encoding="utf-8")
    print(f"galeria: {total_fotos} fotos processadas, 2 paginas compiladas")


def main() -> int:
    try:
        gerar_pessoas()
        gerar_publicacoes()
        gerar_noticias()
        gerar_cursos()
        gerar_galeria()
    except ErroDeConteudo as erro:
        print(f"conteudo invalido: {erro}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())


