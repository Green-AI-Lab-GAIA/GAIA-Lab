#!/usr/bin/env python3
"""Esquema das tabelas de conteudo: quais colunas existem e com que nome de pergunta.

O cabecalho da planilha do Google e o proprio texto da pergunta do formulario, que
e quem escreve a linha de titulo. Por isso o codigo nao procura pela palavra
"titulo": procura pelo texto que o formulario mostra, ignorando acento, maiuscula,
pontuacao e espaco extra. Assim o formulario pode ser reescrito sem quebrar nada,
e a mensagem de erro diz a pergunta que falta, nao um nome interno.

Cada coluna tem tres partes: a chave usada no codigo, o texto que aparece na
planilha e se e obrigatoria. Os apelidos cobrem variacoes de redacao.
"""
from __future__ import annotations

import csv
import re
import sys
import unicodedata
from collections import namedtuple
from pathlib import Path

# chave, rotulo (texto da pergunta), obrigatoria, apelidos
Coluna = namedtuple("Coluna", "chave rotulo obrigatoria apelidos", defaults=(False, ()))


COLUNAS = {
    "pessoas": [
        Coluna("nome", "Nome completo", True),
        Coluna("vinculo", "Vínculo", True),
        Coluna("cargo", "Função", True, ("cargo", "funcao exercida")),
        Coluna("formacao", "Formação", True, ("formacao resumida",)),
        Coluna("formacao_detalhe", "Formação detalhada", False),
        Coluna("apresentacao", "Apresentação", False, ("bio", "sobre")),
        Coluna("interesses", "Interesses de pesquisa", False, ("interesses",)),
        Coluna("linkedin", "LinkedIn", False),
        Coluna("email", "E-mail", False, ("email address", "endereco de email", "e mail")),
        Coluna("foto", "Foto", False, ("imagem", "foto do membro")),
        Coluna("slug", "Endereço curto", False, ("slug", "endereco curto", "nome curto")),
        Coluna("cargo_en", "Função em inglês", False),
        Coluna("formacao_en", "Formação em inglês", False),
        Coluna("formacao_detalhe_en", "Formação detalhada em inglês", False),
        Coluna("apresentacao_en", "Apresentação em inglês", False),
        Coluna("interesses_en", "Interesses de pesquisa em inglês", False),
    ],
    "publicacoes": [
        Coluna("titulo", "Título do artigo", True, ("titulo",)),
        Coluna("autores", "Autores, na ordem", True, ("autores",)),
        Coluna("veiculo", "Revista ou evento", True, ("veiculo", "periodico")),
        Coluna("local", "Detalhes (volume, número, páginas, editora)", True,
               ("detalhes", "detalhes da publicacao")),
        Coluna("data", "Data da publicação", True, ("data",)),
        Coluna("url", "Endereço do artigo (DOI ou link)", True,
               ("endereco do artigo", "doi", "link do artigo")),
        Coluna("resumo", "Resumo", True, ("abstract",)),
        Coluna("resumo_curto", "Resumo curto", False, ("resumo curto para a lista",)),
        Coluna("texto", "Texto do artigo", False, ("texto corrido", "corpo")),
        Coluna("citacao", "Como citar, em LaTeX", True, ("como citar", "citacao", "citação")),
        Coluna("imagem", "Imagem de destaque", False, ("miniatura", "capa", "thumbnail")),
        Coluna("figura1", "Figura 1", False),
        Coluna("legenda1", "Legenda da figura 1", False),
        Coluna("figura2", "Figura 2", False),
        Coluna("legenda2", "Legenda da figura 2", False),
        Coluna("slug", "Endereço curto", False, ("slug", "endereco curto", "nome curto")),
        Coluna("titulo_en", "Título em inglês", False),
        Coluna("resumo_en", "Resumo em inglês", False),
        Coluna("resumo_curto_en", "Resumo curto em inglês", False),
        Coluna("texto_en", "Texto do artigo em inglês", False),
    ],
    "noticias": [
        Coluna("titulo", "Título", True, ("titulo",)),
        Coluna("veiculo", "Veículo", True, ("veiculo", "fonte")),
        Coluna("data", "Data", True, ("data",)),
        Coluna("url", "Endereço da matéria", True, ("endereco da materia", "link")),
        Coluna("resumo", "Resumo", True),
        Coluna("imagem", "Imagem", False, ("foto", "capa")),
        Coluna("slug", "Endereço curto", False, ("slug", "endereco curto", "nome curto")),
        Coluna("titulo_en", "Título em inglês", False),
        Coluna("resumo_en", "Resumo em inglês", False),
        Coluna("url_en", "Endereço da matéria em inglês", False),
    ],
}

# colunas que o proprio Google cria e que nao sao erro nenhum: nao vale avisar
RUIDO_DO_FORMULARIO = re.compile(
    r"^(timestamp|carimbo de data hora|email address|endereco de email|score|pontuacao"
    r"|column \d+|coluna \d+|id|hora)$"
)

# o que o formulario oferece na pergunta de vinculo, e a que grupo da pagina corresponde
VINCULOS = {
    "professor": "professor",
    "professor a": "professor",
    "pos doutorado": "postdoc",
    "pos doutorando": "postdoc",
    "postdoc": "postdoc",
    "doutorado": "phd",
    "doutorando": "phd",
    "doutoranda": "phd",
    "phd": "phd",
    "mestrado": "masters",
    "mestrando": "masters",
    "mestranda": "masters",
    "masters": "masters",
    "graduacao": "undergrad",
    "graduando": "undergrad",
    "graduanda": "undergrad",
    "undergrad": "undergrad",
    "alumni": "alumni",
    "egresso": "alumni",
    "egressa": "alumni",
}

MESES = {
    "pt": ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
           "agosto", "setembro", "outubro", "novembro", "dezembro"],
    "en": ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"],
}


class ErroDeConteudo(Exception):
    """Falha de validacao numa tabela, dizendo a linha e a pergunta do problema."""


# ------------------------------------------------------------------- utilidades

def normalizar(texto: str) -> str:
    """Minuscula, sem acento, sem pontuacao: 'Formação' e 'formacao' sao iguais."""
    sem_acento = unicodedata.normalize("NFKD", texto or "")
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", sem_acento.lower()).split())


def slugificar(texto: str, limite: int = 60) -> str:
    """Endereco da pagina a partir do titulo: 'Machine Learning for Climate' vira
    'machine-learning-for-climate'."""
    limpo = normalizar(texto).replace(" ", "-")
    if len(limpo) > limite:
        limpo = limpo[:limite].rsplit("-", 1)[0]
    return limpo.strip("-")


def itens(valor: str) -> list[str]:
    """Lista digitada numa celula: uma linha por item, ou separada por | ou ;."""
    return [p.strip(" -") for p in re.split(r"[\n|;]", valor or "") if p.strip(" -")]


def eh_endereco(valor: str) -> bool:
    return bool(re.match(r"^https?://", (valor or "").strip(), re.I))


def sem_travessao(texto: str) -> str:
    """Regra do site: travessao, meia-risca, hifen cercado de espaco e hifen duplo
    nao entram no texto publicado. Vira virgula, e continua hifen quando separa
    numeros, que e o caso de intervalo de paginas."""
    if not texto:
        return texto
    texto = re.sub(r"(?<=\d)\s*[—–]\s*(?=\d)", "-", texto)
    texto = re.sub(r"\s+[—–]\s+", ", ", texto)
    texto = re.sub(r"\s+-\s+", ", ", texto)
    texto = re.sub(r"\s*--\s*", ", ", texto)
    texto = re.sub(r"[—–]", ", ", texto)
    texto = re.sub(r",\s*,", ",", texto)
    return texto


def data_iso(valor: str) -> tuple[int, int, int]:
    """Aceita 2026-04-24, 2026-04-24 00:00:00, 2026-04-24T00:00:00Z e 24/04/2026."""
    valor = (valor or "").strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", valor)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", valor)
    if m:
        return int(m.group(3)), int(m.group(2)), int(m.group(1))
    raise ErroDeConteudo(
        f"data fora do formato: {valor!r}. Use 2026-04-24, ou formate a coluna da "
        "planilha como texto nesse formato")


def por_extenso(valor: str, lang: str, com_dia: bool) -> str:
    """2026-04-24 vira '24 de abril de 2026' ou 'April 2026', conforme o idioma."""
    ano, mes, dia = data_iso(valor)
    nome = MESES[lang][mes - 1]
    if not com_dia:
        return f"{nome.capitalize()} de {ano}" if lang == "pt" else f"{nome} {ano}"
    return f"{dia} de {nome} de {ano}" if lang == "pt" else f"{nome} {dia}, {ano}"


# ------------------------------------------------------------------ leitura

def mapa_de_colunas(tabela: str, cabecalhos: list[str]) -> dict[str, str]:
    """De qual cabecalho da planilha sai cada chave do esquema."""
    por_rotulo = {}
    for coluna in COLUNAS[tabela]:
        for rotulo in (coluna.rotulo,) + tuple(coluna.apelidos):
            por_rotulo[normalizar(rotulo)] = coluna.chave
    mapa, conhecidos = {}, set()
    for cabecalho in cabecalhos:
        chave = por_rotulo.get(normalizar(cabecalho))
        conhecidos.add(bool(chave))
        if chave and chave not in mapa:
            mapa[chave] = cabecalho
    desconhecidos = [c for c in cabecalhos
                     if normalizar(c) not in por_rotulo
                     and not RUIDO_DO_FORMULARIO.match(normalizar(c))]
    if desconhecidos:
        print(f"aviso: {tabela}: colunas que o esquema nao usa: "
              + ", ".join(repr(c) for c in desconhecidos), file=sys.stderr)
    return mapa


def perguntas_faltando(tabela: str, mapa: dict[str, str]) -> list[str]:
    return [c.rotulo for c in COLUNAS[tabela] if c.obrigatoria and c.chave not in mapa]


def slug_valido(slug: str) -> bool:
    return bool(re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", slug))


def ler_tabela(tabela: str, caminho: Path) -> list[dict]:
    """Le uma tabela e devolve linhas com as chaves do esquema.

    Recusa o que nao der para publicar: pergunta obrigatoria sem coluna, celula
    obrigatoria vazia, endereco repetido. A mensagem cita o texto da pergunta.
    """
    if not caminho.exists():
        raise ErroDeConteudo(f"{caminho.name} nao existe em {caminho.parent.name}/")
    with caminho.open(encoding="utf-8", newline="") as fh:
        bruto = list(csv.DictReader(fh))
    if not bruto:
        raise ErroDeConteudo(f"{caminho.name}: nenhuma linha de dados")
    mapa = mapa_de_colunas(tabela, list(bruto[0].keys()))
    faltando = perguntas_faltando(tabela, mapa)
    if faltando:
        raise ErroDeConteudo(
            f"{caminho.name}: nao encontrei a coluna das perguntas "
            + ", ".join(repr(r) for r in faltando)
            + ". Cabecalhos que chegaram: " + ", ".join(repr(c) for c in bruto[0]))
    linhas, vistos = [], {}
    for numero, linha in enumerate(bruto, start=2):
        dado = {chave: (linha.get(cabecalho) or "").strip() for chave, cabecalho in mapa.items()}
        for coluna in COLUNAS[tabela]:
            if coluna.obrigatoria and not dado.get(coluna.chave):
                raise ErroDeConteudo(f"{caminho.name}, linha {numero}: "
                                     f"sem resposta em {coluna.rotulo!r}")
        if tabela == "pessoas":
            dado["slug"] = dado.get("slug") or slugificar(dado["nome"])
            dado["grupo"] = VINCULOS.get(normalizar(dado["vinculo"]))
            if not dado["grupo"]:
                raise ErroDeConteudo(
                    f"{caminho.name}, linha {numero}: vinculo desconhecido: {dado['vinculo']!r}. "
                    "Use " + ", ".join(sorted({v for v in VINCULOS})))
            partes = dado["nome"].split()
            dado["primeiro"], dado["ultimo"] = partes[0], partes[-1]
        else:
            dado["slug"] = dado.get("slug") or slugificar(dado["titulo"])
        if not slug_valido(dado["slug"]):
            raise ErroDeConteudo(f"{caminho.name}, linha {numero}: endereco invalido: {dado['slug']!r}")
        if dado["slug"] in vistos:
            raise ErroDeConteudo(f"{caminho.name}, linha {numero}: endereco repetido: {dado['slug']} "
                                 f"(ja usado na linha {vistos[dado['slug']]})")
        vistos[dado["slug"]] = numero
        linhas.append(dado)
    return linhas


def texto(linha: dict, chave: str, lang: str) -> str:
    """Texto que o formulario pergunta uma vez em portugues e que, se alguem
    traduzir na planilha, tem versao inglesa. Sem traducao, a pagina inglesa
    reusa o portugues."""
    if lang == "en":
        return linha.get(chave + "_en") or linha.get(chave, "")
    return linha.get(chave, "")
