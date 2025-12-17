import networkx as nx
import sqlite3
from typing import Dict, Any

def build_graph(db_path: str = "ranking_history.db") -> nx.DiGraph:
    """DB 내용을 읽어 온톨로지 그래프를 구성한다."""
    conn = sqlite3.connect(db_path)
    G = nx.DiGraph()
    cur = conn.cursor()

    # 플랫폼 노드
    # Node ID format: P{id}
    for pid, pname in cur.execute("SELECT id, name FROM platform"):
        G.add_node(f"P{pid}", type="Platform", name=pname, label=pname)

    # 카테고리 노드와 관계
    # Node ID format: C{id}
    for cid, cname, pid in cur.execute("SELECT id, name, platform_id FROM category"):
        G.add_node(f"C{cid}", type="Category", name=cname, label=cname)
        G.add_edge(f"C{cid}", f"P{pid}", relation="listedOn")

    # 제품 노드
    # Node ID format: Prod{id}
    for prod_id, prod_name, prod_brand in cur.execute("SELECT id, name, brand FROM product"):
        # brand is optional
        attrs = {"type": "Product", "name": prod_name, "label": prod_name}
        if prod_brand:
            attrs["brand"] = prod_brand
        G.add_node(f"Prod{prod_id}", **attrs)

    # 랭킹 노드 및 관계
    # Node ID format: R{id}
    # Ranking nodes represent a specific event/record
    query = """
    SELECT id, product_id, category_id, platform_id, rank, timestamp, price, rating, review_count
    FROM ranking
    ORDER BY timestamp DESC
    LIMIT 1000
    """
    # LIMIT to avoid building massive graph in memory for this demo,
    # but in production, we might want to filter by time window.

    for rid, prod_id, cat_id, platform_id, rank, ts, price, rating, reviews in cur.execute(query):
        rnode = f"R{rid}"
        desc = f"Rank #{rank} on {ts}"
        G.add_node(
            rnode,
            type="Ranking",
            rank=rank,
            timestamp=ts,
            price=price,
            rating=rating,
            reviews=reviews,
            label=desc
        )

        # Relationships
        # Product -> Ranking (rankedAs)
        G.add_edge(f"Prod{prod_id}", rnode, relation="rankedAs")
        # Ranking -> Category (belongsTo)
        G.add_edge(rnode, f"C{cat_id}", relation="belongsTo")
        # Ranking -> Platform (listedOn)
        G.add_edge(rnode, f"P{platform_id}", relation="listedOn")

        # Time relationship (recordedAt) - could link to a Time node,
        # or just keep it as property.
        # Let's keep it simple for now, but we could add:
        # G.add_node(ts, type="Time")
        # G.add_edge(rnode, ts, relation="recordedAt")

    conn.close()
    return G

def get_node_info(G: nx.DiGraph, node_id: str) -> Dict[str, Any]:
    if G.has_node(node_id):
        return G.nodes[node_id]
    return {}
