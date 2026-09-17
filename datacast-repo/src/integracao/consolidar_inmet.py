import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
ENTRADA = BASE / "raw_organized"                      # [CORRIGIDO]
SAIDA = BASE / "Arquivos" / "INMET_consolidado"

LINHAS_CABECALHO = 8  # as 8 primeiras linhas sao metadados da estacao

# Municipios cujo nome tem hifen de verdade (nao separam sufixo de estacao).
HIFEN_NO_NOME = {"GUARDA-MOR"}

# Estacoes que o INMET renomeou entre um ano e outro: padroniza para um nome so,
# senao a mesma estacao aparece com dois nomes ao longo da serie.
ESTACOES_RENOMEADAS = {
    "PARATI": "PARATY",
    "PRES. KENNEDY": "PRESIDENTE KENNEDY",
    "BEBDOURO": "BEBEDOURO",
    "SAO LUIS DO PARAITINGA": "SAO LUIZ DO PARAITINGA",
    "PAMPULHA": "BELO HORIZONTE (PAMPULHA)",
}

# Codigo da estacao no comeco do nome da pasta, ex: "A701_", "A2116_"
PADRAO_CODIGO_ESTACAO = re.compile(r"^[A-Z]\d+_")       # [NOVO]


def normalizar_estacao(nome_pasta: str) -> str:
    nome = nome_pasta.strip().upper()
    nome = PADRAO_CODIGO_ESTACAO.sub("", nome)           # [NOVO] remove "A701_" etc.
    return ESTACOES_RENOMEADAS.get(nome, nome)


def extrair_municipio(nome_estacao: str) -> str:
    """'CAMPOS DOS GOYTACAZES - SAO TOME' -> 'CAMPOS DOS GOYTACAZES'."""
    nome = re.split(r"\s*\(", nome_estacao)[0]   # BELO HORIZONTE (PAMPULHA)
    nome = re.split(r"\s+-\s*", nome)[0]         # SAO PAULO - MIRANTE
    if nome not in HIFEN_NO_NOME:
        nome = nome.split("-")[0]                # SEROPEDICA-ECOLOGIA AGRICOLA
    return nome.strip()


def ler_csv(caminho: Path) -> pd.DataFrame:
    df = pd.read_csv(
        caminho,
        encoding="latin-1",
        sep=";",
        skiprows=LINHAS_CABECALHO,
        decimal=",",
    )
    df = df.drop(columns=[c for c in df.columns if c.startswith("Unnamed:")])
    df = df.rename(columns={"RADIACAO GLOBAL (Kj/m²)": "RADIACAO GLOBAL (KJ/m²)"})
    return df


def main() -> None:
    if not ENTRADA.exists():
        raise SystemExit(f"Pasta nao encontrada: {ENTRADA}")

    SAIDA.mkdir(parents=True, exist_ok=True)

    #  UF, ano -> lista de (municipio, estacao, caminho)
    grupos = defaultdict(list)
    # aceita .CSV e .csv
    arquivos_encontrados = list(ENTRADA.glob("*/*/*.CSV")) + list(ENTRADA.glob("*/*/*.csv"))
    if not arquivos_encontrados:
        raise SystemExit(
            f"Nenhum arquivo .CSV encontrado em {ENTRADA}\\<UF>\\<ESTACAO>\\. "
            "Confira a estrutura de pastas."
        )

    for arquivo in sorted(arquivos_encontrados):
        uf = arquivo.parent.parent.name
        estacao = normalizar_estacao(arquivo.parent.name)
        ano = arquivo.stem
        grupos[(uf, ano)].append((extrair_municipio(estacao), estacao, arquivo))

    for (uf, ano), itens in sorted(grupos.items()):
        partes = []
        for municipio, estacao, arquivo in itens:
            df = ler_csv(arquivo)
            df.insert(0, "UF", uf)
            df.insert(1, "Municipio", municipio)
            df.insert(2, "Estacao", estacao)
            partes.append(df)

        consolidado = pd.concat(partes, ignore_index=True)
        consolidado = consolidado.sort_values(
            ["Municipio", "Estacao", "Data", "Hora UTC"], kind="stable"
        ).reset_index(drop=True)

        destino = SAIDA / f"{uf}_{ano}.csv"
        consolidado.to_csv(destino, index=False, encoding="utf-8")
        print(
            f"{destino.name}: {len(itens)} estacoes, "
            f"{consolidado['Municipio'].nunique()} municipios, "
            f"{len(consolidado):,} linhas"
        )


if __name__ == "__main__":
    main()
