import pandas as pd
import os
import psycopg2
from pgvector.psycopg2 import register_vector

DB_URI = os.getenv("NEONTECH")

conn = psycopg2.connect(DB_URI)
cur = conn.cursor()

#-----------instalacao do vetor

cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
register_vector(conn)
conn.commit()

#-----------instalacao do vetor

#-----------criacao da tabela no postgree

seedPLAN = pd.read_parquet('gold_proposals.parquet')

type_mapping = {
    "int64": "INTEGER",
    "int32": "INTEGER",
    "float64": "REAL",
    "float32": "REAL",
    "object": "TEXT",
    "bool": "BOOLEAN",
    "datetime64[ns]": "TIMESTAMP",
}

colunas_sql = []

# Reseta a transação se o código falhou
conn.rollback()

for coluna, dtype in seedPLAN.dtypes.items():
    # Limpa o nome da coluna para evitar caracteres inválidos no SQL
    coluna_limpa = (
        coluna.strip().lower().replace(" ", "_").replace("-", "_")
    )

    tipo_pg = type_mapping.get(str(dtype), "TEXT")
    colunas_sql.append(f'"{coluna_limpa}" {tipo_pg}')


DIMENSAO_VETOR = 3072

colunas_sql.append(f"embeddings vector({DIMENSAO_VETOR})")

query_create = f"""
    CREATE TABLE IF NOT EXISTS documentos (
        {", ".join(colunas_sql)}
    );
"""

cur.execute(query_create)
conn.commit()

#-----------criacao da tabela no postgree

#-----------criacao dos embeddings em cache

import json
from google import genai
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)



valoresembed = []

if 'embeddings' not in seedPLAN.columns:

    # Função para obter o embedding de cada texto
    def gerar_embedding(texto):
      if not texto or pd.isna(texto):
        return None
        
      resposta = client.models.embed_content(
      model="gemini-embedding-001",  
      contents=texto
      )
      # Extrai a lista de vetores do objeto de resposta
      return resposta.embeddings[0].values

    # Aplica a função em toda a coluna "texto" e grava no DataFrame
    
    seedPLAN["embeddings"] = seedPLAN["source_excerpt"].apply(gerar_embedding)
                                    #local do texto para vetor
    seedPLAN.to_parquet(engine="pyarrow", index=False)

else:
  print("Coluna 'embeddings' já existe.")

#-----------criacao dos embeddings em cache

#-----------INSERT da tabela parquet em cache
from psycopg2.extras import execute_values

import numpy as np

seedPLAN = seedPLAN.replace({np.nan: None, pd.NaT: None})
# Substitui valores NaT, NaN e infinitos por None
colunas_insercao = list(seedPLAN.columns)

valores = [tuple(row) for row in seedPLAN.to_numpy()]

cols_str = ", ".join([f'"{c}"' for c in colunas_insercao])
query_insert = f"INSERT INTO documentos ({cols_str}) VALUES %s"

execute_values(cur, query_insert, valores)
conn.commit()

#-----------INSERT da tabela parquet em cache
