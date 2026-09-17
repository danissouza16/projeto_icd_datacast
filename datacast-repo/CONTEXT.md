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

## Estado em 16/09/2026 — Seções 3.2 e 3.4 EXECUTADAS

Os scripts da EDA foram rodados sobre a base completa (7.458.432 linhas x 26 colunas,
2019-01-01 a 2024-12-31, 146 municípios). Saídas em `outputs/`:
`Relatorio_Secoes_3_2_e_3_4_DataCast.pdf` (19 páginas, 14 figuras), `outputs/figuras/`,
`outputs/tabelas/`. Pipeline em `src/eda/_00` a `_08`, rodar em ordem numérica.

### Cinco achados (todos verificados na base completa)

1. **BUG — `chuva_cemaden_mm` é SOMA entre estações, não média.** Correlação de +0,910
   (Spearman 0,926, n=86 municípios) entre o nº de estações CEMADEN do município e a chuva
   média registrada. São Paulo (82 estações) recebe 7,39 mm/h de média = ~64.700 mm/ano,
   ~40x a chuva real. Municípios com 1 estação: 0,12 mm/h; com >10 estações: 2,83 mm/h
   (inflação de 23x), enquanto o INMET fica estável em 0,14-0,20 mm/h no mesmo recorte.
   **Corrigir na consolidação**: média (ou máx) entre estações, soma só entre as leituras
   de 10 min da MESMA estação.

2. **BUG — pressão atmosférica bruta mede altitude, não tempo.** O município explica 99,1%
   da variância (R²=0,991). DP entre municípios 36,9 mB vs 3,4 mB dentro. Diamantina 868,4 mB
   (1.300 m) vs Vitória 1015,8 mB (nível do mar). **Usar anomalia** (desvio da média da
   própria estação).

3. **Chuva x vazão é ~0 na hora, mas forte no acumulado.** Spearman +0,04 horário →
   pico de 0,343 com lag de 3 dias → 0,607 com acumulado de 60 dias. Janelas:
   1d=0,286 / 7d=0,479 / 30d=0,513 / 60d=0,607 (mediana intra-município, 52 municípios).
   **Feature engineering de maior retorno**: somas móveis de 3, 7, 15, 30 e 60 dias.

4. **Agregação entre municípios destrói relações (Simpson).** cota x vazão = +0,437 global
   mas **+0,957 dentro de cada município** (mediana, n=52; IQR 0,932–0,981). Cada rio tem
   sua curva-chave. **Sempre condicionar ao município.**

5. **12 pares redundantes (|r| >= 0,95).** Trio de pressão r=1,000; temperatura 0,982–0,988;
   orvalho 0,977–0,988; umidade 0,969–0,980. As 20 variáveis carregam ~10 dimensões.

### Outros números apurados

- Precipitação INMET: 92,58% zeros, assim.=18,99, curtose=568. Com chuva>0: p50=0,6 p90=5,0
  p99=21,0 max=131 mm/h. Horas >25 mm: 0,047% (1:2145).
- Vazão: assim.=7,91, aproximadamente **lognormal** (log resolve). p50=13,5 p99=1.408,9 max=6.805,9.
- Cota: 0,91% negativa (zero da régua é referência arbitrária — não é erro).
- Nulos: INMET 7,6–15,2% | CEMADEN 46,6% | cota 69,4% / vazão 68,7% (cobertura geográfica).
- Sazonalidade: semestre úmido (out–mar) 1.089 mm vs seco (abr–set) 229 mm = 4,8x.
- Ciclo diário (dados em **UTC**): pico de chuva 21h UTC (18h local), mínimo 13h UTC (10h local).
- Desbalanceamento: dias acima do p99 local de vazão = 1,01% (1:98); p95 = 4,98% (1:19).
- Cobertura: só 38 dos 143 municípios geocodificados têm as 3 fontes; 43 só INMET;
  52 municípios com dado da ANA (limite de escopo do modelo de vazão).
- Maior evento da base: São Romão (MG), 20/01/2022, 6.806 m³/s (enchentes de MG em 2022).

### Pendências

1. Corrigir os dois bugs (CEMADEN e pressão) no pipeline de integração/limpeza.
2. Colar o conteúdo do PDF nas seções 3.2 e 3.4 do Google Docs.
3. Seção 3.5 (insights): o insight de desbalanceamento já está escrito; os achados 1 a 4
   acima são material novo para essa seção.
4. Sprint 2: feature engineering (acumulados, anomalia de pressão, seno/cosseno do vento),
   partição treino/validação **por ano completo** (não aleatória).

## O que fazer a seguir (pendências originais da Sprint 1)

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
