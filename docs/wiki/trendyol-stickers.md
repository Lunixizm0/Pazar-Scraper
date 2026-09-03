# Ürün Çıkartmaları (Stickers)

Retrieves decorative/promotional stickers shown on a product for a given set of `stickerIds`. In our sample this returned a single "authorized seller" sticker linking to a help page.

## Endpoint

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/stickers/stickers
```

## Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `stickerIds` | string | Yes | Comma-separated sticker ids (e.g. `1044`). |
| `platform` | string | Yes | e.g. `WEB`, `ANDROID`, `IOS`. |
| `channelId` | number | NO | The sales channel identifier. Use `1` for the web channel. |

## Request Headers

Same header set as the other storefront endpoints (see [`review_read.md`](trendyol-review_read)).

## Response

Top-level wrapper: `{ "isSuccess", "statusCode", "result" }`. The `result` is an array of sticker objects, each with:

- **`description`** - text (may be empty).
- **`stickerImageUrl`** - sticker image URL.
- **`stickerClickableUrl`** - link the sticker navigates to.
- **`isAuthorizedSellerSticker`** - boolean; whether it denotes an authorized merchant.

## Example

**Request:**

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/stickers/stickers?stickerIds=1044&platform=WEB&channelId=1
```

**Response:**

``` json
{
    "isSuccess": true,
    "statusCode": 200,
    "result": [
        {
            "description": "",
            "stickerImageUrl": "https://cdn.dsmcdn.com/indexing-sticker-stamp/moon/98388081-20db-4862-9367-2f698d53eeea.png",
            "stickerClickableUrl": "ty://?Page=InWeb&WebUrl=https%3A%2F%2Fm.trendyol.com%2Fs%2Fbluetooth-kulakliklarinda-sikca-sorulan-sorular",
            "isAuthorizedSellerSticker": false
        }
    ]
}
```