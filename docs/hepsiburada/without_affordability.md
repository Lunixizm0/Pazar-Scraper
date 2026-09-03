# Without Affordability (Campaign + Discount)

Returns the product's "Sepete özel" discounted price, discount rate, applicable campaigns, and the free shipping threshold. It is the core of Hepsiburada's price display (PDP) logic. While the JSON-LD only contains the shelf price (942.00), the **discounted price (659.4)** comes from this API.

## Endpoint

```
POST https://www.hepsiburada.com/api/v1/withoutAffordability
```

## Request Headers

The `x-gotham_*` headers are required (captured from a real request, without assumptions):

| Header | Value |
| --- | --- |
| `accept` | `application/json, text/plain, */*` |
| `content-type` | `application/json` |
| `origin` | `https://www.hepsiburada.com` |
| `referer` | the product page URL |
| `x-gotham_is_include_premium_clubs` | `true` |
| `x-gotham_is_include_payment_campaigns` | `true` |
| `x-gotham_is_enabled_next_eligible_campaign` | `true` |
| `x-gotham_is_enabled_evaluate_coupon` | `true` |
| `x-gotham_app-key` | `All` |
| `cookie` | `hbus_anonymousId` and Akamai cookies |

## Request Body

```json
{
  "userId": "d0965061-6de7-4275-9138-7bbe5f942d90",
  "product": {
    "productTags": ["1200-300-home-kuponu", "200-tl-visa-kampanyasi", "..."],
    "finalPrice": 942,
    "sku": "HBCV0000EBN5K8",
    "listingId": "0f6040d3-dda6-43af-bbf0-0eb838c800b2",
    "productId": "HBC0000EBN5K2",
    "brand": "Elart",
    "merchantId": "9040f2fb-b962-4d99-bc4d-27626d64ad92",
    "rootCategoryList": [60002028, 2147483618, 512226, 9010353],
    "rootBuyingCategoryList": [9010353],
    "definitionName": "Pike Takımları",
    "definitionId": "559",
    "finalPriceOnSale": 942,
    "taxVatRate": 10,
    "campaignIds": [],
    "campaigns": []
  },
  "affordabilityRequest": {
    "product": null,
    "additionalData": null,
    "definitionId": "559"
  }
}
```

Note: in the real request `productTags` is a very long campaign tag list; it can be fed from the `paymentTag` of the `listing` API, or from the `withoutAffordability` request body. The `rootCategoryList`, `rootBuyingCategoryList`, `definitionId`, `merchantId`, `productId`, `listingId`, and `finalPrice` values are derived from `product/listings` and the meta tags. `userId` = the `hbus_anonymousId` cookie value.

## Response

Top-level container: `{ "statusCode": 200, "data": { "result": { "product": {...} } }, "redirection": {...} }`.

### `result.product` fields

| Field | Type | Example Value |
| --- | --- | --- |
| `sku` | string | `HBCV0000EBN5K8` |
| `listingId` | string (UUID) | `0f6040d3-...` |
| `merchantId` | string (UUID) | `9040f2fb-...` |
| `priceData` | object | `{ "discountedPrice": 659.4, "priceText": "Sepete özel", "priceTextColor": "#009319", "isPremium": false }` |
| `discountRateData` | object | `{ "formattedText": "...%30...", "text": "%30", "bgColor": "#009319", "type": "basket", "discountRate": 30 }` |
| `promoData` | object | Campaign detail (see below) |
| `labelList` | null | `null` |

### `result.product.promoData.data` sub-structure

- `campaignEvaluateResult.evaluateResult` — `{ campaignText, campaigns[], discountedPrice }`
  - Each `campaigns[]`: `{ id, name, totalDiscount, type, discountValue, conditionAmount, conditionQuantity, awardQuantity, isPremium, isAdditionalBenefit, endDateTime }`
  - Example: `id: 95592497`, `name: "ELART satıcılı seçili ürünlerde %30 indirim"`, `totalDiscount: 282.6`, `discountValue: 30`, `endDateTime: "2026-09-30T23:59:00+03:00"`
- `campaigns.campaignTabDetailList.discountCampaignList[]` — discount campaigns
- `campaigns.campaignTabDetailList.freeShippingCampaignList[]` — free shipping campaigns
  - Example: `{ id: 24055363, name: "300 TL üzeri kargo bedava", type: 6, conditionAmount: 300 }`
- `campaigns.campaignTabDetailList.totalCampaignCount` — `2`
- `nextEligibleCampaign` — `{ campaignId, isPremiumCampaign, text }`

## Example (structural)

```json
{
  "statusCode": 200,
  "data": {
    "result": {
      "product": {
        "sku": "HBCV0000EBN5K8",
        "priceData": { "discountedPrice": 659.4, "priceText": "Sepete özel" },
        "discountRateData": { "text": "%30", "discountRate": 30 },
        "promoData": {
          "data": {
            "campaignEvaluateResult": {
              "evaluateResult": {
                "campaignText": "ELART satıcılı seçili ürünlerde %30 indirim",
                "discountedPrice": 659.4,
                "campaigns": [
                  { "id": 95592497, "name": "ELART satıcılı seçili ürünlerde %30 indirim", "discountValue": 30, "totalDiscount": 282.6 }
                ]
              }
            },
            "campaigns": {
              "campaignTabDetailList": {
                "freeShippingCampaignList": [
                  { "id": 24055363, "name": "300 TL üzeri kargo bedava", "conditionAmount": 300 }
                ]
              },
              "totalCampaignCount": 2
            }
          }
        }
      }
    }
  }
}
```

## Notes

- `priceData.discountedPrice` is the price to pay after the discount (659.4). The shelf price comes from the JSON-LD (942) and the listings API.
- The campaign `endDateTime` value is in UTC+03:00 format (e.g. `2026-09-30T23:59:00+03:00`).
- `discountRateData.type` can be `"basket"` (sepete özel); this indicates the discount is only applied in the cart.
