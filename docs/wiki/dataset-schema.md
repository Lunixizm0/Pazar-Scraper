# Product Dataset Schema

Both providers reduce their enriched product data to a single plain-JSON record: the `ProductDataset` dataclass (`src/scrape/dataset.py`).

## Definition (for now)

``` python
@dataclass
class ProductDataset:
    source: str                       # "trendyol" | "hepsiburada"
    category: str = "unknown"         # detected category (leaf name), never null
    name: str | None = None
    brand: str | None = None
    price: str | None = None          # formatted, e.g. "3839.00 TL"
    currency: str | None = None       # e.g. "TRY"
    url: str | None = None            # canonical product URL
    sku: str | None = None
    image: str | None = None          # single primary image URL
    description: str | None = None
    availability: str | None = None   # schema.org availability URL
    item_condition: str | None = None # schema.org itemCondition URL
    reviews: dict | None = None
    vas: list | None = None           # value-added services / attributes
    installments: dict | None = None
    custom_data: dict = field(default_factory=dict)
```

`to_dict()` (`dataset.py`) mirrors every field name verbatim; `to_json()` serializes it with `ensure_ascii=False`, i.e. Turkish characters stay literal.

## Field mapping per provider

| Field | Trendyol | Hepsiburada |
| --- | --- | --- |
| `category` | `_find_category_path_in_shared_props` (leaf of `categoryTree`/`webCategoryTree`), overridable | `_detect_category` (leaf of `productState.product` category list / breadcrumbs), overridable |
| `name` / `brand` | JSON-LD `name`, `brand.name` | JSON-LD `name`, `brand.name` |
| `price` / `currency` | `extract_price` (buy-box from `merchantListing.winnerVariant`), JSON-LD `offers.priceCurrency` | `extract_price` (JSON-LD `offers.price`, mirrors redux `prices[1]`), JSON-LD `offers.priceCurrency` |
| `url` | JSON-LD `@id` | JSON-LD `offers.url` (+ redux/slug fallback) |
| `sku` | JSON-LD `sku` | redux `productState.product.sku` (or JSON-LD) |
| `image` | ImageObject `contentUrl` | `_extract_image` (JSON-LD `image` → `data-*` picture) |
| `description` | **API** (`component-read`) + sentence-marker strip | **DOM** (`div#ProductDescription` / `[class*=ProductDescription]`), JSON-LD only as fallback |
| `availability` / `item_condition` | JSON-LD `offers.availability` / `itemCondition` | `_extract_availability` (offers/stock) / `offers.itemCondition` |
| `reviews` | `_extract_reviews_custom` from `product.ratingScore` | `productState.product.reviews` → `{score, count}` |
| `vas` | `_build_vas` (11 entries from attributes/anc) | `_build_vas` (`get_vas_from_api`) |
| `installments` | `_build_installments` from `__envoy__SHARED_PROPS` | `api_data.installment` |
| `custom_data` | `_detect_custom_data` + merged caller data + `api_data` | merged + `api_data` |

## On-page vs API enrichment

The 16 dataset fields come from four sources per provider:

1. **JSON-LD** - identity fields (`name`, `brand`, `sku`, `url`, `image`, `offers`).
2. **Embedded state** - Trendyol `window["__envoy__SHARED_PROPS"]=`, Hepsiburada `script#reduxStore`. Fills what JSON-LD lacks: category tree, buybox merchant/price, all listings, review score, merchant context.
3. **Live APIs** - Trendyol component-read (description) + the `api_data` sections (delivery, merchant questions, seller store, slicing attributes, video, currencies, VAS, installments, ...); Hepsiburada VAS/installment/payment APIs.
4. **DOM** - description block (Hepsiburada) and regex backfill for ids when state is missing.

## Captured examples

### Trendyol (`product_data.json` query dataset)

``` json
{
  "source": "trendyol",
  "category": "Kulak İçi Bluetooth Kulaklık",
  "name": "Xiaomi Redmi Buds 8 Pro Siyah ..., Xiaomi Türkiye Garantili",
  "brand": "Xiaomi",
  "price": "3839.00 TL",
  "currency": "TRY",
  "sku": "1081766367",
  "availability": "https://schema.org/InStock",
  "item_condition": "https://schema.org/NewCondition",
  "reviews": { "score": 4.349056603773585, "count": 56 },
  "vas": [ { "key": "Garanti Tipi", "value": "Resmi Distribütör Garantili" }, "... 10 more" ]
}
```

`custom_data`: `{ pattern, attributes, reviews, listings[], merchant, category_path[], api_data{} }`. `category_path` here = `["Elektronik", "Giyilebilir Teknoloji", "Kulaklıklar", "Kulak içi TWS Bluetooth Kulaklık"]`; `listings` (winning merchant first) as `{ merchant, price, original_price }` - Trendyol/3839, Xiaomi Resmi Mağazası/4499, VATAN BİLGİSAYAR/4499, ARVONX GLOBAL/5930.45, EnSonu/6199.

### Hepsiburada (`expected/*`)

``` json
{
  "source": "hepsiburada",
  "category": "Kulak Üstü Kulaklık",
  "name": "Razer BlackShark V2 Pro 2023 Kablosuz Gaming Kulaklık, Beyaz RZ04-04530200-R3M1",
  "brand": "Razer",
  "price": "7890.00 TL",
  "currency": "TRY",
  "sku": "HBCV00004MW5Q6",
  "url": "https://www.hepsiburada.com/razer-blackshark-v2-pro-2023-kablosuz-gaming-kulaklik-beyaz-rz04-04530200-r3m1-p-HBCV00004MW5Q6",
  "image": "https://productimages.hepsiburada.net/s/435/375/110000467783749.jpg/format:webp",
  "description": "Razer BlackShark V2 Pro 2023 Kablosuz Gaming Kulaklık, Beyaz RZ04-04530200-R3M1",
  "availability": "https://schema.org/InStock",
  "reviews": { "score": 4.6, "count": 82 }
}
```

`custom_data`: `{ merchant: "Nethouse", product_id, category_path, listings[], reviews, api_data{} }`; `product_ctx.json` holds the extended raw context (definition_id 297, merchant_id, listing_id, root_category_list, root_buying_category_list, ...).

## Notes

- `category` has no `None` fallback in the dataclass signature but each parser substitutes the leaf name or `"unknown"` - so it always exists in the exported JSON.
- `price` is stored as a **formatted string** (`"3839.00 TL"`), not a number; the numeric value (3839) lives in `custom_data.listings[].price`.
- `description` on Trendyol reflects the post-strip text (see [trendyol-description](trendyol-description)); on Hepsiburada the DOM title line (see [hepsiburada-description](hepsiburada-description)).
- New `api_data` sections are additive and only appear in the output when the corresponding live call succeeded.