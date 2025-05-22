# content_extractor.py
import json
import csv
import time
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

# --- Configuration ---
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds between retries

def fetch_with_retry(url):
    """
    Fetch a URL with retry logic. Returns response text or raises.
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"[{attempt}/{MAX_RETRIES}] Error fetching {url}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                raise

def parse_products_from_page(html, base_url):
    """
    Given HTML of an eBay category page, extract product data.
    Returns a list of dicts and the URL of the next page (or None).
    """
    soup = BeautifulSoup(html, 'html.parser')
    products = []

    for li in soup.select('li.s-item'):
        title_tag = li.select_one('h3.s-item__title')
        price_tag = li.select_one('span.s-item__price')
        link_tag = li.select_one('a.s-item__link')
        desc_tag = li.select_one('div.s-item__subtitle')

        product = {
            'title':       title_tag.get_text(strip=True) if title_tag else None,
            'price':       price_tag.get_text(strip=True) if price_tag else None,
            'url':         urljoin(base_url, link_tag['href']) if link_tag and link_tag.get('href') else None,
            'description': desc_tag.get_text(strip=True) if desc_tag else None
        }
        products.append(product)

    # Pagination: look for "Next" button link
    next_page = None
    next_btn = soup.select_one('a.pagination__next')
    if next_btn and next_btn.get('href'):
        next_page = urljoin(base_url, next_btn['href'])

    return products, next_page

def save_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Data saved to JSON: {output_file}")

def save_to_csv(data, output_file):
    if not data:
        print("No data to save")
        return
    keys = data[0].keys()
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Data saved to CSV: {output_file}")
