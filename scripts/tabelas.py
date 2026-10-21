#!/usr/bin/env python3
"""Esquema das tabelas de conteudo: quais colunas existem e com que nome de pergunta.

O cabecalho da planilha do Google ou do Excel usa exatamente os nomes definidos
neste esquema. O codigo procura pelo texto exato de cada coluna, ignorando apenas
espacos e quebras de linha extras nas pontas.

Cada coluna tem tres partes: a chave usada no codigo, o texto que aparece na
planilha e se e obrigatoria. Nao ha aceitacao por apelidos.
"""
from __future__ import annotations

import csv
import datetime
import io
import re
import sys
import unicodedata
from collections import namedtuple
from pathlib import Path

# chave, rotulo (texto exato da coluna), obrigatoria
Coluna = namedtuple("Coluna", "chave rotulo obrigatoria", defaults=(False,))


COLUNAS = {
    "pessoas": [
        Coluna("nome", "Nome completo", True),
        Coluna("vinculo", "Vínculo", True),
        Coluna("cargo", "Função", True),
        Coluna("formacao", "Formação", True),
        Coluna("formacao_detalhe", "Formação detalhada", False),
        Coluna("apresentacao", "Apresentação", False),
        Coluna("interesses", "Interesses de pesquisa", False),
        Coluna("linkedin", "LinkedIn", False),
        Coluna("email", "E-mail", False),
        Coluna("foto", "Foto", False),
        Coluna("cargo_en", "Função em inglês", False),
        Coluna("formacao_en", "Formação em inglês", False),
        Coluna("formacao_detalhe_en", "Formação detalhada em inglês", False),
        Coluna("apresentacao_en", "Apresentação em inglês", False),
        Coluna("interesses_en", "Interesses de pesquisa em inglês", False),
        Coluna("exibir", "Exibir", False),
    ],
    "publicacoes": [
        Coluna("titulo", "Título", True),
        Coluna("autores", "Autores, na ordem", True),
        Coluna("veiculo", "Revista ou evento", True),
        Coluna("local", "Detalhes (volume, número, páginas, editora)", True),
        Coluna("data", "Data da publicação", True),
        Coluna("url", "Endereço do artigo (DOI ou link)", True),
        Coluna("resumo", "Resumo", True),
        Coluna("resumo_curto", "Resumo curto", False),
        Coluna("citacao", "Como citar, em LaTeX", True),
        Coluna("imagem", "Imagem de destaque", False),
        Coluna("figura1", "Figura 1", False),
        Coluna("legenda1", "Legenda da figura 1", False),
        Coluna("figura2", "Figura 2", False),
        Coluna("legenda2", "Legenda da figura 2", False),
        Coluna("legenda1_en", "Legenda da figura 1 em inglês", False),
        Coluna("legenda2_en", "Legenda da figura 2 em inglês", False),
        Coluna("resumo_en", "Resumo em inglês", False),
        Coluna("resumo_curto_en", "Resumo curto em inglês", False),
        Coluna("titulo_en", "Título em inglês", False),
        Coluna("exibir", "Exibir", False),
    ],
    "noticias": [
        Coluna("titulo", "Título", True),
        Coluna("veiculo", "Veículo", True),
        Coluna("data", "Data", True),
        Coluna("url", "Endereço da matéria", True),
        Coluna("resumo", "Resumo", True),
        Coluna("imagem", "Imagem", False),
        Coluna("titulo_en", "Título em inglês", False),
        Coluna("resumo_en", "Resumo em inglês", False),
        Coluna("url_en", "Endereço da matéria em inglês", False),
        Coluna("exibir", "Exibir", False),
    ],
    "cursos": [
        Coluna("titulo", "Nome do curso", True),
        Coluna("titulo_en", "Nome do curso em inglês", False),
        Coluna("nivel", "Nível ou programa", True),
        Coluna("nivel_en", "Nível ou programa em inglês", False),
        Coluna("professor", "Professor(es)", True),
        Coluna("carga_horaria", "Carga horária", True),
        Coluna("aulas", "Horário e formato das aulas", True),
        Coluna("aulas_en", "Horário e formato das aulas em inglês", False),
        Coluna("oferta", "Período de oferta", True),
        Coluna("oferta_en", "Período de oferta em inglês", False),
        Coluna("url", "Página do curso", True),
        Coluna("url_en", "Página do curso em inglês", False),
        Coluna("imagem", "Imagem ilustrativa", False),
        Coluna("exibir", "Exibir", False),
    ],
    "galeria": [
        Coluna("imagem", "Imagem", True),
        Coluna("legenda", "Legenda em português", True),
        Coluna("legenda_en", "Legenda em inglês", False),
        Coluna("exibir", "Exibir", False),
    ],
}
COLUNAS["galeria_fotos"] = COLUNAS["galeria"]

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


# Utilidades

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


def deve_exibir(valor: str | bool | None) -> bool:
    """Interpreta o valor da coluna 'Exibir'.

    Por padrao, itens sao exibidos (celula vazia ou sem a coluna = True).
    Valores negativos (Ocultar, Nao, Nao exibir, Esconder, False, Falso, 0)
    ocultam o item da publicacao no site.
    """
    if valor is None:
        return True
    if isinstance(valor, bool):
        return valor
    v = normalizar(str(valor))
    if not v:
        return True
    if v in ("false", "falso", "nao", "nao exibir", "ocultar", "esconder", "0"):
        return False
    return True


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


# Leitura

def mapa_de_colunas(tabela: str, cabecalhos: list[str]) -> dict[str, str]:
    """De qual cabecalho da planilha sai cada chave do esquema."""
    por_rotulo = {coluna.rotulo.strip(): coluna.chave for coluna in COLUNAS[tabela]}
    mapa = {}
    for cabecalho in cabecalhos:
        h_limpo = (cabecalho or "").strip()
        chave = por_rotulo.get(h_limpo)
        if chave and chave not in mapa:
            mapa[chave] = cabecalho
    desconhecidos = [c for c in cabecalhos
                     if (c or "").strip() not in por_rotulo
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
                elif t == "b":
                    val = "TRUE" if v is not None and v.text == "1" else "FALSE"
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
        if not any(dado.values()):
            continue
        if not deve_exibir(dado.get("exibir", "")):
            continue
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
            if not slug_valido(dado["slug"]):
                raise ErroDeConteudo(f"{caminho.name}, linha {numero}: endereco invalido: {dado['slug']!r}")
            if dado["slug"] != simples:
                print(f"aviso: {tabela}: {simples!r} ja estava em uso; linha {numero} "
                      f"virou {dado['slug']!r}")
            linhas.append(dado)
        elif tabela in ("galeria", "galeria_fotos"):
            raw_imgs = dado["imagem"]
            if eh_endereco(raw_imgs):
                urls = [u.strip() for u in re.split(r",\s*(?=https?://)|[\r\n]+", raw_imgs) if u.strip()]
            else:
                urls = [u.strip() for u in re.split(r"[\r\n]+|,\s*", raw_imgs) if u.strip()]
            if not urls:
                urls = [raw_imgs]

            if len(urls) > 1:
                linhas_pt = [p.strip() for p in re.split(r"[\r\n]+|[|;]", dado.get("legenda", "")) if p.strip()]
                linhas_en = [p.strip() for p in re.split(r"[\r\n]+|[|;]", dado.get("legenda_en", "")) if p.strip()]
            else:
                linhas_pt = [dado.get("legenda", "")]
                linhas_en = [dado.get("legenda_en", "")]

            for idx, img_val in enumerate(urls):
                item_dado = dict(dado)
                item_dado["imagem"] = img_val
                if len(urls) > 1:
                    item_dado["legenda"] = linhas_pt[idx] if idx < len(linhas_pt) else (linhas_pt[0] if linhas_pt else "")
                    item_dado["legenda_en"] = linhas_en[idx] if idx < len(linhas_en) else (linhas_en[0] if linhas_en else "")

                texto_base = item_dado.get("legenda") or Path(img_val).stem or f"foto-{numero}-{idx + 1}"
                simples = slugificar(texto_base)
                if not simples:
                    simples = f"foto-{numero}-{idx + 1}"
                item_dado["slug"] = endereco_unico(simples, usados)
                if not slug_valido(item_dado["slug"]):
                    raise ErroDeConteudo(f"{caminho.name}, linha {numero}: endereco invalido: {item_dado['slug']!r}")
                linhas.append(item_dado)
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



# Linha de comando

def perguntas(tabelas_: list[str]) -> int:
    """Os textos que a planilha tem de usar. Quem monta a planilha copia daqui."""
    for tabela in tabelas_:
        if tabela not in COLUNAS:
            print(f"tabela desconhecida: {tabela!r}. Use " + ", ".join(COLUNAS), file=sys.stderr)
            return 2
        print(f"\n{tabela}")
        for coluna in COLUNAS[tabela]:
            marca = "obrigatoria" if coluna.obrigatoria else "opcional   "
            print(f"  {marca}  {coluna.rotulo}")
    return 0


def conferir(tabela: str, cabecalhos: list[str]) -> int:
    """Confere a linha de titulo de uma planilha contra o esquema."""
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
        print(f"  ok         {coluna.rotulo!r} <- {chegou!r}")
    if faltando:
        print("\nSem as perguntas obrigatorias nao da para publicar: "
              + ", ".join(repr(f) for f in faltando))
        print("Ponha esse texto exato na planilha, conforme o esquema em tabelas.py.")
        return 1
    print("\nTodas as perguntas obrigatorias chegaram.")
    return 0


def main(argv: list[str]) -> int:
    uso = ("uso:\n"
           "  python3 scripts/tabelas.py perguntas [pessoas|publicacoes|noticias|cursos|galeria]\n"
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
            if not conteudo.strip():
                print("nada para conferir", file=sys.stderr)
                return 2
            corte = "\t" if "\t" in conteudo else ","
            cabecalhos = [c.strip() for c in next(csv.reader(io.StringIO(conteudo), delimiter=corte), [])]
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
            elif caminho:
                with caminho.open(encoding="utf-8-sig", newline="") as fh:
                    conteudo_amostra = fh.readline()
                    corte = "\t" if "\t" in conteudo_amostra else ","
                    fh.seek(0)
                    cabecalhos = [c.strip() for c in next(csv.reader(fh, delimiter=corte), [])]
            else:
                conteudo = origem
                if not conteudo.strip():
                    print("nada para conferir", file=sys.stderr)
                    return 2
                corte = "\t" if "\t" in conteudo else ","
                cabecalhos = [c.strip() for c in next(csv.reader(io.StringIO(conteudo), delimiter=corte), [])]
        return conferir(tabela, cabecalhos)
    print(uso)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
