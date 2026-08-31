# Satışla Birlikte Önerilen Ekstra Ürünler (VAS) THIS SHIT NEEDS UPDATEEEE

Retrieves value-added services (VAS) offered alongside a product purchase - e.g. extended warranty / insurance packages with a calculated price, seller, category, and marketing description. This is a `POST` endpoint.

## Endpoint

```
POST https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/vas/
```

## Query Parameters (Known)

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `storefrontId` | number | Yes | e.g. `1`. |
| `language` | string | Yes | e.g. `tr`. |
| `channelId` | number | Yes | The sales channel identifier. Use `1` for the web channel. |

## Response

Top-level wrapper: `{ "isSuccess", "statusCode", "result" }`. The `result` is an array of VAS offers, each with:

- **`id`** - VAS offer id (UUID).
- **`calculatedPrice`** / **`calculatedPriceText`** / **`calculatedPriceTextWithCurrency`** - price and formatted variants.
- **`currency`** - e.g. `TRY`.
- **`category`** / **`categoryId`** - e.g. `Sigorta` / `1000`.
- **`description`** - array of marketing description lines.
- **`sellerId`** / **`sellerName`** - offering seller.
- **`sellerLandingUrl`** / **`sellerLogoUrl`** - seller links.
- **`subCategory`** / **`subCategoryId`** - e.g. `3 Yıl Ek Garanti` / `1004`.
- **`variant`** - `{ name, message }` selection rules.

## Example Response

``` json
{
  "isSuccess": true,
  "statusCode": 200,
  "result": [
    {
      "id": "234e2a629d5433086e402394cf67037a",
      "calculatedPrice": 881,
      "calculatedPriceText": "881",
      "calculatedPriceTextWithCurrency": "881 TL",
      "currency": "TRY",
      "category": "Sigorta",
      "categoryId": 1000,
      "description": ["2 ay ücretsiz YouTube Premium!", "Garantini 3 yıl daha uzat!"],
      "sellerId": 463180,
      "sellerName": "Trendyol Sigorta",
      "subCategory": "3 Yıl Ek Garanti",
      "subCategoryId": 1004
    }
  ]
}
```

## The Response i got 
``` json
{
    "isSuccess": false,
    "statusCode": 400,
    "message": "Invalid request: categoryId is required in body, brandId is required in body, sellerId is required in body, sellingPrice is required in body, attributes is required in body",
    "result": []
}
```