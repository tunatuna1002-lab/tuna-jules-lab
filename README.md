# Beauty Ranking Crawler & Graph-RAG System

This project is a Python-based system that periodically scrapes beauty product rankings from **Amazon US** and **@cosme JP**, stores the data in a SQLite database, builds a Knowledge Graph, and provides a Retrieval-Augmented Generation (RAG) interface for natural language queries.

## Features

- **Multi-Platform Crawler:**
  - **Amazon US:** Scrapes Best Sellers using `requests` with robust User-Agent rotation to handle anti-bot measures.
  - **@cosme JP:** Scrapes ranking pages using `Playwright` to handle dynamic content and Japanese text.
- **Data Storage:** SQLite database with a normalized schema (Platform, Category, Product, Ranking).
- **Knowledge Graph:** Builds a `networkx` graph modeling relationships (e.g., `Product --rankedAs--> Ranking --belongsTo--> Category`).
- **Graph-RAG:**
  - Indexes ranking records into a Vector Database (`ChromaDB`) using `SentenceTransformers`.
  - Retrieves relevant context for user queries.
  - Generates natural language answers (currently using a Mock LLM, ready for Google Gemini/OpenAI integration).
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

3. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

## Usage

### 1. Crawl Data
Run the crawler manually to fetch the latest rankings from all configured URLs.
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
- `COSME_URLS`: Dictionary of @cosme ranking URLs.
- `DB_PATH`: Path to the SQLite database file.
- `CHROMA_PATH`: Path to the ChromaDB vector store.

## Architecture

- **`src/crawlers/`**: Modules for scraping specific platforms.
- **`src/database.py`**: SQLite schema and data access layer.
- **`src/knowledge_graph.py`**: Logic to transform DB records into a NetworkX graph.
- **`src/rag.py`**: RAG pipeline (Indexing, Retrieval, Prompt Generation).
- **`main.py`**: Entry point and CLI handler.

## Note on LLM
The current implementation uses a **Mock LLM** function in `src/rag.py` to demonstrate the pipeline without requiring an API key. To enable real generation:
1. Obtain an API key (e.g., Google Gemini or OpenAI).
2. Uncomment the LLM integration code in `src/rag.py`.
