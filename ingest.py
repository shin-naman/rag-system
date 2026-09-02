"""Ingest stage: turn URLs into markdown files on disk plus a manifest.

Pure fetch/write/record — no chunking or embedding logic lives here.
"""
import re
import ssl
import urllib.request
import urllib.error
import json
from pathlib import Path
import sys

import certifi

# Trust store: python.org builds ship no system CA bundle, so point at certifi's.
_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def fetch(url):
    """Fetch a URL as text. Returns the body, or None on any HTTP/URL failure."""
    req = urllib.request.Request(url, headers={"User-Agent": "myrag/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=30, context=_SSL_CONTEXT) as r:
            return r.read().decode("utf-8", errors="replace")
    except (urllib.error.HTTPError, urllib.error.URLError):
        return None

def _looks_like_index(text: str) -> bool:
    lines = [l for l in text.splitlines() if l.strip()]
    links = sum(l.lstrip().startswith(("- [", "* [", "[")) for l in lines)
    return links / max(len(lines), 1) > 0.5

def discover(base_url: str) -> tuple[str, str] | None:
    base = base_url.rstrip("/")
    # 1. prefer the full concatenated content
    full = fetch(base + "/llms-full.txt")
    if full:
        return full, "llms-full"
    # 2. fall back to llms.txt, but warn if it's just links
    idx = fetch(base + "/llms.txt")
    if idx:
        if _looks_like_index(idx):
            print("WARNING: llms.txt looks like a link index, not content. "
                  "Indexing it gives titles, not answers. (Link-following is v2.)")
        return idx, "llms"
    return None

def title_of(md: str, fallback: str) -> str:
    m = re.search(r"^#\s+(.*)", md, flags=re.MULTILINE)
    return m.group(1).strip() if m else fallback

def save(content: str, base_url: str, docs_dir="docs"):
    Path(docs_dir).mkdir(parents=True, exist_ok=True)
    path = f"{docs_dir}/content.md"          # v1: one file
    Path(path).write_text(content, encoding="utf-8")
    manifest = [{
        "path":  path,
        "url":   base_url,                   # coarse for v1; per-page in v2
        "title": title_of(content, base_url),
    }]
    Path(f"{docs_dir}/manifest.json").write_text(json.dumps(manifest, indent=2))

def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else "https://docs.rome.builders"
    result = discover(base_url)
    if not result:
        sys.exit("No llms-full.txt or llms.txt found. (sitemap/crawl is v2.)")
    content, strategy = result
    save(content, base_url)
    print(f"Ingested via '{strategy}'. Next: python build_index.py")

if __name__ == "__main__":
    main()