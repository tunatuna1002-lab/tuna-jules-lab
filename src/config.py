import os

# Database Settings
DB_PATH = "ranking_history.db"
CHROMA_PATH = "./chroma_db"

# Embedding Model
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

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

# User Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"
]
