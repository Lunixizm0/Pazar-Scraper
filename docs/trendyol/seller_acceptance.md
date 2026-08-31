# Satıcı Soru Kabul Durumu

Checks whether a given seller accepts product questions (i.e. whether the question form is available on a seller's listing). A tiny helper endpoint useful before deciding whether to fetch merchant questions.

## Endpoint

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/merchant-questions/seller-acceptance
```

## Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `sellerId` | number | Yes | The merchant/seller id (e.g. `624588`). |
| `isMobile` | boolean | Yes | e.g. `false`. |
| `channelId` | number | Yes | The sales channel identifier. Use `1` for the web channel. |

## Request Headers

Same header set as the other storefront endpoints (see `review_read.md`).

## Response

``` json
{
  "isSellerAcceptQuestions": true,
  "isSuccess": true
}
```

- **`isSellerAcceptQuestions`** - boolean; whether the seller accepts questions.
- **`isSuccess`** - boolean.