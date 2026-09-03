# JSON-LD Structured Data (Product Page)

Hepsiburada's product detail page (PDP) exposes two separate JSON-LD blocks inside `script[type="application/ld+json"]` tags:

1. **WebPage + Product (main block)** - page and product information.
2. **Review list** - product reviews inside a single JSON array.

Both blocks were captured live from the following test product:
`https://www.hepsiburada.com/elart-riva-100-pamuk-cift-kisilik-pike-sari-p-HBCV0000EBN5K8` (sku: `HBCV0000EBN5K8`).

## Block 1: WebPage + Product

The root object has `@type: WebPage` and contains a `@type: Product` within its `@graph` array. The Product element's fields:

| Field | Type | Example Value |
| --- | --- | --- |
| `@type` | string | `Product` |
| `name` | string | `Elart Riva %100 Pamuk Çift Kişilik Pike` |
| `description` | string | `Elart Riva %100 Pamuk Çift Kişilik Pike Sarı en iyi fiyatla Hepsiburada'dan satın alın! ...` |
| `category` | string | `Ev Dekorasyon > Ev Tekstili > Pike / Pike Takımı > Pike` |
| `sku` | string | `HBCV0000EBN5K8` |
| `color` | string | `Sarı` |
| `gtin` | string | `8682773153248` |
| `brand` | object | `{ "@additionalType": "Organization", "name": "Elart" }` |
| `image` | array | URL list (in webp format) |
| `aggregateRating` | object | `{ "@type": "AggregateRating", "ratingValue": 5, "ratingCount": 2 }` |
| `offers` | object | of type `Offer` (see below) |
| `hasMerchantReturnPolicy` | object | return policy |

### `offers` (Offer) sub-structure

| Field | Type | Example Value |
| --- | --- | --- |
| `@type` | string | `Offer` |
| `url` | string | Product page URL |
| `availability` | string | `https://schema.org/InStock` |
| `price` | string | `942.00` |
| `priceCurrency` | string | `TRY` |
| `itemCondition` | string | `https://schema.org/NewCondition` |
| `shippingDetails` | object | `OfferShippingDetails` (see below) |
| `seller` | object | `{ "@type": "Organization", "name": "Elart" }` |

### `offers.shippingDetails` (OfferShippingDetails) sub-structure

| Field | Type | Example Value |
| --- | --- | --- |
| `shippingRate` | object | `{ "@type": "MonetaryAmount", "value": "44.90", "currency": "TRY" }` |
| `shippingDestination` | object | `{ "@type": "DefinedRegion", "addressCountry": "TR" }` |
| `deliveryTime` | object | `ShippingDeliveryTime` (businessDays, handlingTime `0–2 days`, cutoffTime `18:00-09:00`, transitTime `0–10 days`) |

### `hasMerchantReturnPolicy`

| Field | Type | Example Value |
| --- | --- | --- |
| `merchantReturnLink` | string | `https://www.hepsiburada.com/kolay-iade` |
| `merchantReturnDays` | string | `14` |

### WebPage root fields (useful part)

| Field | Type | Example Value |
| --- | --- | --- |
| `name` | string | `Elart Riva %100 Pamuk Çift Kişilik Pike Sarı` |
| `description` | string | Meta description |
| `url` | string | Canonical product URL |
| `inLanguage` | string | `tr-tr` |
| `breadcrumb` | object | `BreadcrumbList` - category crumbs via `itemListElement[]` (6 levels) |
| `relatedLink` | array | Category and brand links |

## Block 2: Review List

The second JSON-LD block is a JSON **array**; each element has `@type: Review`:

| Field | Type | Example Value |
| --- | --- | --- |
| `@type` | string | `Review` |
| `author` | string | `Ç***** E******` (has masking) |
| `datePublished` | string | `2026-09-01` |
| `reviewBody` | string\|null | `Çok kaliteli` (may be null) |
| `reviewRating` | object | `{ "@type": "Rating", "ratingValue": 5 }` |
| `itemReviewed` | object | `{ "@type": "Product", "name": ..., "image": ..., "sku": "HBCV0000EBN5K8", "brand": {...} }` |

## Notes

- The `price` value in the JSON-LD shows the **non-discounted/shelf price** (942.00); the discounted "Sepete özel" price (`659.4`) only comes from the `/api/v1/withoutAffordability` API. The JSON-LD price alone is not sufficient.
- `aggregateRating.ratingCount` gives the total number of ratings on the page and `ratingValue` the average score; however, the merchant rating is different and comes from the `ratingSummary.lifetimeRating` field in `/api/v1/product/listings/{sku}`.
- Category information is available both in the JSON-LD `category` (a string with arrows) and in the `breadcrumb`.
