from __future__ import annotations

import csv
import json
import random
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://quotes.toscrape.com"
START_PATH = "/js/"
REQUEST_TIMEOUT = 15
REQUEST_DELAY_RANGE = (0.5, 1.5)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
]

DATA_RE = re.compile(r"var\s+data\s*=\s*(\[.*?\])\s*;\s*\n\s*for", re.DOTALL)


@dataclass(frozen=True, slots=True)
class Quote:
    text: str
    author: str
    author_goodreads_link: str
    tags: str
    scraped_at: str
    source_page: str


def random_headers() -> dict:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
    }


def fetch_page(session: requests.Session, path: str) -> str:
    url = f"{BASE_URL}{path}"
    resp = session.get(url, headers=random_headers(), timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.text


def extract_quotes_from_html(html: str, source_page: str, scraped_at: str) -> list[Quote]:
    soup = BeautifulSoup(html, "html.parser")

    script_text = None
    for script in soup.find_all("script"):
        if script.string and "var data" in script.string:
            script_text = script.string
            break

    if script_text is None:
        raise ValueError(f"Не найден <script> с 'var data' на странице {source_page}")

    match = DATA_RE.search(script_text)
    if not match:
        raise ValueError(f"Не удалось вырезать JSON-массив на странице {source_page}")

    items = json.loads(match.group(1))

    quotes = []
    for item in items:
        quotes.append(
            Quote(
                text=item["text"],
                author=item["author"]["name"],
                author_goodreads_link=item["author"]["goodreads_link"],
                tags=", ".join(item["tags"]),
                scraped_at=scraped_at,
                source_page=source_page,
            )
        )
    return quotes


def find_next_page(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    next_li = soup.select_one("li.next a")
    if next_li and next_li.get("href"):
        return next_li["href"]
    return None


def scrape_all(max_pages: int | None = None) -> list[Quote]:
    scraped_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    all_quotes: list[Quote] = []
    path = START_PATH
    page_num = 1

    with requests.Session() as session:
        while path is not None:
            html = fetch_page(session, path)
            quotes = extract_quotes_from_html(html, source_page=path, scraped_at=scraped_at)
            all_quotes.extend(quotes)
            print(f"[{page_num}] {path} -> {len(quotes)} цитат", file=sys.stderr)

            if max_pages is not None and page_num >= max_pages:
                break

            path = find_next_page(html)
            page_num += 1

            if path is not None:
                time.sleep(random.uniform(*REQUEST_DELAY_RANGE))

    return all_quotes


def save_csv(quotes: list[Quote], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [f.name for f in Quote.__dataclass_fields__.values()]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for q in quotes:
            writer.writerow(asdict(q))


def main() -> None:
    quotes = scrape_all()
    out_path = Path(__file__).resolve().parent.parent / "data" / "quotes.csv"
    save_csv(quotes, out_path)
    print(f"Сохранено {len(quotes)} цитат в {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
