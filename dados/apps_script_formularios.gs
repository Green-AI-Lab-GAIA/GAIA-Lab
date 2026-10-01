/**
 * Monta os três formulários do GAIA Lab a partir da especificação de
 * dados/FORMULARIOS.md. Feito para rodar no Apps Script, dentro da conta que
 * é dona dos formulários (thiago.franke.ms@gmail.com).
 *
 * Como usar
 *   1. script.google.com  ->  Novo projeto
 *   2. apague o conteúdo de Código.gs e cole este arquivo inteiro
 *   3. salve (Ctrl+S) e rode a função montar()  ->  Autorizar
 *   4. a janela de execução mostra, formulário por formulário, o que mudou
 *
 * O que ele faz, e o que ele NÃO faz
 *   - Casa pergunta pelo TEXTO DO TÍTULO, que é o cabeçalho da coluna na
 *     planilha. Título que já existe nunca é apagado nem reescrito: só o tipo,
 *     o texto de apoio e o obrigatório são ajustados - e só quando a
 *     especificação manda (tipo ou obrigatório em branco significa: não mexe).
 *   - No formulário de membros ele NÃO troca tipo nem obrigatoriedade de nada:
 *     só escreve o texto de apoio. Função é escolha de propósito, com Other
 *     para o Alumni escrever o cargo de fora; Foto é obrigatória; E-mail é
 *     opcional. Tudo isso fica como está.
 *   - Endereço curto não é pergunta, e não tem coluna na planilha: quem monta o
 *     endereço da página é o gerador do site, a partir do nome ou do título.
 *   - Tipo de pergunta o Apps Script não troca no lugar, então quando o tipo
 *     está errado o item é apagado e recriado na mesma posição. Isso só é
 *     seguro antes de existir resposta gravada: com resposta na planilha, o
 *     apagamento tira a coluna. Rode uma vez, antes de divulgar o formulário.
 *   - Imagem entra como ENDEREÇO (https://...): o Apps Script não cria pergunta
 *     de upload de arquivo, o Forms não expõe isso na API. Quem preferir upload
 *     troca o tipo da pergunta na tela do Forms, em Editar.
 *   - Notícias e artigos: TODAS as perguntas são obrigatórias, menos a Figura 1, a
 *     Figura 2 e as duas legendas. A legenda só é exigida quando a figura vem
 *     junto, e quem cobra isso é o gerador do site, não o formulário: o Forms não
 *     sabe exigir uma pergunta em função de outra.
 *   - A ordem das perguntas segue esta especificação, e cada pergunta em
 *     português fica colada na sua versão em inglês. A API só deixa inserir no
 *     fim, então a função ordenar() recoloca todo mundo no lugar depois.
 *   - Formatação não existe na API: o getHelpText() devolve String, sem negrito
 *     nem itálico, e não há método nenhum de formatação no serviço Forms. Quem
 *     escreve negrito e itálico é a tela. O que dá para fazer pelo script é o que
 *     está feito aqui: título curto e impessoal, exemplo em linha própria,
 *     começando com "Exemplo:", e o resto do texto de apoio em frase corrida.
 *   - Por isso o texto de apoio de pergunta que JÁ EXISTE não é reescrito: quem
 *     formatou à mão na tela perderia tudo na rodada seguinte. O texto da
 *     especificação entra em pergunta nova, ou quando o campo está vazio. Para
 *     refazer o texto de uma pergunta antiga, limpe o campo na tela; para
 *     reescrever tudo sempre, ponha ESCREVER_APOIO_EXISTENTE = true.
 *
 * Duas manhas da API que este arquivo já embute (as duas custaram uma rodada):
 *   - FormApp.ItemType não serve para comparar tipo aqui: o que getType()
 *     devolve são as strings 'TEXT', 'PARAGRAPH_TEXT', 'MULTIPLE_CHOICE', 'LIST',
 *     'FILE_UPLOAD'. O mapa TIPO guarda essas strings.
 *   - getItems() devolve item genérico, sem setRequired nem isRequired. Quem
 *     tem esses métodos é o item tipado, que sai de asTextItem(),
 *     asParagraphTextItem(), asMultipleChoiceItem(). A função comTipo faz a
 *     conversão.
 */

var FORMULARIOS = {
  membros: '1dWZlk5hudHvi6aDo6W_U0OODGj_Or_Ygl_XocbK0WoU',
  noticias: '1iQIZMKDWweSuJYGdnSCBbe9uHgOJLWR5it8v7xkg6xQ',
  artigos: '1Nh_vArruFFtVgmLmZ0hXrItWaa4whXMj64oYXkkwYJo',
  cursos: '' // Preencha com o ID do formulário de cursos após criá-lo com gerar_formulario_cursos.gs
};

// O que getType() devolve, exatamente.
var TIPO = {
  curto: 'TEXT',
  paragrafo: 'PARAGRAPH_TEXT',
  escolha: 'MULTIPLE_CHOICE',
  lista: 'LIST',
  imagem: 'FILE_UPLOAD'
};

var QUEBRA = String.fromCharCode(10);

// Vínculo, na ordem em que o site mostra as seções.
var VINCULOS = [
  'Professor', 'Pós-doutorado', 'Doutorado', 'Mestrado',
  'Graduação', 'Colaborador', 'Alumni'
];

// Pergunta: título exato, tipo, obrigatória, texto de apoio.
// A ordem aqui é a ordem final das perguntas no formulário: cada pergunta em
// português e, logo abaixo, a versão em inglês. Quem recoloca é ordenar().
var ESPECIFICACOES = {
  noticias: [
    ['Título', TIPO.curto, true, 'O título da matéria, como saiu no veículo. Vira o título do cartão e da página.'],
    ['Título em inglês', TIPO.curto, true, 'O mesmo título, em inglês. É este texto que aparece na página em inglês.'],
    ['Veículo', TIPO.curto, true, 'Onde a matéria saiu, em uma palavra ou duas.' + QUEBRA + 'Exemplo: FGV, Folha, Agência Brasil.'],
    ['Data', TIPO.curto, true, 'A data da publicação.' + QUEBRA + 'Formato: DD-MM-AAAA. Exemplo: 24-04-2026.'],
    ['Endereço da matéria', TIPO.curto, true, 'O endereço completo, começando com https://. Vira o destino do botão e do cartão.'],
    ['Endereço da matéria em inglês', TIPO.curto, true, 'O endereço da versão em inglês, quando a matéria também saiu em inglês.' + QUEBRA + 'Se não saiu em inglês, repita o endereço da versão em português.'],
    ['Resumo', TIPO.paragrafo, true, 'Duas ou três frases sobre a matéria, em texto corrido. Vira o cartão e a abertura da página.'],
    ['Resumo em inglês', TIPO.paragrafo, true, 'O mesmo resumo, em inglês. É este texto que aparece na página em inglês.'],
    ['Imagem', TIPO.curto, true, 'Anexe o arquivo da imagem, deitada e na proporção 16:9 (por exemplo 1600x900): é assim que ela aparece no cartão e na abertura da página.']
  ],
  artigos: [
    ['Título', TIPO.curto, true, 'Título oficial do artigo, independentemente do idioma. Como no artigo, sem ponto no fim.'],
    ['Autores, na ordem', TIPO.curto, true, 'Os nomes na ordem de assinatura do artigo, separados por vírgula.'],
    ['Revista ou evento', TIPO.curto, true, 'O nome por extenso, como aparece na publicação.' + QUEBRA + 'Exemplo: Nature Climate Change, NeurIPS 2026.'],
    ['Detalhes (volume, número, páginas, editora)', TIPO.curto, true, 'Só os detalhes bibliográficos: volume, número, páginas, editora. No caso de livro, o editor; no caso de congresso, o nome do evento.'],
    ['Data da publicação', TIPO.curto, true, 'A data em que o artigo saiu.' + QUEBRA + 'Formato: DD-MM-AAAA. Exemplo: 24-04-2026.'],
    ['Endereço do artigo (DOI ou link)', TIPO.curto, true, 'O endereço completo, começando com https://. Vale o DOI em forma de link.' + QUEBRA + 'Exemplo: https://doi.org/10.1000/xyz123'],
    ['Resumo', TIPO.paragrafo, true, 'O resumo do artigo, em texto corrido. Pode ser longo: o site deixa como parágrafo.'],
    ['Resumo em inglês', TIPO.paragrafo, true, 'O mesmo resumo, em inglês. É este texto que aparece na página em inglês.'],
    ['Resumo curto', TIPO.paragrafo, true, 'Uma frase para o cartão da listagem, em texto corrido. É o que aparece na lista de publicações, ao lado da imagem de destaque.'],
    ['Resumo curto em inglês', TIPO.paragrafo, true, 'A mesma frase, em inglês. É este texto que aparece na lista de publicações em inglês.'],
    ['Como citar, em LaTeX', TIPO.paragrafo, true, 'A única resposta com sintaxe: cole a entrada BibTeX ou o trecho em LaTeX. Sai num bloco de código na página.' + QUEBRA + 'Exemplo: @article{souza2026, title={...}, year={2026}}'],
    ['Imagem de destaque', TIPO.curto, true, 'Anexe o arquivo: é o print da primeira página do artigo, ou uma imagem que o represente. É a miniatura no cartão da listagem e a imagem de abertura da página.'],
    ['Figura 1', TIPO.curto, false, 'Anexe o arquivo da Figura 1: ela entra depois do Resumo. Em branco, o artigo fica só com a imagem de destaque.'],
    ['Legenda da figura 1', TIPO.curto, false, 'A legenda da Figura 1, em uma linha. Aceita sintaxe LaTeX (veja os exemplos já publicados).' + QUEBRA + 'Obrigatória se você anexou a Figura 1; sem figura, deixe em branco.'],
    ['Figura 2', TIPO.curto, false, 'Anexe o arquivo da Figura 2: ela entra depois da Figura 1. Em branco, o artigo fica sem ela.'],
    ['Legenda da figura 2', TIPO.curto, false, 'A legenda da Figura 2, em uma linha. Aceita sintaxe LaTeX (veja os exemplos já publicados).' + QUEBRA + 'Obrigatória se você anexou a Figura 2; sem figura, deixe em branco.']
  ],
  // Membros: o formulário já tem as 15 perguntas, com os tipos e a
  // obrigatoriedade que o Thiago escolheu. Tipo e obrigatório vão null de
  // propósito: aqui o script só escreve o texto de apoio que aparece embaixo
  // de cada pergunta. Pergunta fora desta lista não é tocada.
  membros: [
    ['Nome completo', null, null, 'Como você quer aparecer no site. O endereço da sua página sai deste nome.'],
    ['Vínculo', null, null, 'Em que degrau do grupo você está hoje. É a seção em que você aparece na página de pessoas.'],
    ['Função', null, null, 'Escolha a opção que mais se aproxima. Se nenhuma serve - Alumni com emprego fora do laboratório, por exemplo - escolha Other e escreva seu cargo.'],
    ['Função em inglês', null, null, 'A mesma função, em inglês. Escolha a opção equivalente ou use Other. Em branco, a página em inglês reusa o português.'],
    ['Formação', null, null, 'O curso mais alto que você concluiu, com a instituição, em uma linha.'],
    ['Formação em inglês', null, null, 'A mesma formação, em inglês. Em branco, a página em inglês reusa o português.'],
    ['Formação detalhada', null, null, 'Um item por linha, do mais recente ao mais antigo.'],
    ['Formação detalhada em inglês', null, null, 'Um item por linha, em inglês. Em branco, a página em inglês reusa o português.'],
    ['Apresentação', null, null, 'Um parágrafo curto sobre você, em texto corrido. Vira a abertura da sua página.'],
    ['Apresentação em inglês', null, null, 'O mesmo parágrafo, em inglês. Em branco, a página em inglês reusa o português.'],
    ['Interesses de pesquisa', null, null, 'Em que você trabalha, em texto corrido.'],
    ['Interesses de pesquisa em inglês', null, null, 'Os mesmos interesses, em inglês. Em branco, a página em inglês reusa o português.'],
    ['LinkedIn', null, null, 'O endereço completo, começando com https://. Vira o botão do seu perfil.'],
    ['E-mail', null, null, 'O e-mail de contato que você quer deixar público. Em branco, o site não mostra botão de e-mail.'],
    ['Foto', null, null, 'Anexe o arquivo da foto, de rosto: quadrada (1:1), JPG ou PNG, no mínimo 600x600, até 1 MB.']
  ],
  cursos: [
    ['Nome do curso', TIPO.curto, true, 'Nome oficial da disciplina ou curso em português. Vira o título no cartão do site.' + QUEBRA + 'Exemplo: Aprendizado Profundo'],
    ['Nome do curso em inglês', TIPO.curto, true, 'Official course title in English. Aparece na versão em inglês do site.' + QUEBRA + 'Exemplo: Deep Learning'],
    ['Nível ou programa', TIPO.curto, true, 'Nível de ensino e programa acadêmico que oferta o curso.' + QUEBRA + 'Exemplo: Graduação em Ciência de Dados e IA, EMAp'],
    ['Nível ou programa em inglês', TIPO.curto, true, 'Academic program and education level in English.' + QUEBRA + 'Exemplo: Undergraduate program in Data Science and AI, EMAp'],
    ['Professor(es)', TIPO.curto, true, 'Nome do(s) docente(s) responsável(is) pela disciplina (usado em português e inglês).' + QUEBRA + 'Exemplo: Dário Oliveira'],
    ['Carga horária', TIPO.curto, true, 'Carga horária total da disciplina (usada em português e inglês).' + QUEBRA + 'Exemplo: 60h'],
    ['Horário e formato das aulas', TIPO.curto, true, 'Dias da semana, horários e se as aulas são presenciais ou online.' + QUEBRA + 'Exemplo: presenciais, terças e quintas, das 9h20 às 11h (horário de Brasília)'],
    ['Horário e formato das aulas em inglês', TIPO.curto, true, 'Class schedule and format in English.' + QUEBRA + 'Exemplo: in person, Tuesdays and Thursdays, 9:20–11:00 am (Brasília time)'],
    ['Período de oferta', TIPO.curto, true, 'Quando a disciplina é ofertada regularmente ao longo do ano letivo.' + QUEBRA + 'Exemplo: todo segundo semestre'],
    ['Período de oferta em inglês', TIPO.curto, true, 'Offering term/period in English.' + QUEBRA + 'Exemplo: every second semester'],
    ['Página do curso', TIPO.curto, true, 'Endereço oficial (URL começando com https://) com ementa, grade curricular ou detalhes do programa.' + QUEBRA + 'Exemplo: https://emap.fgv.br/curso/doutorado#aba-disciplinas'],
    ['Página do curso em inglês', TIPO.curto, true, 'Official course page URL in English. Se não houver versão em inglês, repita o link em português.' + QUEBRA + 'Exemplo: https://emap.fgv.br/curso/doutorado#aba-disciplinas'],
    ['Imagem ilustrativa', TIPO.curto, false, 'Link ou endereço no Drive da imagem/ícone representativo (proporção 16:9 ou 16:10, SVG/PNG/JPG).' + QUEBRA + 'Opcional: se deixado em branco, o site atribui o ícone padrão correspondente.']
  ]
};

var DESCRICAO = {
  membros: 'Suas respostas viram a sua página no site do GAIA Lab, em português e em inglês. Escreva texto corrido, sem código e sem sintaxe: quem monta as seções, os botões e os cartões é o gerador. Nada é publicado sem passar por revisão.' + QUEBRA + QUEBRA +
    'Antes de responder, veja as páginas já publicadas, para ver o formato: https://green-ai-lab-gaia.github.io/people/' + QUEBRA + QUEBRA +
    'A foto é anexada como arquivo (não cole link): de rosto, quadrada, no mínimo 600x600, até 1 MB.',
  artigos: 'Cada resposta vira a página de um artigo publicado pelo grupo, em português e em inglês. Escreva texto corrido, sem sintaxe; só o campo de citação e as legendas das figuras aceitam LaTeX.' + QUEBRA + QUEBRA +
    'Antes de responder, veja os artigos já publicados, para ver o formato: https://green-ai-lab-gaia.github.io/publications/' + QUEBRA + QUEBRA +
    'Datas no formato DD-MM-AAAA (exemplo: 24-04-2026). As imagens são anexadas como arquivo (não cole link).',
  noticias: 'Cada resposta vira a página de uma notícia sobre o grupo, em português e em inglês: matéria, divulgação, prêmio, participação em evento. Escreva texto corrido, sem sintaxe.' + QUEBRA + QUEBRA +
    'Antes de responder, veja as notícias já publicadas, para ver o formato: https://green-ai-lab-gaia.github.io/publications/#noticias' + QUEBRA + QUEBRA +
    'Datas no formato DD-MM-AAAA (exemplo: 24-04-2026).' + QUEBRA + QUEBRA +
    'A imagem é anexada como arquivo (não cole link), deitada e na proporção 16:9 (por exemplo 1600x900).',
  cursos: 'Cada resposta vira o cartão de uma disciplina ofertada por integrantes do GAIA Lab na FGV EMAp, em português e em inglês.' + QUEBRA + QUEBRA +
    'Antes de responder, veja os cursos já cadastrados: https://green-ai-lab-gaia.github.io/courses/' + QUEBRA + QUEBRA +
    'O link externo é sempre o botão Página do curso. As informações são revisadas antes de irem para o site.'
};

// Onde a ordem das perguntas é recolocada no fim da montagem: a API só insere
// pergunta no fim da lista, então pergunta criada depois nasce fora de lugar.
// Membros fica de fora: aquele formulário é do jeito que o Thiago montou.
var ORDENAR = { membros: false, noticias: true, artigos: true, cursos: true };

// Texto de apoio de pergunta que já existe. false preserva o que está na tela -
// inclusive o negrito e o itálico, que a API do Forms não sabe ler nem escrever.
// true reescreve tudo a partir da especificação, jogando fora o que foi formatado
// à mão.
var ESCREVER_APOIO_EXISTENTE = false;

// Formulário que já tem resposta gravada não é tocado - nem a descrição, nem o
// tipo de pergunta, nem a criação de pergunta nova. Ligue só sabendo o que muda.
// A descrição do formulário também só é escrita quando está vazia: texto escrito
// à mão na tela nunca é sobrescrito (foi o que apagou a descrição de notícias).
var PERMITIR_EM_FORMULARIO_VIVO = false;

// Recoloca as perguntas na ordem da especificação - pergunta em português e,
// logo abaixo, a versão em inglês. Pergunta que não está na especificação
// (criada à mão na tela) fica onde está, depois das outras.
function ordenar(form, especificacoes, linhas) {
  var itens = form.getItems();
  var desejada = [];
  for (var j = 0; j < especificacoes.length; j++) {
    for (var i = 0; i < itens.length; i++) {
      if (itens[i].getTitle().trim() === especificacoes[j][0]) {
        desejada.push(itens[i]);
        break;
      }
    }
  }
  for (var k = 0; k < itens.length; k++) {
    if (desejada.indexOf(itens[k]) < 0) desejada.push(itens[k]);
  }
  var movidas = 0, recusadas = 0;
  for (var pos = 0; pos < desejada.length; pos++) {
    if (desejada[pos].getIndex() === pos) continue;
    try {
      form.moveItem(desejada[pos].getIndex(), pos);
      movidas++;
    } catch (erro) {
      recusadas++;
    }
  }
  if (movidas) linhas.push('  > ' + movidas + ' perguntas fora de ordem, recolocadas');
  if (recusadas) linhas.push('    ! ' + recusadas + ' perguntas que a API não deixou mover');
}

// Confere o que ficou na tela: cada pergunta em inglês tem que estar logo abaixo
// da pergunta em português dela - que é a pergunta imediatamente anterior na
// especificação. É o pedido do Thiago, e o único jeito de saber que o moveItem
// fez o que devia. Não dá para deduzir o par pelo título: em artigos o par de
// "Título em inglês" é "Título".
function conferirPares(form, especificacoes, linhas) {
  var SUFIXO = ' em inglês';
  var itens = form.getItems();
  var fora = [];
  for (var j = 1; j < especificacoes.length; j++) {
    var titulo = especificacoes[j][0];
    if (titulo.slice(-SUFIXO.length) !== SUFIXO) continue;
    var pos = -1;
    for (var i = 0; i < itens.length; i++) {
      if (itens[i].getTitle().trim() === titulo) { pos = i; break; }
    }
    if (pos > 0 && itens[pos - 1].getTitle().trim() === especificacoes[j - 1][0]) continue;
    fora.push(titulo);
  }
  linhas.push(fora.length
    ? '    ! inglês fora de lugar: ' + fora.join('; ')
    : '  > pares conferidos: cada versão em inglês logo abaixo da portuguesa');
}

function tipoDoItem(item) {
  var t = String(item.getType());
  if (t === 'TEXT') return TIPO.curto;
  if (t === 'PARAGRAPH') return TIPO.paragrafo;
  if (t === 'MULTIPLE_CHOICE') return TIPO.escolha;
  if (t === 'LIST') return TIPO.lista;
  if (t === 'FILE_UPLOAD') return TIPO.imagem;
  return t;
}

// getItems() devolve item genérico: setRequired e isRequired só existem no item
// tipado. Sem esta conversão, a obrigatoriedade nunca é aplicada.
function comTipo(item) {
  var t = tipoDoItem(item);
  if (t === TIPO.curto && item.asTextItem) return item.asTextItem();
  if (t === TIPO.paragrafo && item.asParagraphTextItem) return item.asParagraphTextItem();
  if (t === TIPO.escolha && item.asMultipleChoiceItem) return item.asMultipleChoiceItem();
  if (t === TIPO.lista && item.asListItem) return item.asListItem();
  return item;
}

function obrigatoriaDe(item) {
  var tipado = comTipo(item);
  if (!tipado.isRequired) return 'obrigatoriedade não exposta';
  return tipado.isRequired() ? 'obrigatória' : 'opcional';
}

// O texto de apoio que está na tela agora. A API devolve String: a formatação
// (negrito, itálico) fica invisível aqui, e é justamente por isso que reescrever
// às cegas apaga o trabalho de quem formatou na tela.
function apoioAtual(item) {
  try {
    var tipado = comTipo(item);
    if (tipado && tipado.getHelpText) return String(tipado.getHelpText() || '');
  } catch (erro) {
    // Item que não expõe getHelpText (upload de arquivo, por exemplo): trata como
    // vazio, que é o comportamento antigo.
  }
  return '';
}

function montar() {
  var relatorio = [];
  for (var chave in ESPECIFICACOES) {
    relatorio.push(montarUm(chave, FORMULARIOS[chave], ESPECIFICACOES[chave]));
  }
  Logger.log(relatorio.join(QUEBRA));
}

function montarUm(chave, id, especificacoes) {
  if (!id || !id.trim()) {
    return ['', '=== ' + chave + ': ignorado (preencha o ID do formulário em FORMULARIOS)'].join(QUEBRA);
  }
  var form = FormApp.openById(id);
  var linhas = ['', '=== ' + chave + ': ' + form.getTitle()];
  var respostas = form.getResponses().length;
  if (respostas && !PERMITIR_EM_FORMULARIO_VIVO) {
    return linhas.join(QUEBRA) + QUEBRA + '  ! ' + respostas +
           ' respostas gravadas: não mexi em nada (PERMITIR_EM_FORMULARIO_VIVO = false)';
  }
  if (!String(form.getDescription() || '').trim() && DESCRICAO[chave]) {
    form.setDescription(DESCRICAO[chave]);
  }

  // Índice das perguntas que já existem, por título. Sobra de rascunho
  // ("Untitled Question") entra na lista para ser removida.
  var existentes = form.getItems();
  var porTitulo = {};
  var rascunhos = [];
  for (var i = 0; i < existentes.length; i++) {
    var titulo = existentes[i].getTitle().trim();
    if (titulo === '' || titulo === 'Untitled Question') rascunhos.push(existentes[i]);
    else porTitulo[titulo] = existentes[i];
  }
  for (var r = 0; r < rascunhos.length; r++) {
    form.deleteItem(rascunhos[r]);
    linhas.push('  - apagado o rascunho sem título');
  }

  for (var j = 0; j < especificacoes.length; j++) {
    var espec = especificacoes[j];
    var tituloAlvo = espec[0], tipoAlvo = espec[1], obrigatoria = espec[2], apoio = espec[3];
    var item = porTitulo[tituloAlvo];

    // Tipo em branco: a pergunta é do jeito que o Thiago montou (Função e
    // Função em inglês, por exemplo: escolha com Other). Aqui só o texto de
    // apoio é escrito, e o tipo e a obrigatoriedade ficam intocados.
    if (!tipoAlvo) {
      if (!item) {
        linhas.push('  ? não existe, e a especificação não manda criar: ' + tituloAlvo);
        continue;
      }
      if (apoioAtual(item) && !ESCREVER_APOIO_EXISTENTE) {
        linhas.push('  = texto de apoio preservado: ' + tituloAlvo + ' (' + tipoDoItem(item) +
                    ', ' + obrigatoriaDe(item) + ')');
        continue;
      }
      item.setHelpText(apoio);
      linhas.push('  = só texto de apoio: ' + tituloAlvo + ' (' + tipoDoItem(item) +
                  ', ' + obrigatoriaDe(item) + ')');
      continue;
    } else if (!item) {
      item = criarItem(form, tipoAlvo, tituloAlvo, apoio);
      linhas.push('  + criada: ' + tituloAlvo + ' (' + tipoDoItem(item) + ')');
    } else if (tipoDoItem(item) === TIPO.imagem && tipoAlvo !== TIPO.imagem) {
      // Pergunta de upload feita à mão na tela: a API não cria nem converte esse
      // tipo, então o script nunca desfaz a escolha do Thiago.
      linhas.push('  = mantida como upload: ' + tituloAlvo + ' (texto de apoio e tipo intocados)');
      continue;
    } else if (tipoDoItem(item) !== tipoAlvo) {
      var tipoAntigo = tipoDoItem(item);
      var posicao = item.getIndex();
      form.deleteItem(item);
      item = criarItem(form, tipoAlvo, tituloAlvo, apoio);
      form.moveItem(item.getIndex(), posicao);
      linhas.push('  ~ tipo trocado: ' + tituloAlvo + ' (' + tipoAntigo + ' -> ' + tipoDoItem(item) + ')');
    } else if (apoioAtual(item) && !ESCREVER_APOIO_EXISTENTE) {
      linhas.push('  = mantida, texto de apoio preservado: ' + tituloAlvo + ' (' + tipoDoItem(item) + ')');
    } else {
      item.setHelpText(apoio);
      linhas.push('  = mantida: ' + tituloAlvo + ' (' + tipoDoItem(item) + ')');
    }
    // Obrigatório em branco: quem manda é o que já está no formulário.
    if (obrigatoria === null || obrigatoria === undefined) continue;
    try {
      comTipo(item).setRequired(obrigatoria);
    } catch (erro) {
      linhas.push('    ! obrigatoriedade não aplicável: ' + erro.message);
    }
  }
  if (ORDENAR[chave]) ordenar(form, especificacoes, linhas);
  conferirPares(form, especificacoes, linhas);
  linhas.push('  perguntas agora: ' + form.getItems().length);
  return linhas.join(QUEBRA);
}

function criarItem(form, tipo, titulo, apoio) {
  var item;
  if (tipo === TIPO.curto) {
    item = form.addTextItem();
  } else if (tipo === TIPO.paragrafo) {
    item = form.addParagraphTextItem();
  } else if (tipo === TIPO.escolha) {
    item = form.addMultipleChoiceItem();
    item.setChoiceValues(titulo === 'Vínculo' ? VINCULOS : []);
  } else if (tipo === TIPO.imagem) {
    // A API não cria upload de arquivo; quem pedir FILE_UPLOAD cai aqui e
    // recebe um campo de endereço, que o site lê do mesmo jeito.
    item = form.addTextItem();
  } else {
    item = form.addTextItem();
  }
  item.setTitle(titulo);
  if (item.setHelpText) item.setHelpText(apoio || '');
  return item;
}

/** Só confere o que está lá, sem mexer em nada. */
function conferir() {
  var relatorio = [];
  for (var chave in FORMULARIOS) {
    if (!FORMULARIOS[chave] || !FORMULARIOS[chave].trim()) {
      relatorio.push(['', '=== ' + chave + ': ignorado (preencha o ID do formulário em FORMULARIOS)'].join(QUEBRA));
      continue;
    }
    var form = FormApp.openById(FORMULARIOS[chave]);
    var itens = form.getItems();
    var linhas = ['', '=== ' + chave + ': ' + form.getTitle() + ' (' + itens.length + ' perguntas)'];
    for (var i = 0; i < itens.length; i++) {
      linhas.push('  ' + (itens[i].getTitle() || '(sem título)') + ' | ' + tipoDoItem(itens[i]) +
                  ' | ' + obrigatoriaDe(itens[i]));
    }
    relatorio.push(linhas.join(QUEBRA));
  }
  Logger.log(relatorio.join(QUEBRA));
}
