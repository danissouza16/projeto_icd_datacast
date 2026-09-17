# -*- coding: utf-8 -*-
"""
Histogramas das variáveis numéricas - Seção 3.2 do relatório.

Corrige um bug do histogramas.py original (Raphael): o corpo do `if` não
estava indentado, então plt.hist/xlabel/ylabel/show ficavam fora do laço e
o script processava só a última coluna do dataframe (ou dava erro).
"""
import pandas as pd
import matplotlib.pyplot as plt

PATH = "./data/dataset_limpo_final.csv"  # <-- ajuste para o caminho local

df = pd.read_csv(PATH)
print(df.columns)

for col in df.columns:
    if (df[col].dtype == int or df[col].dtype == float) and col != "hora":
        plt.figure(figsize=(8, 5))
        plt.hist(df[col].dropna(), bins=20)
        plt.xlabel(col)
        plt.ylabel("Quantidade")
        plt.title(f"Histograma - {col}")
        plt.tight_layout()
        plt.savefig(f"histograma_{col[:30].strip().replace(' ', '_').replace('/', '-')}.png", dpi=150)
        plt.show()
