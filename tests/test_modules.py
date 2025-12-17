import unittest
import sqlite3
import os
import networkx as nx
from src.database import init_db, save_rankings, insert_product
from src.knowledge_graph import build_graph

class TestModules(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_ranking.db"
        self.conn = init_db(self.test_db)

    def tearDown(self):
        self.conn.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_database_insertion(self):
        records = [
            {
                "rank": 1,
                "product_name": "Test Product",
                "price": "$10",
                "rating": "4.5",
                "review_count": "100",
                "timestamp": "2023-01-01"
            }
        ]
        save_rankings(self.conn, "Test Platform", "Test Category", "http://test.com", records)

        cur = self.conn.cursor()
        cur.execute("SELECT * FROM ranking")
        rows = cur.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][4], 1) # rank

    def test_knowledge_graph(self):
        records = [
            {
                "rank": 1,
                "product_name": "Test Product",
                "price": "$10",
                "rating": "4.5",
                "review_count": "100",
                "timestamp": "2023-01-01"
            }
        ]
        save_rankings(self.conn, "Test Platform", "Test Category", "http://test.com", records)

        G = build_graph(self.test_db)
        self.assertTrue(len(G.nodes) > 0)

        # Check if Product node exists
        prod_id = self.conn.execute("SELECT id FROM product WHERE name='Test Product'").fetchone()[0]
        self.assertTrue(G.has_node(f"Prod{prod_id}"))

if __name__ == "__main__":
    unittest.main()
