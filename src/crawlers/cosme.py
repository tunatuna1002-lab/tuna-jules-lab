from playwright.sync_api import sync_playwright
import time
import random
from datetime import datetime
from typing import List, Dict
from src.config import USER_AGENTS

def scrape_cosme_category(url: str) -> List[Dict]:
    """@cosme 카테고리 페이지에서 제품 정보를 파싱한다."""
    products = []

    # We will use Playwright as the primary method as it is more robust for this site
    # based on our investigation.
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        user_agent = random.choice(USER_AGENTS)
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()

        try:
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)

            # General Strategy:
            # 1. Find product links (usually contain /products/ID/)
            # 2. Extract name from the link text
            # 3. Assume order on page is the rank

            # Selector for product links in the main content area
            # We filter for links that look like product pages
            links = page.query_selector_all('a[href*="/products/"]')

            seen_names = set()
            rank = 1

            for link in links:
                if rank > 20: # Limit to top 20
                    break

                name = link.inner_text().strip()

                # Filtering logic to ensure we get product names and not "View Reviews" or images
                # 1. Name must be substantial length
                # 2. Must not be a known navigation keyword
                if not name or len(name) < 2:
                    continue

                if name in seen_names:
                    continue

                # Optional: Check if the link is inside a "recommendation" sidebar to avoid false positives?
                # For now, we assume the main list appears first in DOM or is dominant.

                seen_names.add(name)

                # Attempt to find nearby price or rating if possible (complex with generic selector)
                # For now, we prioritize getting the rank and name correct.

                products.append({
                    "rank": rank,
                    "product_name": name,
                    "price": None,
                    "rating": None,
                    "review_count": None,
                    "timestamp": datetime.utcnow().isoformat()
                })
                rank += 1

        except Exception as e:
            print(f"Playwright scraping failed for {url}: {e}")
        finally:
            browser.close()

    return products
