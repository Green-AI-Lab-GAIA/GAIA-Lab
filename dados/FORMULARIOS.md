# Formulários do site, pergunta por pergunta

Documento de trabalho para montar os três formulários do Google. Cada formulário
grava numa aba da planilha, e a aba vira as páginas do site.

**A regra que não pode escapar:** o **título da pergunta** é o cabeçalho da coluna
na planilha. Ele tem de ser exatamente o que está na coluna *Pergunta* abaixo. Já a
**Descrição** fica só no formulário, aparece em cinza embaixo do enunciado e **não
chega na planilha**, então é ali que vai toda a explicação, sem risco de quebrar
nada.

Onde ficam: no cartão da pergunta, o menu de três pontinhos (⋮) tem *Descrição*.
No topo do formulário, ao lado do título, tem a descrição geral. Cada seção também
aceita uma descrição própria.

---

## Formulário 1: equipe

**Título sugerido:** GAIA Lab: quero aparecer no site

**Descrição do formulário** (cole no topo):

> Suas respostas viram a sua página no site do GAIA Lab, em português e em inglês.
> Escreva texto corrido, sem código e sem sintaxe: quem monta as seções, os botões
> e os cartões é o gerador. Nada é publicado sem passar por revisão.
>
> Antes de responder, veja as páginas já publicadas, para ver o formato:
> https://green-ai-lab-gaia.github.io/people/
>
> A foto é anexada como arquivo (não cole link): de rosto, quadrada, no mínimo
> 600×600, até 1 MB.

| Pergunta (título exato) | Tipo | Obrigatória | Descrição (cole aqui) |
|---|---|---|---|
| Nome completo | Resposta curta | sim | Como você quer aparecer no site, com nome e sobrenome. É daqui que saem o título da sua página e o endereço dela. |
| Vínculo | **Lista suspensa** | sim | Em que posição você está no grupo hoje. A escolha define em qual listagem do site a sua ficha aparece. |
| Função | Resposta curta | sim | Uma linha só, o que você faz no grupo, por exemplo: Pesquisador, Doutoranda, Iniciação Científica. Aparece embaixo do seu nome. |
| Formação | Resposta curta | sim | Uma linha só: o título mais alto e a instituição, por exemplo: Doutorado em Ciência da Computação, UFRJ. |
| Formação detalhada | **Parágrafo** | não | Opcional. Um item por linha, do mais recente ao mais antigo: aperte Enter entre um item e outro. Quem preferir tudo numa linha pode separar por barra vertical. |
| Apresentação | Parágrafo | não | Opcional. Um parágrafo curto sobre você, que vira a abertura da sua página. Pode escrever na primeira pessoa. |
| Interesses de pesquisa | Parágrafo | não | Opcional. Em que você trabalha, em texto corrido. O gerador monta os itens da seção. |
| LinkedIn | Resposta curta | não | Opcional. O endereço completo, começando com https://. Vira o botão do seu perfil. |
| E-mail | Resposta curta | não | Opcional. O e-mail de contato que você quer deixar público. Vira o botão de e-mail. |
| Foto | Envio de arquivo | não | Opcional. **Anexe o arquivo** (não cole link): foto de rosto **na proporção 1:1, quadrada**, com o rosto no centro e na metade de cima. **JPG ou PNG**, no mínimo 600×600, até 1 MB. Foto retangular é recortada, não esticada. Sem foto, entra o avatar genérico do site. |
| Função em inglês | Resposta curta | não | Opcional, em inglês. Em branco, a página em inglês reusa o português. |
| Formação em inglês | Resposta curta | não | Opcional, em inglês. Em branco, a página em inglês reusa o português. |
| Formação detalhada em inglês | Parágrafo | não | Opcional, em inglês. Mesma regra de Formação detalhada: um item por linha. Em branco, reusa o português. |
| Apresentação em inglês | Parágrafo | não | Opcional, em inglês. Em branco, a página em inglês reusa o português. |
| Interesses de pesquisa em inglês | Parágrafo | não | Opcional, em inglês. Em branco, a página em inglês reusa o português. |

**Opções da pergunta Vínculo**, nesta ordem e com este texto:

| Opção | Onde a pessoa aparece no site |
|---|---|
| Professor | seção Professor |
| Pós-doutorado | seção Pós-Doutorado (hoje comentada, ativa quando houver alguém) |
| Doutorado | seção Doutorado |
| Mestrado | seção Mestrado |
| Graduação | seção Graduação |
| Colaborador | seção Colaborador |
| Alumni | seção Alumni |

Quem não tem vínculo com a FGV, mas pesquisa com o grupo (pesquisador convidado,
parceiro de outra instituição), é **Colaborador**. Opção fora dessa lista
não entra no site: o job para e avisa qual valor não reconheceu.

---

## Formulário 2: artigos

**Título sugerido:** GAIA Lab: envio de artigo

**Descrição do formulário** (cole no topo):

> Cada resposta vira a página de um artigo publicado pelo grupo, em português e em
> inglês. Escreva texto corrido, sem sintaxe; só o campo de citação e as legendas
> das figuras aceitam LaTeX.
>
> Antes de responder, veja os artigos já publicados, para ver o formato:
> https://green-ai-lab-gaia.github.io/publications/
>
> Datas no formato DD-MM-AAAA (exemplo: 24-04-2026). As imagens são anexadas como
> arquivo (não cole link).

| Pergunta (título exato) | Tipo | Obrigatória | Descrição (cole aqui) |
|---|---|---|---|
| Título | Resposta curta | sim | Título oficial do artigo, independentemente do idioma. Como no artigo, sem ponto no fim. |
| Autores, na ordem | Resposta curta | sim | Os nomes na ordem de assinatura do artigo, separados por vírgula. |
| Revista ou evento | Resposta curta | sim | O nome por extenso, como aparece na publicação, por exemplo: Nature Climate Change, NeurIPS 2026. |
| Detalhes (volume, número, páginas, editora) | Resposta curta | sim | Só os detalhes bibliográficos: volume, número, páginas, editora. No caso de livro, o editor; no caso de congresso, o nome do evento. |
| Data da publicação | Resposta curta | sim | No formato DD-MM-AAAA, por exemplo: 24-04-2026. Se a planilha insistir em converter em data, formate a coluna como texto. |
| Endereço do artigo (DOI ou link) | Resposta curta | sim | O endereço completo, começando com https://. Vale o DOI em forma de link. Vira o destino do botão e do cartão. |
| Resumo | Parágrafo | sim | O resumo do artigo, em texto corrido. Pode ser longo: o site deixa como parágrafo. |
| Resumo curto | Parágrafo | não | Opcional. Uma frase para o cartão da listagem. Em branco, o gerador usa a primeira frase do Resumo. |
| Como citar, em LaTeX | Parágrafo | sim | A única resposta com sintaxe: cole a entrada BibTeX ou o trecho em LaTeX. Sai num bloco de código na página. |
| Imagem de destaque | Envio de arquivo | não | Opcional. **Anexe o arquivo**: é o print da primeira página do artigo, ou uma imagem que o represente. Vira a miniatura do cartão e a imagem de abertura da página. |
| Figura 1 | Envio de arquivo | não | Opcional. **Anexe o arquivo da Figura 1**: ela entra depois do Resumo. Em branco, o artigo fica só com a imagem de destaque. |
| Legenda da figura 1 | Resposta curta | não | Opcional. A legenda da Figura 1, em uma linha. **Aceita sintaxe LaTeX** (veja os exemplos já publicados). Obrigatória se você anexou a Figura 1. |
| Figura 2 | Envio de arquivo | não | Opcional. **Anexe o arquivo da Figura 2**: ela entra depois da Figura 1. Em branco, o artigo fica sem ela. |
| Legenda da figura 2 | Resposta curta | não | Opcional. A legenda da Figura 2, em uma linha. **Aceita sintaxe LaTeX** (veja os exemplos já publicados). Obrigatória se você anexou a Figura 2. |
| Resumo em inglês | Parágrafo | não | Opcional, em inglês. Em branco, a página em inglês reusa o português. |
| Resumo curto em inglês | Parágrafo | não | Opcional, em inglês. Em branco, a página em inglês reusa o português. |

---

## Formulário 3: notícias

**Título sugerido:** GAIA Lab: envio de notícia

**Descrição do formulário** (cole no topo):

> Cada resposta vira a página de uma notícia sobre o grupo, em português e em
> inglês: matéria, divulgação, prêmio, participação em evento. Escreva texto
> corrido, sem sintaxe.
>
> Antes de responder, veja as notícias já publicadas, para ver o formato:
> https://green-ai-lab-gaia.github.io/publications/#noticias
>
> Datas no formato DD-MM-AAAA (exemplo: 24-04-2026).
>
> A imagem é anexada como arquivo (não cole link), deitada e na proporção 16:9
> (por exemplo 1600×900).

| Pergunta (título exato) | Tipo | Obrigatória | Descrição (cole aqui) |
|---|---|---|---|
| Título | Resposta curta | sim | O título da matéria, como saiu no veículo. Vira o título do cartão e da página. |
| Veículo | Resposta curta | sim | Onde a matéria saiu, em uma palavra ou duas: FGV, Folha, Agência Brasil. |
| Data | Resposta curta | sim | No formato DD-MM-AAAA, por exemplo: 24-04-2026. Se a planilha insistir em converter em data, formate a coluna como texto. |
| Endereço da matéria | Resposta curta | sim | O endereço completo da matéria, começando com https://. Vira o destino do botão e do cartão. |
| Resumo | Parágrafo | sim | Duas ou três frases sobre a matéria, em texto corrido. Vira o cartão e a abertura da página. |
| Imagem | Envio de arquivo | não | Opcional. **Anexe o arquivo**, deitada e na proporção 16:9 (por exemplo 1600×900): é assim que ela aparece no cartão e na abertura da página. |
| Título em inglês | Resposta curta | não | Opcional, em inglês. Em branco, a página em inglês reusa o português. |
| Resumo em inglês | Parágrafo | não | Opcional, em inglês. Em branco, a página em inglês reusa o português. |
| Endereço da matéria em inglês | Resposta curta | não | Opcional, em inglês, para quando a matéria também saiu em inglês. Em branco, reusa o português. |

---

## Formulário 4: cursos

**Título sugerido:** GAIA Lab: cadastro de curso ou disciplina

**Descrição do formulário** (cole no topo):

> Cada resposta vira o cartão de uma disciplina ofertada por integrantes do GAIA Lab na FGV EMAp, exibido em português e inglês no site do laboratório. Escreva texto corrido, sem código e sem sintaxe.
>
> Veja as páginas já publicadas para ter exemplos visuais de como preencher: https://green-ai-lab-gaia.github.io/courses/
>
> Este formulário é editável: guarde o link da sua resposta (aparece depois de enviar) para poder editar este curso mais tarde.
>
> A publicação é automática, mas não é instantânea: o site se atualiza numa rotina que roda todo sábado à 0h. Confira e revise a informação preenchida antes de enviar. Mesmo o deploy do site sendo automático, você pode ter que esperar até uma semana para que uma correção seja publicada.
>
> A imagem ilustrativa da disciplina é opcional e anexada como arquivo: deitada, na proporção 16:9 ou 16:10 (por exemplo 1600×900 ou 800×500), JPG ou PNG, até 10 MB. Se não anexar nenhuma imagem, o site usará a ilustração padrão do laboratório.

| Pergunta (título exato) | Tipo | Obrigatória | Descrição (cole aqui) |
|---|---|---|---|
| Nome do curso | Resposta curta | sim | Nome oficial da disciplina ou curso em português. Vira o título no cartão do site. Exemplo: Aprendizado Profundo. |
| Nome do curso em inglês | Resposta curta | sim | Official course title in English. Aparece na versão em inglês do site. Exemplo: Deep Learning. |
| Nível ou programa | Resposta curta | sim | Nível de ensino e programa acadêmico que oferta o curso. Exemplo: Graduação em Ciência de Dados e IA, EMAp. |
| Nível ou programa em inglês | Resposta curta | sim | Academic program and education level in English. Exemplo: Undergraduate program in Data Science and AI, EMAp. |
| Professor(es) | Resposta curta | sim | Nome do(s) docente(s) responsável(is) pela disciplina (usado em português e inglês). Exemplo: Dário Oliveira. |
| Carga horária | Resposta curta | sim | Carga horária total da disciplina (usada em português e inglês). Exemplo: 60h. |
| Horário e formato das aulas | Resposta curta | sim | Dias da semana, horários e se as aulas são presenciais ou online. Exemplo: presenciais, terças e quintas, das 9h20 às 11h (horário de Brasília). |
| Horário e formato das aulas em inglês | Resposta curta | sim | Class schedule and format in English. Exemplo: in person, Tuesdays and Thursdays, 9:20–11:00 am (Brasília time). |
| Período de oferta | Resposta curta | sim | Quando a disciplina é ofertada regularmente ao longo do ano letivo. Exemplo: todo segundo semestre. |
| Período de oferta em inglês | Resposta curta | sim | Offering term/period in English. Exemplo: every second semester. |
| Página do curso | Resposta curta | sim | Endereço oficial (URL começando com https://) com ementa, grade curricular ou detalhes do programa. Exemplo: https://emap.fgv.br/curso/doutorado#aba-disciplinas. |
| Página do curso em inglês | Resposta curta | sim | Official course page URL in English. Se não houver versão em inglês, repita o link em português. Exemplo: https://emap.fgv.br/curso/doutorado#aba-disciplinas. |
| Imagem ilustrativa | Resposta curta | não | Opcional. Link ou arquivo no Drive da imagem/ícone representativo (proporção 16:9 ou 16:10, SVG/PNG/JPG). Sem imagem, o site usa a ilustração padrão. |

---

## Depois de montar

### Montar por script (recomendado)

`apps_script_formularios.gs` monta as perguntas das três formas a partir da
especificação acima, sem clicar em nada: em [script.google.com](https://script.google.com),
*Novo projeto*, cole o arquivo, rode `montar()` e autorize. Ele casa pergunta
pelo título, então pergunta que já existe é mantida — só tipo e obrigatória
mudam — e o que falta é criado na ordem da especificação. O **texto de apoio** só
é escrito em pergunta nova, ou em pergunta que está sem texto: o que já está na
tela fica como está, porque é ali que mora o negrito e o itálico (ver adiante). A
função `conferir()` lista o que está lá sem mexer em nada.

No formulário de membros ele **não troca tipo nem obrigatoriedade**: quem monta
aquele formulário é o Thiago, e as escolhas de lá valem. *Função* e *Função em
inglês* são escolha de propósito, para padronizar a entrada, com a opção
*Other* onde o Alumni com emprego fora do laboratório escreve o cargo. *Foto* é
obrigatória; *E-mail* é opcional. Ali o script só escreve o texto de apoio das
perguntas novas, ou das que estiverem sem texto.

Nos formulários de notícias e de artigos, que estavam vazios, ele cria as
perguntas na ordem da especificação. Tipo de pergunta o Apps Script não troca no
lugar: apaga e recria na mesma posição - o que tira a coluna da planilha se já
houver resposta gravada, então rode antes de divulgar o formulário.

Três limites da API que o script já contorna, porque custaram uma rodada cada:
`addFileUploadItem` **não existe**, então as perguntas de imagem entram como
resposta curta, com o endereço começando em `https://` (o site lê igual); quem
preferir upload troca o tipo na tela, em Editar. `getItems()` devolve item
genérico, sem `setRequired` nem `isRequired` - é preciso `asTextItem()`,
`asParagraphTextItem()`, `asMultipleChoiceItem()` para chegar no item tipado.
E `getType()` devolve as strings `TEXT`, `PARAGRAPH_TEXT`, `MULTIPLE_CHOICE`,
`LIST`, `FILE_UPLOAD`, não as constantes de `FormApp.ItemType`.

**Negrito e itálico: só pela tela.** Não há método nenhum de formatação no serviço
Forms do Apps Script - `setHelpText()` recebe `String`, e `getHelpText()` devolve
`String`, sem a formatação. Quem escreve negrito, itálico, sublinhado, link ou
lista é a interface do Forms (recurso de 2022). Como a API não lê a formatação, o
`montar()` não reescreve o texto de apoio de pergunta que já existe: se reescrevesse
às cegas, apagaria o trabalho feito à mão. Para refazer o texto de uma pergunta
antiga, limpe o campo na tela (ou ponha `ESCREVER_APOIO_EXISTENTE = true` no
script, que aí ele volta a reescrever tudo e joga a formatação fora).

Rodado em 22/set/2026: 9 perguntas em notícias, 19 em artigos, e as 15 de
membros só com texto de apoio. Segunda execução não mexeu em nada (0 tipo
trocado, 0 criada): é seguro rodar de novo.

**Decisão de 22/set/2026:** nas formas de notícias e de artigos, todas as
perguntas são obrigatórias - envio completo nas duas línguas, com imagem e
figuras. As tabelas deste arquivo continuam marcando quais nasceram opcionais
na especificação original, mas quem manda é o `true`/`false` do script.

1. Em cada formulário, na aba **Respostas**, ligar a planilha: *Vincular à
   planilha*, escolhendo a planilha com as abas `pessoas`, `publicacoes` e
   `noticias`. O Google cria uma aba nova para cada formulário; renomeie para o
   nome da tabela e apague a aba em branco, se sobrar.
2. Em cada aba, **Arquivo > Compartilhar > Publicar na web**, formato **CSV**, e
   mandar o endereço para quem cuida dos scripts.
3. Os arquivos de imagem e as pastas de resposta precisam ficar compartilhados
   como "qualquer pessoa com o link", senão o baixador não consegue ler.
4. Marcar as perguntas obrigatórias: célula vazia em campo obrigatório derruba a
   geração, de propósito, em vez de publicar página incompleta.

Confira as perguntas contra o esquema antes de publicar:

```bash
python3 scripts/tabelas.py perguntas          # os textos que o formulário tem de usar
```

E, depois de ter a planilha, cole a linha de título para conferir o casamento:

```bash
xclip -o | python3 scripts/tabelas.py conferir pessoas -    # Linux
pbpaste | python3 scripts/tabelas.py conferir pessoas -     # macOS
```
