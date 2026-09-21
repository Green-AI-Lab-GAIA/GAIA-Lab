/**
 * Recebe as inscrições do formulário "Junte-se a nós" e avisa o coordenador.
 *
 * Como colocar no ar:
 *   1. Criar uma planilha só para inscrições, separada das planilhas de conteúdo,
 *      com a primeira aba chamada "inscricoes".
 *   2. Extensões, Apps Script, colar este arquivo e ajustar as constantes abaixo.
 *   3. Implantar, Nova implantação, tipo "Aplicativo da web",
 *      executar como "eu", acessar como "qualquer pessoa". Autorizar quando pedir.
 *   4. Copiar a URL /exec e colar em data-endpoint no formulário, nos dois
 *      idiomas, em join-us/index.pt.qmd e index.en.qmd.
 *
 * A planilha é um banco de dados: nada é apagado automaticamente, a exclusão é
 * manual. Não guarde nada aqui que não possa ficar registrado.
 */

var ABA = "inscricoes";
var DESTINO = "dario.oliveira@fgv.br";
var TOKEN = "troque-por-um-texto-aleatorio";   // igual ao data-token do formulário
var LIMITE_POR_HORA = 3;                       // por e-mail, para segurar abuso

function doPost(e) {
  var p = (e && e.parameter) || {};

  // honeypot: campo escondido por CSS, robô preenche
  if (p.website) return json({ ok: false, motivo: "spam" });
  if (TOKEN && p.token !== TOKEN) return json({ ok: false, motivo: "token" });

  var nome = limpar(p.nome, 120);
  var email = limpar(p.email, 160);
  var nivel = limpar(p.nivel, 60);
  var mensagem = limpar(p.mensagem, 4000);
  var pagina = limpar(p.pagina, 120);
  var idioma = limpar(p.idioma, 8);

  if (!nome || !email || !mensagem) return json({ ok: false, motivo: "campos" });
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return json({ ok: false, motivo: "email" });

  var aba = SpreadsheetApp.getActive().getSheetByName(ABA);
  if (!aba) return json({ ok: false, motivo: "aba " + ABA + " nao encontrada" });

  if (excedeuLimite(aba, email)) return json({ ok: false, motivo: "limite" });

  aba.appendRow([new Date(), nome, email, nivel, mensagem, idioma, pagina]);

  MailApp.sendEmail({
    to: DESTINO,
    replyTo: email,
    subject: "[Join Us] " + nivel + " - " + nome,
    body: "Nome: " + nome + "\nE-mail: " + email + "\nNivel: " + nivel +
          "\nIdioma: " + idioma + "\nPagina: " + pagina + "\n\n" + mensagem,
  });

  return json({ ok: true });
}

// Responde mesmo quando o navegador não pode ler a resposta: serve para
// conferir na mão, abrindo a URL /exec no navegador, e para quem tiver CORS.
function doGet() {
  return json({ ok: true, mensagem: "endpoint de inscricoes do GAIA Lab ativo" });
}

function json(objeto) {
  return ContentService.createTextOutput(JSON.stringify(objeto))
    .setMimeType(ContentService.MimeType.JSON);
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
