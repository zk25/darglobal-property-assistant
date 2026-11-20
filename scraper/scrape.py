"""Polite crawler for the public DarGlobal and Wasalt websites.

It respects robots.txt, waits between requests, stays on each site's own
domain, keeps English pages only, and writes one Markdown file per page in the
same front-matter format the chatbot loads (data/scraped/<site>/<page>.md).

Usage:
    python scraper/scrape.py                     # crawl both sites (default 40 pages each)
    python scraper/scrape.py --max-pages 80 --delay 2
    python scraper/scrape.py --seeds-only        # fetch only the seed pages

Some project pages render their content with JavaScript; those come back with
very little text and are skipped (listed in manifest.json). The hand-checked
files in data/darglobal and data/wasalt cover those pages.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from urllib import robotparser
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = "PropertyAssistantBot/1.0 (technical assignment; polite crawler)"
MIN_TEXT_CHARS = 300
SKIP_EXT = re.compile(r"\.(pdf|jpe?g|png|gif|webp|svg|mp4|webm|zip|docx?|xlsx?|css|js|ico|woff2?)$", re.I)
NON_ENGLISH = re.compile(r"^/(ar|ru|zh|fr|de|es|it|tr|fa|ur|hi)(/|$)", re.I)

SITES = {
    "darglobal": {
        "name": "DarGlobal",
        "hosts": {"darglobal.co.uk", "www.darglobal.co.uk"},
        "seeds": [
            "https://darglobal.co.uk/",
            "https://darglobal.co.uk/about",
            "https://darglobal.co.uk/projects",
            "https://darglobal.co.uk/investor",
            "https://darglobal.co.uk/why-invest",
            "https://darglobal.co.uk/hospitality",
            "https://darglobal.co.uk/luxury-golf-communities",
            "https://darglobal.co.uk/exclusive-membership",
            "https://darglobal.co.uk/tokenization",
            "https://darglobal.co.uk/press",
        ],
        "allow_path": lambda path: not NON_ENGLISH.match(path),
    },
    "wasalt": {
        "name": "Wasalt",
        "hosts": {"wasalt.sa", "www.wasalt.sa", "wasalt.com", "www.wasalt.com"},
        "seeds": [
            "https://wasalt.sa/en",
            "https://wasalt.sa/en/corporate",
            "https://wasalt.com/en/about",
        ],
        "allow_path": lambda path: path.startswith("/en"),
    },
}


def slugify(url: str) -> str:
    parsed = urlparse(url)
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", f"{parsed.netloc}{parsed.path}").strip("-").lower()
    return slug[:120] or "index"


def extract(html: str, url: str) -> tuple[str, str, list[str]]:
    """Return (title, markdown_text, links) for a page."""
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.title.get_text(strip=True) if soup.title else "") or url
    links = [a.get("href") for a in soup.find_all("a", href=True)]

    for tag in soup(["script", "style", "noscript", "svg", "iframe", "form", "header", "footer", "nav"]):
        tag.decompose()

    lines: list[str] = []
    seen: set[str] = set()
    for el in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "td", "th"]):
        text = re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip()
        if len(text) < 3 or text in seen:
            continue
        seen.add(text)
        if el.name in ("h1", "h2"):
            lines.append(f"\n## {text}")
        elif el.name in ("h3", "h4"):
            lines.append(f"\n### {text}")
        elif el.name == "li":
            lines.append(f"- {text}")
        else:
            lines.append(text)
    return title, "\n".join(lines).strip(), links


def crawl(key: str, cfg: dict, out_dir: Path, max_pages: int, delay: float, seeds_only: bool) -> dict:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    robots: dict[str, robotparser.RobotFileParser] = {}

    def allowed(url: str) -> bool:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base not in robots:
            rp = robotparser.RobotFileParser()
            try:
                resp = session.get(f"{base}/robots.txt", timeout=15)
                rp.parse(resp.text.splitlines() if resp.ok else [])
            except requests.RequestException:
                rp.parse([])
            robots[base] = rp
        return robots[base].can_fetch(USER_AGENT, url)

    site_dir = out_dir / key
    site_dir.mkdir(parents=True, exist_ok=True)
    queue = deque(cfg["seeds"])
    visited: set[str] = set()
    saved, skipped = [], []

    while queue and len(visited) < max_pages:
        url = urldefrag(queue.popleft())[0].rstrip("/")
        if url in visited:
            continue
        visited.add(url)
        if not allowed(url):
            skipped.append({"url": url, "reason": "robots.txt"})
            continue
        try:
            resp = session.get(url, timeout=25)
        except requests.RequestException as exc:
            skipped.append({"url": url, "reason": type(exc).__name__})
            continue
        finally:
            time.sleep(delay)
        if resp.status_code != 200 or "text/html" not in resp.headers.get("content-type", ""):
            skipped.append({"url": url, "reason": f"HTTP {resp.status_code}"})
            continue

        title, text, links = extract(resp.text, url)
        if len(text) < MIN_TEXT_CHARS:
            skipped.append({"url": url, "reason": "little text (likely rendered by JavaScript)"})
        else:
            stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            doc = f"---\ntitle: {title}\nsource: {url}\nsite: {cfg['name']}\nscraped_at: {stamp}\n---\n\n# {title}\n\n{text}\n"
            (site_dir / f"{slugify(url)}.md").write_text(doc, encoding="utf-8")
            saved.append(url)
            print(f"[{cfg['name']}] saved {url} ({len(text)} chars)")

        if seeds_only:
            continue
        for href in links:
            nxt = urldefrag(urljoin(url, href))[0]
            parsed = urlparse(nxt)
            if (
                parsed.scheme in ("http", "https")
                and parsed.netloc in cfg["hosts"]
                and cfg["allow_path"](parsed.path or "/")
                and not SKIP_EXT.search(parsed.path)
                and nxt.rstrip("/") not in visited
            ):
                queue.append(nxt)

    return {"site": cfg["name"], "saved": saved, "skipped": skipped}


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl public DarGlobal and Wasalt pages into Markdown.")
    parser.add_argument("--out", default=str(Path(__file__).resolve().parent.parent / "data" / "scraped"))
    parser.add_argument("--max-pages", type=int, default=40, help="maximum pages per site")
    parser.add_argument("--delay", type=float, default=1.5, help="seconds to wait between requests")
    parser.add_argument("--sites", nargs="+", default=list(SITES), choices=list(SITES))
    parser.add_argument("--seeds-only", action="store_true", help="fetch only the seed URLs")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = [crawl(k, SITES[k], out_dir, args.max_pages, args.delay, args.seeds_only) for k in args.sites]
    (out_dir / "manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    for r in report:
        print(f"{r['site']}: {len(r['saved'])} pages saved, {len(r['skipped'])} skipped")
    if not any(r["saved"] for r in report):
        raise SystemExit("No pages were saved. Check your internet connection; skipped pages are listed in manifest.json.")


if __name__ == "__main__":
    main()
