# Pazar Scraper - Turkish E-commerce Product Scraper

A Python web scraper for extracting structured product data from Turkish e-commerce platforms currently **Trendyol** and **Hepsiburada**.

## Overview

Given a product URL from sites, the tool fetches the HTML page, parses embedded structured data (JSON-LD, Redux store state, shared props), and produces normalized JSON output containing product information: name, brand, price, currency, SKU, image, description, availability, reviews, merchant listings, and category paths.

Also includes **API integrations** to fetch richer product information via each platform's internal storefront APIs (Trendyol and Hepsiburada).

## Features

- **Trendyol** (`utils/trendyol.py`): extracts product data from JSON-LD, `__envoy__SHARED_PROPS`, and API
- **Hepsiburada** (`utils/hepsiburada.py`): extracts from JSON-LD, Redux store (`reduxStore`), DOM and API
- **Unified CLI**: `scrape <product-url>` - auto-detects platform and dispatches to correct scraper
- **Structured output**: `ProductDataset` dataclass with 12 fields, JSON serialization
- **Description building**: fallback (API > cleaned JSON-LD > attribute synthesis)
- **Turkish boilerplate filtering**: 35 common phrases filtered from descriptions (will changed)

## Quick Start

```bash
# Install dependencies
uv sync

# Scrape a Trendyol product
uv run scrape "https://www.trendyol.com/brand/product-p-id"

# Scrape a Hepsiburada product
uv run scrape "https://www.hepsiburada.com/product-p-id"

# Print operation steps to stderr
uv run scrape --debug "https://www.trendyol.com/brand/product-p-id"

# Hide the final JSON, show only debug lines
uv run scrape --debug --no-output "https://www.trendyol.com/brand/product-p-id"

# Write the final JSON to both a file and the terminal
uv run scrape --out product.json "https://www.trendyol.com/brand/product-p-id"

# Write everything shown on the terminal (including debug) to a log file too
uv run scrape --debug --out-std scrape.log "https://www.trendyol.com/brand/product-p-id"
```

`--debug` writes network requests, HTTP statuses, HTML/JSON-LD parsing, dataset building, and Trendyol API enrichments to stderr. The normal JSON result stays on stdout, so it remains compatible with output redirection. `--no-output` hides only the final JSON result.

`--out FILE` writes the final dataset JSON to both a file and stdout. `--out-std FILE` additionally writes everything that reaches the terminal (stdout, debug, and HTTP body) to a log file. `--no-output` hides the final JSON from stdout; if `--out` is given the JSON is still written to the file. If no output option is given, the result is written to stdout, consistent with prior behavior.

## See `docs/trendyol/example.json` and `docs/hepsiburada/example.json` for example output. 

## Project Structure

```
src/scrape/
├── __init__.py          # CLI entry point (scrape command)
├── main.py              # URL detection, argparse CLI, dispatch logic
├── dataset.py           # ProductDataset dataclass
├── debug.py             # Leveled, colorized debug logging
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
├── trendyol/
│   ├── README.md                    # API documentation index
│   ├── component_data.md            # Component-read endpoint
│   ├── kredi_teklifleri.md          # Credit/installment endpoint (external)
│   ├── review_read.md               # Reviews + AI summary
│   ├── delivery_date.md             # Delivery dates
│   ├── installment.md               # Bank installment options
│   ├── merchant_questions.md        # Q&A
│   ├── seller_acceptance.md         # Seller question acceptance
│   ├── slicing_attributes.md        # Variants/colors
│   ├── seller_store.md              # Seller store info
│   ├── sellerstore_follow.md        # Follower count
│   ├── social_proof.md              # Favorites
│   ├── video_content.md             # Product videos
│   ├── stamps.md                    # Badges/stamps
│   ├── stickers.md                  # Stickers
│   ├── currencies.md                # Exchange rates
│   ├── product_eligibility.md       # Eligibility
│   └── vas.md                       # Value-added services
└── hepsiburada/
    ├── README.md                    # API documentation index
    ├── product_listings.md          # Seller listings
    ├── without_affordability.md     # Discounted price + campaign
    ├── installment.md               # Installment / credit options
    ├── other_merchants.md           # Other sellers
    ├── payment_options.md           # Payment options
    ├── shipping_due_date.md         # Shipping delivery date
    ├── ask_to_seller.md             # Seller question status
    ├── vas.md                       # Value-added services
    └── jsonld.md                    # HTML-embedded structured data
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

## Discovered Storefront APIs

`docs/trendyol/` contains documentation for 18 internal Trendyol endpoints discovered via browser network inspection:

- review-read, component-read, delivery-date, installment, merchant-questions, seller-acceptance, currencies, stickers, video-content, complete-the-look
- slicing-attributes, social-proof, seller-store, sellerstore-follow, stamps, product-eligibility, coc-webview credit endpoint

See `docs/trendyol/README.md` for full endpoint list, headers, and accessibility matrix.

`docs/hepsiburada/` contains documentation for the Hepsiburada PDP storefront APIs and JSON-LD structured data:

- product listings, withoutAffordability (discounted price + campaign), installment, other merchants, payment options, shipping due date, ask-to-seller, VAS

For Hepsiburada, Akamai `_abck` protection may require browser-session cookies; see `docs/hepsiburada/README.md` for the accessibility details.
