# Tamamlayıcı Ürün İşaretçileri (Complete the Look)

Retrieves clickable marker positions for "complete-the-look" style recommendations overlaid on the product image. For many products this returns an empty `markers` array (feature not active); kept here for completeness.

## Endpoint

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/complete-the-look/markers
```

## Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `contentId` | number | Yes | The product id (e.g. `1081766367`). |
| `intersactionAreaPadding` | number | Yes | Image interaction padding (e.g. `5`). |
| `pointLabelGap` | number | Yes | `30` |
| `labelsGap` | number | Yes | `4` |
| `labelHeight` | number | Yes | `28` |
| `imageSize` | string | Yes | Image dimensions (e.g. `398x597`). |
| `labelPrefix` | string | Yes | `+` |
| `culture` | string | Yes | e.g. `tr-TR`. |
| `channelId` | number | Yes | Channel id, `1` for web. |

## Request Headers

Same header set as the other storefront endpoints (see [`review_read.md`](trendyol-review_read)).

## Response

Top-level wrapper: `{ "isSuccess", "statusCode", "result" }`. The `result` object contains a `markers` array.

## Example

**Request:**

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/complete-the-look/markers?contentId=1081766367&intersactionAreaPadding=5&pointLabelGap=30&labelsGap=4&labelHeight=28&imageSize=398x597&labelPrefix=+&culture=tr-TR&channelId=1
```

**Response:**

``` json
{
  "isSuccess": true,
  "statusCode": 200,
  "result": { "markers": [] }
}
```