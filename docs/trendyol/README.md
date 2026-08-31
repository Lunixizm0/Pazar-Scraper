# Trendyol API Documentation (Storefront)

This directory documents the internal APIs that the Trendyol product page calls when visited. Each document covers the endpoint, parameters, headers, response schema, and real JSON examples captured from a live page.

All endpoints share this base URL:

```
https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api
```

## Common Request Headers

The storefront gateway's anti-bot checks are bypassed by using the `x-agentname` + `x-web-req-source` + `Origin` and etc. With these, **all 18 endpoints are accessible via plain `requests`**:

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

## Accessibility

All 18 endpoints work with plain `requests`/curl when using the header combination above. No endpoints require a real browser session.

## Endpoint List

| # | Endpoint | Purpose | Parameters |
| --- | --- | --- | --- |
| 1 | [`review-read/product-reviews/detailed`](review_read.md) `/review-read/product-reviews/detailed` | Reviews + AI summary | `contentId`, `page`, `pageSize`, `channelId` |
| 2 | [`component-read/component/{id}`](component_data.md) `/component-read/component/{id}` | Description | `componentId`, `channelId` |
| 3 | [`delivery-date-content/delivery-date/{contentId}/itemNumber/{itemNo}`](delivery_date.md) `/delivery-date-content/delivery-date/{contentId}/itemNumber/{itemNo}` | Delivery | `contentId`, `itemNumber`, `winnerListingId`, `channelId` |
| 4 | [`installment/`](installment.md) `/installment/` | Installments | `amount`, `totalAmount`, `categoryId`, `categoryIds`, `codEligible`, `clientPage`, `isUserTyPlusActive`, `groupTagIds`, `channelId` |
| 5 | [`merchant-questions/content/{id}/answered`](merchant_questions.md) `/merchant-questions/content/{id}/answered` | Q&A | `contentId`, `fulfilmentType`, `excludeTag`, `page`, `size`, `isMobile`, `channelId` |
| 6 | [`merchant-questions/seller-acceptance`](seller_acceptance.md) `/merchant-questions/seller-acceptance` | Question acceptance | `sellerId`, `isMobile`, `channelId` |
| 7 | [`video-content/{videoId}`](video_content.md) `/video-content/{videoId}` | Video | `videoId`, `channelId` |
| 8 | [`currencies`](currencies.md) `/currencies` | Exchange rates | `storefrontId`, `culture`, `channelId` |
| 9 | [`stickers/stickers`](stickers.md) `/stickers/stickers` | Stickers | `stickerIds`, `platform`, `channelId` |
| 10 | [`complete-the-look/markers`](complete_the_look.md) `/complete-the-look/markers` | CTL | `contentId`, `intersactionAreaPadding`, `pointLabelGap`, `labelsGap`, `labelHeight`, `imageSize`, `labelPrefix`, `culture`, `channelId` |
| 11 | [`slicing-attributes/product-group/{gid}/slicing-attributes`](slicing_attributes.md) `/slicing-attributes/product-group/{gid}/slicing-attributes` | Variants | `groupId`, `contentId`, `channelId` |
| 12 | [`social-proof/`](social_proof.md) `/social-proof/` | Favorites | `contentIds`, `channelId` |
| 13 | [`seller-store/{sid}/header-information`](seller_store.md) `/seller-store/{sid}/header-information` | Seller | `sellerId`, `channelId` |
| 14 | [`sellerstore-follow/{sid}/follower-count`](sellerstore_follow.md) `/sellerstore-follow/{sid}/follower-count` | Followers | `sellerId`, `culture`, `checkCoupon`, `channelId` |
| 15 | [`stamps/`](stamps.md) `/stamps/` | Badges | `tagIds`, `platform`, `channelId` |
| 16 | [`product-eligibility/`](product_eligibility.md) `/product-eligibility/` | Eligibility | (parameters vary) |
| 17 | [`vas/`](vas.md) `/vas/` (POST) | VAS/insurance | `storefrontId`, `language`, `channelId` (JSON body) |
| 18 | [`kredi-teklifleri`](kredi_teklifleri.md) `coc-webview/.../monthly-payments/calculated` | Credit (external) | Cloudflare protected (returns 403) |

*asterisk: installment endpoint may intermittently return `429` under burst rate limits; add a short delay between calls.*

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