# Contexto do projeto — para retomar com Claude Code

Este arquivo resume o que já foi discutido/decidido numa conversa anterior com o Claude
(claude.ai), para que o trabalho continue de forma consistente aqui no terminal.

## O projeto

Grupo D — DataCast. Disciplina ENG 4040 (Projeto Integrado 4). Tema: prever risco de
enchentes na região Sudeste do Brasil, a partir de dados históricos de chuva (INMET,
CEMADEN) e nível/vazão de rios (ANA/HidroWeb), 2019–2024. Cliente fictício: Ministério do
Meio Ambiente e Mudança do Clima.

Integrantes: Rodrigo Touma Costa, Raphael Vincenzo Maniero, Eduardo Luiz Meireles,
Pedro Monteiro Bernardes, Daniel Santana.

Tudo relacionado ao projeto (dados, notebooks, o relatório da Sprint 1 em Google Docs) vive
na pasta do Google Drive **"Projeto Integrado - Ciência de Dados"**. O notebook principal e
mais atualizado é **`Colab final.ipynb`**, também no Drive.

## Pipeline (3 etapas)

1. **Integração** (`src/integracao/`): INMET (base horária, chave `municipio_norm+UF+data+hora`)
   + CEMADEN (chuva agregada por município/hora) + ANA (cota/vazão diárias). Merge `how="left"`
   com INMET como base, para preservar todo registro horário mesmo sem chuva/vazão. Município
   é normalizado (upper, sem acento, sem código de estação) porque o INMET grafa nomes de
   estação de forma inconsistente entre anos (ex.: "PARATI"→"PARATY").

2. **Limpeza** (`src/limpeza/limpeza_e_tratamento.py`), nesta ordem:
   - Unifica coluna de radiação duplicada (`KJ/m²` vs `Kj/m²`) com `combine_first`.
   - Agrega estações duplicadas do mesmo município/hora pela média.
   - Marca `tem_estacao_cemaden`/`tem_estacao_ana` (cobertura geográfica, não qualidade).
   - Interpola linearmente (limite 6h, por município) variáveis meteorológicas contínuas —
     **chuva é excluída de propósito** (interpolar chuva criaria chuva artificial onde não
     choveu).
   - Filtra por limites físicos plausíveis (pressão 860–1050 mB, radiação 0–4000 KJ/m²,
     chuva 0–400 mm/h) — fora da faixa vira ausente, não remove a linha.
   - Gera `dataset_limpo_final.csv` (a base final, ~1GB, não versionada no git).

3. **EDA** (`src/eda/`):
   - Estatísticas descritivas + % de nulos: **já calculadas** (estão na Seção 3.1 do
     relatório). Achado principal: cota_cm/vazao_m3s têm ~69%/68,7% de nulos por cobertura
     geográfica limitada da ANA, não por falha de sensor; precipitação é fortemente
     assimétrica à direita (maioria zero, cauda de eventos extremos).
   - Outliers via IQR: **já calculados**, mas NÃO usados para filtrar dados (só diagnóstico)
     — a filtragem real usa limites físicos (ver limpeza), porque um outlier estatístico em
     chuva/vazão pode ser exatamente o evento de enchente que o projeto quer prever.
   - Histogramas, matriz de correlação, dispersão, séries temporais, geoespacial: **código
     pronto em `src/eda/`, mas ainda não executado** com o dataset completo. Falta rodar e
     colar os resultados reais no relatório.

## Bugs conhecidos já corrigidos nos scripts deste repo

- `histogramas.py` original: o `if` não tinha o corpo indentado (plt.hist ficava fora do
  laço). Corrigido em `src/eda/histogramas.py`.
- `series_temporais.py` original: o bloco de plot estava fora do `for municipio_alvo in ...`,
  então só processava o último município sorteado; também não tinha `random.seed()` (resultado
  não reprodutível). Ambos corrigidos em `src/eda/eda_secao_3_4.py`.

## O relatório (Google Docs "Relatório Sprint 1 - Grupo D")

Segue o roteiro padrão da disciplina (1. Introdução, 2. Obtenção e Tratamento, 3. Análise
Exploratória). Dentro da Seção 3:
- 3.1 (estatísticas descritivas): pronta.
- 3.2 (histogramas): já tem as imagens coladas pelo usuário; texto ainda em elaboração.
- 3.4 (correlação/dispersão/série temporal/geoespacial): pendente de rodar os scripts e
  colar os resultados — o texto discursivo (tendências, força de correlação, padrões
  espaciais) só pode ser escrito depois de ver os números/gráficos reais.
- 3.5 (insights): já tem o primeiro insight escrito (assimetria da chuva → classes
  desbalanceadas → sugestão de oversampling das horas de chuva extrema).

## O que fazer a seguir (pendências)

1. Rodar `src/eda/eda_secao_3_4.py` localmente (ajustar `PATH` no topo) e revisar os PNGs/CSVs
   gerados: matriz de correlação, dispersão chuva×vazão e temperatura×umidade, séries
   temporais de 5 municípios, mapas de precipitação/vazão média.
2. Com esses resultados, escrever o texto da Seção 3.4 do relatório (que descreve os padrões
   reais encontrados — não deve ser escrito sem rodar o código antes).
3. Escrever o texto da Seção 3.2 por variável de histograma (pendente: descobrir/confirmar
   quais variáveis específicas o usuário já colocou no documento e em que ordem).
4. Considerar geocodificar os municípios via tabela pública do IBGE
   (`https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv`)
   já que o dataset limpo não guarda lat/lon — isso é o que o script de geoespacial já faz.
