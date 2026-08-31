# Trendyol API Documentation (Storefront)

This directory documents the internal APIs that the Trendyol product page calls when visited. Each document covers the endpoint, parameters, headers, response schema, and real JSON examples captured from a live page.

All endpoints share this base URL:

```
https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api
```

## Common Request Headers

The storefront gateway's anti-bot checks are bypassed by using the `x-agentname` + `x-web-req-source` + `Origin` combination together with a `csrf-secret` cookie. With these, many endpoints are accessible via plain `requests`:

| Header | Value |
| --- | --- |
| `User-Agent` | Browser UA (e.g. Firefox). |
| `Accept` | `application/json, text/plain, */*` |
| `Accept-Language` | `tr-TR,tr;q=0.9,en-US;q=0.8` |
| `x-agentname` | `StorefrontProductGateway` |
| `x-web-req-source` | `StorefrontProductGateway` |
| `Origin` | `https://www.trendyol.com` |
| `Cookie` | `platform=web; AZ_SELECTED=false; storefrontId=1; countryCode=TR; language=tr; csrf-secret=...` |

Note: Without `countryCode=TR` the gateway returns `418` ("Required country information is wrong or missing").

## Accessibility (requests vs browser)

Some endpoints work with plain `requests`/curl, while others have stricter WAF protection and require a real browser session (camoufox/Playwright).

### Working with plain `requests`
- [review_read.md](review_read.md) - reviews, AI summary, rating distribution
- [component_data.md](component_data.md) - product description blocks (already used in the project)
- [delivery_date.md](delivery_date.md) - delivery date/cargo time
- [installment.md](installment.md) - per-bank installment options (intermittent 429)
- [merchant_questions.md](merchant_questions.md) - answered Q&A
- [seller_acceptance.md](seller_acceptance.md) - whether seller accepts questions
- [video_content.md](video_content.md) - product video
- [currencies.md](currencies.md) - TCMB exchange rates
- [stickers.md](stickers.md) - product stickers
- [complete_the_look.md](complete_the_look.md) - "complete the look" markers

### Browser (camoufox) required
- [slicing_attributes.md](slicing_attributes.md) - variants/colors
- [social_proof.md](social_proof.md) - favorite count
- [seller_store.md](seller_store.md) - seller store info
- [sellerstore_follow.md](sellerstore_follow.md) - seller follower count
- [stamps.md](stamps.md) - product badges
- [product_eligibility.md](product_eligibility.md) - product eligibility check

### External / Cloudflare protected
- [kredi_teklifleri.md](kredi_teklifleri.md) - `coc-webview.trendyol.com` credit endpoint (returns 403). The same installment data is available via [installment.md](installment.md) which is preferred.

## Endpoint List

| # | Endpoint | Purpose | Access |
| --- | --- | --- | --- |
| 1 | [review_read.md](review_read.md) `/review-read/product-reviews/detailed` | Reviews + AI summary | requests |
| 2 | [component_data.md](component_data.md) `/component-read/component/{id}` | Description | requests |
| 3 | [delivery_date.md](delivery_date.md) `/delivery-date-content/delivery-date/{contentId}/itemNumber/{itemNo}` | Delivery | requests |
| 4 | [installment.md](installment.md) `/installment/` | Installments | requests* |
| 5 | [merchant_questions.md](merchant_questions.md) `/merchant-questions/content/{id}/answered` | Q&A | requests |
| 6 | [seller_acceptance.md](seller_acceptance.md) `/merchant-questions/seller-acceptance` | Question acceptance | requests |
| 7 | [video_content.md](video_content.md) `/video-content/{id}` | Video | - |
| 8 | [currencies.md](currencies.md) `/currencies` | Exchange rates | requests |
| 9 | [stickers.md](stickers.md) `/stickers/stickers` | Stickers | - |
| 10 | [complete_the_look.md](complete_the_look.md) `/complete-the-look/markers` | CTL | - |
| 11 | [slicing_attributes.md](slicing_attributes.md) `/slicing-attributes/product-group/{gid}/slicing-attributes` | Variants | browser |
| 12 | [social_proof.md](social_proof.md) `/social-proof/` | Favorites | browser |
| 13 | [seller_store.md](seller_store.md) `/seller-store/{sid}/header-information` | Seller | browser |
| 14 | [sellerstore_follow.md](sellerstore_follow.md) `/sellerstore-follow/{sid}/follower-count` | Followers | browser |
| 15 | [stamps.md](stamps.md) `/stamps/` | Badges | browser |
| 16 | [product_eligibility.md](product_eligibility.md) `/product-eligibility/` | Eligibility | browser |
| 17 | [vas.md](vas.md) `/vas/` (POST) | VAS/insurance | - |
| 18 | [kredi_teklifleri.md](kredi_teklifleri.md) `coc-webview/.../monthly-payments/calculated` | Credit (external) | Cloudflare |

*asterisk: may intermittently return 429; add a short delay between calls.

## Example: Real working curl request

```
curl "https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/review-read/product-reviews/detailed?contentId=1081766367&page=0&pageSize=5&channelId=1" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:154.0) Gecko/20100101 Firefox/154.0" \
  -H "Accept: application/json, text/plain, */*" \
  -H "Accept-Language: tr-TR,tr;q=0.9,en-US;q=0.8" \
  -H "x-agentname: StorefrontProductGateway" \
  -H "x-web-req-source: StorefrontProductGateway" \
  -H "Origin: https://www.trendyol.com" \
  -H "Cookie: platform=web; AZ_SELECTED=false; storefrontId=1; countryCode=TR; language=tr; csrf-secret=..."
```