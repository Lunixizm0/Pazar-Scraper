# Ürün Videonun Bilgisi

Retrieves the metadata of a product video: the MP4 source URL, thumbnail, dimensions, duration, and view/click counts. The video content id must be known in advance (it appears in the product page's shared props).

## Endpoint

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/video-content/{videoId}
```

## Path Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `videoId` | string | Yes | The video UUID (e.g. `6d1ee37d-be18-4bf1-a17f-464d7c2a3643`). |

## Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `channelId` | number | Yes | The sales channel identifier. Use `1` for the web channel. |

## Request Headers

Same header set as the other storefront endpoints (see `review_read.md`).

## Response

Top-level wrapper: `{ "isSuccess", "statusCode", "result" }`. The `result` object contains:

- **`id`** - video UUID.
- **`url`** - MP4 video URL (on `video-content.dsmcdn.com`).
- **`thumbnail`** - thumbnail image URL.
- **`dimensions`** - `{ width, height }`.
- **`duration`** - duration in seconds.
- **`type`** - e.g. `INTERNAL`.
- **`viewCount`** / **`clickCount`** - engagement counts.
- **`videoSourceType`** - e.g. `mp4`.

## Example

**Request:**

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/video-content/6d1ee37d-be18-4bf1-a17f-464d7c2a3643?channelId=1
```

**Response:**

``` json
{
  "isSuccess": true,
  "statusCode": 200,
  "result": {
    "id": "6d1ee37d-be18-4bf1-a17f-464d7c2a3643",
    "url": "https://video-content.dsmcdn.com/prod/720p/2019922/2022913/2037868/6d1ee37d-be18-4bf1-a17f-464d7c2a3643.mp4",
    "thumbnail": "https://video-content-img.dsmcdn.com/prod/thumb/2019922/2022913/2037868/6d1ee37d-be18-4bf1-a17f-464d7c2a3643.jpg",
    "dimensions": { "width": 1280, "height": 720 },
    "duration": 33,
    "type": "INTERNAL",
    "viewCount": 1200,
    "clickCount": 1200,
    "videoSourceType": "mp4"
  }
}
```