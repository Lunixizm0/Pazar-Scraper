# Pazar Scraper - Turkish E-commerce Product Scraper

A Python web scraper for extracting structured product data from Turkish e-commerce platforms currently **Trendyol** and **Hepsiburada**.

## Overview

Given a product URL from sites, the tool fetches the HTML page, parses embedded structured data (JSON-LD, Redux store state, shared props), and produces normalized JSON output containing product information: name, brand, price, currency, SKU, image, description, availability, reviews, merchant listings, and category paths.

Also includes a **Trendyol API integration** to fetch richer product information via Trendyol's internal API.

## Features

- **Trendyol** (`utils/trendyol.py`): extracts product data from JSON-LD, `__envoy__SHARED_PROPS`, and API
- **Hepsiburada** (`utils/hepsiburada.py`): extracts from JSON-LD, Redux store (`reduxStore`), and DOM
- **Unified CLI**: `scrape <product-url>` - auto-detects platform and dispatches to correct scraper
- **Structured output**: `ProductDataset` dataclass with 12 fields, JSON serialization
- **Description building**: Multi-strategy fallback (API > cleaned JSON-LD > attribute synthesis)
- **Turkish boilerplate filtering**: 35 common phrases filtered from descriptions

## Quick Start

```bash
# Install dependencies
uv sync

# Scrape a Trendyol product
uv run scrape "https://www.trendyol.com/brand/product-p-id"

# Scrape a Hepsiburada product
uv run scrape "https://www.hepsiburada.com/product-p-id"

# İşlem adımlarını stderre yazdır
uv run scrape --debug "https://www.trendyol.com/brand/product-p-id"

# Son JSONu gizle yalnızca debug satırlarını göster
uv run scrape --debug --no-output "https://www.trendyol.com/brand/product-p-id"

# Son JSONu hem dosyaya hem terminale yaz
uv run scrape --out product.json "https://www.trendyol.com/brand/product-p-id"

# Terminalde görünen her şeyi (debug dahil) günlük dosyasına da yaz
uv run scrape --debug --out-std scrape.log "https://www.trendyol.com/brand/product-p-id"
```

`--debug` ağ isteklerini, HTTP durumlarını, HTML/JSON-LD ayrıştırmasını, veri seti oluşturmayı ve Trendyol API zenginleştirmelerini stderr'e yazar. Normal JSON sonuç stdout'ta kalır; bu nedenle çıktı yönlendirmesiyle de uyumludur. `--no-output`, yalnızca nihai JSON sonucunu gizler.

`--out DOSYA` final dataset JSON'unu hem dosyaya hem stdout'a yazar. `--out-std DOSYA`, terminale gelen her şeyi (stdout, debug ve HTTP body dahil) ek olarak günlük dosyasına da yazar. `--no-output`, final JSON'u stdout'tan gizler; `--out` verilmişse JSON yine dosyaya yazılır. Hiçbir çıktı seçeneği verilmezse sonuç, önceki davranışla uyumlu olarak stdout'a yazılır.

## See `docs/trendyol/example.json` and `docs/hepsiburada/example.json` for example output. 

## Project Structure

```
src/scrape/
├── __init__.py          # CLI entry point (scrape command)
├── main.py              # URL detection, argparse CLI, dispatch logic
├── dataset.py           # ProductDataset dataclass
└── utils/
    ├── trendyol.py      # Trendyol scraper
    └── hepsiburada.py   # Hepsiburada scraper
tests/
├── trendyol/
│   ├── test_trendyol.py             # Live integration tests
│   └── get_products.py              # Fetches URLs from Trendyol best-sellers API
└── hepsiburada/
    ├── test_hepsiburada.py          # Live integration tests
    └── get_hepsiburada_products.py  # Fetches URLs from Hepsiburada homepage
docs/
└── trendyol/
    ├── README.md                    # API documentation index (this dir)
    ├── component_data.md            # Component-read endpoint
    ├── kredi_teklifleri.md          # Credit/installment endpoint (external)
    ├── review_read.md               # Reviews + AI summary
    ├── delivery_date.md             # Delivery dates
    ├── installment.md               # Bank installment options
    ├── merchant_questions.md        # Q&A
    ├── seller_acceptance.md         # Seller question acceptance
    ├── slicing_attributes.md        # Variants/colors
    ├── seller_store.md              # Seller store info
    ├── sellerstore_follow.md        # Follower count
    ├── social_proof.md              # Favorites
    ├── video_content.md             # Product videos
    ├── stamps.md                    # Badges/stamps
    ├── stickers.md                  # Stickers
    ├── currencies.md                # Exchange rates
    ├── product_eligibility.md       # Eligibility
    └── vas.md                       # Value-added services
```

## Requirements

- Python 3.14
- uv (package manager)
- Dependencies: `requests`, `beautifulsoup4`, `lxml`
- Dev: `pytest`, `ruff`, `urllib3`

## Testing

Tests are live integration tests that hit real product pages (require internet):

```bash
uv run pytest                    # All tests
uv run pytest tests/trendyol/    # Trendyol only
uv run pytest tests/hepsiburada/ # Hepsiburada only
```

## Linting

```bash
uv run ruff check src/ tests/
```

## Discovered Trendyol APIs

The `docs/trendyol/` directory contains documentation for 18 internal Trendyol endpoints discovered via browser network inspection:

- review-read, component-read, delivery-date, installment, merchant-questions, seller-acceptance, currencies, stickers, video-content, complete-the-look
- slicing-attributes, social-proof, seller-store, sellerstore-follow, stamps, product-eligibility, coc-webview credit endpoint
  
See `docs/trendyol/README.md` for full endpoint list, headers, and accessibility matrix.
