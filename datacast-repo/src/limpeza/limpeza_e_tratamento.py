# -*- coding: utf-8 -*-
"""
Limpeza e Tratamento de Dados - dataset_integrado.csv -> dataset_limpo_final.csv
Extraido do Colab final.ipynb do grupo (secao 2). Ajuste PASTA_PROJETO abaixo.
"""
import pandas as pd
import numpy as np

PASTA_PROJETO = "./data/"  # <-- ajuste para o caminho local com dataset_integrado.csv

df = pd.read_csv(PASTA_PROJETO + "dataset_integrado.csv")
print(f"Formato original: {df.shape[0]:,} linhas x {df.shape[1]} colunas")

# 1. Corrige a coluna de radiacao duplicada

df["RADIACAO GLOBAL (KJ/m²)"] = df["RADIACAO GLOBAL (KJ/m²)"].combine_first(df["RADIACAO GLOBAL (Kj/m²)"])
df = df.drop(columns=["RADIACAO GLOBAL (Kj/m²)"])

# 2. Agrega estacoes duplicadas do mesmo municipio na mesma hora.

colunas_chave = ["municipio_norm", "UF", "data", "hora"]
colunas_numericas = [c for c in df.columns if c not in colunas_chave]

antes = len(df)
df = df.groupby(colunas_chave, as_index=False)[colunas_numericas].mean()
print(f"\nApós agregar estações por municipio+hora: {antes:,} -> {len(df):,} linhas")

dup_restante = df.duplicated(subset=colunas_chave).sum()
print(f"Duplicatas restantes (deveria ser 0): {dup_restante}")

# 3. Ausência estrutural ou pontual

municipios_com_cemaden = set(
    df.loc[df["chuva_cemaden_mm"].notna(), "municipio_norm"].unique()
)
municipios_com_ana = set(
    df.loc[df["cota_cm"].notna(), "municipio_norm"].unique()
)

df["tem_estacao_cemaden"] = df["municipio_norm"].isin(municipios_com_cemaden)
df["tem_estacao_ana"] = df["municipio_norm"].isin(municipios_com_ana)

print(f"\nMunicipios com CEMADEN: {len(municipios_com_cemaden)} de {df['municipio_norm'].nunique()}")
print(f"Municipios com ANA: {len(municipios_com_ana)} de {df['municipio_norm'].nunique()}")

# 4. Preenche valores faltantes, com exceção da chuva

COLUNAS_INTERPOLAVEIS = [
    'PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)',
    'PRESSÃO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)',
    'PRESSÃO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)',
    'RADIACAO GLOBAL (KJ/m²)',
    'TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)',
    'TEMPERATURA DO PONTO DE ORVALHO (°C)',
    'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)',
    'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)',
    'TEMPERATURA ORVALHO MAX. NA HORA ANT. (AUT) (°C)',
    'TEMPERATURA ORVALHO MIN. NA HORA ANT. (AUT) (°C)',
    'UMIDADE REL. MAX. NA HORA ANT. (AUT) (%)',
    'UMIDADE REL. MIN. NA HORA ANT. (AUT) (%)',
    'UMIDADE RELATIVA DO AR, HORARIA (%)',
    'VENTO, DIREÇÃO HORARIA (gr) (° (gr))',
    'VENTO, RAJADA MAXIMA (m/s)',
    'VENTO, VELOCIDADE HORARIA (m/s)',
    'cota_cm',
    'vazao_m3s',
]
COLUNAS_CHUVA = ['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)', 'chuva_cemaden_mm']

df = df.sort_values(['municipio_norm', 'data', 'hora']).reset_index(drop=True)

antes_interp = df[COLUNAS_INTERPOLAVEIS].isna().sum().sum()
df[COLUNAS_INTERPOLAVEIS] = (
    df.groupby('municipio_norm')[COLUNAS_INTERPOLAVEIS]
    .transform(lambda s: s.interpolate(method='linear', limit=6, limit_direction='both'))
)
depois_interp = df[COLUNAS_INTERPOLAVEIS].isna().sum().sum()
print(f"\nValores ausentes interpolados: {antes_interp:,} -> {depois_interp:,}")

print("\nChuva (NAO interpolada, mantida como ausente):")
print(df[COLUNAS_CHUVA].isna().sum())

df.to_csv("dataset_limpo_etapa1.csv", index=False, encoding="utf-8")
print(f"\nSalvo: dataset_limpo_etapa1.csv ({df.shape[0]:,} linhas x {df.shape[1]} colunas)")

colunas_numericas_analise = [
    'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
    'PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)',
    'PRESSÃO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)',
    'PRESSÃO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)',
    'RADIACAO GLOBAL (KJ/m²)',
    'TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)',
    'TEMPERATURA DO PONTO DE ORVALHO (°C)',
    'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)',
    'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)',
    'TEMPERATURA ORVALHO MAX. NA HORA ANT. (AUT) (°C)',
    'TEMPERATURA ORVALHO MIN. NA HORA ANT. (AUT) (°C)',
    'UMIDADE REL. MAX. NA HORA ANT. (AUT) (%)',
    'UMIDADE REL. MIN. NA HORA ANT. (AUT) (%)',
    'UMIDADE RELATIVA DO AR, HORARIA (%)',
    'VENTO, DIREÇÃO HORARIA (gr) (° (gr))',
    'VENTO, RAJADA MAXIMA (m/s)',
    'VENTO, VELOCIDADE HORARIA (m/s)',
    'chuva_cemaden_mm',
    'cota_cm',
    'vazao_m3s',
]

media = df[colunas_numericas_analise].mean()
mediana = df[colunas_numericas_analise].median()
minimo = df[colunas_numericas_analise].min()
maximo = df[colunas_numericas_analise].max()
desvio_padrao = df[colunas_numericas_analise].std()
nulos = df[colunas_numericas_analise].isna().sum()

estatisticas = pd.DataFrame({
    'min': minimo,
    'max': maximo,
    'mean': media,
    'median': mediana,
    'std': desvio_padrao,
    'nulos': nulos,
})
estatisticas['nulos_%'] = (estatisticas['nulos'] / len(df) * 100).round(1)

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
print("\nEstatisticas descritivas:")
print(estatisticas.round(2))

estatisticas.round(2).to_csv("estatisticas_descritivas.csv", encoding="utf-8")
print("\nSalvo: estatisticas_descritivas.csv")

outliers_por_variavel = {}
resumo_outliers = []

for col in colunas_numericas_analise:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1

    outliers = df[
        (df[col] < Q1 - 1.5 * IQR) |
        (df[col] > Q3 + 1.5 * IQR)
    ]

    outliers_por_variavel[col] = outliers
    resumo_outliers.append({'variavel': col, 'qtd_outliers': len(outliers)})
    print(f"{col}: {len(outliers):,} outliers (IQR)")

pd.DataFrame(resumo_outliers).to_csv("outliers_por_variavel.csv", index=False, encoding="utf-8")
print("\nSalvo: outliers_por_variavel.csv")

print("\nExemplos de outliers em chuva_cemaden_mm:")
print(outliers_por_variavel['chuva_cemaden_mm'][
    ['municipio_norm', 'data', 'hora', 'chuva_cemaden_mm']
].head(10))

LIMITES_FISICOS = {
    'PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)': (860, 1050),
    'PRESSÃO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)': (860, 1050),
    'PRESSÃO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)': (860, 1050),
    'RADIACAO GLOBAL (KJ/m²)': (0, 4000),
    'chuva_cemaden_mm': (0, 400),
    'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)': (0, 400),
}

for col, (limite_inf, limite_sup) in LIMITES_FISICOS.items():
    invalidos = ((df[col] < limite_inf) | (df[col] > limite_sup)).sum()
    df.loc[(df[col] < limite_inf) | (df[col] > limite_sup), col] = pd.NA
    print(f"{col}: {invalidos:,} valores fora do limite fisico -> marcados como ausentes")

df.to_csv("dataset_limpo_final.csv", index=False, encoding="utf-8")
print(f"\nSalvo: dataset_limpo_final.csv ({df.shape[0]:,} linhas x {df.shape[1]} colunas)")