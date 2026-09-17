# -*- coding: utf-8 -*-
"""
Seção 3.4 - Análise de Relações entre Variáveis
Projeto DataCast - Previsão de Enchentes na Região Sudeste

Este script adapta e completa o que já estava no "Colab final.ipynb" do grupo:
  - Corrige o bug de indentação do bloco de séries temporais (estava fora do for)
  - Fixa random.seed() para os municípios sorteados serem reprodutíveis
  - Adiciona gráficos de dispersão (pedidos explicitamente no roteiro 3.4)
  - Adiciona uma visão geoespacial simples (pedida no roteiro, ainda não existia)

COMO USAR:
  1. Ajuste a variável PATH abaixo para o caminho local do dataset_limpo_final.csv
  2. pip install pandas numpy matplotlib seaborn requests
  3. Rode o script. Ele salva os PNGs na pasta atual.
  4. Me mande os prints/PNGs gerados e eu escrevo o texto da seção 3.4 com os
     números e padrões reais (não posso inventar correlações/tendências sem rodar).
"""

import re
import random
import unicodedata

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------------------------
# 0. CONFIGURAÇÃO — ajuste este caminho para o seu ambiente local
# ---------------------------------------------------------------------------
PATH = r"C:\caminho\para\dataset_limpo_final.csv"  # <-- AJUSTE AQUI

random.seed(42)          # reprodutibilidade dos municípios sorteados
np.random.seed(42)       # reprodutibilidade das amostras usadas nos scatterplots

df = pd.read_csv(PATH)
print(f"Base carregada: {df.shape[0]:,} linhas x {df.shape[1]} colunas")

COL_PRECIPITACAO = "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)"
COL_TEMPERATURA = "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)"
COL_UMIDADE = "UMIDADE RELATIVA DO AR, HORARIA (%)"
COL_VAZAO = "vazao_m3s"
COL_CHUVA_CEMADEN = "chuva_cemaden_mm"


# ---------------------------------------------------------------------------
# 1. MATRIZ DE CORRELAÇÃO E HEATMAP
#    (igual ao que já estava escrito no Colab final.ipynb, só roda de fato)
# ---------------------------------------------------------------------------
COLUNAS_EXCLUIR = ["hora", "data", "tem_estacao_cemaden", "tem_estacao_ana"]
colunas_numericas = [
    col for col in df.columns
    if pd.api.types.is_numeric_dtype(df[col]) and col not in COLUNAS_EXCLUIR
]

matriz_corr = df[colunas_numericas].corr()
matriz_corr.round(3).to_csv("matriz_correlacao.csv", encoding="utf-8")

plt.figure(figsize=(14, 12))
sns.heatmap(
    matriz_corr, annot=True, fmt=".2f", cmap="coolwarm",
    center=0, vmin=-1, vmax=1, square=True, linewidths=0.5,
    cbar_kws={"label": "Correlação"},
)
plt.title("Matriz de Correlação — Variáveis Meteorológicas e Hidrológicas")
plt.xticks(rotation=45, ha="right")
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig("matriz_correlacao.png", dpi=150)
plt.show()

# Top 15 pares de maior correlação em módulo
corr_pares = (
    matriz_corr.where(~np.eye(len(matriz_corr), dtype=bool))
    .stack()
    .reset_index()
)
corr_pares.columns = ["variavel_1", "variavel_2", "correlacao"]
corr_pares["par_ordenado"] = corr_pares.apply(
    lambda r: tuple(sorted([r["variavel_1"], r["variavel_2"]])), axis=1
)
corr_pares = corr_pares.drop_duplicates(subset="par_ordenado").drop(columns="par_ordenado")
corr_pares["correlacao_abs"] = corr_pares["correlacao"].abs()
top_correlacoes = corr_pares.sort_values("correlacao_abs", ascending=False).head(15)
print("\nTop 15 pares de maior correlação (em módulo):")
print(top_correlacoes[["variavel_1", "variavel_2", "correlacao"]].to_string(index=False))
top_correlacoes.drop(columns="correlacao_abs").to_csv(
    "top_correlacoes.csv", index=False, encoding="utf-8"
)


# ---------------------------------------------------------------------------
# 2. GRÁFICOS DE DISPERSÃO (pedidos no roteiro 3.4, não existiam ainda)
#    Amostra de 30k linhas para não estourar memória/poluir o gráfico.
# ---------------------------------------------------------------------------
amostra = df.sample(min(30_000, len(df)), random_state=42)

# 2.1 Chuva (CEMADEN) x Vazão — a relação mais central para o projeto
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(amostra[COL_CHUVA_CEMADEN], amostra[COL_VAZAO], alpha=0.25, s=10)
ax.set_xlabel("Chuva CEMADEN (mm/h)")
ax.set_ylabel("Vazão (m³/s)")
ax.set_title("Dispersão: Chuva (CEMADEN) x Vazão do rio")
plt.tight_layout()
plt.savefig("dispersao_chuva_vazao.png", dpi=150)
plt.show()

# 2.2 Temperatura x Umidade — par classicamente anticorrelacionado, bom
#     contraste para discutir linearidade na seção 3.4
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(amostra[COL_TEMPERATURA], amostra[COL_UMIDADE], alpha=0.15, s=8, color="darkorange")
ax.set_xlabel("Temperatura do ar (°C)")
ax.set_ylabel("Umidade relativa (%)")
ax.set_title("Dispersão: Temperatura x Umidade relativa")
plt.tight_layout()
plt.savefig("dispersao_temperatura_umidade.png", dpi=150)
plt.show()


# ---------------------------------------------------------------------------
# 3. SÉRIES TEMPORAIS — precipitação x vazão por município
#    (bug de indentação do notebook original corrigido: antes as linhas de
#    plot ficavam fora do for, então só processava o último município)
# ---------------------------------------------------------------------------
def normalizar_municipio(nome: str) -> str:
    if pd.isna(nome):
        return nome
    nome = str(nome).strip().upper()
    nome = unicodedata.normalize("NFKD", nome)
    nome = nome.encode("ascii", "ignore").decode("ascii")
    nome = re.sub(r"\s+", " ", nome)
    return nome


df_com_ana = df[df["tem_estacao_ana"] == True]
vazao_por_municipio = df_com_ana.groupby("municipio_norm")[COL_VAZAO].count()
municipios_com_vazao = vazao_por_municipio[vazao_por_municipio > 0].index.tolist()

if len(municipios_com_vazao) == 0:
    raise ValueError("Nenhum município com estação ANA possui dados de vazão preenchidos.")

municipios_sorteados = random.sample(municipios_com_vazao, min(5, len(municipios_com_vazao)))
print("\nMunicípios analisados (semente fixa, reprodutível):")
for m in municipios_sorteados:
    print(f"- {m}")

for municipio_alvo in municipios_sorteados:
    df_mun = df[df["municipio_norm"] == municipio_alvo].copy()
    df_mun["data"] = pd.to_datetime(df_mun["data"], errors="coerce")
    df_mun["timestamp"] = df_mun["data"] + pd.to_timedelta(df_mun["hora"], unit="h")
    df_mun = df_mun.sort_values("timestamp")

    serie_diaria = (
        df_mun.groupby(df_mun["timestamp"].dt.date)
        .agg(
            precipitacao_mm_dia=(COL_PRECIPITACAO, "sum"),
            vazao_m3s=(COL_VAZAO, "mean"),
        )
        .reset_index()
        .rename(columns={"timestamp": "data"})
    )
    serie_diaria["data"] = pd.to_datetime(serie_diaria["data"])

    fig, ax1 = plt.subplots(figsize=(16, 6))
    ax1.set_xlabel("Data")
    ax1.set_ylabel("Precipitação diária (mm)", color="tab:blue")
    ax1.plot(serie_diaria["data"], serie_diaria["precipitacao_mm_dia"],
              color="tab:blue", linewidth=1.2, alpha=0.8, label="Precipitação (mm/dia)")
    ax1.tick_params(axis="y", labelcolor="tab:blue")

    ax2 = ax1.twinx()
    ax2.set_ylabel("Vazão (m³/s)", color="tab:red")
    ax2.plot(serie_diaria["data"], serie_diaria["vazao_m3s"],
              color="tab:red", linewidth=1.5, label="Vazão (m³/s)")
    ax2.tick_params(axis="y", labelcolor="tab:red")

    plt.title(f"Precipitação x Vazão — {municipio_alvo} (2019-2024)")
    fig.tight_layout()
    plt.savefig(f"serie_temporal_{municipio_alvo.replace(' ', '_')}.png", dpi=150)
    plt.show()


# ---------------------------------------------------------------------------
# 4. ANÁLISE GEOESPACIAL (pedida no roteiro, ainda não existia no projeto)
#    O dataset limpo só tem municipio_norm/UF, sem lat/lon. Usamos uma tabela
#    pública do IBGE (município -> lat/lon) para geocodificar e enxergar
#    padrões espaciais de chuva/vazão média por município.
# ---------------------------------------------------------------------------
IBGE_URL = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
UF_CODIGO_IBGE = {"ES": 32, "MG": 31, "RJ": 33, "SP": 35}

ibge = pd.read_csv(IBGE_URL)
ibge["municipio_norm"] = ibge["nome"].map(normalizar_municipio)
ibge_sudeste = ibge[ibge["codigo_uf"].isin(UF_CODIGO_IBGE.values())]

media_por_municipio = (
    df.groupby("municipio_norm")
    .agg(
        precipitacao_media=(COL_PRECIPITACAO, "mean"),
        chuva_cemaden_media=(COL_CHUVA_CEMADEN, "mean"),
        vazao_media=(COL_VAZAO, "mean"),
    )
    .reset_index()
)

geo = media_por_municipio.merge(
    ibge_sudeste[["municipio_norm", "latitude", "longitude"]],
    on="municipio_norm",
    how="inner",  # só municípios que deram match no IBGE
)
print(f"\nMunicípios geocodificados: {len(geo)} de {len(media_por_municipio)}")

fig, ax = plt.subplots(figsize=(9, 9))
sc = ax.scatter(
    geo["longitude"], geo["latitude"],
    c=geo["precipitacao_media"], cmap="Blues", s=60, edgecolor="grey", linewidth=0.3,
)
plt.colorbar(sc, label="Precipitação média (mm/h)")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title("Distribuição espacial da precipitação média por município (Sudeste)")
plt.tight_layout()
plt.savefig("geo_precipitacao_media.png", dpi=150)
plt.show()

fig, ax = plt.subplots(figsize=(9, 9))
sc = ax.scatter(
    geo["longitude"], geo["latitude"],
    c=geo["vazao_media"], cmap="Reds", s=60, edgecolor="grey", linewidth=0.3,
)
plt.colorbar(sc, label="Vazão média (m³/s)")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title("Distribuição espacial da vazão média por município (Sudeste)")
plt.tight_layout()
plt.savefig("geo_vazao_media.png", dpi=150)
plt.show()

print("\nConcluído. Arquivos gerados na pasta atual:")
for f in [
    "matriz_correlacao.csv", "matriz_correlacao.png", "top_correlacoes.csv",
    "dispersao_chuva_vazao.png", "dispersao_temperatura_umidade.png",
    "geo_precipitacao_media.png", "geo_vazao_media.png",
]:
    print(f"- {f}")
print("- serie_temporal_<município>.png (5 arquivos)")
