# -*- coding: utf-8 -*-
"""Estilo visual comum a todas as figuras do relatorio."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

AZUL, VERMELHO, VERDE, LARANJA, ROXO, CINZA = "#1f4e79", "#c0392b", "#27ae60", "#e67e22", "#8e44ad", "#7f8c8d"

def aplicar():
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 150, "savefig.bbox": "tight",
        "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
        "axes.labelsize": 10, "axes.edgecolor": "#444444", "axes.linewidth": 0.8,
        "grid.color": "#dddddd", "grid.linewidth": 0.6,
        "legend.frameon": True, "legend.framealpha": 0.9,
        "figure.facecolor": "white", "axes.facecolor": "white",
    })

# nomes curtos para rotulos de graficos
CURTO = {
    "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)": "Precipitação INMET (mm/h)",
    "PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)": "Pressão atmosf. (mB)",
    "PRESSÃO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)": "Pressão máx. h-1 (mB)",
    "PRESSÃO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)": "Pressão mín. h-1 (mB)",
    "RADIACAO GLOBAL (KJ/m²)": "Radiação global (KJ/m²)",
    "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)": "Temperatura do ar (°C)",
    "TEMPERATURA DO PONTO DE ORVALHO (°C)": "Ponto de orvalho (°C)",
    "TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)": "Temp. máx. h-1 (°C)",
    "TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)": "Temp. mín. h-1 (°C)",
    "TEMPERATURA ORVALHO MAX. NA HORA ANT. (AUT) (°C)": "Orvalho máx. h-1 (°C)",
    "TEMPERATURA ORVALHO MIN. NA HORA ANT. (AUT) (°C)": "Orvalho mín. h-1 (°C)",
    "UMIDADE REL. MAX. NA HORA ANT. (AUT) (%)": "Umidade máx. h-1 (%)",
    "UMIDADE REL. MIN. NA HORA ANT. (AUT) (%)": "Umidade mín. h-1 (%)",
    "UMIDADE RELATIVA DO AR, HORARIA (%)": "Umidade relativa (%)",
    "VENTO, DIREÇÃO HORARIA (gr) (° (gr))": "Direção do vento (°)",
    "VENTO, RAJADA MAXIMA (m/s)": "Rajada máxima (m/s)",
    "VENTO, VELOCIDADE HORARIA (m/s)": "Velocidade do vento (m/s)",
    "chuva_cemaden_mm": "Chuva CEMADEN (mm/h)",
    "cota_cm": "Cota do rio (cm)",
    "vazao_m3s": "Vazão (m³/s)",
}
def curto(c): return CURTO.get(c, c)
