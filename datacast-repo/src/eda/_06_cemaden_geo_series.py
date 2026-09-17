# -*- coding: utf-8 -*-
"""SECAO 3.4 (cont.) - achado CEMADEN, series temporais e analise geoespacial."""
import os, sys, re, random, unicodedata, glob
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _00_carregar import carregar, BASE
from _estilo import aplicar, curto, AZUL, VERMELHO, VERDE, LARANJA, ROXO, CINZA

aplicar(); random.seed(42); np.random.seed(42)
FIG = os.path.join(BASE, "outputs", "figuras"); TAB = os.path.join(BASE, "outputs", "tabelas")
P, C, V, CO = "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)", "chuva_cemaden_mm", "vazao_m3s", "cota_cm"
df = carregar()

def norm(s):
    s = str(s).strip().upper()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s)

# =================================================================== #
# A. ACHADO: chuva_cemaden_mm escala com o nº de estacoes do municipio
# =================================================================== #
print("[1/3] contando estacoes CEMADEN por municipio (todos os anos/UFs)...")
est = {}
for f in sorted(glob.glob(os.path.join(BASE, "data", "raw", "CEMADEN", "consolidado", "*.csv"))):
    d = pd.read_csv(f, usecols=["municipio", "codEstacao"])
    for m, n in d.groupby("municipio")["codEstacao"].nunique().items():
        k = norm(m); est[k] = max(est.get(k, 0), int(n))
est = pd.Series(est, name="n_estacoes")
print(f"      {len(est)} municipios com estacao CEMADEN")

perf = df.groupby("municipio_norm", observed=True).agg(
    chuva_cem_media=(C, "mean"), chuva_cem_max=(C, "max"),
    chuva_inmet_media=(P, "mean"), n=(C, "count")).query("n > 1000")
comp = perf.join(est, how="inner").dropna()
comp.to_csv(os.path.join(TAB, "cemaden_estacoes_vs_chuva.csv"), encoding="utf-8")
r_p = comp.n_estacoes.corr(comp.chuva_cem_media)
r_s = comp.n_estacoes.corr(comp.chuva_cem_media, method="spearman")
print(f"      n={len(comp)} municipios | Pearson={r_p:+.3f} Spearman={r_s:+.3f}")

fig, axes = plt.subplots(1, 2, figsize=(14.5, 5.8))
ax = axes[0]
ax.scatter(comp.n_estacoes, comp.chuva_cem_media, s=48, color=VERMELHO, alpha=0.75,
           edgecolor="white", linewidth=0.6, label="CEMADEN (agregado por soma)")
ax.scatter(comp.n_estacoes, comp.chuva_inmet_media, s=34, color=AZUL, alpha=0.7,
           edgecolor="white", linewidth=0.5, marker="s", label="INMET (referência, 1 estação)")
z = np.polyfit(comp.n_estacoes, comp.chuva_cem_media, 1)
xs = np.linspace(1, comp.n_estacoes.max(), 50)
ax.plot(xs, np.polyval(z, xs), "--", color=VERMELHO, lw=1.6,
        label=f"ajuste linear: y = {z[0]:.3f}·x + {z[1]:.2f}")
for m in ["SAO PAULO", "RIO DE JANEIRO", "ANGRA DOS REIS", "JUIZ DE FORA"]:
    if m in comp.index:
        ax.annotate(m.title(), (comp.loc[m, "n_estacoes"], comp.loc[m, "chuva_cem_media"]),
                    textcoords="offset points", xytext=(-8, 8), fontsize=8.5, fontweight="bold")
ax.set_xlabel("Nº de estações CEMADEN no município")
ax.set_ylabel("Chuva horária média registrada (mm/h)")
ax.set_title(f"(a) A chuva CEMADEN cresce com o nº de estações\nPearson r = {r_p:+.3f}   (a chuva física não deveria depender disso)")
ax.legend(fontsize=8.5)

ax = axes[1]
faixas = pd.cut(comp.n_estacoes, [0, 1, 2, 5, 10, 200],
                labels=["1", "2", "3–5", "6–10", ">10"])
g = comp.groupby(faixas, observed=True).agg(cem=("chuva_cem_media", "mean"), inm=("chuva_inmet_media", "mean"), n=("n_estacoes", "size"))
x = np.arange(len(g)); w = 0.38
ax.bar(x - w/2, g.cem, w, color=VERMELHO, label="CEMADEN", edgecolor="white")
ax.bar(x + w/2, g.inm, w, color=AZUL, label="INMET", edgecolor="white")
for i, (a, b, nn) in enumerate(zip(g.cem, g.inm, g.n)):
    ax.text(i - w/2, a + .06, f"{a:.2f}", ha="center", fontsize=8.5, fontweight="bold")
    ax.text(i + w/2, b + .06, f"{b:.2f}", ha="center", fontsize=8.5)
    ax.text(i, a + .30, f"n={nn}", ha="center", fontsize=7.5, color=CINZA)
ax.set_xticks(x); ax.set_xticklabels(g.index)
ax.set_xlabel("Nº de estações CEMADEN no município")
ax.set_ylabel("Chuva horária média (mm/h)")
_fator = g.cem.iloc[-1] / g.cem.iloc[0]
ax.set_title(f"(b) INMET permanece estável; CEMADEN infla {_fator:.0f}×\ndo município com 1 estação para os com mais de 10")
ax.set_ylim(0, g.cem.max() * 1.22)
ax.legend(fontsize=9)
fig.suptitle("Seção 3.4 — Achado de integração: chuva_cemaden_mm é SOMA entre estações, não média",
             fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig(os.path.join(FIG, "3_4_achado_cemaden.png")); plt.close(fig)
print("[fig] 3_4_achado_cemaden.png")

# =================================================================== #
# B. SERIES TEMPORAIS — 5 municipios com vazao
# =================================================================== #
print("[2/3] series temporais...")
diario = pd.read_parquet(os.path.join(BASE, "outputs", "cache", "serie_diaria.parquet"))
cob = diario.dropna(subset=["vazao"]).groupby("municipio_norm", observed=True).agg(
    dias=("vazao", "size"), amp=("vazao", lambda s: s.max() / max(s.median(), .01)))
elegiveis = cob[cob.dias > 1200].index.tolist()
sorteados = random.sample(elegiveis, 5)
print(f"      elegiveis={len(elegiveis)} | sorteados={sorteados}")

fig, axes = plt.subplots(5, 1, figsize=(15.5, 17), sharex=True)
for ax, m in zip(axes, sorteados):
    s = diario[diario.municipio_norm == m].sort_values("data")
    ax2 = ax.twinx()
    ax.bar(s.data, s.chuva_inmet, color=AZUL, width=1.6, alpha=0.65, label="Chuva INMET (mm/dia)")
    ax.set_ylabel("Chuva (mm/dia)", color=AZUL, fontsize=9)
    ax.tick_params(axis="y", labelcolor=AZUL, labelsize=8)
    ax.invert_yaxis()
    ax2.plot(s.data, s.vazao, color=VERMELHO, lw=1.15, label="Vazão (m³/s)")
    ax2.set_ylabel("Vazão (m³/s)", color=VERMELHO, fontsize=9)
    ax2.tick_params(axis="y", labelcolor=VERMELHO, labelsize=8)
    q = s.vazao.quantile(.99)
    ax2.axhline(q, color=LARANJA, ls="--", lw=1.2)
    ax2.text(s.data.min(), q, f" p99 = {q:,.0f} m³/s", color=LARANJA, fontsize=8, va="bottom", fontweight="bold")
    val = s.dropna(subset=["vazao"])
    ax.set_title(f"{m.title()} — {len(val):,} dias com vazão | chuva anual média ≈ {s.chuva_inmet.sum()/6:,.0f} mm",
                 fontsize=11, loc="left")
    ax.grid(alpha=.3)
axes[-1].set_xlabel("Data")
fig.suptitle("Seção 3.4 — Séries temporais: chuva diária (barras, eixo invertido) × vazão (linha), 2019–2024\n"
             "Cada pico de vazão é precedido por um período chuvoso; a resposta não é instantânea",
             fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.968])
fig.savefig(os.path.join(FIG, "3_4_series_temporais.png")); plt.close(fig)
print("[fig] 3_4_series_temporais.png")

# zoom num evento extremo
alvo = diario.loc[diario.vazao.idxmax(), "municipio_norm"]
s = diario[diario.municipio_norm == alvo].sort_values("data")
pico = s.loc[s.vazao.idxmax(), "data"]
jan = s[(s.data >= pico - pd.Timedelta(days=60)) & (s.data <= pico + pd.Timedelta(days=30))]
fig, ax = plt.subplots(figsize=(14, 5.6)); ax2 = ax.twinx()
ax.bar(jan.data, jan.chuva_inmet, color=AZUL, width=.8, alpha=.75)
ax.set_ylabel("Chuva INMET (mm/dia)", color=AZUL); ax.invert_yaxis()
ax.tick_params(axis="y", labelcolor=AZUL)
ax2.plot(jan.data, jan.vazao, color=VERMELHO, lw=2.2, marker="o", ms=3)
ax2.set_ylabel("Vazão (m³/s)", color=VERMELHO); ax2.tick_params(axis="y", labelcolor=VERMELHO)
ax2.axvline(pico, color=VERDE, ls="--", lw=1.8)
ax2.annotate(f"pico de vazão\n{pico.date()}\n{s.vazao.max():,.0f} m³/s", xy=(pico, s.vazao.max()),
             xytext=(-185, 55), textcoords="offset points", fontsize=9, fontweight="bold", color=VERDE,
             arrowprops=dict(arrowstyle="->", color=VERDE))
ax.set_title(f"Seção 3.4 — Zoom no maior evento da base: {alvo.title()} (janela de 90 dias em torno do pico)")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "3_4_evento_extremo.png")); plt.close(fig)
print("[fig] 3_4_evento_extremo.png")

# =================================================================== #
# C. GEOESPACIAL
# =================================================================== #
print("[3/3] geoespacial...")
ibge = pd.read_csv("https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv")
ibge["municipio_norm"] = ibge["nome"].map(norm)
UF_COD = {"ES": 32, "MG": 31, "RJ": 33, "SP": 35}
sud = ibge[ibge.codigo_uf.isin(UF_COD.values())]

med = df.groupby(["municipio_norm", "UF"], observed=True).agg(
    precip_media=(P, "mean"), vazao_media=(V, "mean"), cota_media=(CO, "mean"), n=(P, "size")).reset_index()
med["cod"] = med.UF.map(UF_COD)
geo = med.merge(sud[["municipio_norm", "codigo_uf", "latitude", "longitude"]],
                left_on=["municipio_norm", "cod"], right_on=["municipio_norm", "codigo_uf"], how="inner")
geo["precip_anual"] = geo.precip_media * 24 * 365.25
print(f"      geocodificados: {len(geo)} de {med.municipio_norm.nunique()} municipios")
geo.to_csv(os.path.join(TAB, "geo_municipios.csv"), index=False, encoding="utf-8")

fig, axes = plt.subplots(1, 2, figsize=(16.5, 6.8))
for ax, (col, cmap, tit, unid) in zip(axes, [
        ("precip_anual", "YlGnBu", "Precipitação média anual (INMET)", "mm/ano"),
        ("vazao_media", "Reds", "Vazão média (ANA/HidroWeb)", "m³/s")]):
    ax.scatter(sud.longitude, sud.latitude, s=1.2, color="#e8e8e8", zorder=1)  # contorno da regiao
    g = geo.dropna(subset=[col])
    kw = dict(s=95, edgecolor="#333333", linewidth=.5, zorder=3, cmap=cmap)
    if col == "vazao_media":
        import matplotlib.colors as mc
        sc = ax.scatter(g.longitude, g.latitude, c=g[col], norm=mc.LogNorm(vmin=max(g[col].min(), .5), vmax=g[col].max()), **kw)
    else:
        sc = ax.scatter(g.longitude, g.latitude, c=g[col], **kw)
    plt.colorbar(sc, ax=ax, label=f"{unid}" + (" (escala log)" if col == "vazao_media" else ""), shrink=.8)
    ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
    ax.set_title(f"{tit}\n{len(g)} municípios com dado")
    ax.set_aspect("equal"); ax.grid(alpha=.3)
    for _, r in g.nlargest(4, col).iterrows():
        ax.annotate(r.municipio_norm.title(), (r.longitude, r.latitude),
                    textcoords="offset points", xytext=(6, 5), fontsize=8, fontweight="bold")
fig.suptitle("Seção 3.4 — Distribuição espacial no Sudeste (pontos cinza = todos os municípios da região)",
             fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.97])
fig.savefig(os.path.join(FIG, "3_4_geoespacial.png")); plt.close(fig)
print("[fig] 3_4_geoespacial.png")

# cobertura das fontes
fig, ax = plt.subplots(figsize=(9.5, 8.5))
cob2 = df.groupby(["municipio_norm", "UF"], observed=True).agg(
    cem=("tem_estacao_cemaden", "max"), ana=("tem_estacao_ana", "max")).reset_index()
cob2["cod"] = cob2.UF.map(UF_COD)
cg = cob2.merge(sud[["municipio_norm", "codigo_uf", "latitude", "longitude"]],
                left_on=["municipio_norm", "cod"], right_on=["municipio_norm", "codigo_uf"], how="inner")
cg["cls"] = np.select([cg.cem & cg.ana, cg.cem & ~cg.ana, ~cg.cem & cg.ana],
                      ["INMET + CEMADEN + ANA", "INMET + CEMADEN", "INMET + ANA"], "somente INMET")
ax.scatter(sud.longitude, sud.latitude, s=1.2, color="#ececec", zorder=1)
for cls, cor, mk in [("INMET + CEMADEN + ANA", VERDE, "o"), ("INMET + CEMADEN", AZUL, "^"),
                     ("INMET + ANA", LARANJA, "s"), ("somente INMET", VERMELHO, "X")]:
    s = cg[cg.cls == cls]
    ax.scatter(s.longitude, s.latitude, s=85, color=cor, marker=mk, edgecolor="#333", linewidth=.5,
               label=f"{cls} ({len(s)})", zorder=3)
ax.legend(fontsize=9.5, loc="lower left", title="Fontes disponíveis no município")
ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude"); ax.set_aspect("equal"); ax.grid(alpha=.3)
ax.set_title("Seção 3.4 — Cobertura das três fontes por município\nA ausência de cota/vazão é geográfica, não falha de sensor")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "3_4_cobertura_fontes.png")); plt.close(fig)
print("[fig] 3_4_cobertura_fontes.png")
print(cg.cls.value_counts().to_string())
