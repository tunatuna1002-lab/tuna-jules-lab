import requests
from bs4 import BeautifulSoup
import random
import time
from datetime import datetime
from typing import List, Dict
from src.crawlers.base import USER_AGENTS

def get_random_headers() -> Dict[str, str]:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }

def scrape_amazon_category(url: str) -> List[Dict]:
    """Amazon 베스트셀러 카테고리 페이지에서 제품 정보를 파싱한다."""
    headers = get_random_headers()

    # Random delay before request
    time.sleep(random.uniform(2.0, 5.0))

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    products = []

    # Amazon Best Sellers grid selector
    # Depending on the specific page layout, this might vary.
    # Usually `zg-grid-general-faceout` works for the main best sellers grid.
    items = soup.select("div.zg-grid-general-faceout")
    if not items:
        # Fallback or alternative layout check could go here
        pass

    for idx, item in enumerate(items, start=1):
        # Title
        title_el = item.select_one("div.p13n-sc-truncate-desktop-type2") or \
                   item.select_one("div._cDEzb_p13n-sc-css-line-clamp-3_g3dy1") or \
                   item.select_one("span.a-truncate-cut")

        # Price
        price_el = item.select_one("span.p13n-sc-price") or \
                   item.select_one("span._cDEzb_p13n-sc-price_3mJ9Z")

        # Rating
        rating_el = item.select_one("span.a-icon-alt")

        # Reviews
        reviews_el = item.select_one("span.a-size-small") or \
                     item.select_one("div._cDEzb_p13n-sc-css-line-clamp-1_1Fn1y")

        product_name = title_el.get_text(strip=True) if title_el else "Unknown Product"

        products.append({
            "rank": idx,
            "product_name": product_name,
            "price": price_el.get_text(strip=True) if price_el else None,
            "rating": rating_el.get_text(strip=True) if rating_el else None,
            "review_count": reviews_el.get_text(strip=True) if reviews_el else None,
            "timestamp": datetime.utcnow().isoformat()
        })

    return products
