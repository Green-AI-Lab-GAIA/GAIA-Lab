#!/usr/bin/env python3
"""Gera o guia de documentação em PDF (README.pdf) e HTML (readme.html)
para os arquivos do Google Drive e fluxo de automação do site do GAIA Lab.
"""
import base64
import os
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

with open(RAIZ / "icon" / "icon.png", "rb") as f:
    logo_b64 = base64.b64encode(f.read()).decode("utf-8")

html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>GAIA Lab — Guia do Google Drive e Automação do CMS</title>
<style>
  @page {{
    size: A4;
    margin: 8mm 12mm 8mm 12mm;
  }}
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #24292f;
    line-height: 1.35;
    font-size: 11.5px;
    background: #fff;
  }}
  .page {{
    page-break-after: always;
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 279mm;
  }}
  .page:last-child {{
    page-break-after: auto;
  }}
  .header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #365902;
    padding-bottom: 6px;
    margin-bottom: 8px;
  }}
  .header-left h1 {{
    font-size: 18.5px;
    color: #365902;
    margin-bottom: 2px;
    font-weight: 700;
    letter-spacing: -0.2px;
  }}
  .header-left p {{
    font-size: 10.5px;
    color: #57606a;
  }}
  .site-link {{
    display: inline-block;
    margin-top: 3px;
    font-size: 10px;
    color: #365902;
    text-decoration: none;
    font-weight: 600;
    background: #eef5e6;
    padding: 2px 7px;
    border-radius: 4px;
    border: 1px solid #c9dec0;
  }}
  .logo {{
    height: 44px;
    width: auto;
    object-fit: contain;
  }}
  .intro {{
    background: #f6f8fa;
    border-left: 3.5px solid #365902;
    padding: 6px 10px;
    font-size: 11px;
    color: #333;
    margin-bottom: 8px;
    border-radius: 0 4px 4px 0;
    line-height: 1.35;
  }}
  h2 {{
    font-size: 12px;
    color: #24292f;
    border-bottom: 1px solid #d0d7de;
    padding-bottom: 3px;
    margin-top: 5px;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  h2 .badge {{
    background: #365902;
    color: #fff;
    font-size: 9.5px;
    padding: 1px 6px;
    border-radius: 10px;
    text-transform: none;
    font-weight: 600;
  }}
  .grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 7px;
  }}
  .card {{
    border: 1px solid #e1e4e8;
    border-radius: 5px;
    padding: 6px 8px;
    background: #ffffff;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .card-header {{
    display: flex;
    align-items: center;
    gap: 5px;
    margin-bottom: 2px;
  }}
  .card-icon {{
    font-size: 12.5px;
  }}
  .card-title {{
    font-size: 11px;
    font-weight: 700;
    color: #1b3300;
  }}
  .card-tag {{
    margin-left: auto;
    font-size: 8.5px;
    padding: 1px 5px;
    border-radius: 6px;
    font-weight: 600;
    text-transform: uppercase;
  }}
  .tag-pasta {{ background: #e8f0fe; color: #1a73e8; }}
  .tag-planilha {{ background: #e6f4ea; color: #137333; }}
  .tag-form {{ background: #fce8e6; color: #c5221f; }}
  .tag-script {{ background: #fef7e0; color: #b06000; }}

  .card p {{
    font-size: 10px;
    color: #444;
    line-height: 1.25;
  }}
  .card ul {{
    margin-top: 2px;
    margin-left: 13px;
    font-size: 9.5px;
    color: #555;
    line-height: 1.2;
  }}
  .form-link-btn {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    margin-top: 3px;
    padding: 2px 6px;
    background: #fdf2f2;
    border: 1px solid #f5c2c7;
    border-radius: 4px;
    color: #a71d2a;
    font-size: 9px;
    font-weight: 600;
    text-decoration: none;
    align-self: flex-start;
  }}

  /* DIAGRAMA SVG */
  .diagram-wrapper {{
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 6px 8px;
    margin-top: 2px;
    margin-bottom: 8px;
    text-align: center;
  }}
  .diagram-svg {{
    width: 100%;
    max-height: 108mm;
    display: block;
  }}

  /* TABELA */
  .table-summary {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 2px;
    margin-bottom: 7px;
    font-size: 9.5px;
  }}
  .table-summary th, .table-summary td {{
    border: 1px solid #d0d7de;
    padding: 3.5px 6px;
    text-align: left;
    line-height: 1.2;
  }}
  .table-summary th {{
    background: #f6f8fa;
    color: #1b3300;
    font-weight: 600;
    font-size: 9.5px;
  }}
  .table-summary tr:nth-child(even) td {{
    background: #fafbfc;
  }}
  .table-summary code {{
    font-size: 8.5px;
    background: #f0f3f6;
    padding: 1px 3px;
    border-radius: 3px;
  }}

  /* REGRAS */
  .rules {{
    background: #fffdf5;
    border: 1px solid #ffeeba;
    border-left: 3.5px solid #d4a72c;
    border-radius: 4px;
    padding: 5px 8px;
    font-size: 9.5px;
    margin-bottom: 6px;
    line-height: 1.25;
  }}
  .rules ul {{
    margin-left: 13px;
    margin-top: 2px;
  }}
  .rules li {{
    margin-bottom: 2px;
  }}

  .footer {{
    margin-top: auto;
    text-align: center;
    font-size: 9px;
    color: #6a737d;
    border-top: 1px solid #eaecef;
    padding-top: 4px;
  }}
</style>
</head>
<body>

<!-- PÁGINA 1: ESTRUTURA DO DRIVE & FORMULÁRIOS -->
<div class="page">
  <div class="header">
    <div class="header-left">
      <h1>GAIA Lab — Guia do Google Drive</h1>
      <p>Estrutura dos 10 arquivos e pastas que alimentam o site institucional</p>
      <a class="site-link" href="https://green-ai-lab-gaia.github.io/" target="_blank">
        🌐 Site Oficial: https://green-ai-lab-gaia.github.io/
      </a>
    </div>
    <img class="logo" src="data:image/png;base64,{logo_b64}" alt="Logo GAIA Lab">
  </div>

  <div class="intro">
    A pasta <strong>gaia-lab-website</strong> no Google Drive funciona como <strong>o gerenciador de conteúdo do site do Gaia Lab</strong>. O site é mantido como uma aplicação estática e segura no GitHub Pages, enquanto toda a alimentação de membros, artigos, notícias, cursos e contatos ocorre diretamente pelos itens descritos abaixo.
  </div>

  <h2>
    Estrutura do Google Drive &amp; Links dos Formulários
    <span class="badge">10 Itens</span>
  </h2>

  <div class="grid">
    <!-- 1. Pessoas Folder -->
    <div class="card">
      <div class="card-header">
        <span class="card-icon">📁</span>
        <span class="card-title">pessoas</span>
        <span class="card-tag tag-pasta">Pasta</span>
      </div>
      <p>Armazena as fotos de perfil (avatares) de toda a equipe do laboratório.</p>
      <ul>
        <li>Recebe as fotos enviadas pelo formulário de novos membros.</li>
        <li>Contém a subpasta automática de uploads: <em>Foto (File responses)</em>.</li>
        <li>Alimenta visualmente as fichas e perfis em <code>/people/</code>.</li>
      </ul>
    </div>

    <!-- 2. Publicações Folder -->
    <div class="card">
      <div class="card-header">
        <span class="card-icon">📁</span>
        <span class="card-title">publicacoes</span>
        <span class="card-tag tag-pasta">Pasta</span>
      </div>
      <p>Armazena todas as imagens e ilustrações científicas dos artigos do grupo.</p>
      <ul>
        <li>Guarda as miniaturas de destaque dos papers e figuras explicativas.</li>
        <li>Contém as subpastas criadas pelo formulário de novos artigos.</li>
        <li>Ilustra as páginas de publicações em <code>/publications/</code>.</li>
      </ul>
    </div>

    <!-- 3. Notícias Folder -->
    <div class="card">
      <div class="card-header">
        <span class="card-icon">📁</span>
        <span class="card-title">noticias</span>
        <span class="card-tag tag-pasta">Pasta</span>
      </div>
      <p>Guarda as imagens de capa das reportagens e divulgações de mídia do lab.</p>
      <ul>
        <li>Imagens na proporção 16:9 para cartões e cabeçalhos de notícias.</li>
        <li>Contém a subpasta de uploads de respostas de notícias.</li>
        <li>Integradas automaticamente às listagens em <code>/news/</code>.</li>
      </ul>
    </div>

    <!-- 4. Cursos Folder -->
    <div class="card">
      <div class="card-header">
        <span class="card-icon">📁</span>
        <span class="card-title">cursos</span>
        <span class="card-tag tag-pasta">Pasta</span>
      </div>
      <p>Armazena as imagens de divulgação das disciplinas ofertadas pelo lab.</p>
      <ul>
        <li>Imagens na proporção horizontal 16:9 (ex.: 1600×900) dos cursos.</li>
        <li>Recebe os arquivos anexados pelo formulário de novos cursos.</li>
        <li>Exibidas nos cartões de cursos ofertados em <code>/courses/</code>.</li>
      </ul>
    </div>

    <!-- 5. Planilha Central -->
    <div class="card">
      <div class="card-header">
        <span class="card-icon">📊</span>
        <span class="card-title">Informações do site do Gaia Lab</span>
        <span class="card-tag tag-planilha">Planilha Central</span>
      </div>
      <p><strong>A base de dados central de todo o site</strong> (Google Sheets com 5 abas):</p>
      <ul>
        <li><strong>pessoas:</strong> cadastro de membros, biografias, links e fotos.</li>
        <li><strong>publicacoes:</strong> artigos científicos, autores, periódicos e LaTeX.</li>
        <li><strong>noticias:</strong> matérias da imprensa, destaques e coberturas.</li>
        <li><strong>cursos:</strong> disciplinas ofertadas na FGV EMAp, ementas e links.</li>
        <li><strong>contatos:</strong> mensagens recebidas via formulário do site.</li>
      </ul>
    </div>

    <!-- 6. Apps Script inscricoes -->
    <div class="card">
      <div class="card-header">
        <span class="card-icon">⚡</span>
        <span class="card-title">inscricoes</span>
        <span class="card-tag tag-script">Apps Script</span>
      </div>
      <p>Backend de mensageria da página Fale Conosco (<code>/join-us/</code>).</p>
      <ul>
        <li>Endpoint Web App que recebe mensagens enviadas pelo site.</li>
        <li>Grava na tabela <code>contatos</code> (data, nome, e-mail, motivo, msg).</li>
        <li>Dispara e-mail ao coordenador com cópia (cc) para o solicitante.</li>
      </ul>
    </div>

    <!-- 7. Form Membro -->
    <div class="card">
      <div class="card-header">
        <span class="card-icon">📝</span>
        <span class="card-title">Registrar novo membro no site...</span>
        <span class="card-tag tag-form">Formulário</span>
      </div>
      <p>Formulário público para novos integrantes e colaboradores do lab.</p>
      <ul>
        <li>Coleta nome, vínculo, bio, redes e foto quadrada (1:1).</li>
        <li>Grava automaticamente na aba <code>pessoas</code> da planilha.</li>
      </ul>
      <a class="form-link-btn" href="https://forms.gle/RvgpCadeTmXkg5897" target="_blank">
        🔗 https://forms.gle/RvgpCadeTmXkg5897
      </a>
    </div>

    <!-- 8. Form Artigo -->
    <div class="card">
      <div class="card-header">
        <span class="card-icon">📝</span>
        <span class="card-title">Registrar novo artigo no site...</span>
        <span class="card-tag tag-form">Formulário</span>
      </div>
      <p>Formulário para os pesquisadores cadastrarem novas publicações.</p>
      <ul>
        <li>Coleta título, autores, periódico, DOI, LaTeX e figuras (1 e 2).</li>
        <li>Grava automaticamente na aba <code>publicacoes</code> da planilha.</li>
      </ul>
      <a class="form-link-btn" href="https://forms.gle/QNTqVWMRj8MXTWkb6" target="_blank">
        🔗 https://forms.gle/QNTqVWMRj8MXTWkb6
      </a>
    </div>

    <!-- 9. Form Notícia -->
    <div class="card">
      <div class="card-header">
        <span class="card-icon">📝</span>
        <span class="card-title">Registrar nova notícia no site...</span>
        <span class="card-tag tag-form">Formulário</span>
      </div>
      <p>Formulário para registrar matérias na mídia, prêmios e divulgações.</p>
      <ul>
        <li>Coleta título, veículo jornalístico, data, link e imagem (16:9).</li>
        <li>Grava automaticamente na aba <code>noticias</code> da planilha.</li>
      </ul>
      <a class="form-link-btn" href="https://forms.gle/nENCQL9z6MukRTA38" target="_blank">
        🔗 https://forms.gle/nENCQL9z6MukRTA38
      </a>
    </div>

    <!-- 10. Form Curso -->
    <div class="card">
      <div class="card-header">
        <span class="card-icon">📝</span>
        <span class="card-title">Registrar novo curso no site...</span>
        <span class="card-tag tag-form">Formulário</span>
      </div>
      <p>Formulário para cadastrar disciplinas e workshops ofertados na EMAp.</p>
      <ul>
        <li>Coleta nome, nível, carga horária, professor, link e imagem (16:9).</li>
        <li>Grava automaticamente na aba <code>cursos</code> da planilha.</li>
      </ul>
      <a class="form-link-btn" href="https://forms.gle/3v1ZMRcUi9XoDk5k9" target="_blank">
        🔗 https://forms.gle/3v1ZMRcUi9XoDk5k9
      </a>
    </div>
  </div>

  <div class="footer">
    GAIA Lab — Guia de Arquivos do Google Drive • Página 1 de 2
  </div>
</div>

<!-- PÁGINA 2: ARQUITETURA, DIAGRAMA E AUTOMAÇÃO -->
<div class="page">
  <div class="header">
    <div class="header-left">
      <h1>GAIA Lab — Arquitetura e Automação do CMS</h1>
      <p>Fluxo de dados de ponta a ponta: formulários, sincronização e deploy contínuo</p>
      <a class="site-link" href="https://green-ai-lab-gaia.github.io/" target="_blank">
        🌐 https://green-ai-lab-gaia.github.io/
      </a>
    </div>
    <img class="logo" src="data:image/png;base64,{logo_b64}" alt="Logo GAIA Lab">
  </div>

  <h2>Diagrama do Fluxo de Dados e Automação</h2>

  <div class="diagram-wrapper">
    <svg class="diagram-svg" viewBox="0 0 710 395" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <!-- Marcadores de seta -->
        <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#365902" />
        </marker>
        <marker id="arrow-gray" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#57606a" />
        </marker>
        <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#0969da" />
        </marker>
      </defs>

      <!-- NÍVEL 1: ENTRADA (FORMULÁRIOS) -->
      <g>
        <rect x="75" y="6" width="560" height="36" rx="5" fill="#fdf4f4" stroke="#f5c2c7" stroke-width="1.2"/>
        <text x="355" y="22" font-family="-apple-system, sans-serif" font-size="11" font-weight="700" fill="#a71d2a" text-anchor="middle">
          📝 1. ENTRADA DE CONTEÚDO (4 Google Forms + Fale Conosco no Site)
        </text>
        <text x="355" y="35" font-family="-apple-system, sans-serif" font-size="9" fill="#555" text-anchor="middle">
          Formulários: Membro, Artigo, Notícia e Curso preenchidos por pesquisadores / integrantes
        </text>
      </g>

      <!-- SETA 1 -> 2 -->
      <line x1="355" y1="42" x2="355" y2="60" stroke="#365902" stroke-width="1.8" marker-end="url(#arrow-green)"/>
      <text x="362" y="53" font-family="-apple-system, sans-serif" font-size="8" fill="#365902" font-weight="600">
        Respostas salvas em tempo real
      </text>

      <!-- NÍVEL 2: NUVEM GOOGLE -->
      <g>
        <rect x="75" y="61" width="560" height="36" rx="5" fill="#f2f9f3" stroke="#b7e1cd" stroke-width="1.2"/>
        <text x="355" y="77" font-family="-apple-system, sans-serif" font-size="11" font-weight="700" fill="#137333" text-anchor="middle">
          ☁️ 2. NUVEM GOOGLE (Planilha Central Sheets &amp; Pastas de Mídia no Drive)
        </text>
        <text x="355" y="90" font-family="-apple-system, sans-serif" font-size="9" fill="#555" text-anchor="middle">
          Planilha com 5 abas (pessoas, publicacoes, noticias, cursos, contatos) + Pastas de upload de imagens
        </text>
      </g>

      <!-- SETA 2 -> 3 -->
      <line x1="355" y1="97" x2="355" y2="115" stroke="#365902" stroke-width="1.8" marker-end="url(#arrow-green)"/>
      <text x="362" y="108" font-family="-apple-system, sans-serif" font-size="8" fill="#365902" font-weight="600">
        Disparo semanal agendado (Sábado 00:00)
      </text>

      <!-- NÍVEL 3: CRON / ATUALIZAR.SH -->
      <g>
        <rect x="75" y="116" width="560" height="36" rx="5" fill="#fefbee" stroke="#ffeaa7" stroke-width="1.2"/>
        <text x="355" y="132" font-family="-apple-system, sans-serif" font-size="11" font-weight="700" fill="#b06000" text-anchor="middle">
          ⏰ 3. DISPARO NO SERVIDOR (Cron ➔ scripts/atualizar.sh)
        </text>
        <text x="355" y="145" font-family="-apple-system, sans-serif" font-size="9" fill="#555" text-anchor="middle">
          Configura PATH, bloqueia bytecode __pycache__ e aplica trava flock anti-concorrência
        </text>
      </g>

      <!-- SETA 3 -> 4 (ENTRA NO GUARDA-CHUVA) -->
      <line x1="355" y1="152" x2="355" y2="171" stroke="#365902" stroke-width="2" marker-end="url(#arrow-green)"/>
      <text x="362" y="164" font-family="-apple-system, sans-serif" font-size="8.5" fill="#365902" font-weight="700">
        Chama: python3 scripts/sincronizar.py --push
      </text>

      <!-- NÍVEL 4: O GUARDA-CHUVA SINCRONIZAR.PY -->
      <g>
        <!-- Caixa guarda-chuva externa -->
        <rect x="10" y="172" width="690" height="152" rx="7" fill="#f8faf6" stroke="#365902" stroke-width="1.8" stroke-dasharray="5,4"/>
        
        <!-- Faixa de cabeçalho do guarda-chuva -->
        <path d="M 10 179 Q 10 172 17 172 L 693 172 Q 700 172 700 179 L 700 196 L 10 196 Z" fill="#eaf2e3"/>
        <text x="20" y="189" font-family="-apple-system, sans-serif" font-size="10.5" font-weight="700" fill="#1b3300">
          ⚙️ 4. GUARDA-CHUVA: scripts/sincronizar.py (Orquestrador do Pipeline e Deploy Contínuo)
        </text>

        <!-- CAIXINHA A: Download CSVs -->
        <g>
          <rect x="20" y="206" width="118" height="106" rx="5" fill="#ffffff" stroke="#c9dec0" stroke-width="1.2"/>
          <rect x="25" y="211" width="50" height="13" rx="3" fill="#365902"/>
          <text x="50" y="221" font-family="-apple-system, sans-serif" font-size="8" font-weight="700" fill="#ffffff" text-anchor="middle">ETAPA A</text>
          <text x="26" y="235" font-family="-apple-system, sans-serif" font-size="9.5" font-weight="700" fill="#1b3300">Download CSV</text>
          <text x="26" y="247" font-family="monospace" font-size="8.5" fill="#0550ae">tabelas.py</text>
          <text x="26" y="261" font-family="-apple-system, sans-serif" font-size="8" fill="#555">
            <tspan x="26" dy="0">• Baixa planilhas</tspan>
            <tspan x="26" dy="11">• Valida colunas</tspan>
            <tspan x="26" dy="11">• Confere diff local</tspan>
            <tspan x="26" dy="11">• Atualiza dados/</tspan>
          </text>
        </g>

        <!-- SETA A -> B -->
        <line x1="138" y1="259" x2="151" y2="259" stroke="#365902" stroke-width="1.8" marker-end="url(#arrow-green)"/>

        <!-- CAIXINHA B: Download Imagens -->
        <g>
          <rect x="154" y="206" width="118" height="106" rx="5" fill="#ffffff" stroke="#c9dec0" stroke-width="1.2"/>
          <rect x="159" y="211" width="50" height="13" rx="3" fill="#365902"/>
          <text x="184" y="221" font-family="-apple-system, sans-serif" font-size="8" font-weight="700" fill="#ffffff" text-anchor="middle">ETAPA B</text>
          <text x="160" y="235" font-family="-apple-system, sans-serif" font-size="9.5" font-weight="700" fill="#1b3300">Baixar Imagens</text>
          <text x="160" y="247" font-family="monospace" font-size="8.5" fill="#0550ae">baixar_imagens.py</text>
          <text x="160" y="261" font-family="-apple-system, sans-serif" font-size="8" fill="#555">
            <tspan x="160" dy="0">• Lê links do Drive</tspan>
            <tspan x="160" dy="11">• Baixa novas fotos</tspan>
            <tspan x="160" dy="11">• Salva nos itens</tspan>
            <tspan x="160" dy="11">• Cache imagens.json</tspan>
          </text>
        </g>

        <!-- SETA B -> C -->
        <line x1="272" y1="259" x2="285" y2="259" stroke="#365902" stroke-width="1.8" marker-end="url(#arrow-green)"/>

        <!-- CAIXINHA C: Gerar Conteúdo -->
        <g>
          <rect x="288" y="206" width="122" height="106" rx="5" fill="#ffffff" stroke="#c9dec0" stroke-width="1.2"/>
          <rect x="293" y="211" width="50" height="13" rx="3" fill="#365902"/>
          <text x="318" y="221" font-family="-apple-system, sans-serif" font-size="8" font-weight="700" fill="#ffffff" text-anchor="middle">ETAPA C</text>
          <text x="294" y="235" font-family="-apple-system, sans-serif" font-size="9.5" font-weight="700" fill="#1b3300">Gerar Conteúdo</text>
          <text x="294" y="247" font-family="monospace" font-size="8.5" fill="#0550ae">gerar_conteudo.py</text>
          <text x="294" y="261" font-family="-apple-system, sans-serif" font-size="8" fill="#555">
            <tspan x="294" dy="0">• Gera .qmd das 4 seções</tspan>
            <tspan x="294" dy="11">• Fichas e cartões</tspan>
            <tspan x="294" dy="11">• Galeria do Sobre</tspan>
            <tspan x="294" dy="11">• Remove itens antigos</tspan>
          </text>
        </g>

        <!-- SETA C -> D -->
        <line x1="410" y1="259" x2="423" y2="259" stroke="#365902" stroke-width="1.8" marker-end="url(#arrow-green)"/>

        <!-- CAIXINHA D: Build Quarto -->
        <g>
          <rect x="426" y="206" width="120" height="106" rx="5" fill="#ffffff" stroke="#c9dec0" stroke-width="1.2"/>
          <rect x="431" y="211" width="50" height="13" rx="3" fill="#365902"/>
          <text x="456" y="221" font-family="-apple-system, sans-serif" font-size="8" font-weight="700" fill="#ffffff" text-anchor="middle">ETAPA D</text>
          <text x="432" y="235" font-family="-apple-system, sans-serif" font-size="9.5" font-weight="700" fill="#1b3300">Build Quarto</text>
          <text x="432" y="247" font-family="monospace" font-size="8.5" fill="#0550ae">build.sh / Quarto</text>
          <text x="432" y="261" font-family="-apple-system, sans-serif" font-size="8" fill="#555">
            <tspan x="432" dy="0">• Compila pt e en</tspan>
            <tspan x="432" dy="11">• flatten_lang.py</tspan>
            <tspan x="432" dy="11">• Protege e-mails</tspan>
            <tspan x="432" dy="11">• Cria docs/.nojekyll</tspan>
          </text>
        </g>

        <!-- SETA D -> E -->
        <line x1="546" y1="259" x2="559" y2="259" stroke="#0969da" stroke-width="1.8" marker-end="url(#arrow-blue)"/>

        <!-- CAIXINHA E: Deploy Contínuo Git -->
        <g>
          <rect x="562" y="206" width="128" height="106" rx="5" fill="#f0f7ff" stroke="#0969da" stroke-width="1.5"/>
          <rect x="567" y="211" width="86" height="13" rx="3" fill="#0969da"/>
          <text x="610" y="221" font-family="-apple-system, sans-serif" font-size="7.8" font-weight="700" fill="#ffffff" text-anchor="middle">ETAPA E (DEPLOY)</text>
          <text x="568" y="235" font-family="-apple-system, sans-serif" font-size="9.5" font-weight="700" fill="#0969da">Deploy Contínuo</text>
          <text x="568" y="247" font-family="monospace" font-size="8.2" fill="#1b3300">git add/commit/push</text>
          <text x="568" y="261" font-family="-apple-system, sans-serif" font-size="8" fill="#333">
            <tspan x="568" dy="0">• git add dados/ docs/ ...</tspan>
            <tspan x="568" dy="11">• Commit com sumário</tspan>
            <tspan x="568" dy="11">• git pull --rebase</tspan>
            <tspan x="568" dy="11" font-weight="bold" fill="#0969da">• git push (disparo)</tspan>
          </text>
        </g>
      </g>

      <!-- SETA E -> 5 (SAI DO DEPLOY CONTÍNUO PARA O GITHUB PAGES) -->
      <path d="M 626 312 L 626 343" stroke="#0969da" stroke-width="2.2" fill="none" marker-end="url(#arrow-blue)"/>
      <text x="633" y="333" font-family="-apple-system, sans-serif" font-size="8.5" font-weight="700" fill="#0969da">
        git push
      </text>

      <!-- NÍVEL 5: GITHUB PAGES -->
      <g>
        <rect x="360" y="344" width="340" height="42" rx="5" fill="#f6faff" stroke="#0969da" stroke-width="1.5"/>
        <text x="530" y="361" font-family="-apple-system, sans-serif" font-size="11" font-weight="700" fill="#0969da" text-anchor="middle">
          🚀 5. GITHUB PAGES (Servidor CDN / Site no Ar)
        </text>
        <text x="530" y="375" font-family="-apple-system, sans-serif" font-size="8.5" fill="#555" text-anchor="middle">
          Serve os HTMLs pré-compilados da pasta docs/ em: green-ai-lab-gaia.github.io
        </text>
      </g>
    </svg>
  </div>

  <h2>Mapeamento de Responsabilidade dos Arquivos</h2>
  <table class="table-summary">
    <thead>
      <tr>
        <th style="width: 27%;">Item no Google Drive</th>
        <th style="width: 12%;">Tipo</th>
        <th style="width: 28%;">Destino no Repositório / Site</th>
        <th style="width: 33%;">Script Responsável no Pipeline</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>pessoas</strong></td>
        <td>Pasta</td>
        <td><code>people/*/avatar.*</code></td>
        <td><code>scripts/baixar_imagens.py</code></td>
      </tr>
      <tr>
        <td><strong>publicacoes</strong></td>
        <td>Pasta</td>
        <td><code>publications/*/*.*</code></td>
        <td><code>scripts/baixar_imagens.py</code></td>
      </tr>
      <tr>
        <td><strong>noticias</strong></td>
        <td>Pasta</td>
        <td><code>news/*/*.*</code></td>
        <td><code>scripts/baixar_imagens.py</code></td>
      </tr>
      <tr>
        <td><strong>cursos</strong></td>
        <td>Pasta</td>
        <td><code>courses/images/*.*</code></td>
        <td><code>scripts/baixar_imagens.py</code></td>
      </tr>
      <tr>
        <td><strong>Informações do site do Gaia Lab</strong></td>
        <td>Planilha</td>
        <td><code>dados/*.csv</code></td>
        <td><code>scripts/sincronizar.py</code> (com <code>tabelas.py</code>)</td>
      </tr>
      <tr>
        <td><strong>Formulário de Membro</strong></td>
        <td>Formulário</td>
        <td>Aba <code>pessoas</code></td>
        <td>Nativo Google Forms</td>
      </tr>
      <tr>
        <td><strong>Formulário de Artigo</strong></td>
        <td>Formulário</td>
        <td>Aba <code>publicacoes</code></td>
        <td>Nativo Google Forms</td>
      </tr>
      <tr>
        <td><strong>Formulário de Notícia</strong></td>
        <td>Formulário</td>
        <td>Aba <code>noticias</code></td>
        <td>Nativo Google Forms</td>
      </tr>
      <tr>
        <td><strong>Formulário de Curso</strong></td>
        <td>Formulário</td>
        <td>Aba <code>cursos</code></td>
        <td>Nativo Google Forms</td>
      </tr>
      <tr>
        <td><strong>inscricoes</strong></td>
        <td>Apps Script</td>
        <td>Aba <code>contatos</code> / E-mails</td>
        <td><code>ferramentas/apps-script/inscricoes.gs</code></td>
      </tr>
    </tbody>
  </table>

  <h2>Recomendações e Boas Práticas do CMS</h2>
  <div class="rules">
    <ul>
      <li><strong>Permissões no Google Drive:</strong> Mantenha a pasta principal <code>gaia-lab-website</code> e as subpastas de uploads compartilhadas como <strong>"Qualquer pessoa com o link" → "Leitor"</strong>. Isso permite que a rotina do lab baixe imagens sem login.</li>
      <li><strong>Nomes e Títulos das Abas:</strong> Nunca renomeie as abas da planilha (<code>pessoas</code>, <code>publicacoes</code>, <code>noticias</code>, <code>cursos</code>, <code>contatos</code>), pois os scripts de sincronização utilizam esses nomes para compilar o site.</li>
      <li><strong>Edição de Registros:</strong> Os formulários são editáveis. Guarde o link de edição exibido após o envio para corrigir ou atualizar dados posteriormente. O deploy semanal reflete alterações automaticamente.</li>
      <li><strong>Proporções das Imagens:</strong> Fotos de pessoas devem ser quadradas (1:1, mín. 600×600); imagens de notícias e cursos devem ser horizontais (16:9, ex.: 1600×900).</li>
    </ul>
  </div>

  <div class="footer">
    GAIA Lab (Green AI Lab) — FGV EMAp / Rio de Janeiro • Documentação Oficial do Sistema • Página 2 de 2
  </div>
</div>

</body>
</html>
"""

html_path = RAIZ / "readme.html"
pdf_path = RAIZ / "README.pdf"

html_path.write_text(html_content, encoding="utf-8")
print(f"HTML gerado em: {html_path}")

cmd = [
    "/opt/google/chrome/chrome",
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_path}",
    f"file://{html_path}"
]
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0 and pdf_path.exists():
    size_kb = pdf_path.stat().st_size / 1024
    print(f"Sucesso! PDF gerado em: {pdf_path} ({size_kb:.1f} KB)")
else:
    print(f"Erro ao gerar PDF: {res.stderr}")
