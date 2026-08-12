# Quotes Tracker

[![Daily quotes scrape](https://github.com/MickyLangello/Quotes-Parser/actions/workflows/scrape.yml/badge.svg)](https://github.com/MickyLangello/Quotes-Parser/actions/workflows/scrape.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![uv](https://img.shields.io/badge/managed%20with-uv-de5fe9)
![License](https://img.shields.io/badge/license-MIT-green)

Автоматизированный сбор данных с [quotes.toscrape.com/js/](http://quotes.toscrape.com/js/)
по расписанию с публикацией актуального результата на GitHub Pages.

## Возможности

- Сбор данных со всех страниц пагинации источника
- Ротация User-Agent между запросами
- Хранение результата в CSV (`data/quotes.csv`)
- Автоматическая генерация HTML-страницы (`docs/index.html`) для GitHub Pages
- Запуск по расписанию через GitHub Actions (cron), а также вручную
- Покрытие тестами (pytest) на фиксированной HTML-фикстуре

## Структура проекта

```
src/scraper.py      — сбор данных, запись в data/quotes.csv
src/build_page.py   — генерация docs/index.html из CSV
data/quotes.csv      — текущий снэпшот данных
docs/index.html      — статическая страница для GitHub Pages
tests/                — тесты парсера
.github/workflows/    — конфигурация запуска по расписанию
```

## Установка и запуск

```bash
uv sync
uv run python src/scraper.py
uv run python src/build_page.py
uv run pytest -q
```

## Данные

Файл `data/quotes.csv` перезаписывается при каждом запуске и содержит
снэпшот последнего сбора без хранения истории.

## Лицензия

MIT
