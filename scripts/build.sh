#!/usr/bin/env bash
# Gera o site completo em docs/: português na raiz e inglês em docs/en/.
set -euo pipefail
cd "$(dirname "$0")/.."

quarto render --profile pt
quarto render --profile en

# As páginas com sufixo de idioma só existem para o "quarto preview";
# a versão publicada usa apenas os nomes finais (sem .pt/.en)
find docs -name '*.pt.html' -delete -o -name '*.en.html' -delete

# Impede o processamento Jekyll no GitHub Pages
touch docs/.nojekyll
