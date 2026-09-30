import pandas as pd

seedPLAN = pd.read_excel('gold_proposals.xlsx', sheet_name='Página1')


# 3. Caminho do arquivo Parquet de saída
seedParq = "gold_proposals.parquet"

# 4. Salvar como Parquet
seedPLAN.to_parquet(seedParq, engine="pyarrow", index=False)

print("Conversão concluída com sucesso!")