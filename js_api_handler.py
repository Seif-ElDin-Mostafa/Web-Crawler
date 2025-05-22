# js_api_handler.py
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import argparse
import platform

def is_js_heavy_static_check(url, min_product_count=5):
    """
    Checks if static content contains enough eBay product entries.
    Returns (js_heavy: bool, raw_html: str).
    """
    headers = {"User-Agent": "Mozilla/5.0 (compatible; Bot/1.0)"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    items = soup.select('li.s-item')
    print(f"[Static Check] Found {len(items)} product items.")
    return len(items) < min_product_count, resp.text

def render_page_with_selenium(url):
    """
    Renders a page using Selenium and returns the full HTML.
    """
    print(f"Starting Selenium rendering for URL: {url}")
    try:
        print("Setting up Chrome options...")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        print("Installing/Setting up ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        
        print("Creating Chrome browser instance...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            print(f"Navigating to URL: {url}")
            driver.get(url)
            
            print("Waiting for page load...")
            # Wait for 3 seconds after page load
            driver.implicitly_wait(3)
            
            print("Getting page content...")
            content = driver.page_source
            
            if not content:
                print("Warning: Empty content received from page")
                return None
                
            print(f"Successfully retrieved content (length: {len(content)})")
            return content
            
        except Exception as e:
            print(f"Error during page operations: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return None
        finally:
            print("Closing browser...")
            driver.quit()
            
    except Exception as e:
        print(f"Error initializing Selenium: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return None

def extract_product_count_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    return len(soup.select('li.s-item'))

def find_rss_feeds(html):
    """
    Finds any RSS links in the HTML.
    """
    soup = BeautifulSoup(html, 'html.parser')
    return [link['href'] for link in soup.find_all('link', type='application/rss+xml')]

def main(url):
    print(f"\n🔍 Checking JS requirements for: {url}")
    is_js_heavy, static_html = is_js_heavy_static_check(url)

    # Check RSS too (optional)
    feeds = find_rss_feeds(static_html)
    if feeds:
        print("📡 RSS feeds found:")
        for f in feeds:
            print(f" - {f}")
    else:
        print("📡 No RSS feeds detected.")

    if not is_js_heavy:
        print("✅ Static HTML sufficient—no rendering needed.")
    else:
        print("⚠️ JS-heavy content—rendering with Selenium...")
        rendered = render_page_with_selenium(url)
        if rendered:
            count = extract_product_count_from_html(rendered)
            print(f"[Rendered Check] Found {count} product items after rendering.")
        else:
            print("Failed to render page with Selenium.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JS/API handler using Selenium")
    parser.add_argument("url", help="Category page URL")
    args = parser.parse_args()
    main(args.url)
