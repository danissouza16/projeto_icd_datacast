import re
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
SAIDA = BASE / "Arquivos" / "Cemaden"

PADRAO_ZIP = re.compile(r"^([a-z]{2})(\d{4})cemaden\.zip$", re.IGNORECASE)

encontrados = 0
for zip_path in BASE.glob("*cemaden.zip"):
    m = PADRAO_ZIP.match(zip_path.name)
    if not m:
        print(f"Ignorado (nome fora do padrao): {zip_path.name}")
        continue

    uf, ano = m.group(1).upper(), m.group(2)
    destino = SAIDA / uf / ano
    destino.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path) as z:
        z.extractall(destino)

    n_arquivos = len(list(destino.glob("*")))
    print(f"{zip_path.name} -> {destino.relative_to(BASE)} ({n_arquivos} arquivos)")
    encontrados += 1

if encontrados == 0:
    print("Nenhum .zip 'cemaden' encontrado nesta pasta. "
          "Confirme se o script esta na mesma pasta dos arquivos .zip.")
else:
    print(f"\n{encontrados} arquivos .zip extraidos com sucesso.")
    print("Agora rode o gerar_cemaden_estado_ano.py.")
