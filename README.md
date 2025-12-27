# Beauty Ranking Crawler & Graph-RAG System

This project is a Python-based system that periodically scrapes beauty product rankings from **Amazon US**, stores the data in a SQLite database, builds a Knowledge Graph, and provides a Retrieval-Augmented Generation (RAG) interface for natural language queries using **Google Gemini**.

## Features

- **Platform Crawler:**
  - **Amazon US:** Scrapes Best Sellers using `requests` with robust User-Agent rotation to handle anti-bot measures.
- **Data Storage:** SQLite database with a normalized schema (Platform, Category, Product, Ranking).
- **Knowledge Graph:** Builds a `networkx` graph modeling relationships (e.g., `Product --rankedAs--> Ranking --belongsTo--> Category`).
- **Graph-RAG:**
  - Indexes ranking records into a Vector Database (`ChromaDB`) using `SentenceTransformers`.
  - Retrieves relevant context for user queries.
  - Augments context with Graph traversals (e.g. cross-category listings).
  - Generates natural language answers using **Google Gemini API**.
- **CLI Interface:** Easy-to-use command line tools for crawling, querying, and exporting data.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google API Key:**
   Get an API key from [Google AI Studio](https://aistudio.google.com/) and export it:
   ```bash
   export GOOGLE_API_KEY="your_api_key_here"
   ```

## Usage

### 1. Crawl Data
Run the crawler manually to fetch the latest rankings from configured Amazon URLs.
```bash
python main.py crawl
```

### 2. Ask a Question
Query the system about product rankings.
```bash
python main.py ask "How is Laneige ranked in Lip Care?"
```

### 3. Schedule Automatic Crawling
Run the crawler continuously on a schedule (default: every 6 hours).
```bash
python main.py schedule --interval 6
```

### 4. Export Data
Export the database content to a CSV file for analysis.
```bash
python main.py export --file my_rankings.csv
```

## Configuration

Settings are located in `src/config.py`:
- `AMAZON_URLS`: Dictionary of Amazon Best Seller URLs.
- `DB_PATH`: Path to the SQLite database file.
- `CHROMA_PATH`: Path to the ChromaDB vector store.
- `LLM_MODEL_NAME`: The Gemini model to use (default: `gemini-pro`).

## Architecture

- **`src/crawlers/`**: Modules for scraping.
- **`src/database.py`**: SQLite schema and data access layer.
- **`src/knowledge_graph.py`**: Logic to transform DB records into a NetworkX graph.
- **`src/rag.py`**: RAG pipeline (Indexing, Retrieval, Generation via Google SDK).
- **`main.py`**: Entry point and CLI handler.
