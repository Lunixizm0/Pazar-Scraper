# Sosyal Kanıt (Favori / Beğeni Sayıları)

Retrieves "social proof" badges for one or more products - e.g. how many users favorited the product. The response is keyed by `contentId`.

## Endpoint

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/social-proof/
```

## Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `contentIds` | string | Yes | Comma-separated product ids (e.g. `1081766367`). |
| `channelId` | number | Yes | The sales channel identifier. Use `1` for the web channel. |

## Response

The response is an object keyed by `contentId`; each value contains:

- **`socialProofs`** - array of badge objects:
    - `id` - badge id (e.g. `favorite-count`).
    - `count` - display string (e.g. `2,4B`).
    - `icon` - icon URL.
    - `order` - display order.
- **`sentiments`** - array (currently empty).

## Example

**Request:**

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/social-proof/?contentIds=1081766367&channelId=1
```

**Response:**

``` json
{
  "1081766367": {
    "socialProofs": [
      { "id": "favorite-count", "count": "2,4B", "icon": "https://cdn.dsmcdn.com/mnresize/30/30/mobile/pdp/Additional/orange-heart_1f9e1.png", "order": 2 }
    ],
    "sentiments": []
  }
}
```