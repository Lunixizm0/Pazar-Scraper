# Other Merchants (Other Sellers)

Returns the other sellers that sell the same product, along with their prices, discount rates, and campaign counts. Unlike the single-seller (buybox) list, it shows cross-seller competition.

## Endpoint

```
POST https://www.hepsiburada.com/api/v1/otherMerchants
```

## Request Headers

| Header | Value |
| --- | --- |
| `accept` | `application/json, text/plain, */*` |
| `content-type` | `application/json;charset=utf-8` |
| `origin` | `https://www.hepsiburada.com` |
| `referer` | the product page URL |
| `cookie` | `hbus_anonymousId` and Akamai cookies |

## Request Body

```json
{
  "userId": "d0965061-6de7-4275-9138-7bbe5f942d90",
  "product": {
    "productTags": ["1200-300-home-kuponu", "200-tl-visa-kampanyasi", "..."],
    "sku": "HBCV0000EBN5K8",
    "productId": "HBC0000EBN5K2",
    "brand": "Elart",
    "rootCategoryList": [60002028, 2147483618, 512226, 9010353],
    "rootBuyingCategoryList": [9010353],
    "definitionName": "Pike Takımları",
    "definitionId": "559",
    "taxVatRate": 10,
    "campaignIds": [],
    "otherMerchants": [
      {
        "productTags": ["..."],
        "campaignIds": [],
        "finalPriceOnSale": 942,
        "minimumPriceForNLastDays": 370.69,
        "merchantId": "9040f2fb-b962-4d99-bc4d-27626d64ad92",
        "merchantName": "ELART",
        "listingId": "0f6040d3-dda6-43af-bbf0-0eb838c800b2"
      }
    ]
  }
}
```

Note: `productTags` is a long campaign tag list. The `otherMerchants` array contains summary info of the current merchant(s). `userId` = `hbus_anonymousId`.

## Response

Top-level container: `{ "statusCode": 200, "data": { "result": { "product": {...} } }, "redirection": {...} }`.

### `result.product` fields

| Field | Type | Example Value |
| --- | --- | --- |
| `sku` | string | `HBCV0000EBN5K8` |
| `productId` | string | `HBC0000EBN5K2` |
| `merchantName` | string | `ELART` |
| `merchantId` | string (UUID) | `9040f2fb-...` |
| `listingId` | string (UUID) | `0f6040d3-...` |
| `price` | number | `942` |
| `discountedPrice` | number | `659.4` |
| `discountRate` | number | `30` |
| `couponCount` | number | (coupon count) |
| `campaignCount` | number | (campaign count) |

Note: In the observed test product the fields are of an object-structure with `merchantName`/`priceData`; in some responses field names may be in the form `merchantName`, `couponCount`, `campaignCount`, `priceData: {price, discountedPrice}`. A real observed example is given below.

## Example (real observation)

The following response shows the merchant info returned in the `result.product` section of the `otherMerchants` request (it matches the `otherMerchants` array in the request body one-to-one):

```json
{
  "statusCode": 200,
  "data": {
    "result": {
      "product": {
        "finalPriceOnSale": 942,
        "minimumPriceForNLastDays": 370.69,
        "merchantId": "9040f2fb-b962-4d99-bc4d-27626d64ad92",
        "merchantName": "ELART",
        "listingId": "0f6040d3-dda6-43af-bbf0-0eb838c800b2"
      }
    }
  }
}
```

> Note: In this example the `otherMerchants` array in the body only contains the current merchant (single seller). In multi-merchant products this array contains multiple companies, each returning separate price/campaign data. Field names (`price`, `discountedPrice`, `discountRate`, `couponCount`, `campaignCount`) may be seen in different products; the scraper should handle all variations safely (`dict.get`).

## Notes

- Unlike `product/listings`, this endpoint carries the **competitive price and campaigns of other sellers**.
- For single-seller products, `otherMerchants` only contains the main merchant; for multi-merchant products it provides comparative price data.
- `minimumPriceForNLastDays` - the seller's lowest price over the last N days (370.69).
