import re
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
ENTRADA = BASE / "Arquivos" / "Cemaden"
SAIDA = BASE / "Arquivos" / "CEMADEN_consolidado"

MESES = [
    "janeiro", "fevereiro", "marco", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]
NUM_DO_MES = {nome: i for i, nome in enumerate(MESES, start=1)}

COLUNAS = [
    "municipio", "codEstacao", "uf", "nomeEstacao",
    "latitude", "longitude", "datahora", "valorMedida",
]
# indices dos campos que usam virgula decimal na origem
CAMPOS_NUMERICOS = (4, 5, 7)


def campo_csv(valor):
    """Coloca aspas so quando o texto tem virgula ou aspas."""
    if "," in valor or '"' in valor:
        return '"' + valor.replace('"', '""') + '"'
    return valor


def converter_linha(linha, origem):
    campos = linha.rstrip("\r\n").split(";")
    if len(campos) != len(COLUNAS):
        raise ValueError(
            f"{origem}: esperava {len(COLUNAS)} campos, veio {len(campos)}: {linha!r}"
        )
    for i in CAMPOS_NUMERICOS:
        campos[i] = campos[i].replace(",", ".")
    return campos


def meses_do_ano(pasta, uf, ano):
    """Devolve os arquivos do ano ordenados de janeiro a dezembro."""
    arquivos = {}
    for p in pasta.glob("*.csv"):
        m = re.fullmatch(rf"{uf.lower()}_([a-z]+)_{ano}_cemaden\.csv", p.name)
        if not m or m.group(1) not in NUM_DO_MES:
            raise ValueError(f"nome de arquivo fora do padrao: {p}")
        arquivos[NUM_DO_MES[m.group(1)]] = p
    return [arquivos[n] for n in sorted(arquivos)]


def main():
    if not ENTRADA.exists():
        raise SystemExit(f"Pasta nao encontrada: {ENTRADA}")

    SAIDA.mkdir(parents=True, exist_ok=True)

    grupos = defaultdict(list)
    for pasta_ano in sorted(ENTRADA.glob("*/*")):
        if pasta_ano.is_dir():
            uf, ano = pasta_ano.parent.name, pasta_ano.name
            grupos[(uf, ano)] = meses_do_ano(pasta_ano, uf, ano)

    for (uf, ano), arquivos in sorted(grupos.items()):
        destino = SAIDA / f"{uf}_{ano}.csv"
        total = 0
        municipios = set()

        with open(destino, "w", encoding="utf-8", newline="\n") as saida:
            saida.write(",".join(COLUNAS) + "\n")
            for arquivo in arquivos:
                with open(arquivo, encoding="utf-8-sig", newline="") as entrada:
                    cabecalho = next(entrada).rstrip("\r\n").split(";")
                    if cabecalho != COLUNAS:
                        raise ValueError(f"cabecalho inesperado em {arquivo}: {cabecalho}")
                    for linha in entrada:
                        # 120 dos 240 arquivos terminam com uma linha em branco
                        if not linha.strip():
                            continue
                        campos = converter_linha(linha, arquivo)
                        municipios.add(campos[0])
                        saida.write(",".join(map(campo_csv, campos)) + "\n")
                        total += 1

        print(
            f"{destino.name}: {len(arquivos)} meses, "
            f"{len(municipios)} municipios, {total:,} linhas"
        )


if __name__ == "__main__":
    main()
