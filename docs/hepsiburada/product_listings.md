# Product Listings (Merchant Listings)

Returns price, stock, shipping, merchant rating, and price history data for all of a product's merchants (merchant listings). It includes one record per merchant, including the page's buybox (featured) merchant.

## Endpoint

```
GET https://www.hepsiburada.com/api/v1/product/listings/{sku}
```

`{sku}` — the product's SKU code (e.g. `HBCV0000EBN5K8`).

## Request Headers

Tested with plain `requests`. The required ones are:

| Header | Value |
| --- | --- |
| `accept` | `application/json, text/plain, */*` |
| `referer` | the product page URL |
| `cookie` | `_abck`, `bm_sz`, `hbus_anonymousId`, etc. (Akamai session cookies) |

No auth header is required. However, due to anti-bot protection (Akamai `_abck`), a bare `requests` call may return 403; it may be necessary to use cookies obtained from a browser session.

## Response

Top-level container: `{ "statusCode": 200, "data": { "listings": [...] }, "redirection": {...} }`. `data.listings` is an array; each element is a merchant listing.

### Listing fields

| Field | Type | Example Value |
| --- | --- | --- |
| `merchantId` | string (UUID) | `9040f2fb-b962-4d99-bc4d-27626d64ad92` |
| `listingId` | string (UUID) | `0f6040d3-dda6-43af-bbf0-0eb838c800b2` |
| `merchantName` | string | `ELART` |
| `freeShipping` | boolean | `false` |
| `fastShipping` | boolean | `false` |
| `shipmentDay` | number | `1` |
| `shipmentType` | string | `businessDays` |
| `isSalable` | boolean | `true` |
| `quantity` | number | `405` |
| `buyboxOrder` | number | `1` |
| `warehouseId` | string | `BIRINCIL` |
| `aiBasedShipmentDay` | number | `2` |
| `isFulfilledByHB` | boolean | `false` |
| `isBundle` | boolean | `false` |
| `womanEntrepreneur` | boolean | `false` |
| `isCampaignParticipationClosed` | boolean | `false` |
| `inStockDate` | string\|null | `null` |
| `minimumPurchasableQuantity` | number | `0` |

### Price objects

| Field | Type | Example Value |
| --- | --- | --- |
| `price` | object | `{ "value": 942, "currency": 0 }` |
| `originalPrice` | object | `{ "value": 942, "currency": 0 }` |
| `minimumPrice` | object | `{ "value": 370.69, "currency": 0 }` |
| `minimumPrices` | array | `[{"name":"10","value":370.69},{"name":"30","value":370.69},{"name":"non-segmented-price","value":659.4}]` |
| `vatExcludedPrice` | object | `{ "value": 856.36, "currency": 0 }` (price excluding VAT) |
| `unitPrice` | object\|null | `null` |
| `prices` | array | `[{"formattedPrice":"942,00","value":942,"currency":0,"discountRate":0}]` |
| `discountRate` | number | `0` |

Note: `price.value` is 942 TL in the base currency; the currency amount `0` = TL. The `non-segmented-price` (659.4) in `minimumPrices` matches the "Sepete özel" discounted price.

### Merchant rating and info

| Field | Type | Example Value |
| --- | --- | --- |
| `ratingSummary` | object | `{ "lifetimeRating": 9.6, "ratingQuantity": 100 }` |
| `merchantCity` | string | `BURSA` |
| `merchantCountry` | string | `TÜRKİYE` |
| `merchantInfo` | object | `{ id, name, logo, ratingSummary, merchantLabels, urlPostfix }` |
| `logo` | string | Merchant logo URL |

### Other fields

- `paymentTag` — comma-separated campaign/tag list (very long; same content as `tagList`).
- `tagList` — tag array of the form `[{ "tagId": "1200-300-home-kuponu" }, ...]`.
- `buyboxAlternatives` — buybox algorithm information.
- `jetDeliveryCities` — jet delivery cities (may be empty).
- `shippingProfileId` — shipping profile UUID.
- `customizationConfiguration` — may be an empty array.
- `pbs` — long Akamai protection token (meaningless for the scraper).

## Example

**Request:**
```
GET https://www.hepsiburada.com/api/v1/product/listings/HBCV0000EBN5K8
```

**Response (summary):**
```json
{
  "statusCode": 200,
  "data": {
    "listings": [
      {
        "merchantId": "9040f2fb-b962-4d99-bc4d-27626d64ad92",
        "listingId": "0f6040d3-dda6-43af-bbf0-0eb838c800b2",
        "merchantName": "ELART",
        "freeShipping": false,
        "fastShipping": false,
        "shipmentDay": 1,
        "isSalable": true,
        "price": { "value": 942, "currency": 0 },
        "originalPrice": { "value": 942, "currency": 0 },
        "minimumPrice": { "value": 370.69, "currency": 0 },
        "vatExcludedPrice": { "value": 856.36, "currency": 0 },
        "discountRate": 0,
        "ratingSummary": { "lifetimeRating": 9.6, "ratingQuantity": 100 },
        "merchantCity": "BURSA",
        "quantity": 405,
        "buyboxOrder": 1
      }
    ]
  },
  "redirection": { "url": null, "type": null, "message": null }
}
```

## Notes

- The record with `buyboxOrder: 1` represents the main (buybox) merchant; multi-merchant products return more than one listing.
- The current test product is single-merchant (ELART); `buyboxAlternatives` only contains the algorithm names.
- The `product/listings` API gives only the current merchant's price/rating/stock info, not the full campaign list of other merchants; cross-merchant comparison is done via `/api/v1/otherMerchants`.
