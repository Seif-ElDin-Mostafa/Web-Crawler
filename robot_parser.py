# robot_parser.py
import requests
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

def parse_robots_txt(base_url):
    """
    Download and parse robots.txt manually to extract rules and sitemap links.
    Returns a dict with 'allow', 'disallow', 'crawl_delay', and 'sitemaps'.
    """
    parsed_url = urlparse(base_url)
    if not parsed_url.scheme:
        base_url = 'https://' + base_url

    robots_url = urljoin(base_url, '/robots.txt')
    response = requests.get(robots_url)
    response.raise_for_status()
    lines = response.text.splitlines()

    rules = {
        'allow': [],
        'disallow': [],
        'crawl_delay': None,
        'sitemaps': []
    }

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = [p.strip() for p in line.split(':', 1)]
        if len(parts) != 2:
            continue
        key, value = parts
        key_lower = key.lower()
        if key_lower == 'allow':
            rules['allow'].append(value)
        elif key_lower == 'disallow':
            rules['disallow'].append(value)
        elif key_lower == 'crawl-delay':
            try:
                rules['crawl_delay'] = float(value)
            except ValueError:
                rules['crawl_delay'] = value
        elif key_lower == 'sitemap':
            rules['sitemaps'].append(value)

    return rules

def print_summary(rules):
    """
    Print a human-friendly summary of crawlability rules.
    """
    allow_count = len(rules['allow'])
    disallow_count = len(rules['disallow'])
    crawl_delay = rules['crawl_delay']
    sitemaps = rules['sitemaps']

    print("\n=== Crawlability Summary ===")
    print(f"Total 'Allow' rules:    {allow_count}")
    print(f"Total 'Disallow' rules: {disallow_count}")
    print(f"Crawl-delay:            {crawl_delay or 'None specified'}")
    if sitemaps:
        print("Sitemap URLs:")
        for sm in sitemaps:
            print(f"  - {sm}")
    else:
        print("No sitemap URLs found.")
    print("=== End of Summary ===\n")

def can_crawl(base_url, target_url, user_agent='*'):
    """
    Use urllib.robotparser to check if crawling target_url is permitted by robots.txt.
    """
    parsed_url = urlparse(base_url)
    if not parsed_url.scheme:
        base_url = 'https://' + base_url

    robots_url = urljoin(base_url, '/robots.txt')
    parser = RobotFileParser()
    parser.set_url(robots_url)
    parser.read()
    return parser.can_fetch(user_agent, target_url)
