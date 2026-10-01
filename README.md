# GAIA Lab — Site Institucional

Site institucional do GAIA Lab (Green AI Lab), desenvolvido com [Quarto](https://quarto.org). O conteúdo é bilíngue: português na raiz (`docs/`) e inglês em `docs/en/`.

---

## 1. Gerenciamento de Conteúdo (Camada CMS)

A maior parte do conteúdo do site (membros, publicações, notícias e cursos) é gerenciada de forma descentralizada via Google Forms e Google Sheets, sem necessidade de editar arquivos de código ou Markdown manualmente.

### Formulários de Cadastro

Para adicionar novos itens ao site, utilize os formulários públicos correspondentes:

* **Membro:** [https://forms.gle/RvgpCadeTmXkg5897](https://forms.gle/RvgpCadeTmXkg5897)  
  *Coleta nome, vínculo, função, formação, minibio, links (Lattes, LinkedIn, GitHub, etc.) e foto quadrada (1:1, mín. 600×600).*
* **Artigo:** [https://forms.gle/QNTqVWMRj8MXTWkb6](https://forms.gle/QNTqVWMRj8MXTWkb6)  
  *Coleta título, autores, veículo/conferência, data, DOI, resumo, citação LaTeX e até 3 figuras (miniatura, fig 1 e fig 2).*
* **Notícia:** [https://forms.gle/nENCQL9z6MukRTA38](https://forms.gle/nENCQL9z6MukRTA38)  
  *Coleta título, veículo jornalístico, data, link original, resumo e imagem horizontal (16:9).*
* **Curso:** [https://forms.gle/3v1ZMRcUi9XoDk5k9](https://forms.gle/3v1ZMRcUi9XoDk5k9)  
  *Coleta título, código, nível, carga horária, professor, ementa, link do curso e imagem horizontal (16:9).*

> **Edição de conteúdo:** os formulários são editáveis. Guarde o link de edição exibido após o envio para corrigir ou atualizar dados posteriormente. Alterações também podem ser feitas diretamente na planilha central (*Informações do site do Gaia Lab*).

### Mensagens de Contato
O formulário de contato do site (`/join-us/`) envia mensagens para o backend Google Apps Script (`inscricoes`), que registra os dados na aba `contatos` da planilha central e encaminha uma notificação por e-mail para a coordenação com cópia ao remetente.

---

## 2. Fluxo de Dados e Automação

O deploy e a atualização do site seguem o pipeline automatizado abaixo:

```text
[ 4 Google Forms + Contato ]
            │ (respostas em tempo real)
            ▼
[ Google Sheets (5 abas) + Pastas de Mídia no Drive ]
            │ (disparo agendado no cron: sábado à 00:00)
            ▼
[ Cron ➔ scripts/atualizar.sh ]
            │ (executa com trava flock anti-concorrência)
            ▼
┌────────────────────────────────────────────────────────┐
│ scripts/sincronizar.py                                 │
│  1. Download e validação dos CSVs (scripts/tabelas.py) │
│  2. Download de imagens do Drive (baixar_imagens.py)   │
│  3. Geração dos arquivos .qmd (gerar_conteudo.py)      │
│  4. Compilação estática com Quarto (scripts/build.sh)  │
│  5. Deploy: git add, commit e git push                 │
└───────────────────────────┬────────────────────────────┘
                            │ (git push)
                            ▼
[ GitHub Pages: https://green-ai-lab-gaia.github.io/GAIA-Lab/ ]
```

### Executar a pipeline manualmente

* **Rodada completa com publicação no GitHub:**
  ```bash
  bash scripts/atualizar.sh
  # ou: python3 scripts/sincronizar.py --push
  ```
* **Rodada local (sem fazer push):**
  ```bash
  python3 scripts/sincronizar.py
  ```
* **Apenas verificar alterações pendentes (modo seco):**
  ```bash
  bash scripts/atualizar.sh --seco
  ```

---

## 3. Galeria da Página Sobre (Edição Manual)

Atualmente, a galeria de fotos em `about/` é a única seção que ainda não está integrada à camada de formulários (será migrada para o CMS futuramente).

Para adicionar fotos à galeria:

1. Adicione o arquivo de imagem (`.jpg`, `.png`, `.webp`) na pasta `about/images/galeria/`.
2. Abra `about/images/galeria/legendas.txt` e adicione uma linha no formato:
   ```text
   nome-do-arquivo.jpg | Legenda em português | Caption in English
   ```
3. Regenere o site rodando:
   ```bash
   python3 scripts/gerar_conteudo.py
   bash scripts/build.sh
   ```

---

## 4. Desenvolvimento Local

### Pré-requisitos
* [Quarto CLI](https://quarto.org) (v1.4 ou superior)
* Python 3.10+

### Compilar e visualizar o site localmente

* **Compilar todo o site em `docs/`:**
  ```bash
  bash scripts/build.sh
  ```
* **Visualização com recarregamento em tempo real (preview):**
  ```bash
  quarto preview               # português
  quarto preview --profile en  # inglês
  ```
* **Servidor local estático:**
  ```bash
  python3 -m http.server 4200 --directory docs
  ```

---

## 5. Estrutura do Repositório

```text
├── _quarto.yml            Configuração comum aos dois idiomas
├── _quarto-pt.yml         Navbar e rodapé em português (publica na raiz de docs/)
├── _quarto-en.yml         Navbar e rodapé em inglês (publica em docs/en/)
├── styles.css             Estilos customizados do site
├── dados/                 CSVs locais sincronizados com o Google Sheets (ignorado no git)
├── scripts/
│   ├── atualizar.sh       Disparador chamado pelo Cron semanal
│   ├── sincronizar.py     Orquestrador do pipeline de sincronização e deploy
│   ├── tabelas.py         Esquemas e validações das perguntas das planilhas
│   ├── baixar_imagens.py  Download de fotos do Google Drive para pastas locais
│   ├── gerar_conteudo.py  Gera arquivos .qmd (pessoas, artigos, notícias, cursos, galeria)
│   ├── build.sh           Executa o quarto render (pt e en) e limpeza de temporários
│   └── flatten_lang.py    Pós-processamento: ajusta URLs, mascara e-mails e versiona CSS
├── people/                Fichas de membros (geradas automaticamente)
├── publications/          Páginas de artigos científicos (geradas automaticamente)
├── news/                  Notícias e matérias de imprensa (geradas automaticamente)
├── courses/               Cursos e disciplinas (geradas automaticamente)
├── about/                 Página Sobre e fotos da galeria (about/images/galeria/)
├── research/              Linhas de pesquisa
├── join-us/               Página Fale Conosco
└── docs/                  SAÍDA ESTÁTICA GERADA (servida pelo GitHub Pages — não edite à mão)
```
