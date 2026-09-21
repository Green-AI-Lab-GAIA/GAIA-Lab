# Scripts do site

## Conteúdo a partir das tabelas

```bash
python3 scripts/baixar_imagens.py      # imagens do Drive -> pasta de cada item
python3 scripts/gerar_conteudo.py      # tabelas -> people/, publications/, news/
python3 scripts/sincronizar.py         # baixa, valida, gera, builda e commita
python3 scripts/sincronizar.py --push  # idem, publicando
python3 scripts/sincronizar.py --seco  # só relata o que mudaria
python3 scripts/sincronizar.py --autoteste   # exercita validação e comparação
```

O gerador é idempotente: rodar duas vezes com as mesmas tabelas não muda nada.
Ele valida cada linha e falha apontando o problema, em vez de publicar página
incompleta. O esquema das colunas, com o texto de cada pergunta do formulário,
está em `scripts/tabelas.py`.

## Imagens

`scripts/baixar_imagens.py` lê o endereço que o formulário gravou na célula, baixa
o arquivo e salva na pasta do item com o nome que o site espera
(`people/<pessoa>/avatar.jpg`, `publications/<artigo>/miniatura.png`,
`news/<noticia>/imagem.jpg`). O que já foi baixado fica anotado em
`dados/imagens.json`, então a rodada seguinte não baixa de novo.

Para o download funcionar sem senha, a pasta de respostas do formulário precisa
estar compartilhada como "qualquer pessoa com o link". Se não estiver, o Google
devolve a página de login no lugar da imagem: o script reconhece isso e para,
em vez de gravar a página de login como se fosse a foto.

## Job automático

`scripts/sincronizar.py` baixa cada planilha publicada em CSV (endereços em
`dados/fontes.conf`), recusa o que vier inválido, compara com o CSV versionado,
substitui só quando mudou, baixa as imagens, roda o gerador, faz o build com
`scripts/build.sh` e commita. O push só acontece com `--push`.

A validação olha o texto das perguntas, não nomes internos: se uma pergunta
obrigatória sumir da planilha, o job para dizendo qual pergunta faltou. Colunas
que o formulário cria sozinho (carimbo de data e hora, e-mail de quem respondeu,
Score) são ignoradas.

Antes de commitar, o job confere a árvore de trabalho: se houver alteração fora
de `dados/`, `people/`, `publications/`, `news/` e `docs/`, ele para e avisa, para
não misturar trabalho de gente com trabalho de robô.

### No cron

```cron
# roda às 7h e às 19h, publicando o que mudou
MAILTO=responsavel@fgv.br
0 7,19 * * * cd /caminho/website && flock -n /tmp/site.lock python3 scripts/sincronizar.py --push
```

Saída vazia e código 0 é o caso normal. Qualquer falha imprime no stderr e sai com
código diferente de zero, e o próprio cron avisa o `MAILTO` com essa saída: é assim
que um job silenciosamente quebrado aparece.

Se a máquina não estiver ligada no horário, o cron simplesmente não roda e aquele
horário se perde. Para recuperar a execução perdida, use um timer do systemd, que
também organiza log e reinício:

```ini
# ~/.config/systemd/user/site-sincronizar.service
[Unit]
Description=Sincroniza o conteudo do site com as planilhas

[Service]
Type=oneshot
WorkingDirectory=/caminho/website
ExecStart=/usr/bin/python3 scripts/sincronizar.py --push
```

```ini
# ~/.config/systemd/user/site-sincronizar.timer
[Unit]
Description=Dispara a sincronizacao duas vezes por dia

[Timer]
OnCalendar=07,19:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
systemctl --user enable --now site-sincronizar.timer
```

`Persistent=true` é o que faz a execução perdida acontecer assim que a máquina
voltar.

## Build

```bash
bash scripts/build.sh
```

Renderiza os dois idiomas, limpa os `.pt.html`/`.en.html` intermediários e recria
`docs/.nojekyll`. Os assets de pesquisa (mapas, figuras, fotos) vêm de
`tools/make_website_assets.py`, que fica fora deste repositório.
