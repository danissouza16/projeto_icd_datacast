# DataCast — Previsão de Enchentes na Região Sudeste

Projeto Integrado 4 (ENG 4040) — Grupo D.

**Tema:** Previsão de risco de enchentes na região Sudeste do Brasil.
**Cliente:** Ministério do Meio Ambiente e Mudança do Clima.

## Integrantes

| Nome | Matrícula |
|---|---|
| Rodrigo Touma Costa | 2510583 |
| Raphael Vincenzo Maniero | 2510285 |
| Eduardo Luiz Meireles | 2510502 |
| Pedro Monteiro Bernardes | 2510962 |
| Daniel Santana | 2310995 |

## Sobre o projeto

Pipeline de dados em três etapas:

1. **Integração das Bases de Dados** — união de INMET (meteorologia horária), CEMADEN (chuva)
   e ANA/HidroWeb (cota e vazão dos rios). Ver `src/integracao/`.
2. **Limpeza e Tratamento de Dados** — duplicatas, valores ausentes, limites físicos. Ver
   `src/limpeza/`.
3. **Análise Exploratória de Dados (EDA)** — estatísticas descritivas, outliers, distribuições,
   correlações, séries temporais e visão geoespacial. Ver `src/eda/`.

Os arquivos de dados brutos e intermediários (CSVs grandes, .zip do INMET/CEMADEN) **não**
ficam neste repositório — eles vivem no Google Drive do grupo. Veja `docs/dicionario_de_dados.md`
para a estrutura do dataset final (`dataset_limpo_final.csv`).

## Estrutura

```
.
├── src/
│   ├── integracao/       # consolidar_inmet.py, consolidar_cemaden.py, extrair_cemaden.py
│   ├── limpeza/          # limpeza_e_tratamento.py
│   └── eda/              # histogramas.py, matriz_correlacao.py, eda_secao_3_4.py
├── docs/
│   └── dicionario_de_dados.md
├── data/
│   ├── raw/              # INMET, CEMADEN, ANA (brutos e consolidados — fora do git)
│   └── processados/      # dataset_limpo_final.csv
├── outputs/
│   ├── Relatorio_Secoes_3_2_e_3_4_DataCast.pdf
│   ├── figuras/          # 14 PNGs das seções 3.2 e 3.4
│   ├── tabelas/          # CSVs de apoio com os valores em precisão completa
│   └── cache/            # parquet da base (fora do git)
├── requirements.txt
└── CONTEXT.md            # contexto do projeto para retomar com Claude Code
```

## Como rodar

```bash
pip install -r requirements.txt
```

1. Coloque `dataset_integrado.csv` (ou os brutos INMET/CEMADEN/ANA) em `data/`.
2. Rode `src/limpeza/limpeza_e_tratamento.py` para gerar `dataset_limpo_final.csv`.
3. Rode os scripts de `src/eda/` sobre o dataset limpo.

Cada script tem uma variável `PATH`/`PASTA_PROJETO` no topo — ajuste para o seu caminho local.

## Estado atual

- Integração e limpeza: implementadas (ver ressalvas abaixo).
- Estatísticas descritivas e outliers (IQR): executados.
- **Seções 3.2 e 3.4: executadas sobre a base completa** (7.458.432 linhas). O relatório
  está em `outputs/Relatorio_Secoes_3_2_e_3_4_DataCast.pdf` (19 páginas, 14 figuras).

### Dois bugs a corrigir antes da modelagem

1. `chuva_cemaden_mm` é a **soma** entre as estações do município, não a média — a variável
   mede densidade de sensores (r = +0,910 com o nº de estações), não chuva.
2. A pressão atmosférica bruta é um proxy de altitude (R² = 0,991 com o município). Usar
   anomalia em relação à média da própria estação.

Detalhes e mais três achados em `CONTEXT.md`.

## Pipeline da EDA

Rodar em ordem numérica, a partir da raiz do repositório:

```bash
python src/eda/_00_carregar.py            # cache parquet (~10s após a 1a vez)
python src/eda/_01_perfil.py              # estatísticas descritivas
python src/eda/_02_correlacao.py          # Pearson + Spearman
python src/eda/_03_defasagem.py           # lag e janelas de acumulação
python src/eda/_04_secao_3_2.py           # Figuras 1-5
python src/eda/_05_secao_3_4.py           # Figuras 6-9
python src/eda/_06_cemaden_geo_series.py  # Figuras 10-14 (baixa tabela do IBGE)
python src/eda/_07_numeros_texto.py       # sazonalidade, ciclo diário, raridade
python src/eda/_08_gerar_pdf.py           # monta o PDF
```

Os caminhos são resolvidos a partir da raiz do repositório — não é preciso ajustar `PATH`.
A base deve estar em `data/processados/dataset_limpo_final.csv` e os consolidados do
CEMADEN em `data/raw/CEMADEN/consolidado/`.
