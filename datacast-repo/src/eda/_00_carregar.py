# -*- coding: utf-8 -*-
"""Carrega o dataset_limpo_final.csv com dtypes otimizados e salva cache parquet."""
import os, sys, time
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV = os.path.join(BASE, "data", "processados", "dataset_limpo_final.csv")
PARQUET = os.path.join(BASE, "outputs", "cache", "dataset_limpo_final.parquet")

COL_MUN, COL_UF, COL_DATA, COL_HORA = "municipio_norm", "UF", "data", "hora"
FLAGS = ["tem_estacao_cemaden", "tem_estacao_ana"]


def carregar():
    if os.path.exists(PARQUET):
        print(f"[cache] lendo {PARQUET}")
        return pd.read_parquet(PARQUET)

    print(f"[csv] lendo {CSV} ...")
    t0 = time.time()
    header = pd.read_csv(CSV, nrows=0)
    cols = list(header.columns)
    dtypes = {}
    for c in cols:
        if c in (COL_MUN, COL_UF):
            dtypes[c] = "category"
        elif c == COL_HORA:
            dtypes[c] = "int8"
        elif c in FLAGS:
            dtypes[c] = "boolean"
        elif c == COL_DATA:
            pass  # parse depois
        else:
            dtypes[c] = "float32"

    df = pd.read_csv(CSV, dtype=dtypes, parse_dates=[COL_DATA])
    print(f"[csv] {df.shape[0]:,} linhas x {df.shape[1]} colunas em {time.time()-t0:.0f}s")
    print(f"[mem] {df.memory_usage(deep=True).sum()/1e9:.2f} GB")
    df.to_parquet(PARQUET, index=False, compression="snappy")
    print(f"[cache] salvo em {PARQUET}")
    return df


if __name__ == "__main__":
    df = carregar()
    print(df.dtypes.to_string())
