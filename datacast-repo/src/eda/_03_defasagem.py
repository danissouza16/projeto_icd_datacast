# -*- coding: utf-8 -*-
"""Por que chuva x vazao ~ 0? Analise de defasagem (lag) e de agregacao por municipio."""
import os, sys
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _00_carregar import carregar, BASE

P, C, V, CO = "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)", "chuva_cemaden_mm", "vazao_m3s", "cota_cm"
df = carregar()

# ---- 1. cota x vazao: global vs dentro de cada municipio (efeito de pooling) ----
sub = df[df[V].notna() & df[CO].notna()]
print("="*100, f"\n1. COTA x VAZAO  (n={len(sub):,})")
print(f"   Pearson global (todos municipios juntos): {sub[[CO,V]].corr().iloc[0,1]:+.3f}")
por_mun = sub.groupby("municipio_norm", observed=True).apply(
    lambda g: g[CO].corr(g[V]) if len(g) > 100 else np.nan, include_groups=False).dropna()
print(f"   Pearson DENTRO de cada municipio: mediana={por_mun.median():+.3f} | "
      f"media={por_mun.mean():+.3f} | n_mun={len(por_mun)}")
print(f"   quartis: q25={por_mun.quantile(.25):+.3f}  q75={por_mun.quantile(.75):+.3f}")
por_mun.sort_values(ascending=False).to_csv(os.path.join(BASE,"outputs","tabelas","corr_cota_vazao_por_municipio.csv"), encoding="utf-8")

# ---- 2. Serie diaria por municipio: chuva acumulada vs vazao, com defasagem ----
print("\n" + "="*100, "\n2. DEFASAGEM CHUVA -> VAZAO (serie diaria por municipio)")
d = df[df["tem_estacao_ana"] == True][["municipio_norm","data",P,C,V]].copy()
diario = d.groupby(["municipio_norm","data"], observed=True).agg(
    chuva_inmet=(P,"sum"), chuva_cem=(C,"sum"), vazao=(V,"mean")).reset_index()
diario = diario.sort_values(["municipio_norm","data"])
print(f"   dias-municipio: {len(diario):,}")

res = []
for lag in range(0, 11):
    g = diario.groupby("municipio_norm", observed=True)
    cl = g["chuva_inmet"].shift(lag)
    tmp = pd.DataFrame({"c": cl, "v": diario["vazao"], "m": diario["municipio_norm"]}).dropna()
    # correlacao dentro de cada municipio (remove efeito de escala entre rios)
    r_int = tmp.groupby("m", observed=True).apply(
        lambda x: x["c"].corr(x["v"], method="spearman") if len(x) > 200 else np.nan,
        include_groups=False).dropna()
    res.append({"lag_dias": lag, "spearman_mediano_intra_municipio": r_int.median(),
                "spearman_global": tmp["c"].corr(tmp["v"], method="spearman"), "n_mun": len(r_int)})
lagdf = pd.DataFrame(res)
print("\n   Chuva INMET (acum. diario) x Vazao, por defasagem:")
print(lagdf.to_string(index=False))

# chuva acumulada em janelas (3,5,7,15,30 dias) x vazao
print("\n   Chuva ACUMULADA em janela x Vazao (mesmo dia), intra-municipio:")
res2 = []
for jan in [1,2,3,5,7,10,15,30,60]:
    g = diario.groupby("municipio_norm", observed=True)["chuva_inmet"]
    acum = g.transform(lambda s: s.rolling(jan, min_periods=max(1,jan//2)).sum())
    tmp = pd.DataFrame({"c": acum, "v": diario["vazao"], "m": diario["municipio_norm"]}).dropna()
    r_int = tmp.groupby("m", observed=True).apply(
        lambda x: x["c"].corr(x["v"], method="spearman") if len(x) > 200 else np.nan,
        include_groups=False).dropna()
    res2.append({"janela_dias": jan, "spearman_mediano": r_int.median(),
                 "q25": r_int.quantile(.25), "q75": r_int.quantile(.75), "n_mun": len(r_int)})
jandf = pd.DataFrame(res2)
print(jandf.to_string(index=False))

lagdf.to_csv(os.path.join(BASE,"outputs","tabelas","defasagem_chuva_vazao.csv"), index=False, encoding="utf-8")
jandf.to_csv(os.path.join(BASE,"outputs","tabelas","janela_chuva_vazao.csv"), index=False, encoding="utf-8")
diario.to_parquet(os.path.join(BASE,"outputs","cache","serie_diaria.parquet"), index=False)
print(f"\n[salvo] tabelas de defasagem e cache da serie diaria")
