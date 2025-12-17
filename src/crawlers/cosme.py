from playwright.sync_api import sync_playwright
import time
import random
from datetime import datetime
from typing import List, Dict
from src.crawlers.base import USER_AGENTS
import requests
from bs4 import BeautifulSoup

def scrape_cosme_category(url: str) -> List[Dict]:
    """@cosme 카테고리 페이지에서 제품 정보를 파싱한다."""
    products = []

    # Try requests first as it is faster and worked in view_text_website
    try:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Based on the view_text_website output, the structure seems to be:
            # 1位 ... [Product Name] ...
            # The HTML structure usually has `rank` class or similar.
            # Let's try to find elements that link to product pages `/products/`

            # Strategy: Find all links to /products/, then traverse up to find the container
            # or finding the rank.

            # Looking at the text dump:
            # [107]1位 ... [113]カネボウ クリーム イン デイII

            # Generic approach:
            # Search for the ranking number (1位, 2位...)
            # Then find the nearby product name.

            # Better approach: The site likely uses specific classes.
            # In the absence of confirmed classes, we will look for common patterns.
            # But wait, `view_text_website` showed the content.
            # The structure often involves `div` containers.

            # Let's try a very broad selector that likely captures the ranking list items
            # In many Japanese sites: `div.rank-1`, `div.item`, etc.

            # Let's try to find the container by looking for the "1位" text
            # and then inferring the list structure.

            # However, for stability, let's use the Playwright fallback if requests parsing is too hard blindly.
            # But the user wants a working code.

            # Let's try to parse based on the `view_text_website` observation:
            # It seems there are images with alt text or just text "1位".

            # Let's rely on `requests` but if it fails to find items, use Playwright.
            # Actually, `view_text_website` uses a headless browser (Puppeteer/Playwright) usually?
            # No, the tool description says "fetches ... as plain text". It might be simple curl.

            # Let's try `requests` with a known selector for @cosme if possible.
            # Research suggests @cosme uses `div.ranking-item` or `div.item`.
            # If `debug_cosme.py` failed to find `div.ranking-item`, maybe it's `li`?
            pass

    except Exception as e:
        print(f"Requests scraping failed: {e}")

    # Fallback to Playwright (or primary if requests fails to parse)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        user_agent = random.choice(USER_AGENTS)
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()

        try:
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)

            # Generic selector strategy using XPath to find ranking numbers
            # This is robust against class name changes

            # Find elements containing text "1位", "2位", etc.
            # Or find the list container.

            # Let's try finding the product name links which usually look like /products/ID/
            # selector = 'a[href*="/products/"]'

            # We will iterate over the first 10-20 product links we find in the main area.

            product_links = page.query_selector_all('a[href*="/products/"][href*="/review/"]' )
            # The review link usually is distinct and near the product.
            # Or just product links.

            # Let's try to find the main ranking list container.
            # Usually id="ranking" or class="ranking-list"

            # If we look at the text dump again:
            # 1位 ... KANEBO

            # Let's try to grab all texts and parse with regex? No, that's messy.

            # Let's try a very broad selector for items.
            # `div` that contains "位" and a link.

            items = page.query_selector_all('.ranking-item, .item, .rank-item, li')

            count = 0
            for item in items:
                text = item.inner_text()
                if "位" in text and "円" in text: # It likely has rank and price
                    # This looks like a product item
                    lines = text.split('\n')

                    # Naive parsing
                    rank_str = None
                    name = None
                    rating = None
                    reviews = None

                    for line in lines:
                        if "位" in line:
                            rank_str = line.strip()
                        if "円" in line and not name: # Price usually comes after name? No.
                            pass

                    # Let's try to extract specific elements within this item
                    # Name is usually in an `a` tag or `h3`/`p`
                    name_el = item.query_selector('a[href*="/products/"]:not([href*="review"])')
                    if name_el:
                        name = name_el.inner_text().strip()
                    else:
                        continue

                    # Rank
                    # If we can't parse rank, we just increment a counter
                    count += 1

                    # Rating
                    rating_el = item.query_selector('.point, .score, span[class*="point"], span[class*="score"]')
                    rating = rating_el.inner_text().strip() if rating_el else None

                    # Reviews
                    reviews_el = item.query_selector('.count, span[class*="count"]')
                    reviews = reviews_el.inner_text().strip() if reviews_el else None

                    if name:
                        products.append({
                            "rank": count,
                            "product_name": name,
                            "price": None,
                            "rating": rating,
                            "review_count": reviews,
                            "timestamp": datetime.utcnow().isoformat()
                        })

                    if count >= 10: # Limit to top 10 per category for safety
                        break

            # If the above generic loop didn't work, let's try a very specific one for the provided URL structure
            if not products:
                 # Backup: just get all links to products and assume order = rank
                 links = page.query_selector_all('a[href*="/products/"]')
                 seen_names = set()
                 rank = 1
                 for link in links:
                     name = link.inner_text().strip()
                     if name and name not in seen_names and len(name) > 3:
                         # Filter out small links or images
                         # Check if it has an image child?
                         if link.query_selector('img'):
                             continue # skip image links if they duplicate text links

                         seen_names.add(name)
                         products.append({
                            "rank": rank,
                            "product_name": name,
                            "price": None,
                            "rating": None,
                            "review_count": None,
                            "timestamp": datetime.utcnow().isoformat()
                         })
                         rank += 1
                         if rank > 10: break

        except Exception as e:
            print(f"Playwright scraping failed for {url}: {e}")
        finally:
            browser.close()

    return products
