from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, BaseLoader

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "quotes.csv"
OUT_PATH = ROOT / "docs" / "index.html"

TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Quotes Tracker — последний сбор</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root { color-scheme: light dark; }
  body { font-family: -apple-system, Segoe UI, Roboto, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; }
  h1 { font-size: 1.4rem; }
  .meta { color: #666; font-size: 0.9rem; margin-bottom: 1.5rem; }
  table { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
  th, td { text-align: left; padding: 0.5rem 0.6rem; border-bottom: 1px solid #ddd; vertical-align: top; }
  th { border-bottom: 2px solid #999; }
  tr:hover { background: rgba(127,127,127,0.08); }
  .tags { color: #666; font-size: 0.82rem; }
</style>
</head>
<body>
<h1>Страница генерируется автоматически ежедневно</h1>
<p class="meta">
  Источник: quotes.toscrape.com/js/ &middot;
  Собрано записей: {{ count }} &middot;
  Последнее обновление: {{ scraped_at }} UTC
</p>
<table>
  <thead>
    <tr><th>Цитата</th><th>Автор</th><th>Теги</th></tr>
  </thead>
  <tbody>
    {% for q in quotes %}
    <tr>
      <td>{{ q.text }}</td>
      <td><a href="https://www.goodreads.com{{ q.author_goodreads_link }}" target="_blank" rel="noopener">{{ q.author }}</a></td>
      <td class="tags">{{ q.tags }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>
</body>
</html>
"""


def load_quotes() -> list[dict]:
    if not CSV_PATH.exists():
        return []
    with CSV_PATH.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build() -> None:
    quotes = load_quotes()
    scraped_at = quotes[0]["scraped_at"] if quotes else datetime.now(timezone.utc).isoformat(timespec="seconds")

    env = Environment(loader=BaseLoader(), autoescape=True)
    html = env.from_string(TEMPLATE).render(quotes=quotes, count=len(quotes), scraped_at=scraped_at)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"Сгенерирована страница {OUT_PATH} ({len(quotes)} цитат)")


if __name__ == "__main__":
    build()
