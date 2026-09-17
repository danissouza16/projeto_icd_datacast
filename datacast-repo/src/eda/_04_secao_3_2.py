# -*- coding: utf-8 -*-
"""SECAO 3.2 - Distribuicoes (histogramas) das variaveis numericas."""
import os, sys
import numpy as np, pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _00_carregar import carregar, BASE
from _estilo import aplicar, curto, AZUL, VERMELHO, VERDE, LARANJA

aplicar()
FIG = os.path.join(BASE, "outputs", "figuras")
df = carregar()
num = [c for c in df.select_dtypes(include=[np.number]).columns if c != "hora"]

# ------------------------------------------------------------------ #
# 3.2.a  Painel geral com as 20 variaveis
# ------------------------------------------------------------------ #
fig, axes = plt.subplots(5, 4, figsize=(17, 18))
for ax, c in zip(axes.ravel(), num):
    v = df[c].dropna()
    ax.hist(v, bins=50, color=AZUL, edgecolor="white", linewidth=0.3)
    ax.set_title(curto(c), fontsize=10)
    ax.set_ylabel("Frequência", fontsize=8)
    ax.tick_params(labelsize=8)
    ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 4))
    if abs(v.skew()) > 3:
        ax.set_yscale("log")
        ax.set_ylabel("Frequência (log)", fontsize=8)
fig.suptitle("Seção 3.2 — Distribuição das variáveis numéricas (7.458.432 registros horários, 2019–2024)",
             fontsize=14, fontweight="bold", y=0.997)
fig.tight_layout(rect=[0, 0, 1, 0.985])
fig.savefig(os.path.join(FIG, "3_2_painel_histogramas.png"))
plt.close(fig)
print("[fig] 3_2_painel_histogramas.png")

# ------------------------------------------------------------------ #
# 3.2.b  Precipitacao: o problema da massa em zero
# ------------------------------------------------------------------ #
P, C = "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)", "chuva_cemaden_mm"
fig, axes = plt.subplots(2, 2, figsize=(14, 9))

for i, (col, cor, nome) in enumerate([(P, AZUL, "INMET"), (C, VERDE, "CEMADEN")]):
    v = df[col].dropna()
    ax = axes[i, 0]
    ax.hist(v, bins=60, color=cor, edgecolor="white", linewidth=0.3)
    ax.set_yscale("log")
    ax.set_title(f"{nome} — todas as horas  ({(v==0).mean()*100:.1f}% são zero)")
    ax.set_xlabel(curto(col)); ax.set_ylabel("Frequência (escala log)")

    vp = v[v > 0]
    ax = axes[i, 1]
    ax.hist(vp, bins=np.logspace(np.log10(max(vp.min(), 0.01)), np.log10(vp.max()), 50),
            color=cor, edgecolor="white", linewidth=0.3)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_title(f"{nome} — apenas horas com chuva > 0  (n={len(vp):,})")
    ax.set_xlabel(f"{curto(col)} — escala log"); ax.set_ylabel("Frequência (escala log)")
    for q, cq in [(0.90, LARANJA), (0.99, VERMELHO)]:
        x = vp.quantile(q)
        ax.axvline(x, color=cq, ls="--", lw=1.5, label=f"p{int(q*100)} = {x:.1f} mm")
    ax.legend(fontsize=8)

fig.suptitle("Seção 3.2 — Precipitação: assimetria extrema e cauda de eventos intensos",
             fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(os.path.join(FIG, "3_2_precipitacao_detalhe.png"))
plt.close(fig)
print("[fig] 3_2_precipitacao_detalhe.png")

# ------------------------------------------------------------------ #
# 3.2.c  Hidrologicas (cota / vazao)
# ------------------------------------------------------------------ #
fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
v = df["cota_cm"].dropna()
axes[0].hist(v, bins=70, color=LARANJA, edgecolor="white", linewidth=0.3)
axes[0].set_title(f"Cota do rio (cm) — {df['cota_cm'].isna().mean()*100:.1f}% ausentes")
axes[0].set_xlabel("Cota (cm)"); axes[0].set_ylabel("Frequência")
axes[0].axvline(0, color=VERMELHO, ls=":", lw=1.5, label="zero da régua")
axes[0].legend(fontsize=8)

v = df["vazao_m3s"].dropna()
axes[1].hist(v, bins=70, color=VERMELHO, edgecolor="white", linewidth=0.3)
axes[1].set_yscale("log")
axes[1].set_title(f"Vazão (m³/s) — assimetria = {v.skew():.1f}")
axes[1].set_xlabel("Vazão (m³/s)"); axes[1].set_ylabel("Frequência (log)")

vp = v[v > 0]
axes[2].hist(vp, bins=np.logspace(np.log10(vp.min()), np.log10(vp.max()), 60),
             color=VERMELHO, edgecolor="white", linewidth=0.3)
axes[2].set_xscale("log")
axes[2].set_title("Vazão > 0 em escala log — distribuição aproximadamente lognormal")
axes[2].set_xlabel("Vazão (m³/s) — escala log"); axes[2].set_ylabel("Frequência")
fig.suptitle("Seção 3.2 — Variáveis hidrológicas (ANA/HidroWeb)", fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig(os.path.join(FIG, "3_2_hidrologicas.png"))
plt.close(fig)
print("[fig] 3_2_hidrologicas.png")

# ------------------------------------------------------------------ #
# 3.2.d  Meteorologicas bem-comportadas + vento
# ------------------------------------------------------------------ #
sel = ["TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)", "UMIDADE RELATIVA DO AR, HORARIA (%)",
       "PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)", "RADIACAO GLOBAL (KJ/m²)",
       "VENTO, VELOCIDADE HORARIA (m/s)", "VENTO, DIREÇÃO HORARIA (gr) (° (gr))"]
cores = [VERMELHO, AZUL, VERDE, LARANJA, "#8e44ad", "#16a085"]
fig, axes = plt.subplots(2, 3, figsize=(16, 8.5))
for ax, c, cor in zip(axes.ravel(), sel, cores):
    v = df[c].dropna()
    ax.hist(v, bins=60, color=cor, edgecolor="white", linewidth=0.3)
    ax.set_title(f"{curto(c)}\nassim.={v.skew():+.2f} | ausentes={df[c].isna().mean()*100:.1f}%", fontsize=10)
    ax.set_xlabel(curto(c)); ax.set_ylabel("Frequência")
    ax.axvline(v.mean(), color="black", ls="-", lw=1.4, label=f"média {v.mean():.1f}")
    ax.axvline(v.median(), color="black", ls="--", lw=1.4, label=f"mediana {v.median():.1f}")
    ax.legend(fontsize=8)
fig.suptitle("Seção 3.2 — Variáveis meteorológicas contínuas", fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(os.path.join(FIG, "3_2_meteorologicas.png"))
plt.close(fig)
print("[fig] 3_2_meteorologicas.png")

# ------------------------------------------------------------------ #
# 3.2.e  Completude (% ausentes) — contexto para ler os histogramas
# ------------------------------------------------------------------ #
nul = (df[num].isna().mean() * 100).sort_values()
fig, ax = plt.subplots(figsize=(10, 7))
cores_b = [VERMELHO if x > 40 else (LARANJA if x > 12 else VERDE) for x in nul.values]
ax.barh([curto(c) for c in nul.index], nul.values, color=cores_b, edgecolor="white")
for i, x in enumerate(nul.values):
    ax.text(x + 0.7, i, f"{x:.1f}%", va="center", fontsize=8.5)
ax.set_xlabel("% de valores ausentes"); ax.set_xlim(0, 80)
ax.set_title("Seção 3.2 — Completude por variável após a limpeza")
fig.tight_layout()
fig.savefig(os.path.join(FIG, "3_2_completude.png"))
plt.close(fig)
print("[fig] 3_2_completude.png")

# ------ numeros para o texto ------
print("\n" + "="*90 + "\nNUMEROS PARA O TEXTO 3.2\n")
for col, nome in [(P, "INMET"), (C, "CEMADEN")]:
    v = df[col].dropna(); vp = v[v > 0]
    print(f"{nome}: zeros={100*(v==0).mean():.2f}% | n>0={len(vp):,} | "
          f"p50>0={vp.median():.1f} p90>0={vp.quantile(.9):.1f} p99>0={vp.quantile(.99):.1f} max={v.max():.1f}")
    print(f"       massa: horas>10mm={100*(v>10).mean():.3f}% | >25mm={100*(v>25).mean():.4f}% | >50mm={100*(v>50).mean():.5f}%")
v = df["vazao_m3s"].dropna()
print(f"VAZAO: p50={v.median():.1f} p90={v.quantile(.9):.1f} p99={v.quantile(.99):.1f} max={v.max():.1f} | zeros={100*(v==0).mean():.2f}%")
v = df["cota_cm"].dropna()
print(f"COTA : p50={v.median():.1f} p99={v.quantile(.99):.1f} max={v.max():.1f} | negativos={100*(v<0).mean():.2f}%")
v = df["RADIACAO GLOBAL (KJ/m²)"].dropna()
print(f"RADIACAO: zeros={100*(v==0).mean():.2f}% | p50={v.median():.1f} | no teto 4000={100*(v>=3999).mean():.4f}%")
