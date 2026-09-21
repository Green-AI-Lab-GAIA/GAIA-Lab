# As três tabelas

Estas tabelas são a fonte da verdade do conteúdo do site. Elas vivem em planilhas
do Google Sheets e a cópia versionada aqui em `dados/` é baixada pelo job
`scripts/sincronizar.py`. Nenhum arquivo de `people/`, `publications/` ou `news/`
deve ser editado à mão: todos são gerados por `scripts/gerar_conteudo.py`.

Uma linha por item. Coluna vazia é permitida onde indicado; nas demais, o gerador
falha e aponta a linha, em vez de publicar torto.

## pessoas.csv

| Coluna | O que é |
|---|---|
| `slug` | pasta da pessoa em `people/`, minúsculo com hífen (ex.: `dario-oliveira`) |
| `grupo` | `professor`, `postdoc`, `phd`, `masters`, `undergrad` ou `alumni`; define em qual listagem a pessoa aparece |
| `nome` | nome completo, como aparece no cartão e no título da página |
| `primeiro`, `ultimo` | nome e sobrenome, usados em ordenações e no rodapé do perfil |
| `imagem` | arquivo dentro da pasta da pessoa (ex.: `avatar.jpg`) |
| `cargo_pt`, `cargo_en` | função, uma linha (ex.: `Assistente de Pesquisa`) |
| `formacao_pt`, `formacao_en` | formação resumida, uma linha (ex.: `Doutorando, FGV EMAp`) |
| `linkedin` | endereço do perfil; obrigatório |
| `email` | endereço sem `mailto:`; pode ficar vazio |
| `bio_pt`, `bio_en` | parágrafo de apresentação |
| `formacao_detalhe_pt`, `formacao_detalhe_en` | itens da seção Formação, separados por `\|` |
| `interesses_pt`, `interesses_en` | texto da seção Interesses |

## publicacoes.csv

| Coluna | O que é |
|---|---|
| `slug` | pasta do artigo em `publications/` |
| `data` | data ISO (`2026-04-03`); define a ordem da listagem |
| `imagem` | miniatura dentro da pasta (ex.: `thumbnail.png`) |
| `titulo`, `titulo_en` | título; `titulo_en` vazio reaproveita `titulo` |
| `autores` | lista de autores, como aparece na página |
| `veiculo` | nome do periódico ou evento |
| `local_pt`, `local_en` | complemento do veículo, localizado (ex.: `v. 47, n. 7, p. 3213–3238 (Taylor & Francis)`) |
| `publicado_pt`, `publicado_en` | texto da data, localizado (ex.: `Abril de 2026`) |
| `resumo_pt`, `resumo_en` | resumo curto do cartão |
| `botao1_pt`, `botao1_en`, `botao1_url` | primeiro botão; o endereço também é o link da miniatura |
| `botao2_pt`, `botao2_en`, `botao2_url` | segundo botão; deixe vazio para não aparecer |
| `texto_pt`, `texto_en` | resumo longo da página; vazio reaproveita o resumo curto |

## noticias.csv

| Coluna | O que é |
|---|---|
| `slug` | pasta da notícia em `news/` |
| `data` | data ISO; define a ordem |
| `imagem` | imagem da notícia, com o caminho relativo a `publications/` quando for o caso |
| `titulo_pt`, `titulo_en` | títulos |
| `fonte_pt`, `fonte_en` | veículo (ex.: `FGV`) |
| `data_texto_pt`, `data_texto_en` | data por extenso, localizada |
| `url_pt`, `url_en` | endereço da matéria; muda entre idiomas quando o portal tem versão própria |
| `resumo_pt`, `resumo_en` | resumo do cartão |

## Regras que o job garante

- Planilha vazia, página de login em HTML, cabeçalho sem as colunas ou tabela sem
  linha de dados são recusados antes de qualquer substituição.
- Comparação é feita pelo conteúdo interpretado, não pelos bytes: reordenar linhas
  ou mexer em formatação não gera commit.
- Linha removida da planilha remove a página correspondente do site.
- A ordem das listagens do site é por nome (`sort: title`) em pessoas e por data
  (`sort: date desc`) em publicações e notícias, não pela ordem das linhas.
