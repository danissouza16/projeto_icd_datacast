# -*- coding: utf-8 -*-
"""SECAO 3.4 - Relacoes entre variaveis: correlacao, dispersao, series temporais, geoespacial."""
import os, sys, re, random, unicodedata
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _00_carregar import carregar, BASE
from _estilo import aplicar, curto, AZUL, VERMELHO, VERDE, LARANJA, ROXO, CINZA

aplicar(); random.seed(42); np.random.seed(42)
FIG = os.path.join(BASE, "outputs", "figuras"); TAB = os.path.join(BASE, "outputs", "tabelas")
df = carregar()

P, C, V, CO = "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)", "chuva_cemaden_mm", "vazao_m3s", "cota_cm"
T, U, R = "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)", "UMIDADE RELATIVA DO AR, HORARIA (%)", "RADIACAO GLOBAL (KJ/m²)"
PR = "PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)"

# =================================================================== #
# 3.4.a  HEATMAP DE CORRELACAO
# =================================================================== #
EXCL = ["hora", "tem_estacao_cemaden", "tem_estacao_ana"]
num = [c for c in df.select_dtypes(include=[np.number]).columns if c not in EXCL]
corr = df[num].corr()
rot = [curto(c) for c in corr.columns]
fig, ax = plt.subplots(figsize=(13.5, 11.5))
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1,
            square=True, linewidths=0.5, linecolor="white", annot_kws={"size": 7},
            xticklabels=rot, yticklabels=rot, cbar_kws={"label": "Correlação de Pearson", "shrink": .7}, ax=ax)
ax.set_title("Seção 3.4 — Matriz de correlação de Pearson entre as variáveis numéricas", pad=14)
plt.xticks(rotation=45, ha="right", fontsize=8.5); plt.yticks(rotation=0, fontsize=8.5)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "3_4_heatmap_correlacao.png")); plt.close(fig)
print("[fig] 3_4_heatmap_correlacao.png")

# =================================================================== #
# 3.4.b  BLOCOS REDUNDANTES vs SINAL UTIL
# =================================================================== #
pares = corr.where(~np.eye(len(corr), dtype=bool)).stack().reset_index()
pares.columns = ["v1", "v2", "r"]
pares["chave"] = pares.apply(lambda x: tuple(sorted([x.v1, x.v2])), axis=1)
pares = pares.drop_duplicates("chave").drop(columns="chave")
top = pares.reindex(pares.r.abs().sort_values(ascending=False).index).head(18)
fig, ax = plt.subplots(figsize=(11, 7.5))
lab = [f"{curto(a)}  ×  {curto(b)}" for a, b in zip(top.v1, top.v2)]
cores = [VERMELHO if abs(r) >= 0.95 else (LARANJA if abs(r) >= 0.8 else AZUL) for r in top.r]
ax.barh(range(len(top))[::-1], top.r.values, color=cores, edgecolor="white")
ax.set_yticks(range(len(top))[::-1]); ax.set_yticklabels(lab, fontsize=8.5)
for i, r in zip(range(len(top))[::-1], top.r.values):
    ax.text(r + (0.02 if r > 0 else -0.02), i, f"{r:+.3f}", va="center",
            ha="left" if r > 0 else "right", fontsize=8.5, fontweight="bold")
ax.axvline(0, color="black", lw=0.8); ax.set_xlim(-1.15, 1.15)
ax.set_xlabel("Correlação de Pearson")
ax.set_title("Seção 3.4 — 18 pares de maior correlação absoluta\n(vermelho: |r| ≥ 0,95 = redundância; laranja: 0,80–0,95; azul: < 0,80)")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "3_4_top_correlacoes.png")); plt.close(fig)
print("[fig] 3_4_top_correlacoes.png")

# =================================================================== #
# 3.4.c  DISPERSAO
# =================================================================== #
amo = df.sample(min(120_000, len(df)), random_state=42)

fig, axes = plt.subplots(2, 2, figsize=(14.5, 11))

# (1) temperatura x umidade - relacao forte e nao-linear
a = amo[[T, U]].dropna()
ax = axes[0, 0]
hb = ax.hexbin(a[T], a[U], gridsize=60, cmap="YlOrRd", bins="log", mincnt=1)
plt.colorbar(hb, ax=ax, label="nº de horas (log)")
ax.set_xlabel(curto(T)); ax.set_ylabel(curto(U))
ax.set_title(f"(a) Temperatura × Umidade relativa\nPearson r = {a[T].corr(a[U]):+.3f}  |  Spearman ρ = {a[T].corr(a[U], method='spearman'):+.3f}")

# (2) chuva INMET x chuva CEMADEN - concordancia entre fontes
a = amo[[P, C]].dropna(); a = a[(a[P] > 0) | (a[C] > 0)]
ax = axes[0, 1]
ax.scatter(a[P], a[C], alpha=0.12, s=7, color=VERDE, edgecolor="none")
lim = max(a[P].max(), a[C].max())
ax.plot([0, lim], [0, lim], ls="--", color=VERMELHO, lw=1.4, label="identidade (y = x)")
ax.set_xlabel(curto(P)); ax.set_ylabel(curto(C))
ax.set_title(f"(b) Chuva INMET × Chuva CEMADEN (horas com chuva > 0 em alguma fonte)\nPearson r = {a[P].corr(a[C]):+.3f}")
ax.legend(fontsize=8.5)

# (3) chuva x vazao - a relacao central, e fraca no horario
a = amo[[C, V]].dropna()
ax = axes[1, 0]
ax.scatter(a[C], a[V], alpha=0.18, s=8, color=AZUL, edgecolor="none")
ax.set_xlabel(curto(C)); ax.set_ylabel(curto(V)); ax.set_yscale("symlog")
ax.set_title(f"(c) Chuva CEMADEN × Vazão — MESMA hora\nPearson r = {a[C].corr(a[V]):+.3f}  |  Spearman ρ = {a[C].corr(a[V], method='spearman'):+.3f}  → quase nula")

# (4) cota x vazao - pooling
a = amo[[CO, V, "municipio_norm"]].dropna()
ax = axes[1, 1]
muns = a["municipio_norm"].value_counts().head(6).index
paleta = sns.color_palette("tab10", len(muns))
ax.scatter(a[CO], a[V], alpha=0.10, s=7, color=CINZA, edgecolor="none", label="todos os municípios")
for cor, m in zip(paleta, muns):
    s = a[a["municipio_norm"] == m]
    ax.scatter(s[CO], s[V], alpha=0.65, s=9, color=cor, edgecolor="none", label=m.title())
ax.set_xlabel(curto(CO)); ax.set_ylabel(curto(V)); ax.set_yscale("symlog")
ax.set_title(f"(d) Cota × Vazão — global r = {a[CO].corr(a[V]):+.3f},\nmas cada município é uma curva-chave própria")
ax.legend(fontsize=7.5, markerscale=2, loc="upper left")

fig.suptitle("Seção 3.4 — Gráficos de dispersão entre pares de variáveis", fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.965])
fig.savefig(os.path.join(FIG, "3_4_dispersao.png")); plt.close(fig)
print("[fig] 3_4_dispersao.png")

# =================================================================== #
# 3.4.d  DEFASAGEM E ACUMULADO (explica por que 3.4.c(c) deu ~0)
# =================================================================== #
lagdf = pd.read_csv(os.path.join(TAB, "defasagem_chuva_vazao.csv"))
jandf = pd.read_csv(os.path.join(TAB, "janela_chuva_vazao.csv"))
fig, axes = plt.subplots(1, 2, figsize=(15, 5.6))
ax = axes[0]
ax.plot(lagdf.lag_dias, lagdf.spearman_mediano_intra_municipio, "o-", color=AZUL, lw=2, ms=7, label="mediana intra-município")
ax.plot(lagdf.lag_dias, lagdf.spearman_global, "s--", color=CINZA, lw=1.6, ms=5, label="global (todos juntos)")
imax = lagdf.spearman_mediano_intra_municipio.idxmax()
ax.axvline(lagdf.lag_dias[imax], color=VERMELHO, ls=":", lw=1.6)
ax.annotate(f"pico: {lagdf.lag_dias[imax]:.0f} dias\nρ = {lagdf.spearman_mediano_intra_municipio[imax]:.3f}",
            xy=(lagdf.lag_dias[imax], lagdf.spearman_mediano_intra_municipio[imax]),
            xytext=(5.0, 0.235), fontsize=9, color=VERMELHO, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=VERMELHO))
ax.set_xlabel("Defasagem aplicada à chuva (dias)"); ax.set_ylabel("Spearman ρ  chuva × vazão")
ax.set_title("(a) A vazão responde à chuva com atraso"); ax.legend(fontsize=9); ax.set_ylim(0, 0.42)

ax = axes[1]
ax.plot(jandf.janela_dias, jandf.spearman_mediano, "o-", color=VERDE, lw=2.2, ms=7, label="mediana entre municípios")
ax.fill_between(jandf.janela_dias, jandf.q25, jandf.q75, color=VERDE, alpha=0.18, label="intervalo interquartil")
ax.set_xscale("log"); ax.set_xticks(jandf.janela_dias); ax.set_xticklabels(jandf.janela_dias)
ax.set_xlabel("Janela de chuva acumulada (dias, escala log)"); ax.set_ylabel("Spearman ρ  chuva acumulada × vazão")
ax.set_title("(b) Quanto maior o acúmulo, mais forte o sinal"); ax.legend(fontsize=9)
for x, y in zip(jandf.janela_dias, jandf.spearman_mediano):
    ax.annotate(f"{y:.2f}", (x, y), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=8)

fig.suptitle("Seção 3.4 — Por que a correlação horária chuva × vazão é quase nula: defasagem e acumulação",
             fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig(os.path.join(FIG, "3_4_defasagem.png")); plt.close(fig)
print("[fig] 3_4_defasagem.png")
