# -*- coding: utf-8 -*-
"""Perfil estatístico completo — insumo para escrever as seções 3.2 e 3.4."""
import os, sys, json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _00_carregar import carregar, BASE

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 50)

df = carregar()
n = len(df)
print(f"\n{'='*100}\nDIMENSOES: {n:,} linhas x {df.shape[1]} colunas")
print(f"PERIODO: {df['data'].min().date()} a {df['data'].max().date()}")
print(f"MUNICIPIOS: {df['municipio_norm'].nunique()}  |  UFs: {sorted(df['UF'].unique())}")
print(f"\nLinhas por UF:\n{df['UF'].value_counts().to_string()}")
print(f"\nMunicipios por UF:\n{df.groupby('UF', observed=True)['municipio_norm'].nunique().to_string()}")
print(f"\nFlags: tem_estacao_cemaden={df['tem_estacao_cemaden'].sum():,} ({df['tem_estacao_cemaden'].mean()*100:.1f}%)"
      f" | tem_estacao_ana={df['tem_estacao_ana'].sum():,} ({df['tem_estacao_ana'].mean()*100:.1f}%)")

num = df.select_dtypes(include=[np.number]).columns.drop("hora")
print(f"\n{'='*100}\nESTATISTICAS DESCRITIVAS ({len(num)} variaveis numericas)\n")

linhas = []
for c in num:
    s = df[c]
    v = s.dropna()
    linhas.append({
        "variavel": c,
        "n_validos": len(v),
        "pct_nulos": 100 * (1 - len(v) / n),
        "media": v.mean(), "mediana": v.median(), "desvio": v.std(),
        "min": v.min(), "p1": v.quantile(.01), "q1": v.quantile(.25),
        "q3": v.quantile(.75), "p99": v.quantile(.99), "max": v.max(),
        "assimetria": v.skew(), "curtose": v.kurtosis(),
        "pct_zeros": 100 * (v == 0).mean(),
    })

perfil = pd.DataFrame(linhas)
out = os.path.join(BASE, "outputs", "tabelas", "perfil_variaveis.csv")
perfil.to_csv(out, index=False, encoding="utf-8")

with pd.option_context("display.float_format", lambda x: f"{x:,.2f}"):
    print(perfil[["variavel","pct_nulos","media","mediana","desvio","min","max","assimetria","curtose","pct_zeros"]].to_string(index=False))
print(f"\n[salvo] {out}")
