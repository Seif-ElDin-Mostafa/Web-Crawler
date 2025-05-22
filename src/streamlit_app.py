import streamlit as st
import pandas as pd
from modules.robot_parser import parse_robots_txt, can_crawl
from modules.content_extractor import parse_products_from_page, save_to_json, save_to_csv
from modules.js_api_handler import is_js_heavy_static_check, render_page_with_selenium
import asyncio
from urllib.parse import urljoin
import io
import sys
from pathlib import Path
import os

# --- Setup Output Directory ---
root_dir = Path(__file__).resolve().parent.parent
output_dir = root_dir / 'output'
output_dir.mkdir(exist_ok=True)

# --- UI Sidebar Configuration ---
st.set_page_config(page_title="Web Crawler Dashboard", layout="wide")
stitle = "🕷️ Intelligent Web Crawler Dashboard"
st.header(stitle)

base_url = st.sidebar.text_input("Base URL", "https://www.ebay.com")
category_url = st.sidebar.text_input("Category URL", "https://www.ebay.com/b/Books/bn_1854947")
max_pages = st.sidebar.slider("Max Pages to Crawl", min_value=1, max_value=10, value=3)
run_button = st.sidebar.button("Run Crawler")

if run_button:
    # 1) Crawlability Analysis
    rules = parse_robots_txt(base_url)
    allow = len(rules['allow'])
    disallow = len(rules['disallow'])
    score = int(allow / (allow + disallow) * 100) if (allow + disallow) > 0 else 0

    st.subheader("📄 Crawlability Score")
    st.metric("Score", f"{score}%", delta=f"{allow} Allow, {disallow} Disallow")

    # Recommendation based on robots allow
    if score > 75:
        st.success("High crawlability: HTML scraping should suffice.")
    elif score > 40:
        st.info("Moderate crawlability: consider delaying between requests.")
    else:
        st.warning("Low crawlability: proceed with caution, use APIs if available.")

    # 2) JS Rendering Check
    is_js_heavy, static_html = is_js_heavy_static_check(category_url)
    if is_js_heavy:
        st.subheader("⚠️ JS-heavy Detection")
        st.write("Page appears JS-heavy. Rendering with Selenium...")
        
        # Capture stdout for logging
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        
        try:
            rendered_html = render_page_with_selenium(category_url)
            if rendered_html is None:
                st.error("Failed to render page with Selenium. Falling back to static HTML.")
                html_to_parse = static_html
            else:
                html_to_parse = rendered_html
                st.success("Successfully rendered page via Selenium.")
        except Exception as e:
            st.error(f"Error during page rendering: {str(e)}. Falling back to static HTML.")
            html_to_parse = static_html
        finally:
            # Restore stdout and show logs
            sys.stdout = old_stdout
            logs = new_stdout.getvalue()
            if logs:
                with st.expander("Show Selenium Debug Logs"):
                    st.code(logs)
    else:
        st.subheader("✅ Static HTML Sufficient")
        html_to_parse = static_html

    # 3) Extract Products
    products, _ = parse_products_from_page(html_to_parse, base_url)
    st.subheader("📦 Top Extracted Products")
    df = pd.DataFrame(products)
    st.dataframe(df.head(10))

    # Save data option
    if st.button("Save Current Results"):
        json_path = output_dir / f"crawl_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
        csv_path = output_dir / f"crawl_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        save_to_json(products, str(json_path))
        save_to_csv(products, str(csv_path))
        st.success(f"Results saved to output directory!")

    # 4) Charts
    st.subheader("📊 Product Price Distribution")
    # parse numeric price
    df_clean = df[df['price'].notna()].copy()
    df_clean['price_val'] = df_clean['price'].str.replace(r"[^0-9.]", "", regex=True).astype(float)
    st.bar_chart(df_clean['price_val'])

    st.subheader("📈 Products Per Page Crawl")
    counts = []
    urls = []
    # simulate pagination counts
    page_url = category_url
    for i in range(max_pages):
        _, next_page = parse_products_from_page(html_to_parse, base_url)
        cnt = len(products) if i == 0 else 0  # placeholder
        counts.append(cnt)
        urls.append(f"Page {i+1}")
    st.line_chart(pd.DataFrame({'Page': urls, 'Count': counts}).set_index('Page'))

    # 5) Visual Sitemap
    st.subheader("🗺️ Visual Sitemap")
    sitemap_urls = rules['sitemaps']
    if sitemap_urls:
        dot = "digraph sitemap {\n"
        dot += f"root [label=\"{base_url}\"];\n"
        for i, sm in enumerate(sitemap_urls):
            dot += f"node{i} [label=\"{sm}\"];\n"
            dot += f"root -> node{i};\n"
        dot += "}"
        st.graphviz_chart(dot)
    else:
        st.write("No sitemap URLs in robots.txt.")

    # 6) Crawl Path Flowchart
    st.subheader("🔄 Crawl Path Flowchart")
    flow = "digraph crawl {\nrankdir=LR;"
    prev = 'root'
    flow += "root [label=\"Start: {0}\"];\n".format(category_url)
    page_url = category_url
    for i in range(1, max_pages+1):
        node = f"p{i}"
        flow += f"{node} [label=\"Page {i}\"];\n"
        flow += f"{prev} -> {node};\n"
        prev = node
    flow += "}"
    st.graphviz_chart(flow)

    # 7) API Recommendations
    st.subheader("💡 Recommendation for Crawling Method")
    if is_js_heavy:
        st.write("Use Selenium for JS-rendered pages.")
    else:
        st.write("Plain requests/BeautifulSoup is sufficient.")
    st.write("Alternatively, check for a public API or RSS feed for more robust data access.")

    st.balloons()
