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
import datetime
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
        Coluna("cargo_en", "Função em inglês", False),
        Coluna("formacao_en", "Formação em inglês", False),
        Coluna("formacao_detalhe_en", "Formação detalhada em inglês", False),
        Coluna("apresentacao_en", "Apresentação em inglês", False),
        Coluna("interesses_en", "Interesses de pesquisa em inglês", False),
    ],
    "publicacoes": [
        Coluna("titulo", "Título", True, ("titulo", "título do artigo")),
        Coluna("autores", "Autores, na ordem", True, ("autores",)),
        Coluna("veiculo", "Revista ou evento", True, ("veiculo", "periodico")),
        Coluna("local", "Detalhes (volume, número, páginas, editora)", True,
               ("detalhes", "detalhes da publicacao")),
        Coluna("data", "Data da publicação", True, ("data",)),
        Coluna("url", "Endereço do artigo (DOI ou link)", True,
               ("endereco do artigo", "doi", "link do artigo")),
        Coluna("resumo", "Resumo", True, ("abstract",)),
        Coluna("resumo_curto", "Resumo curto", False, ("resumo curto para a lista",)),
        Coluna("citacao", "Como citar, em LaTeX", True, ("como citar", "citacao", "citação")),
        Coluna("imagem", "Imagem de destaque", False, ("miniatura", "capa", "thumbnail")),
        Coluna("figura1", "Figura 1", False),
        Coluna("legenda1", "Legenda da figura 1", False),
        Coluna("figura2", "Figura 2", False),
        Coluna("legenda2", "Legenda da figura 2", False),
        Coluna("resumo_en", "Resumo em inglês", False),
        Coluna("resumo_curto_en", "Resumo curto em inglês", False),
    ],
    "noticias": [
        Coluna("titulo", "Título", True, ("titulo",)),
        Coluna("veiculo", "Veículo", True, ("veiculo", "fonte")),
        Coluna("data", "Data", True, ("data",)),
        Coluna("url", "Endereço da matéria", True, ("endereco da materia", "link")),
        Coluna("resumo", "Resumo", True),
        Coluna("imagem", "Imagem", False, ("foto", "capa")),
        Coluna("titulo_en", "Título em inglês", False),
        Coluna("resumo_en", "Resumo em inglês", False),
        Coluna("url_en", "Endereço da matéria em inglês", False),
    ],
    "cursos": [
        Coluna("titulo", "Nome do curso", True, ("titulo", "nome da disciplina", "disciplina", "curso")),
        Coluna("titulo_en", "Nome do curso em inglês", False, ("titulo em ingles", "course title", "nome do curso em ingles")),
        Coluna("nivel", "Nível ou programa", True, ("nivel", "programa", "nivel de ensino")),
        Coluna("nivel_en", "Nível ou programa em inglês", False, ("nivel em ingles", "programa em ingles", "level", "program")),
        Coluna("professor", "Professor(es)", True, ("professor", "professores", "docente", "docentes", "instrutor")),
        Coluna("carga_horaria", "Carga horária", True, ("carga horaria", "duracao", "horas", "course load")),
        Coluna("aulas", "Horário e formato das aulas", True, ("horario e formato das aulas", "aulas", "horario das aulas", "horario")),
        Coluna("aulas_en", "Horário e formato das aulas em inglês", False, ("horario e formato das aulas em ingles", "aulas em ingles", "classes", "schedule")),
        Coluna("oferta", "Período de oferta", True, ("periodo de oferta", "oferta", "quando e ofertado", "semestre")),
        Coluna("oferta_en", "Período de oferta em inglês", False, ("periodo de oferta em ingles", "oferta em ingles", "offered", "term")),
        Coluna("url", "Página do curso", True, ("pagina do curso", "link do curso", "endereco do curso", "pagina do programa", "url", "link")),
        Coluna("url_en", "Página do curso em inglês", False, ("pagina do curso em ingles", "course page", "url em ingles")),
        Coluna("imagem", "Imagem ilustrativa", False, ("imagem", "foto", "icone", "ilustracao", "capa")),
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
    "colaborador externo": "colaborador",
    "colaboradora externa": "colaborador",
    "colaborador": "colaborador",
    "colaboradora": "colaborador",
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


LIMITE_DO_ENDERECO = 60


def slugificar(texto: str, limite: int = LIMITE_DO_ENDERECO) -> str:
    """Endereco da pagina a partir do titulo ou do nome: 'Machine Learning for
    Climate' vira 'machine-learning-for-climate'. So letra, numero e hifen, sem
    acento. Passando do limite, o corte cai na ultima palavra inteira."""
    limpo = normalizar(texto).replace(" ", "-")
    if len(limpo) > limite:
        limpo = limpo[:limite].rsplit("-", 1)[0] or limpo[:limite]
    return limpo.strip("-")


def endereco_unico(texto: str, usados: set[str], limite: int = LIMITE_DO_ENDERECO) -> str:
    """O mesmo endereco, sem repetir o que ja saiu nesta tabela. Nome repetido -
    dois 'Joao Silva', dois artigos com o mesmo titulo - recebe sufixo -1, -2, -3
    ... na ordem da planilha. O corte de tamanho ja desconta o sufixo, entao o
    endereco inteiro cabe no limite, e nunca sobra hifen solto no fim."""
    base = slugificar(texto, limite)
    if not base:
        raise ErroDeConteudo(f"sem letra nem numero para virar endereco: {texto!r}")
    if base not in usados:
        usados.add(base)
        return base
    numero = 1
    while True:
        sufixo = f"-{numero}"
        candidato = slugificar(texto, limite - len(sufixo)).strip("-") + sufixo
        if candidato not in usados:
            usados.add(candidato)
            return candidato
        numero += 1


SEPARADOR_DE_ITENS = re.compile(r"[\r\n]+|[|;]|^[ \t]*[-*•–—][ \t]+", re.M)


def itens(valor: str) -> list[str]:
    """Lista digitada numa celula. O jeito natural e uma linha por item: no
    formulario, pergunta do tipo paragrafo (Enter); na planilha, Ctrl+Enter
    dentro da celula. Quem escrever tudo numa linha so nao fica travado: '|' e
    ';' tambem separam. O '- ' ou '* ' no comeco de cada item e enfeite e sai.
    Celula sem separador nenhum vira um item: paragrafo comum continua valendo."""
    return [p.strip() for p in SEPARADOR_DE_ITENS.split(valor or "")
            if p.strip(" \t-–—*•")]


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
    """Aceita 24-04-2026 e 24/04/2026 - dia primeiro, como se escreve em portugues -
    e tambem 2026-04-24, com ou sem hora, que e como o Google Sheets costuma
    devolver a celula. Recusa data que nao existe no calendario."""
    valor = (valor or "").strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", valor)
    if m:
        ano, mes, dia = (int(g) for g in m.groups())
    else:
        m = re.match(r"^(\d{1,2})[-/](\d{1,2})[-/](\d{4})$", valor)
        if not m:
            raise ErroDeConteudo(
                f"data fora do formato: {valor!r}. Escreva dia-mes-ano, como 24-04-2026, "
                "e formate a coluna da planilha como texto")
        dia, mes, ano = (int(g) for g in m.groups())
    try:
        datetime.date(ano, mes, dia)
    except ValueError:
        raise ErroDeConteudo(
            f"data que nao existe no calendario: {valor!r}. Escreva dia-mes-ano, "
            "como 24-04-2026") from None
    return ano, mes, dia


def data_texto(valor: str) -> str:
    """A data na forma de dentro do site, que e a do campo `date:` do `.qmd`: 2026-04-24.
    Ano primeiro de proposito: assim a listagem ordena a data como texto e o Quarto
    entende o campo. Quem digita na planilha escreve dia-mes-ano."""
    ano, mes, dia = data_iso(valor)
    return f"{ano:04d}-{mes:02d}-{dia:02d}"


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


def ler_xlsx_bruto(caminho: Path, nome_aba: str = "") -> list[dict[str, str]]:
    """Le arquivo Excel (.xlsx) nativamente usando zipfile e XML padrao do Python."""
    import zipfile
    import xml.etree.ElementTree as ET

    with zipfile.ZipFile(caminho) as z:
        strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            tree = ET.fromstring(z.read("xl/sharedStrings.xml"))
            ns_main = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
            for si in tree.findall(f"{ns_main}si"):
                text_parts = [t.text or "" for t in si.findall(f".//{ns_main}t")]
                strings.append("".join(text_parts))

        sheet_path = "xl/worksheets/sheet1.xml"
        if "xl/workbook.xml" in z.namelist():
            wb = ET.fromstring(z.read("xl/workbook.xml"))
            ns_wb = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            alvo = normalizar(nome_aba)
            for s in wb.findall(".//m:sheet", ns_wb):
                if alvo and normalizar(s.get("name", "")) == alvo:
                    rid = s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
                    if "xl/_rels/workbook.xml.rels" in z.namelist():
                        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
                        r_ns = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
                        for rel in rels.findall(".//r:Relationship", r_ns):
                            if rel.get("Id") == rid:
                                target = rel.get("Target", "")
                                if target.startswith("/"):
                                    target = target.lstrip("/")
                                elif not target.startswith("xl/"):
                                    target = "xl/" + target
                                sheet_path = target
                                break
                    break

        if sheet_path not in z.namelist():
            candidatas = [n for n in z.namelist() if n.startswith("xl/worksheets/sheet") and n.endswith(".xml")]
            if candidatas:
                sheet_path = candidatas[0]

        sheet = ET.fromstring(z.read(sheet_path))
        ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
        raw_rows = []
        for r in sheet.findall(f".//{ns}row"):
            row = []
            for c in r.findall(f"{ns}c"):
                t = c.get("t")
                v = c.find(f"{ns}v")
                if t == "s" and v is not None and v.text and v.text.isdigit():
                    idx = int(v.text)
                    val = strings[idx] if idx < len(strings) else ""
                elif t == "inlineStr":
                    it = c.find(f".//{ns}t")
                    val = it.text if it is not None and it.text else ""
                else:
                    val = v.text if v is not None and v.text else ""
                row.append(val)
            if any(row):
                raw_rows.append(row)

        if not raw_rows:
            return []
        headers = [h.strip() for h in raw_rows[0]]
        result = []
        for row in raw_rows[1:]:
            d = {}
            for i, h in enumerate(headers):
                if h:
                    d[h] = row[i].strip() if i < len(row) else ""
            result.append(d)
        return result


def ler_tabela(tabela: str, caminho: Path) -> list[dict]:
    """Le uma tabela (CSV ou Excel .xlsx) e devolve linhas com as chaves do esquema.

    Recusa o que nao der para publicar: pergunta obrigatoria sem coluna, celula
    obrigatoria vazia, endereco repetido. A mensagem cita o texto da pergunta.
    """
    if not caminho.exists():
        alternativo_xlsx = caminho.with_suffix(".xlsx")
        if alternativo_xlsx.exists():
            caminho = alternativo_xlsx
        else:
            raise ErroDeConteudo(f"{caminho.name} nao existe em {caminho.parent.name}/")

    if caminho.suffix.lower() == ".xlsx":
        bruto = ler_xlsx_bruto(caminho, nome_aba=tabela)
    else:
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
    linhas, usados = [], set()
    for numero, linha in enumerate(bruto, start=2):
        dado = {chave: (linha.get(cabecalho) or "").strip() for chave, cabecalho in mapa.items()}
        for coluna in COLUNAS[tabela]:
            if coluna.obrigatoria and not dado.get(coluna.chave):
                raise ErroDeConteudo(f"{caminho.name}, linha {numero}: "
                                     f"sem resposta em {coluna.rotulo!r}")
        if "data" in dado and dado["data"]:
            try:
                dado["data"] = data_texto(dado["data"])
            except ErroDeConteudo as erro:
                raise ErroDeConteudo(f"{caminho.name}, linha {numero}: {erro}") from None
        if tabela == "pessoas":
            simples = slugificar(dado["nome"])
            dado["slug"] = endereco_unico(dado["nome"], usados)
            dado["grupo"] = VINCULOS.get(normalizar(dado["vinculo"]))
            if not dado["grupo"]:
                raise ErroDeConteudo(
                    f"{caminho.name}, linha {numero}: vinculo desconhecido: {dado['vinculo']!r}. "
                    "Use " + ", ".join(sorted({v for v in VINCULOS})))
            partes = dado["nome"].split()
            dado["primeiro"], dado["ultimo"] = partes[0], partes[-1]
        else:
            simples = slugificar(dado["titulo"])
            dado["slug"] = endereco_unico(dado["titulo"], usados)
        if not slug_valido(dado["slug"]):
            raise ErroDeConteudo(f"{caminho.name}, linha {numero}: endereco invalido: {dado['slug']!r}")
        if dado["slug"] != simples:
            print(f"aviso: {tabela}: {simples!r} ja estava em uso; linha {numero} "
                  f"virou {dado['slug']!r}")
        linhas.append(dado)
    return linhas


def texto(linha: dict, chave: str, lang: str) -> str:
    """Texto que o formulario pergunta uma vez em portugues e que, se alguem
    traduzir na planilha, tem versao inglesa. Sem traducao, a pagina inglesa
    reusa o portugues."""
    if lang == "en":
        return linha.get(chave + "_en") or linha.get(chave, "")
    return linha.get(chave, "")



# ---------------------------------------------------------------- linha de comando

def perguntas(tabelas_: list[str]) -> int:
    """Os textos que o formulario tem de usar. Quem monta o formulario copia daqui."""
    for tabela in tabelas_:
        if tabela not in COLUNAS:
            print(f"tabela desconhecida: {tabela!r}. Use " + ", ".join(COLUNAS), file=sys.stderr)
            return 2
        print(f"\n{tabela}")
        for coluna in COLUNAS[tabela]:
            marca = "obrigatoria" if coluna.obrigatoria else "opcional   "
            print(f"  {marca}  {coluna.rotulo}")
            for apelido in coluna.apelidos:
                print(f"              {apelido}   (tambem serve)")
    return 0


def conferir(tabela: str, cabecalhos: list[str]) -> int:
    """Confere a linha de titulo de uma planilha contra o esquema.

    O texto da pergunta nao precisa ser identico: acento, maiuscula, pontuacao e
    espaco extra nao contam, e alguns apelidos de redacao valem. O que nao pode e
    faltar uma pergunta obrigatoria, porque ai a coluna nao existe e a resposta
    fica invisivel para o site."""
    mapa = mapa_de_colunas(tabela, cabecalhos)
    faltando = []
    for coluna in COLUNAS[tabela]:
        chegou = mapa.get(coluna.chave)
        if chegou is None:
            if coluna.obrigatoria:
                faltando.append(coluna.rotulo)
                print(f"  FALTA      {coluna.rotulo!r}")
            else:
                print(f"  sem coluna {coluna.rotulo!r}   (opcional)")
            continue
        variacao = "" if normalizar(chegou) == normalizar(coluna.rotulo) else "   [casou por variacao]"
        print(f"  ok         {coluna.rotulo!r} <- {chegou!r}{variacao}")
    if faltando:
        print("\nSem as perguntas obrigatorias nao da para publicar: "
              + ", ".join(repr(f) for f in faltando))
        print("Ponha esse texto exato no formulario, ou acrescente o apelido em "
              "COLUNAS, aqui em tabelas.py.")
        return 1
    print("\nTodas as perguntas obrigatorias chegaram.")
    return 0


def main(argv: list[str]) -> int:
    uso = ("uso:\n"
           "  python3 scripts/tabelas.py perguntas [pessoas|publicacoes|noticias|cursos]\n"
           "  python3 scripts/tabelas.py conferir <tabela> <arquivo.csv|arquivo.xlsx>\n"
           "  python3 scripts/tabelas.py conferir <tabela> -   (linha de titulo pelo stdin)")
    if len(argv) >= 2 and argv[1] == "perguntas":
        return perguntas(argv[2:] or list(COLUNAS))
    if len(argv) >= 3 and argv[1] == "conferir":
        tabela, origem = argv[2], argv[3]
        if tabela not in COLUNAS:
            print(f"tabela desconhecida: {tabela!r}. Use " + ", ".join(COLUNAS), file=sys.stderr)
            return 2
        if origem == "-":
            conteudo = sys.stdin.read()
            linhas = [l for l in conteudo.splitlines() if l.strip()]
            if not linhas:
                print("nada para conferir", file=sys.stderr)
                return 2
            primeira = linhas[0]
            corte = "\t" if "\t" in primeira else ","
            cabecalhos = [c.strip() for c in next(csv.reader([primeira], delimiter=corte))]
        else:
            try:
                caminho = Path(origem) if Path(origem).exists() else None
            except OSError:   # linha de cabecalho colada, longa demais para nome de arquivo
                caminho = None
            if caminho and caminho.suffix.lower() == ".xlsx":
                dados = ler_xlsx_bruto(caminho, nome_aba=tabela)
                if not dados:
                    print("nenhuma linha encontrada no arquivo Excel", file=sys.stderr)
                    return 2
                cabecalhos = list(dados[0].keys())
            else:
                conteudo = (caminho.read_text(encoding="utf-8-sig") if caminho
                            else origem)  # a propria linha de cabecalho, colada
                linhas = [l for l in conteudo.splitlines() if l.strip()]
                if not linhas:
                    print("nada para conferir", file=sys.stderr)
                    return 2
                primeira = linhas[0]
                corte = "\t" if "\t" in primeira else ","
                cabecalhos = [c.strip() for c in next(csv.reader([primeira], delimiter=corte))]
        return conferir(tabela, cabecalhos)
    print(uso)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
