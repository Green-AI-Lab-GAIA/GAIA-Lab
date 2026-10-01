#!/usr/bin/env bash
#
# Rodada do site do GAIA Lab: le as planilhas publicadas em dados/fontes.conf,
# atualiza os CSVs locais, baixa as imagens novas, gera as paginas das tabelas,
# builda o site e publica no GitHub. E o que o cron da maquina do laboratorio chama;
# o trabalho em si esta em scripts/sincronizar.py.
#
#   bash scripts/atualizar.sh          rodada completa, empurra para o GitHub
#   bash scripts/atualizar.sh --seco   so relata o que a planilha tem, nao grava nada
#
# Linha de cron sugerida (todo dia as 6h da manha, saida num log que so cresce):
#   0 6 * * * /bin/bash "$HOME/gaia-site/scripts/atualizar.sh" >> "$HOME/gaia-site.log" 2>&1

set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

# O cron nao herda o PATH da sessao, e o quarto costuma morar em ~/.local/bin.
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
# Sem __pycache__: bytecode escrito a cada rodada sujaria a arvore e travaria o job.
export PYTHONDONTWRITEBYTECODE=1

for ferramenta in git python3 quarto; do
    command -v "$ferramenta" >/dev/null || { echo "falta $ferramenta no PATH" >&2; exit 1; }
done

# Uma rodada por vez: o build demora mais que o intervalo entre duas chamadas.
exec 9>"$RAIZ/.git/atualizar.lock"
flock -n 9 || { echo "ja tem uma rodada em andamento, esta sai"; exit 0; }

echo "== $(date '+%F %T') rodada em $RAIZ, ramo $(git rev-parse --abbrev-ref HEAD)"
python3 scripts/sincronizar.py --push "$@"
echo "== $(date '+%F %T') fim"
