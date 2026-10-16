import os
import psycopg2
from flask import Flask, jsonify, request
from google import genai
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://antonio-manoel-s.github.io"])

# Configurações de API e Banco de Dados
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
DB_URI = os.getenv("NEONTECH")


def get_db_connection():
  return psycopg2.connect(DB_URI)


@app.route("/")
def index():
  return jsonify({"status": "ok"})

@app.route("/search", methods=["POST"])
def search():
  data = request.get_json()
  pergunta = data.get("pergunta", "")

  if not pergunta.strip():
    return jsonify({"error": "A pergunta não pode estar vazia."}), 400

  try:
    # 1. Gera o embedding usando a API do Gemini
    resposta = client.models.embed_content(
        model="models/gemini-embedding-001", contents=pergunta
    )
    vetor_da_busca = resposta.embeddings[0].values

    # 2. Executa a busca no pgvector
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
            SELECT chunk_id, source_excerpt, 1 - (embeddings <=> %s::vector) AS pontuacao_similaridade
            FROM documentos
            ORDER BY embeddings <=> %s::vector
            LIMIT 5;
            """,
        (vetor_da_busca, vetor_da_busca),
    )
    resultados = cur.fetchall()
    cur.close()
    conn.close()

    # 3. Formata os resultados para JSON
    lista_resultados = []
    for linha in resultados:
      lista_resultados.append({
          "chunk_id": linha[0],
          "texto": linha[1],
          "similaridade": round(float(linha[2]), 4),
      })

    return jsonify(lista_resultados)

  except Exception as e:
    return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
  app.run()