# Dados dos visualizadores da página de pesquisa

Recortes mínimos dos produtos do laboratório, no formato que o navegador lê
direto. O repositório guarda só os dados finais; o pipeline que os refaz a
partir das entregas originais fica fora dele, em `../dados_site/`.

## agro/

Projeto AgroInteligência Territorial (FGV Agro), recorte de Campo Verde (MT),
código IBGE 5102678. Gerado por `../dados_site/preparar_dados_agro.py` a partir
dos GeoPackages de classificação e dos Parquets de índices interpolados do
Drive do projeto.

| Arquivo | Conteúdo |
|---|---|
| `municipio.geojson` | Limite municipal, malha do IBGE |
| `talhoes-<ano>.geojson` | Um polígono por talhão. `s1`/`s2`: classe inferida na 1ª e 2ª safra. `mb1`/`mb2`: classe de referência do MapBiomas. `area_ha`, `tile` Sentinel-1 de origem, `tiles` = em quantos tiles o talhão foi inferido |
| `indices-<ano>-<INDICE>.json` | Série de 16 dias de um índice por talhão (`talhoes[fid]`) e percentis 25, 50 e 75 do município (`regional`) |

Coordenadas em EPSG:4326 com cinco casas decimais. Geometrias simplificadas em
2 m; a entrega de 2020, traçada pixel a pixel, em 10 m.

Classes (`s1`, `s2`, `mb1`, `mb2`): 0 soja, 1 milho, 2 algodão, 3 outros;
nulo = sem classificação para o talhão.

Índices disponíveis: ARVI, CIRE, CVI, EVI, EVI2, GNDVI, GARI, GCVI, GRVI,
MSAVI, NBR, NDRE, NDVI, NDWI, RBNDVI, SAVI, VARIgreen. Um arquivo por ano e
índice, com três casas decimais.
