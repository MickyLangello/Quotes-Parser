from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scraper import extract_quotes_from_html, find_next_page  # noqa: E402

FIXTURE = Path(__file__).parent / "fixture_js_page1.html"


def test_extract_quotes_from_real_fixture():
    html = FIXTURE.read_text(encoding="utf-8")
    quotes = extract_quotes_from_html(html, source_page="/js/", scraped_at="2026-08-11T00:00:00+00:00")

    assert len(quotes) == 10
    first = quotes[0]
    assert first.author == "Albert Einstein"
    assert "change" in first.tags
    assert first.text.startswith("\u201cThe world as we have created it")


def test_find_next_page():
    html = FIXTURE.read_text(encoding="utf-8")
    assert find_next_page(html) == "/js/page/2/"


def test_no_next_page_on_last_page():
    html = FIXTURE.read_text(encoding="utf-8").replace(
        '<li class="next">\n            <a href="/js/page/2/">Next <span aria-hidden="true">&rarr;</span></a>\n        </li>',
        "",
    )
    assert find_next_page(html) is None
