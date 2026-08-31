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
# Install dependencies (uses uv)
uv sync

# Scrape a Trendyol product
uv run scrape "https://www.trendyol.com/brand/product-p-id"

# Scrape a Hepsiburada product
uv run scrape "https://www.hepsiburada.com/product-p-id"
```

## Output Example

```json
{
  "source": "trendyol",
  "category": "Kulak İçi Bluetooth Kulaklık",
  "name": "Xiaomi Redmi Buds 8 Pro Siyah Bluetooth Kulakiçi Kulaklık TWS - ANC BT 5.4 (Xiaomi TR Garantili)",
  "brand": "Xiaomi",
  "price": "4199.00 TL",
  "currency": "TRY",
  "url": "https://www.trendyol.com/xiaomi/redmi-buds-8-pro-siyah-bluetooth-kulakici-kulaklik-tws-anc-bt-5-4-xiaomi-tr-garantili-p-1081766367",
  "sku": "1081766367",
  "image": "https://cdn.dsmcdn.com/ty1000319/product/media/images/prod/PIM/20260227/12/a9dc7313-301e-4256-babd-8e0d08ee7623/1_org_zoom.jpg",
  "description": "long ahh description",
  "availability": "https://schema.org/InStock",
  "item_condition": "https://schema.org/NewCondition",
  "custom_data": {
    "pattern": "Kulak İçi Bluetooth Kulaklık",
    "attributes": {
      "Aktif Gürültü Önleme (ANC)": "Var",
      "Dokunmatik Kontrol": "Var",
      "Garanti Tipi": "Resmi Distribütör Garantili",
      "Suya/Tere Dayanıklılık": "Var",
      "Mikrofon": "Var",
      "Bluetooth Versiyon": "5.4",
      "Garanti Süresi": "2 Yıl",
      "Çift Telefon Desteği": "Var",
      "Menşei": "CN",
      "Tamir Edilebilirlik": "Yetkili Servis ile Tamiri Gerekir."
    },
    "reviews": {
      "score": 4.333333333333333,
      "count": 54
    },
    "listings": [
      {
        "merchant": "VATAN BİLGİSAYAR",
        "price": 4199,
        "original_price": 4299
      },
      {
        "merchant": "Trendyol",
        "price": 4458.22,
        "original_price": 4458.22
      } // And others
    ],
    "merchant": "VATAN BİLGİSAYAR",
    "category_path": [
      "Elektronik",
      "Giyilebilir Teknoloji",
      "Kulaklıklar",
      "Kulak içi TWS Bluetooth Kulaklık"
    ]
  }
}
```

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