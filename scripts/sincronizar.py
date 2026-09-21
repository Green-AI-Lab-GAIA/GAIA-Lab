#!/usr/bin/env python3
"""Baixa as planilhas, valida, compara com a copia local e regenera o site.

Feito para rodar no cron: baixa cada tabela publicada em CSV, recusa o que vier
invalido, compara o conteudo ja interpretado com o CSV versionado em dados/,
substitui apenas quando mudou, roda o gerador, builda e commita. O push so
acontece com --push.

Uso:
    python3 scripts/sincronizar.py              # baixa, gera, builda e commita
    python3 scripts/sincronizar.py --push       # tambem faz push
    python3 scripts/sincronizar.py --seco       # so diz o que mudaria

Saida vazia com codigo 0 e o caso normal. Qualquer falha sai com codigo diferente
de zero e mensagem no stderr, e o cron avisa o dono por e-mail (MAILTO).
"""
from __future__ import annotations

import argparse
import csv
import io
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"
FONTES = DADOS / "fontes.conf"

TABELAS = {
    "pessoas": ["slug", "grupo", "nome", "primeiro", "ultimo", "imagem", "cargo_pt", "cargo_en",
                "formacao_pt", "formacao_en", "linkedin", "email", "bio_pt", "bio_en",
                "formacao_detalhe_pt", "formacao_detalhe_en", "interesses_pt", "interesses_en"],
    "publicacoes": ["slug", "data", "imagem", "titulo", "titulo_en", "autores", "veiculo",
                    "local_pt", "local_en", "publicado_pt", "publicado_en", "resumo_pt", "resumo_en",
                    "botao1_pt", "botao1_en", "botao1_url", "botao2_pt", "botao2_en", "botao2_url",
                    "texto_pt", "texto_en"],
    "noticias": ["slug", "data", "imagem", "titulo_pt", "titulo_en", "fonte_pt", "fonte_en",
                 "data_texto_pt", "data_texto_en", "url_pt", "url_en", "resumo_pt", "resumo_en"],
}

# arquivos que o job pode mexer; qualquer outra alteracao na arvore faz o job parar
PERMITIDOS = ("dados/", "people/", "publications/", "news/", "docs/")


def aviso(texto: str) -> None:
    print(texto, file=sys.stderr)


def falhar(texto: str) -> None:
    aviso(f"erro: {texto}")
    sys.exit(1)


def agora() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def rodar(*comando: str, silencioso: bool = False) -> str:
    resultado = subprocess.run(comando, cwd=RAIZ, capture_output=True, text=True)
    if resultado.returncode != 0:
        falhar(f"{' '.join(comando)}: {resultado.stderr.strip() or resultado.stdout.strip()}")
    return "" if silencioso else resultado.stdout.strip()


def ler_fontes() -> dict:
    enderecos = {}
    if not FONTES.exists():
        falhar(f"{FONTES.relative_to(RAIZ)} nao existe")
    for linha in FONTES.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        if "=" in linha:
            nome, url = linha.split("=", 1)
            enderecos[nome.strip()] = url.strip()
    return enderecos


def baixar(url: str) -> str:
    pedido = urllib.request.Request(url, headers={"User-Agent": "gaia-lab-sincronizador"})
    with urllib.request.urlopen(pedido, timeout=60) as resposta:
        return resposta.read().decode("utf-8", errors="replace")


def interpretar(tabela: str, texto: str, origem: str) -> list[dict]:
    """Valida o que chegou e devolve as linhas. Recusa o que nao for a tabela."""
    if not texto.strip():
        falhar(f"{tabela}: {origem} veio vazio")
    if texto.lstrip().startswith("<"):
        falhar(f"{tabela}: {origem} veio como pagina HTML, provavelmente planilha despublicada")
    linhas = list(csv.DictReader(io.StringIO(texto)))
    if not linhas:
        falhar(f"{tabela}: {origem} nao tem nenhuma linha de dados")
    faltando = [c for c in TABELAS[tabela] if c not in linhas[0]]
    if faltando:
        falhar(f"{tabela}: {origem} sem as colunas {faltando}")
    if len(linhas[0]) != len(TABELAS[tabela]):
        falhar(f"{tabela}: {origem} tem {len(linhas[0])} colunas, esperadas {len(TABELAS[tabela])}")
    return [{k: (v or "").strip() for k, v in linha.items()} for linha in linhas]


def normalizar(linhas: list[dict]) -> list[dict]:
    """Compara pelo conteudo: ordem das linhas nao importa, espaco nas pontas nao conta."""
    return sorted(({k: v.strip() for k, v in linha.items()} for linha in linhas),
                  key=lambda l: l["slug"])


def gravavel(linhas: list[dict], colunas: list[str]) -> str:
    saida = io.StringIO()
    escritor = csv.DictWriter(saida, fieldnames=colunas, extrasaction="ignore", lineterminator="\n")
    escritor.writeheader()
    escritor.writerows(linhas)
    return saida.getvalue()


def comparar_com_local(tabela: str, remotas: list[dict]) -> bool:
    """Devolve True se mudou. Substitui o CSV local pelo conteudo remoto normalizado."""
    destino = DADOS / f"{tabela}.csv"
    locais = []
    if destino.exists():
        with destino.open(encoding="utf-8", newline="") as fh:
            locais = [{k: (v or "").strip() for k, v in linha.items()} for linha in csv.DictReader(fh)]
    if normalizar(locais) == normalizar(remotas):
        return False
    destino.write_text(gravavel(normalizar(remotas), TABELAS[tabela]), encoding="utf-8")
    aviso(f"{agora()} {tabela}: {len(locais)} -> {len(remotas)} linhas, CSV atualizado")
    return True


def arquivos_alterados() -> list[str]:
    """Caminhos com alteracao pendente.

    Le o git sem passar pelo strip(): o formato --porcelain comeca com dois
    caracteres de status e um espaco, e aparar a saida come o espaco da primeira
    linha e corta o caminho.
    """
    bruto = subprocess.run(("git", "status", "--porcelain", "-z"), cwd=RAIZ,
                           capture_output=True, text=True).stdout
    itens = [p for p in bruto.split("\0") if len(p) > 3]
    return [p[3:] for p in itens]


def arvore_tem_so_o_que_o_job_mexe() -> None:
    intrusos = [s for s in arquivos_alterados() if not s.startswith(PERMITIDOS)]
    if intrusos:
        falhar("arvore de trabalho com alteracao de fora do job: "
               + ", ".join(intrusos[:5])
               + " (commite ou guarde antes de rodar)")


def autoteste() -> int:
    """Exercita o que costuma dar errado no job, sem rede e sem mexer no git."""
    import shutil
    import tempfile

    global DADOS
    original, temporario = DADOS, Path(tempfile.mkdtemp())
    DADOS = temporario
    falhas = 0
    try:
        shutil.copy(original / "pessoas.csv", temporario / "pessoas.csv")
        conteudo = (temporario / "pessoas.csv").read_text(encoding="utf-8")

        ruins = {
            "planilha vazia": "",
            "pagina de login em HTML": "<!DOCTYPE html><html>Faca login</html>",
            "cabecalho sem as colunas": "nome,email\nx,y\n",
            "sem nenhuma linha": ",".join(TABELAS["pessoas"]) + "\n",
        }
        for nome, texto in ruins.items():
            try:
                interpretar("pessoas", texto, "autoteste")
                aviso(f"autoteste: {nome} deveria ser recusada")
                falhas += 1
            except SystemExit:
                pass

        linhas = interpretar("pessoas", conteudo, "autoteste")
        if comparar_com_local("pessoas", linhas):
            aviso("autoteste: conteudo igual foi tratado como mudanca")
            falhas += 1
        if comparar_com_local("pessoas", list(reversed(linhas))):
            aviso("autoteste: so a ordem das linhas mudou e foi tratado como mudanca")
            falhas += 1
        editadas = [dict(l) for l in linhas]
        editadas[0]["bio_pt"] = "Editado no autoteste."
        if not comparar_com_local("pessoas", editadas):
            aviso("autoteste: celula alterada nao foi detectada")
            falhas += 1
        with (temporario / "pessoas.csv").open(encoding="utf-8", newline="") as fh:
            gravado = list(csv.DictReader(fh))
        if len(gravado) != len(linhas) or not any(l["bio_pt"] == "Editado no autoteste." for l in gravado):
            aviso("autoteste: CSV local nao recebeu a alteracao")
            falhas += 1
    finally:
        DADOS = original
        shutil.rmtree(temporario, ignore_errors=True)

    if falhas:
        aviso(f"autoteste: {falhas} falha(s)")
        return 1
    print("autoteste: validacao e comparacao funcionando")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--push", action="store_true", help="empurra os commits para o remoto")
    ap.add_argument("--seco", action="store_true", help="nao mexe em nada, so relata")
    ap.add_argument("--fontes", default=None,
                    help="usa outro arquivo de enderecos em vez de dados/fontes.conf")
    ap.add_argument("--autoteste", action="store_true",
                    help="exercita validacao e comparacao em copias temporarias, sem git e sem rede")
    args = ap.parse_args()

    if args.autoteste:
        return autoteste()

    if args.fontes:
        global FONTES
        FONTES = Path(args.fontes).resolve()

    enderecos = ler_fontes()
    if not enderecos:
        aviso(f"{agora()} nenhuma planilha configurada em {FONTES.relative_to(RAIZ)}, nada a fazer")
        return 0

    mudou = []
    for tabela in sorted(enderecos):
        if tabela not in TABELAS:
            falhar(f"fontes.conf tem uma tabela desconhecida: {tabela}")
        remotas = interpretar(tabela, baixar(enderecos[tabela]), enderecos[tabela][:60])
        if args.seco:
            aviso(f"{agora()} {tabela}: {len(remotas)} linhas na planilha (modo seco, nada gravado)")
            continue
        if comparar_com_local(tabela, remotas):
            mudou.append(tabela)

    if args.seco:
        return 0

    arvore_tem_so_o_que_o_job_mexe()
    saida = rodar("python3", "scripts/gerar_conteudo.py")
    if saida:
        aviso(f"{agora()} {saida}")

    alterados = arquivos_alterados()
    if not alterados:
        aviso(f"{agora()} nada mudou desde a ultima rodada")
        return 0

    aviso(f"{agora()} build do site")
    rodar("bash", "scripts/build.sh")
    rodar("git", "add", "dados", "people", "publications", "news", "docs")
    resumo = ", ".join(mudou) if mudou else "conteudo"
    rodar("git", "commit", "-m", f"conteudo: atualiza {resumo} a partir das planilhas")
    if args.push:
        rodar("git", "pull", "--rebase", "--autostash")
        rodar("git", "push")
        aviso(f"{agora()} publicado")
    else:
        aviso(f"{agora()} commit local feito; use --push para publicar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
