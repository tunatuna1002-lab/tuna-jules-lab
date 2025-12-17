import sqlite3
from typing import List, Dict, Optional

def init_db(db_path: str = "ranking_history.db") -> sqlite3.Connection:
    """SQLite 데이터베이스를 초기화하고 테이블을 생성한다."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Enable foreign keys
    cur.execute("PRAGMA foreign_keys = ON;")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS platform (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            url TEXT,
            platform_id INTEGER,
            FOREIGN KEY (platform_id) REFERENCES platform(id),
            UNIQUE(name, platform_id)
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            brand TEXT,
            UNIQUE(name)
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ranking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            category_id INTEGER,
            platform_id INTEGER,
            rank INTEGER,
            price TEXT,
            rating TEXT,
            review_count TEXT,
            timestamp TEXT,
            FOREIGN KEY (product_id) REFERENCES product(id),
            FOREIGN KEY (category_id) REFERENCES category(id),
            FOREIGN KEY (platform_id) REFERENCES platform(id)
        );
    """)
    conn.commit()
    return conn

def insert_platform(conn: sqlite3.Connection, name: str) -> int:
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO platform (name) VALUES (?)", (name,))
    conn.commit()
    cur.execute("SELECT id FROM platform WHERE name=?", (name,))
    result = cur.fetchone()
    return result[0] if result else -1

def insert_category(conn: sqlite3.Connection, name: str, url: str, platform_id: int) -> int:
    cur = conn.cursor()
    # Update URL if it changes, but primarily check existence by name + platform
    cur.execute(
        "INSERT OR IGNORE INTO category (name, url, platform_id) VALUES (?, ?, ?)",
        (name, url, platform_id),
    )
    conn.commit()
    cur.execute(
        "SELECT id FROM category WHERE name=? AND platform_id=?",
        (name, platform_id),
    )
    result = cur.fetchone()
    return result[0] if result else -1

def insert_product(conn: sqlite3.Connection, name: str, brand: str = None) -> int:
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO product (name, brand) VALUES (?, ?)",
        (name, brand),
    )
    conn.commit()
    cur.execute("SELECT id FROM product WHERE name=?", (name,))
    result = cur.fetchone()
    return result[0] if result else -1

def save_rankings(
    conn: sqlite3.Connection,
    platform_name: str,
    category_name: str,
    category_url: str,
    records: List[Dict]
) -> None:
    """크롤링된 기록을 DB에 저장한다."""
    platform_id = insert_platform(conn, platform_name)
    category_id = insert_category(conn, category_name, category_url, platform_id)

    for rec in records:
        product_id = insert_product(conn, rec["product_name"])
        conn.execute(
            """
            INSERT INTO ranking (
                product_id, category_id, platform_id, rank,
                price, rating, review_count, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                product_id,
                category_id,
                platform_id,
                rec["rank"],
                rec.get("price"),
                rec.get("rating"),
                rec.get("review_count"),
                rec["timestamp"],
            ),
        )
    conn.commit()
