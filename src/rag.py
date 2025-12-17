import chromadb
from sentence_transformers import SentenceTransformer
import sqlite3
import networkx as nx
from typing import List, Dict, Any
import datetime
import os

# --- Constants ---
DB_PATH = "ranking_history.db"
CHROMA_PATH = "./chroma_db"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# --- RAG Class ---

class RankingRAG:
    def __init__(self):
        # Initialize Embedding Model
        # Using a lightweight model suitable for CPU
        self.encoder = SentenceTransformer(EMBEDDING_MODEL_NAME)

        # Initialize Vector DB (Chroma)
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.collection = self.chroma_client.get_or_create_collection(name="ranking_records")

    def index_data(self):
        """
        Reads recent rankings from DB, creates text summaries, embeds them,
        and stores in Vector DB.
        """
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # Join tables to get full context
        query = """
        SELECT r.id, p.name as product, c.name as category, pl.name as platform,
               r.rank, r.timestamp, r.price, r.rating
        FROM ranking r
        JOIN product p ON r.product_id = p.id
        JOIN category c ON r.category_id = c.id
        JOIN platform pl ON r.platform_id = pl.id
        WHERE r.id NOT IN (
            -- Avoid re-indexing (naive check, in prod use a tracking table)
            -- For now, we will just upsert everything or handle duplicates via ID
            SELECT -1
        )
        ORDER BY r.timestamp DESC
        LIMIT 500
        """

        records = cur.execute(query).fetchall()

        ids = []
        documents = []
        metadatas = []

        for row in records:
            rid, prod, cat, plat, rank, ts, price, rating = row

            # Create a natural language summary
            # "On 2023-10-27, 'Laneige Lip Mask' was ranked #1 in 'Lip Care' on Amazon US. Price: $24."
            text = (
                f"On {ts}, the product '{prod}' was ranked #{rank} "
                f"in the category '{cat}' on platform '{plat}'. "
            )
            if price:
                text += f"Price: {price}. "
            if rating:
                text += f"Rating: {rating}. "

            ids.append(str(rid))
            documents.append(text)
            metadatas.append({
                "product": prod,
                "category": cat,
                "platform": plat,
                "timestamp": ts,
                "rank": rank
            })

        if documents:
            embeddings = self.encoder.encode(documents).tolist()
            self.collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            print(f"Indexed {len(documents)} records.")
        else:
            print("No records to index.")

        conn.close()

    def retrieve_context(self, query: str, top_k: int = 5) -> List[str]:
        """
        Search Vector DB for relevant ranking records.
        """
        query_embedding = self.encoder.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )

        # Flatten results
        retrieved_texts = []
        if results['documents']:
            for doc in results['documents'][0]:
                retrieved_texts.append(doc)

        return retrieved_texts

    def generate_prompt(self, query: str, context: List[str]) -> str:
        """
        Constructs the prompt for the LLM.
        """
        context_str = "\n".join(f"- {txt}" for txt in context)

        prompt = f"""
You are an expert market analyst for beauty products.
Use the provided context data to answer the user's question.
If the answer is not in the context, state that you do not have enough data.
Focus on Laneige products if mentioned.

Context Data:
{context_str}

User Question: {query}

Answer:
"""
        return prompt.strip()

    def mock_llm_call(self, prompt: str) -> str:
        """
        Simulates the LLM generation.
        In a real scenario, this would call `google.generativeai` or OpenAI.
        """
        # For demonstration, we just return a static message or a simple rule-based response
        # indicating that this is where the LLM would generate text.

        return (
            "[MOCK LLM OUTPUT]\n"
            "Based on the retrieved data, here is the analysis:\n"
            "The data shows recent rankings for the requested products. "
            "(This is a placeholder response. To generate real insights, connect a valid API key "
            "and uncomment the LLM call code in src/rag.py)"
        )

    def answer_question(self, query: str) -> str:
        # 1. Retrieve
        context = self.retrieve_context(query)

        # 2. Augment (Prompt)
        prompt = self.generate_prompt(query, context)

        # 3. Generate
        answer = self.mock_llm_call(prompt)

        return answer

if __name__ == "__main__":
    # Test run
    rag = RankingRAG()
    # rag.index_data() # Only run if DB has data
    # print(rag.answer_question("How is Laneige performing?"))
