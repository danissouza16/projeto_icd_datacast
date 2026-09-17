# -*- coding: utf-8 -*-
"""
Matriz de correlacao e heatmap - Secao 3.4 do relatorio.
Requer que "df" seja o dataset_limpo_final.csv carregado (ver limpeza/limpeza_e_tratamento.py).
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

PATH = "./data/dataset_limpo_final.csv"  # <-- ajuste
df = pd.read_csv(PATH)

COLUNAS_EXCLUIR = ["hora", "data", "tem_estacao_cemaden", "tem_estacao_ana"]
colunas_numericas = [
    col for col in df.columns
    if pd.api.types.is_numeric_dtype(df[col]) and col not in COLUNAS_EXCLUIR
]
print(f"\nVariáveis usadas na matriz de correlação ({len(colunas_numericas)}):")
for c in colunas_numericas:
    print(f"  - {c}")
matriz_corr = df[colunas_numericas].corr()
matriz_corr.round(3).to_csv("matriz_correlacao.csv", encoding="utf-8")
print("\nSalvo: matriz_correlacao.csv")
plt.figure(figsize=(14, 12))
sns.heatmap(
    matriz_corr,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0,
    vmin=-1,
    vmax=1,
    square=True,
    linewidths=0.5,
    cbar_kws={"label": "Correlação"},
)
plt.title("Matriz de Correlação — Variáveis Meteorológicas e Hidrológicas")
plt.xticks(rotation=45, ha="right")
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig("matriz_correlacao.png", dpi=150)
plt.show()
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
print("\nSalvo: top_correlacoes.csv")