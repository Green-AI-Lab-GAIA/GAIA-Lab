# Endpoint do formulário de contato

O site é estático e não recebe POST. Quem recebe é um aplicativo da web do Google
Apps Script, que grava a mensagem numa aba da planilha do projeto (a mesma que
guarda pessoas, publicações e notícias) e manda o e-mail para o coordenador.
Não é preciso Workspace: serve uma conta Google comum.

## Colocar no ar

1. A aba `contatos` (com o cabeçalho: data, nome, email, motivo, mensagem)
   é criada sozinha na primeira mensagem, se ainda não existir.
   As outras abas não são tocadas.
2. Na planilha: Extensões, Apps Script, colar `inscricoes.gs`, ajustar `DESTINO`
   e `TOKEN` (e `LIMITE_POR_HORA`, se quiser). O `PLANILHA_ID` já aponta para a
   planilha do projeto.
3. Implantar, Nova implantação, tipo **Aplicativo da web**, executar como **eu**,
   acesso **qualquer pessoa**. Autorizar quando o Google pedir.
4. Copiar a URL `/exec` e colar no atributo `data-endpoint` do formulário, nos
   dois arquivos: `join-us/index.pt.qmd` e `join-us/index.en.qmd`.
5. Colar o mesmo valor de `TOKEN` no atributo `data-token` desses dois arquivos.

Enquanto `data-endpoint` estiver vazio, o formulário continua funcionando pelo
caminho antigo, abrindo o e-mail do visitante. Nada quebra por falta do endpoint.

## O que o script faz

- Descarta envio com o honeypot preenchido (campo invisível que só robô completa).
- Confere o token, os campos obrigatórios e o formato do e-mail.
- Recusa mais de `LIMITE_POR_HORA` mensagens do mesmo e-mail na última hora.
- Grava a linha na aba `contatos` e envia o e-mail com `Reply-To` no remetente,
  então responder no e-mail já vai para a pessoa certa.

## Limites que valem saber

- Cota de e-mail de conta comum: **100 destinatários por dia** (1.500 em Workspace).
  A cota conta destinatários, não mensagens.
- O navegador não consegue ler a resposta do Apps Script por CORS, então a tela
  mostra "enviada" sem poder confirmar erro do servidor. A prova de que chegou é o
  e-mail no destino. Se a rede falhar, aí sim o formulário detecta e avisa.
- A URL `/exec` é pública. O token e o limite de frequência são travas de
  conveniência, não de segurança.

## Continuidade

O script pertence à conta que o criou. Deixe pelo menos **duas contas** com acesso
de edição à planilha e registre aqui quem são os responsáveis.
