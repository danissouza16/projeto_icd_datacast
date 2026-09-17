# Dicionário de Dados — `dataset_limpo_final.csv`

| Coluna | Tipo | Descrição |
|---|---|---|
| `municipio_norm` | texto | Nome do município, maiúsculo, sem acento |
| `UF` | texto | Sigla do estado (ES, MG, RJ, SP) |
| `data` | data | Data da medição (AAAA-MM-DD) |
| `hora` | inteiro | Hora da medição (0–23) |
| `PRECIPITAÇÃO TOTAL, HORÁRIO (mm)` | numérico | Volume de chuva acumulado na hora (INMET) |
| `PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)` | numérico | Pressão atmosférica medida na hora |
| `PRESSÃO ATMOSFERICA MAX. NA HORA ANT. (AUT) (mB)` | numérico | Pressão atmosférica máxima da hora anterior |
| `PRESSÃO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)` | numérico | Pressão atmosférica mínima da hora anterior |
| `RADIACAO GLOBAL (KJ/m²)` | numérico | Radiação solar global incidente na hora |
| `TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)` | numérico | Temperatura do ar medida na hora |
| `TEMPERATURA DO PONTO DE ORVALHO (°C)` | numérico | Temperatura de saturação de umidade do ar |
| `TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)` | numérico | Temperatura máxima da hora anterior |
| `TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)` | numérico | Temperatura mínima da hora anterior |
| `TEMPERATURA ORVALHO MAX. NA HORA ANT. (AUT) (°C)` | numérico | Temp. de orvalho máxima da hora anterior |
| `TEMPERATURA ORVALHO MIN. NA HORA ANT. (AUT) (°C)` | numérico | Temp. de orvalho mínima da hora anterior |
| `UMIDADE REL. MAX. NA HORA ANT. (AUT) (%)` | numérico | Umidade relativa máxima da hora anterior |
| `UMIDADE REL. MIN. NA HORA ANT. (AUT) (%)` | numérico | Umidade relativa mínima da hora anterior |
| `UMIDADE RELATIVA DO AR, HORARIA (%)` | numérico | Umidade relativa do ar medida na hora |
| `VENTO, DIREÇÃO HORARIA (gr) (° (gr))` | numérico | Direção do vento na hora (0–360°) |
| `VENTO, RAJADA MAXIMA (m/s)` | numérico | Velocidade máxima de rajada de vento na hora |
| `VENTO, VELOCIDADE HORARIA (m/s)` | numérico | Velocidade média do vento na hora |
| `chuva_cemaden_mm` | numérico | Chuva acumulada na hora (CEMADEN, agregado de medições a cada 10 min) |
| `cota_cm` | numérico | Nível do rio na estação fluviométrica mais próxima (ANA, dado diário) |
| `vazao_m3s` | numérico | Vazão do rio na estação mais próxima (ANA, dado diário) |
| `tem_estacao_cemaden` | booleano | Indica se o município possui alguma estação CEMADEN |
| `tem_estacao_ana` | booleano | Indica se o município possui alguma estação fluviométrica ANA |

## Origem e chave de integração

- **INMET**: base horária, 150 estações automáticas (ES: 13, MG: 68, RJ: 27, SP: 42), 2019–2024.
- **CEMADEN**: chuva agregada por `município + data + hora` (soma).
- **ANA/HidroWeb**: cota e vazão diárias, deduplicadas por `município + data`.
- Merge: INMET como base horária de referência, `merge(..., how="left")` com CEMADEN e ANA
  por `municipio_norm + UF + data [+ hora]`. Isso preserva todo registro horário do INMET mesmo
  sem chuva/nível de rio disponível para aquele município.

## Tratamentos aplicados (em ordem)

1. Unificação da coluna de radiação duplicada (`combine_first`).
2. Agregação de estações duplicadas do mesmo município/hora (média).
3. Flags `tem_estacao_cemaden` / `tem_estacao_ana` (cobertura geográfica, não qualidade de sensor).
4. Interpolação linear (`limit=6` horas, `limit_direction='both'`, por município) para variáveis
   meteorológicas contínuas — **exceto chuva** (INMET e CEMADEN), mantida ausente de propósito.
5. Filtro por limites físicos plausíveis (ex.: pressão 860–1050 mB, radiação 0–4000 KJ/m²,
   chuva 0–400 mm/h) — valores fora da faixa marcados como ausentes, não removidos como linha.

Ver `src/limpeza/limpeza_e_tratamento.py` para o código exato.
