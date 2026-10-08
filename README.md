# Retrieval, RAG & Semantic Analysis

Projeto de **RAG (Retrieval-Augmented Generation)** desenvolvido na LED. O trabalho
analisa propostas de candidatos às eleições brasileiras de 2026. Fiz parte da equipe
de *Retrieval, RAG & Semantic Analysis*.

## Sobre o projeto

As propostas foram divididas em *chunks* e associadas a metadados dos candidatos,
como partido e origem do conteúdo. Em seguida, foram gerados *embeddings* para permitir
a busca semântica das propostas.

## Dados utilizados

O arquivo `GOLD_PROPOSALS.xlsx` reúne propostas coletadas manualmente por outra equipe.
Para gerar os *embeddings*, foi utilizada a coluna `source_excerpt`, que contém o trecho
completo de cada proposta.

## Etapas do processo

O script `postgreesql.py` reúne as etapas de preparação e armazenamento:

1. **Ativação do suporte a vetores:** importa dependências como `pandas` e `psycopg2`
   e habilita a extensão `vector` no PostgreSQL.
2. **Criação da tabela:** lê os dados do arquivo Parquet, define as colunas e cria uma
   coluna vetorial com dimensão 3072, usada pelo modelo `gemini-embedding-001`.
3. **Geração dos embeddings:** cria embeddings para os valores de `source_excerpt`.
   A nova coluna é mantida no DataFrame durante a execução; o arquivo de origem não é
   alterado nessa etapa.
4. **Inserção no banco:** usa `execute_values` e `numpy` para inserir os dados e os
   embeddings no PostgreSQL.

## Arquivos

- `conversaoParquet.py`: converte a planilha XLSX para Parquet, formato mais adequado
  para armazenar colunas com textos extensos e embeddings.
- `postgreesql.py`: prepara a tabela, gera os embeddings e envia os dados ao PostgreSQL.
- `busca.py`: conecta ao banco e busca as propostas mais semelhantes semanticamente à
  pergunta informada. Similaridade não significa que as propostas concordem entre si.

## Banco de dados

O PostgreSQL é hospedado na [Neon](https://console.neon.tech/).