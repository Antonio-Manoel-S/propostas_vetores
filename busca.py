#pip install -r requirements.txt

# Exemplo de consulta buscando os 3 itens mais parecidos com um vetor de busca
import psycopg2
import os
from google import genai
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

DB_URI = os.getenv("NEONTECH")

conn = psycopg2.connect(DB_URI)
cur = conn.cursor()

# Reseta a transação se o código falhou
conn.rollback()


#LOCAL IMPUT------------------------------------------------

pergunta = "melhoria da segurança publica"
#pergunta

#LOCAL IMPUT------------------------------------------------



resposta = client.models.embed_content(
    model="models/gemini-embedding-001",
    contents=pergunta
)
# 3. Definição da variável: converte a pergunta no vetor de busca
vetor_da_busca = resposta.embeddings[0].values

# 4. Executa a busca no pgvector usando a distância de cosseno (<=>)
cur.execute(
    """
    SELECT chunk_id, source_excerpt, 1 - (embeddings <=> %s::vector) AS pontuacao_similaridade
    FROM documentos
    ORDER BY embeddings <=> %s::vector
    LIMIT 3;
    """,
    (vetor_da_busca, vetor_da_busca)
)
#source_excerpt é o nome da coluna que foi gerado o embedding

# 5. Recupera os resultados
resultados = cur.fetchall()

for linha in resultados:
    print(f"chunk_id: {linha[0]}")
    print(f"Texto: {linha[1]}")
    print(f"Similaridade: {linha[2]:.4f}")
    print("-" * 30)