/**
 * Recebe as mensagens do formulário de contato do site e avisa o coordenador.
 *
 * A planilha de destino é a MESMA que guarda pessoas, publicações e notícias do
 * site (id em PLANILHA_ID). O script grava numa aba própria, "contatos", sem
 * tocar nas outras.
 *
 * Como colocar no ar:
 *   1. A aba "contatos" (data | nome | email | motivo | mensagem)
 *      é criada sozinha; o cabeçalho também é conferido a cada envio.
 *   2. Extensões, Apps Script, colar este arquivo e ajustar as constantes abaixo.
 *   3. Implantar, Nova implantação, tipo "Aplicativo da web",
 *      executar como "eu", acessar como "qualquer pessoa". Autorizar quando pedir.
 *   4. Copiar a URL /exec e colar em data-endpoint do formulário, nos dois
 *      idiomas, em join-us/index.pt.qmd e join-us/index.en.qmd.
 *   5. Colar o mesmo valor de TOKEN em data-token desses dois arquivos.
 *
 * A aba é um registro: nada é apagado automaticamente, a exclusão é manual.
 * Não guarde nada aqui que não possa ficar registrado.
 */

var PLANILHA_ID = "1ZFExkE-MO_9gQ-R7Qj-ApOb1ar8iTXOC53NvG7lpffw";
var ABA = "contatos";
var DESTINO = "dario.oliveira@fgv.br";
var TOKEN = "gaia-contato-9f3c71";              // igual ao data-token do formulário
var LIMITE_POR_HORA = 3;                       // por e-mail, para segurar abuso

function doPost(e) {
  var p = (e && e.parameter) || {};

  // honeypot: campo escondido por CSS, robô preenche
  if (p.website) return json({ ok: false, motivo: "spam" });
  if (TOKEN && p.token !== TOKEN) return json({ ok: false, motivo: "token" });

  var nome = limpar(p.nome, 120);
  var email = limpar(p.email, 160);
  var motivo = limpar(p.motivo, 120);
  var mensagem = limpar(p.mensagem, 4000);

  if (!nome || !email || !mensagem) return json({ ok: false, motivo: "campos" });
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return json({ ok: false, motivo: "email" });

  var aba = abaDeContatos(SpreadsheetApp.openById(PLANILHA_ID));
  if (!aba) return json({ ok: false, motivo: "aba " + ABA + " nao encontrada" });

  if (excedeuLimite(aba, email)) return json({ ok: false, motivo: "limite" });

  aba.appendRow([new Date(), nome, email, motivo, mensagem]);

  MailApp.sendEmail({
    to: DESTINO,
    cc: email,
    replyTo: email,
    name: "GAIA Lab",
    subject: "[Manifestação de interesse Gaia Lab] " + nome,
    body: "Nome: " + nome + "\nMotivo: " + motivo + "\n\n" + mensagem,
  });

  return json({ ok: true });
}

// Responde mesmo quando o navegador não pode ler a resposta: serve para
// conferir na mão, abrindo a URL /exec no navegador, e para quem tiver CORS.
function doGet() {
  var aba = abaDeContatos(SpreadsheetApp.openById(PLANILHA_ID));
  return json({ ok: true, mensagem: "endpoint de contato do GAIA Lab ativo" });
}

function json(objeto) {
  return ContentService.createTextOutput(JSON.stringify(objeto))
    .setMimeType(ContentService.MimeType.JSON);
}

// Devolve a aba "contatos"; cria se faltar e conserta o cabeçalho se estiver
// diferente do esperado (a linha 1 é o cabeçalho, nunca dado de contato).
function abaDeContatos(planilha) {
  var aba = planilha.getSheetByName(ABA);
  if (!aba) aba = planilha.insertSheet(ABA);
  var cabecalho = ["data", "nome", "email", "motivo", "mensagem"];
  var atual = aba.getRange(1, 1, 1, cabecalho.length).getValues()[0].join("|");
  if (atual !== cabecalho.join("|")) {
    aba.getRange(1, 1, 1, cabecalho.length).setValues([cabecalho]);
  }
  return aba;
}

function limpar(valor, limite) {
  return String(valor || "").replace(/[\u0000-\u001f]+/g, " ").trim().slice(0, limite);
}

function excedeuLimite(aba, email) {
  var ultimas = aba.getLastRow();
  if (ultimas < 2) return false;
  var limite = new Date(Date.now() - 60 * 60 * 1000);
  var linhas = aba.getRange(2, 1, ultimas - 1, 3).getValues();
  var contagem = 0;
  for (var i = 0; i < linhas.length; i++) {
    if (String(linhas[i][2]).toLowerCase() === email.toLowerCase() && linhas[i][0] >= limite) contagem++;
  }
  return contagem >= LIMITE_POR_HORA;
}
