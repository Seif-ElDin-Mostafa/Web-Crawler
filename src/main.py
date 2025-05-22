# main.py
import argparse
import asyncio
import os
from pathlib import Path

from modules.robot_parser import parse_robots_txt, print_summary, can_crawl
from modules.content_extractor import parse_products_from_page, save_to_json, save_to_csv
from modules.js_api_handler import is_js_heavy_static_check, render_page_with_selenium

def get_default_output_path(filename):
    """Get the default path in the output directory for a given filename"""
    root_dir = Path(__file__).resolve().parent
    output_dir = root_dir / 'output'
    output_dir.mkdir(exist_ok=True)
    return str(output_dir / filename)

def main():
    parser = argparse.ArgumentParser(description='Web Crawler Main Script')
    parser.add_argument('base_url', help='Base URL of the website (e.g., https://www.ebay.com)')
    parser.add_argument('category_url', help='URL of the category to extract')
    parser.add_argument('--max-pages', type=int, default=3, help='Maximum number of pages to crawl (default: 3)')
    parser.add_argument('--output-json', default=get_default_output_path('data.json'), help='Path to save JSON output (default: output/data.json)')
    parser.add_argument('--output-csv', default=get_default_output_path('data.csv'), help='Path to save CSV output (default: output/data.csv)')
    parser.add_argument('--user-agent', default='*', help='User-Agent for the robots check')
    args = parser.parse_args()

    # Create output directory if it doesn't exist
    for output_path in [args.output_json, args.output_csv]:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 1) Robots.txt
    rules = parse_robots_txt(args.base_url)
    print_summary(rules)
    if not can_crawl(args.base_url, args.category_url, args.user_agent):
        print(f"Crawling not allowed for: {args.category_url}")
        return
    print(f"Crawling is allowed for: {args.category_url}\n")

    # 2) Static check & optional render
    is_js_heavy, static_html = is_js_heavy_static_check(args.category_url)
    html_to_parse = static_html
    if is_js_heavy:
        print("⚠️ JS-heavy content detected. Rendering with Selenium...")
        html_to_parse = render_page_with_selenium(args.category_url)

    # 3) Extract products from whichever HTML we have
    products, next_page = parse_products_from_page(html_to_parse, args.base_url)

    # (Optional) follow pagination for up to max-pages
    page_count = 1
    while next_page and page_count < args.max_pages:
        page_count += 1
        print(f"\n--- Fetching page {page_count}: {next_page}")
        if is_js_heavy:
            raw = render_page_with_selenium(next_page)
        else:
            from modules.content_extractor import fetch_with_retry
            raw = fetch_with_retry(next_page)
        new_products, next_page = parse_products_from_page(raw, args.base_url)
        products.extend(new_products)

    print(f"\nTotal products extracted: {len(products)}\n")

    # 4) Save outputs
    if args.output_json:
        save_to_json(products, args.output_json)
    if args.output_csv:
        save_to_csv(products, args.output_csv)

if __name__ == '__main__':
    main()
