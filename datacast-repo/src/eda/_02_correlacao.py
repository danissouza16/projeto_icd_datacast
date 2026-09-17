# -*- coding: utf-8 -*-
"""Matriz de correlação + top pares — insumo da Seção 3.4."""
import os, sys
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _00_carregar import carregar, BASE

df = carregar()
EXCLUIR = ["hora", "tem_estacao_cemaden", "tem_estacao_ana"]
num = [c for c in df.select_dtypes(include=[np.number]).columns if c not in EXCLUIR]

corr = df[num].corr()
corr.round(4).to_csv(os.path.join(BASE, "outputs", "tabelas", "matriz_correlacao.csv"), encoding="utf-8")

pares = corr.where(~np.eye(len(corr), dtype=bool)).stack().reset_index()
pares.columns = ["v1", "v2", "r"]
pares["chave"] = pares.apply(lambda x: tuple(sorted([x.v1, x.v2])), axis=1)
pares = pares.drop_duplicates("chave").drop(columns="chave")
pares["abs_r"] = pares.r.abs()
top = pares.sort_values("abs_r", ascending=False)
top.drop(columns="abs_r").to_csv(os.path.join(BASE, "outputs", "tabelas", "top_correlacoes.csv"), index=False, encoding="utf-8")

print("="*110, "\nTOP 20 CORRELACOES (|r|)\n")
for _, r in top.head(20).iterrows():
    print(f"  {r.r:+.3f}   {r.v1[:52]:<52} x {r.v2[:48]}")

print("\n" + "="*110, "\nCORRELACOES COM vazao_m3s / cota_cm / chuvas\n")
for alvo in ["vazao_m3s", "cota_cm", "chuva_cemaden_mm", "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)"]:
    s = corr[alvo].drop(alvo).sort_values(key=abs, ascending=False)
    print(f"\n--- {alvo} ---")
    for k, v in s.head(8).items():
        print(f"  {v:+.3f}   {k}")

# Spearman (monotônica) num subconjunto-chave, por causa da forte assimetria
chave = ["PRECIPITAÇÃO TOTAL, HORÁRIO (mm)", "chuva_cemaden_mm", "vazao_m3s", "cota_cm",
         "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)", "UMIDADE RELATIVA DO AR, HORARIA (%)",
         "RADIACAO GLOBAL (KJ/m²)", "PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)"]
amo = df[chave].dropna(subset=["vazao_m3s"]).sample(min(400_000, df["vazao_m3s"].notna().sum()), random_state=42)
sp = amo.corr(method="spearman")
sp.round(4).to_csv(os.path.join(BASE, "outputs", "tabelas", "correlacao_spearman.csv"), encoding="utf-8")
print("\n" + "="*110, "\nSPEARMAN (amostra 400k com vazao valida)\n")
print(sp.round(3).to_string())
