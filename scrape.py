# scraper.py
import os
import requests
from bs4 import BeautifulSoup
import trafilatura
from pathlib import Path

DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def fetch_html(url, timeout=12):
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    return resp.text

def extract_with_bs(html):
    soup = BeautifulSoup(html, "html.parser")
    # remove noise
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()
    main = soup.find("main") or soup.find("article")
    if main:
        text = main.get_text(separator="\n", strip=True)
    else:
        text = soup.get_text(separator="\n", strip=True)
    return text

def extract_text(url):
    html = fetch_html(url)
    try:
        content = trafilatura.extract(html, include_comments=False, favor_recall=True)
        if content and len(content) > 200:  # heuristic to check quality
            return content
    except Exception:
        pass
    return extract_with_bs(html)

def save_text(url, filename=None):
    """Scrape text from URL and save into data/raw/"""
    text = extract_text(url)
    if not text:
        print(f"[WARN] Could not extract content from {url}")
        return None

    # generate filename from URL if not given
    if filename is None:
        safe_name = url.replace("https://", "").replace("http://", "").replace("/", "_")
        filename = safe_name[:80] + ".txt"  # truncate if too long

    file_path = DATA_DIR / filename
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[INFO] Saved content to {file_path}")
    return file_path

# Example usage
if __name__ == "__main__":
    url = "https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/"
    save_text(url, "dsa_page.txt")
