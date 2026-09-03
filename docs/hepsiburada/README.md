# Hepsiburada API Documentation (Storefront)

This directory documents the internal APIs that Hepsiburada's product detail page (PDP) calls when visited, as well as its JSON-LD structured data. Each document covers the endpoint, its parameters, headers, response schema, and real JSON examples captured from a live page.

The data sources fall into two groups:

1. **JSON-LD** - structured data embedded in the HTML (shelf price, name, SKU, brand, review count, etc.).
2. **HTTP APIs** - internal services called by the page's JavaScript (discounted price, campaigns, installments, other sellers, payment, shipping, seller question status).

## Common Request Headers

Due to Hepsiburada's anti-bot protection (Akamai `_abck` / `bm_sz`), bare `requests` calls can return 403. Working calls were verified through a browser session; the headers below were captured from a real request:

| Header | Value |
| --- | --- |
| `User-Agent` | Browser UA (e.g. Firefox). |
| `Accept` | `application/json, text/plain, */*` |
| `Accept-Language` | `en-US,en;q=0.9` |
| `referer` | The product page URL |
| `cookie` | `hbus_anonymousId`, `_abck`, `bm_sz`, etc. (Akamai session cookies) |

POST endpoints additionally use these headers: `origin: https://www.hepsiburada.com`, `content-type: application/json`. The `withoutAffordability` endpoint requires `x-gotham_*` headers.

Most cookies come from the browser session; in particular, without `hbus_anonymousId` (the `userId` value used in request bodies) and the Akamai protection cookies, requests may return 403.

## Endpoint List

| # | Endpoint | Method | Purpose | Parameters |
| --- | --- | --- | --- | --- |
| 1 | [`/api/v1/product/listings/{sku}`](product_listings.md) | GET | Seller listings (price, stock, rating, shipping) | `sku` |
| 2 | [`/api/v1/withoutAffordability`](without_affordability.md) | POST | Discounted price + campaign | JSON body (`userId`, `product`, `affordabilityRequest`) |
| 3 | [`/api/v1/product/installment`](installment.md) | GET | Installment / credit options | `maxInstallment`, `amount`, `definitionId`, `paymentTag`, `sku`, `merchantId`, `taxRatio` |
| 4 | [`/api/v1/otherMerchants`](other_merchants.md) | POST | Other sellers (competitive price) | JSON body (`userId`, `product.otherMerchants[]`) |
| 5 | [`/api/v1/paymentOptions`](payment_options.md) | POST | Payment options | JSON body (`userId`, `affordabilityRequest`) |
| 6 | [`shipping-external.../duedateapi/querymodel/withtext/v2`](shipping_due_date.md) | POST | Shipping delivery date | JSON body (`queryModels[]`) |
| 7 | [`api-asktoseller.../products/{sku}/merchants/accept-questions`](ask_to_seller.md) | GET | Seller question status + rating | `sku` |
| 8 | [`customer-voltran-gw.../api/vas/evaluate`](vas.md) | POST | Value-added services / insurance suggestions (VAS) | JSON body (`definationName`, `merchantName`, `price`, `rootCategories[]`, `sku`) |
| - | [`jsonld.md`](jsonld.md) | - | HTML-embedded structured data | - |

## Accessibility

Unlike Trendyol, Hepsiburada's APIs do **not** always work with plain `requests`: Akamai `_abck` protection blocks out-of-context calls with a 403 ("Security" page). The verified working approach is to open the product page in a browser (Camoufox), collect the session cookies, and make the API calls with those cookies.

## Example: A real working request (with browser session cookies)

```
GET https://www.hepsiburada.com/api/v1/product/listings/HBCV0000EBN5K8
  -H "User-Agent: Mozilla/5.0 ... Firefox/152.0"
  -H "Accept: application/json, text/plain, */*"
  -H "Referer: https://www.hepsiburada.com/elart-riva-100-pamuk-cift-kisilik-pike-sari-p-HBCV0000EBN5K8"
  -H "Cookie: hbus_anonymousId=d0965061-...; _abck=...; bm_sz=..."
```

## Test Product

All examples in these documents were captured from the following product:
`https://www.hepsiburada.com/elart-riva-100-pamuk-cift-kisilik-pike-sari-p-HBCV0000EBN5K8`

- **SKU:** `HBCV0000EBN5K8`
- **Product ID:** `HBC0000EBN5K2`
- **Merchant:** ELART (`9040f2fb-b962-4d99-bc4d-27626d64ad92`)
- **Shelf price:** 942.00 TL (JSON-LD / listings)
- **Discounted price:** 659.40 TL ("Sepete özel" 30%, withoutAffordability)
