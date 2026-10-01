# As tabelas do GAIA Lab

Estas tabelas são a fonte da verdade do conteúdo do site. Cada uma é uma planilha
do Google, alimentada por um formulário, e a cópia versionada aqui em `dados/` é
baixada pelo job `scripts/sincronizar.py`. Nada em `people/`, `publications/`,
`news/` ou `courses/` deve ser editado à mão: tudo é gerado por `scripts/gerar_conteudo.py`.

O que importa para quem preenche é o **texto da pergunta**: o cabeçalho da planilha
é o próprio texto do formulário, e é por ele que o gerador encontra cada campo
(`scripts/tabelas.py`). Renomear uma pergunta pede ajuste lá; o job avisa quando
chega uma coluna que não conhece.

Quem preenche manda **texto corrido, sem sintaxe**. Quem monta os blocos da página
(ficha de autores, figuras, "Como citar", botões, cartões) é o gerador. A única resposta com
sintaxe é "Como citar", que vai em LaTeX ou BibTeX.

## Formulário da equipe → `pessoas.csv`

| Pergunta | Obrigatória | O que vira na página |
|---|---|---|
| Nome completo | sim | título, nome e sobrenome, endereço da página |
| Vínculo (Professor, Pós-doutorado, Doutorado, Mestrado, Graduação, Alumni) | sim | em qual listagem a pessoa aparece |
| Função | sim | linha abaixo do nome |
| Formação | sim | campo de formação do perfil |
| Formação detalhada | não | itens da seção Formação, um por linha |
| Apresentação | não | primeiro parágrafo do perfil |
| Interesses de pesquisa | não | seção Interesses |
| LinkedIn | não | botão do perfil |
| E-mail | não | botão de e-mail |
| Foto | não | foto do perfil; sem ela, entra o desenho padrão |

## Formulário de artigos → `publicacoes.csv`

| Pergunta | Obrigatória | O que vira na página |
|---|---|---|
| Título | sim | título, cartão da listagem, endereço da página |
| Autores, na ordem | sim | ficha de autores |
| Revista ou evento | sim | veículo no cartão |
| Detalhes (volume, número, páginas, editora) | sim | complemento da linha Publicação |
| Data da publicação | sim | data e data por extenso nos dois idiomas |
| Endereço do artigo (DOI ou link) | sim | destino do botão e da miniatura |
| Resumo | sim | seção Resumo |
| Resumo curto | não | frase do cartão; em branco, o gerador usa a primeira frase do Resumo |
| Como citar, em LaTeX | sim | bloco Como citar (BibTeX também é aceito) |
| Imagem de destaque | não | miniatura do cartão e da página |
| Figura 1 e Figura 2 | não | figuras do artigo |
| Legenda da figura 1 e da figura 2 | não | legendas das figuras |
| Resumo em inglês, Resumo curto em inglês | não | versão inglesa; em branco, a página inglesa reusa o português |

## Formulário de notícias → `noticias.csv`

| Pergunta | Obrigatória | O que vira na página |
|---|---|---|
| Título | sim | título do cartão e da página |
| Veículo | sim | veículo mostrado no cartão (ex.: `FGV`) |
| Data | sim | data e data por extenso |
| Endereço da matéria | sim | destino do botão e do cartão |
| Resumo | sim | resumo do cartão e do corpo |
| Imagem | não | imagem do cartão |
| Título em inglês, Resumo em inglês, Endereço da matéria em inglês | não | versão inglesa; em branco, reusa o português |

## Formulário de cursos → `cursos.csv`

| Pergunta | Obrigatória | O que vira na página |
|---|---|---|
| Nome do curso | sim | título da disciplina no cartão em português |
| Nome do curso em inglês | sim | título da disciplina no cartão em inglês |
| Nível ou programa | sim | nível acadêmico e programa em português |
| Nível ou programa em inglês | sim | nível acadêmico e programa em inglês |
| Professor(es) | sim | nome do(s) docente(s) (reutilizado nos dois idiomas) |
| Carga horária | sim | carga horária total da disciplina (ex: `60h`, nos dois idiomas) |
| Horário e formato das aulas | sim | dias, horários e formato em português |
| Horário e formato das aulas em inglês | sim | dias, horários e formato em inglês |
| Período de oferta | sim | período letivo de oferta em português |
| Período de oferta em inglês | sim | período letivo de oferta em inglês |
| Página do curso | sim | endereço oficial com o programa da disciplina (botão "Página do curso") |
| Página do curso em inglês | sim | versão em inglês do endereço (botão "Course page") |
| Imagem ilustrativa | não | ilustração da disciplina (16:9); sem ela, entra o SVG padrão do laboratório |

## O que o gerador faz sozinho

- Endereço da página, a partir do título ou do nome: sem acento, minúsculo, só
  letra, número e hífen, cortado em 60 caracteres na última palavra inteira. Título
  ou nome repetido ganha sufixo `-1`, `-2`, `-3`..., na ordem da planilha, e o corte
  já desconta o sufixo, para o endereço inteiro caber no limite.
- Nome e sobrenome, a partir do nome completo.
- Data por extenso nos dois idiomas (`Abril de 2026`, `April 2026`, `16 de julho de 2025`).
- Rótulo do botão, fixo por tipo de página, e a ficha da publicação e do curso.
- Primeira frase do resumo, quando não vem resumo curto para o cartão.
- Regra do site de não usar travessão no texto publicado. A troca só não acontece
  no bloco "Como citar", que é código.

## Imagens

O formulário de upload grava na célula o endereço do arquivo no Drive.
`scripts/baixar_imagens.py` baixa esse arquivo e salva na pasta do item com o nome
que o site espera (`people/<slug>/avatar.*`, `publications/<slug>/miniatura.*`,
`news/<slug>/imagem.*`, `courses/images/<slug>.*`), então quem preenche não precisa
saber nome de arquivo nem caminho. Para o download funcionar sem senha, a pasta de respostas
precisa estar compartilhada como "qualquer pessoa com o link"; sem isso o Google devolve a página
de login e o job para, em vez de publicar a página de login como se fosse a foto.

## Regras que o job garante

- Planilha vazia, página de login em HTML, pergunta obrigatória sem coluna ou
  tabela sem linha de dados são recusados antes de qualquer substituição.
- Comparação é feita pelo conteúdo interpretado, não pelos bytes: reordenar linhas
  ou mexer em formatação não gera commit.
- Linha removida da planilha remove a página e a pasta do item, com as imagens
  junto: pasta que fica para trás ocupa um endereço que pode ser de quem entrou
  depois.
- Colunas que o Google cria sozinho (carimbo de data e hora, e-mail de quem
  respondeu, Score) são ignoradas.
- A ordem das listagens é por data em publicações e notícias e por nome em pessoas,
  não pela ordem das linhas na planilha.

## Endereços das planilhas

Em `dados/fontes.conf`, no formato `tabela=endereço`. Enquanto o endereço não for
preenchido, o job ignora aquela tabela e o site usa o CSV versionado aqui.
