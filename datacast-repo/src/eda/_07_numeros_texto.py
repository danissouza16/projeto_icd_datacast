# -*- coding: utf-8 -*-
"""Numeros finais citados no texto das secoes 3.2 e 3.4."""
import os, sys, json
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _00_carregar import carregar, BASE

df = carregar()
P,C,V,CO = "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)","chuva_cemaden_mm","vazao_m3s","cota_cm"
T,U,R = "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)","UMIDADE RELATIVA DO AR, HORARIA (%)","RADIACAO GLOBAL (KJ/m²)"
PR = "PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)"
out = {}

print("="*95, "\n1. SAZONALIDADE")
df["mes"] = df["data"].dt.month
mes = df.groupby("mes").agg(chuva=(P,"mean"), vazao=(V,"mean"), temp=(T,"mean")).round(3)
mes["chuva_mm_mes"] = (mes.chuva*24*30.4).round(0)
print(mes.to_string())
umido = mes.loc[[10,11,12,1,2,3],"chuva_mm_mes"].sum(); seco = mes.loc[[4,5,6,7,8,9],"chuva_mm_mes"].sum()
print(f"\n  semestre umido (out-mar) = {umido:,.0f} mm | seco (abr-set) = {seco:,.0f} mm | razao {umido/seco:.1f}x")
out["sazonalidade_razao"] = round(umido/seco,2)
mes.to_csv(os.path.join(BASE,"outputs","tabelas","sazonalidade_mensal.csv"))

print("\n"+"="*95, "\n2. CICLO DIARIO (chuva por hora do dia)")
h = df.groupby("hora").agg(chuva=(P,"mean"), temp=(T,"mean"), umid=(U,"mean"), rad=(R,"mean")).round(3)
print(h.to_string())
print(f"  hora de pico da chuva (UTC): {h.chuva.idxmax()} | minimo: {h.chuva.idxmin()}")

print("\n"+"="*95, "\n3. REDUNDANCIA (blocos com |r| >= 0.95)")
num=[c for c in df.select_dtypes(include=[np.number]).columns if c not in ["hora","tem_estacao_cemaden","tem_estacao_ana"]]
corr=df[num].corr(); alto=(corr.abs()>=0.95)&(~np.eye(len(corr),dtype=bool))
print(f"  pares com |r|>=0.95: {int(alto.values.sum()/2)}")
print(f"  pares com |r|>=0.99: {int(((corr.abs()>=0.99)&(~np.eye(len(corr),dtype=bool))).values.sum()/2)}")
for g,cols in {"pressao":[c for c in num if "PRESS" in c],"temp_ar":[c for c in num if "TEMPERATURA" in c and "ORVALHO" not in c],
               "orvalho":[c for c in num if "ORVALHO" in c],"umidade":[c for c in num if "UMIDADE" in c]}.items():
    sub=corr.loc[cols,cols].where(~np.eye(len(cols),dtype=bool)).stack()
    print(f"  {g:<9} ({len(cols)} col.): r de {sub.min():.3f} a {sub.max():.3f}")
out["pares_095"]=int(alto.values.sum()/2)

print("\n"+"="*95, "\n4. PRESSAO = ALTITUDE")
v=df[[PR,"municipio_norm"]].dropna(); mg=v.groupby("municipio_norm",observed=True)[PR].transform("mean")
r2=1-((v[PR]-mg)**2).sum()/((v[PR]-v[PR].mean())**2).sum()
print(f"  R2 municipio->pressao = {r2:.3f} | dp entre mun = {v.groupby('municipio_norm',observed=True)[PR].mean().std():.1f} mB | dp dentro (mediano) = {v.groupby('municipio_norm',observed=True)[PR].std().median():.1f} mB")
out["r2_pressao_municipio"]=round(float(r2),3)

print("\n"+"="*95, "\n5. COTA x VAZAO / CHUVA x VAZAO (resumo)")
cv=pd.read_csv(os.path.join(BASE,"outputs","tabelas","corr_cota_vazao_por_municipio.csv"),index_col=0).iloc[:,0]
print(f"  cota x vazao: global={df[[CO,V]].corr().iloc[0,1]:+.3f} | intra-mun mediana={cv.median():+.3f} (n={len(cv)})")
lag=pd.read_csv(os.path.join(BASE,"outputs","tabelas","defasagem_chuva_vazao.csv"))
jan=pd.read_csv(os.path.join(BASE,"outputs","tabelas","janela_chuva_vazao.csv"))
i=lag.spearman_mediano_intra_municipio.idxmax()
print(f"  chuva x vazao lag0={lag.spearman_mediano_intra_municipio[0]:.3f} | pico lag={lag.lag_dias[i]:.0f}d rho={lag.spearman_mediano_intra_municipio[i]:.3f}")
print(f"  acumulado: 1d={jan.spearman_mediano[0]:.3f} 7d={jan[jan.janela_dias==7].spearman_mediano.iloc[0]:.3f} 30d={jan[jan.janela_dias==30].spearman_mediano.iloc[0]:.3f} 60d={jan[jan.janela_dias==60].spearman_mediano.iloc[0]:.3f}")
amo=df[[C,V,T,U]].dropna(subset=[C,V]).sample(300000,random_state=42)
print(f"  chuva CEMADEN x vazao (horario): Pearson={amo[C].corr(amo[V]):+.3f} Spearman={amo[C].corr(amo[V],method='spearman'):+.3f}")

print("\n"+"="*95, "\n6. EVENTOS EXTREMOS / DESBALANCEAMENTO")
d=pd.read_parquet(os.path.join(BASE,"outputs","cache","serie_diaria.parquet"))
dv=d.dropna(subset=["vazao"])
lim=dv.groupby("municipio_norm",observed=True)["vazao"].transform(lambda s: s.quantile(.99))
print(f"  dias-municipio com vazao: {len(dv):,}")
print(f"  acima do p99 local: {(dv.vazao>lim).sum():,} ({100*(dv.vazao>lim).mean():.2f}%)")
for q in [0.95,0.99]:
    l=dv.groupby("municipio_norm",observed=True)["vazao"].transform(lambda s: s.quantile(q))
    print(f"    p{int(q*100)}: {100*(dv.vazao>l).mean():.2f}% -> proporcao 1:{(dv.vazao<=l).sum()/max((dv.vazao>l).sum(),1):.0f}")
h_ext=(df[P]>25).sum(); print(f"  horas INMET com chuva > 25 mm/h: {h_ext:,} de {df[P].notna().sum():,} ({100*h_ext/df[P].notna().sum():.4f}%) -> 1:{df[P].notna().sum()/h_ext:.0f}")
out["pct_p99"]=round(float(100*(dv.vazao>lim).mean()),2)

print("\n"+"="*95, "\n7. COBERTURA TEMPORAL POR MUNICIPIO")
cob=df.groupby("municipio_norm",observed=True).agg(h=("data","size"), d=("data","nunique"))
print(f"  horas por municipio: mediana={cob.h.median():,.0f} min={cob.h.min():,} max={cob.h.max():,}")
print(f"  dias distintos: mediana={cob.d.median():,.0f} (de 2192 possiveis = {100*cob.d.median()/2192:.1f}%)")
print(f"  municipios com serie completa (2192 dias): {(cob.d==2192).sum()}")

json.dump(out, open(os.path.join(BASE,"outputs","tabelas","numeros_chave.json"),"w"), indent=2)
print(f"\n[salvo] numeros_chave.json")
