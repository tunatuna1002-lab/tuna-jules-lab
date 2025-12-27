import chromadb
from sentence_transformers import SentenceTransformer
import sqlite3
import networkx as nx
import os
import google.generativeai as genai
from typing import List, Dict, Any
from src.config import DB_PATH, CHROMA_PATH, EMBEDDING_MODEL_NAME, LLM_MODEL_NAME
from src.knowledge_graph import build_graph

class RankingRAG:
    def __init__(self):
        # Initialize Embedding Model
        self.encoder = SentenceTransformer(EMBEDDING_MODEL_NAME)

        # Initialize Vector DB (Chroma)
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.collection = self.chroma_client.get_or_create_collection(name="ranking_records")

        # Initialize Graph (Lazily or eager)
        try:
            self.graph = build_graph(DB_PATH)
        except Exception:
            self.graph = nx.DiGraph()

    def index_data(self):
        """
        Reads recent rankings from DB, creates text summaries, embeds them,
        and stores in Vector DB.
        """
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        query = """
        SELECT r.id, p.name as product, c.name as category, pl.name as platform,
               r.rank, r.timestamp, r.price, r.rating, p.id
        FROM ranking r
        JOIN product p ON r.product_id = p.id
        JOIN category c ON r.category_id = c.id
        JOIN platform pl ON r.platform_id = pl.id
        ORDER BY r.timestamp DESC
        LIMIT 500
        """

        records = cur.execute(query).fetchall()

        ids = []
        documents = []
        metadatas = []

        for row in records:
            rid, prod, cat, plat, rank, ts, price, rating, pid = row

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
                "product_id": pid,
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
        Search Vector DB for relevant ranking records and augment with Graph context.
        """
        query_embedding = self.encoder.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )

        retrieved_texts = []
        product_ids_found = set()

        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                retrieved_texts.append(doc)
                meta = results['metadatas'][0][i]
                if 'product_id' in meta:
                    product_ids_found.add(meta['product_id'])

        # Graph Augmentation
        if self.graph:
            for pid in product_ids_found:
                node_id = f"Prod{pid}"
                if self.graph.has_node(node_id):
                    # Traverse: Product -> Ranking -> Category
                    ranking_nodes = [n for n in self.graph.successors(node_id)]
                    categories = set()
                    for r_node in ranking_nodes:
                         for neighbor in self.graph.successors(r_node):
                             if neighbor.startswith("C"):
                                 cat_name = self.graph.nodes[neighbor].get('name', 'Unknown')
                                 categories.add(cat_name)

                    if categories:
                         cats_str = ", ".join(categories)
                         prod_name = self.graph.nodes[node_id].get('name', 'Product')
                         retrieved_texts.append(f"Graph Insight: {prod_name} has appeared in categories: {cats_str}.")

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

    def call_llm(self, prompt: str) -> str:
        """
        Calls the Google Gemini API to generate the response.
        Requires GOOGLE_API_KEY environment variable.
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return (
                "[WARNING] GOOGLE_API_KEY not found in environment variables.\n"
                "Please set it to use the AI generation features.\n\n"
                "Context Retrieved (Raw):\n" + prompt.split("Context Data:")[1].split("User Question:")[0]
            )

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(LLM_MODEL_NAME)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"[ERROR] Failed to call Google API: {e}"

    def answer_question(self, query: str) -> str:
        context = self.retrieve_context(query)
        prompt = self.generate_prompt(query, context)
        answer = self.call_llm(prompt)
        return answer

if __name__ == "__main__":
    rag = RankingRAG()
