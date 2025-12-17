import argparse
import sys
import time
import pandas as pd
import sqlite3
from apscheduler.schedulers.blocking import BlockingScheduler
from src.database import init_db, save_rankings
from src.crawlers.amazon import scrape_amazon_category
from src.crawlers.cosme import scrape_cosme_category
from src.rag import RankingRAG
from src.knowledge_graph import build_graph

# --- Configuration ---
DB_PATH = "ranking_history.db"

# Target URLs
AMAZON_URLS = {
    "Beauty Best Sellers": "https://www.amazon.com/Best-Sellers-Beauty-Personal-Care/zgbs/beauty/ref=zg_bs_nav_beauty_0",
    "Lip Care": "https://www.amazon.com/Best-Sellers-Beauty-Personal-Care-Lip-Care-Products/zgbs/beauty/3761351/ref=zg_bs_nav_beauty_2_11060451",
    "Skin Care": "https://www.amazon.com/Best-Sellers-Beauty-Personal-Care-Skin-Care-Products/zgbs/beauty/11060451/ref=zg_bs_nav_beauty_1",
    "Lip Makeup": "https://www.amazon.com/Best-Sellers-Beauty-Personal-Care-Lip-Makeup/zgbs/beauty/11059031/ref=zg_bs_nav_beauty_2_11058281",
    "Face Powder": "https://www.amazon.com/Best-Sellers-Beauty-Personal-Care-Face-Powder/zgbs/beauty/11058971/ref=zg_bs_nav_beauty_3_11058691"
}

COSME_URLS = {
    "Products Ranking": "https://www.cosme.net/ranking/products",
    "Category 800": "https://www.cosme.net/categories/item/800/",
    "Category 1005": "https://www.cosme.net/categories/item/1005/",
    "Category 904": "https://www.cosme.net/categories/item/904/",
    "Category 803": "https://www.cosme.net/categories/item/803/"
}

def perform_crawling():
    print(f"[{time.ctime()}] Starting crawl job...")
    conn = init_db(DB_PATH)

    # Amazon
    print("Crawling Amazon US...")
    for cat_name, url in AMAZON_URLS.items():
        print(f"  - {cat_name}")
        records = scrape_amazon_category(url)
        if records:
            save_rankings(conn, "Amazon US", cat_name, url, records)
            print(f"    Saved {len(records)} records.")
        else:
            print("    Failed to fetch or parse.")

    # @cosme
    print("Crawling @cosme JP...")
    for cat_name, url in COSME_URLS.items():
        print(f"  - {cat_name}")
        records = scrape_cosme_category(url)
        if records:
            save_rankings(conn, "@cosme JP", cat_name, url, records)
            print(f"    Saved {len(records)} records.")
        else:
            print("    Failed to fetch or parse.")

    conn.close()

    # Update Vector Index after crawling
    print("Updating RAG Index...")
    rag = RankingRAG()
    rag.index_data()
    print(f"[{time.ctime()}] Crawl job finished.")

def export_csv(output_file: str = "ranking_dump.csv"):
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT r.timestamp, pl.name as platform, c.name as category,
           r.rank, p.name as product, r.price, r.rating, r.review_count
    FROM ranking r
    JOIN product p ON r.product_id = p.id
    JOIN category c ON r.category_id = c.id
    JOIN platform pl ON r.platform_id = pl.id
    ORDER BY r.timestamp DESC
    """
    df = pd.read_sql_query(query, conn)
    df.to_csv(output_file, index=False)
    conn.close()
    print(f"Exported data to {output_file}")

def run_scheduler(interval_hours: int = 6):
    scheduler = BlockingScheduler()
    scheduler.add_job(perform_crawling, 'interval', hours=interval_hours)
    print(f"Scheduler started. Running every {interval_hours} hours. Press Ctrl+C to exit.")
    try:
        perform_crawling() # Run once immediately
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

def main():
    parser = argparse.ArgumentParser(description="Beauty Ranking Crawler & RAG System")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: crawl
    subparsers.add_parser("crawl", help="Run the crawler immediately for all URLs")

    # Command: ask
    ask_parser = subparsers.add_parser("ask", help="Ask a question to the RAG system")
    ask_parser.add_argument("query", type=str, help="The question to ask")

    # Command: schedule
    sched_parser = subparsers.add_parser("schedule", help="Run the crawler on a schedule")
    sched_parser.add_argument("--interval", type=int, default=6, help="Interval in hours")

    # Command: export
    export_parser = subparsers.add_parser("export", help="Export database to CSV")
    export_parser.add_argument("--file", type=str, default="ranking_dump.csv", help="Output filename")

    args = parser.parse_args()

    if args.command == "crawl":
        perform_crawling()
    elif args.command == "ask":
        rag = RankingRAG()
        answer = rag.answer_question(args.query)
        print("\n=== Answer ===\n")
        print(answer)
        print("\n==============")
    elif args.command == "schedule":
        run_scheduler(args.interval)
    elif args.command == "export":
        export_csv(args.file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
