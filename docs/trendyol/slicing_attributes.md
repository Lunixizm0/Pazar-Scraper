# Ürün Varyantları (Renk / Seçenek Grupları)

Retrieves the variant attributes (e.g. color options) of a product group, including for each variant the alternative product id, its page URL, image, and merchant/campaign info. This is how the site renders the "Renk: Siyah / Mavi / Beyaz" selector, so it links sibling products within the same product family.

## Endpoint

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/slicing-attributes/product-group/{groupId}/slicing-attributes
```

## Path Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `groupId` | number | Yes | The product group id (e.g. `821600500`). This is the `pGroupId`/group identifier of the product family, distinct from the individual `contentId`. |

## Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `contentId` | number | Yes | The current product id (e.g. `1081766367`). |
| `channelId` | number | Yes | The sales channel identifier. Use `1` for the web channel. |

## Request Headers

Requires the full browser-style header set. In our tests this endpoint returned `429`/`418` for non-browser (curl) clients behind the storefront gateway's stricter WAF rules, though it works when issued from a real browser session. See notes in the main README about the ones that need a browser.

## Response

Top-level wrapper: `{ "isSuccess", "statusCode", "result" }`. The `result` is an array of attribute groups. Each group has:

- **`type`** - internal type slug (e.g. `DsmColor`).
- **`title`** - display title (e.g. `Renk`).
- **`displayType`** - how it renders (e.g. `IMAGE_ONLY`).
- **`values`** - array of variant values, each with:
    - `name` - display name (e.g. `Siyah`).
    - `beautifiedName` - URL-safe slug (e.g. `siyah`).
    - `isSelected` - whether this is the currently selected variant.
    - `products` - array of `{ id, name, pageUrl, imageUrl, merchantId, campaignId, isSelected }` for the product(s) matching this variant. `pageUrl` links to the sibling product page.

## Example

**Request:**

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/slicing-attributes/product-group/821600500/slicing-attributes?contentId=1081766367&channelId=1
```

**Response (excerpt):**

``` json
{
  "isSuccess": true,
  "statusCode": 200,
  "result": [
    {
      "type": "DsmColor",
      "title": "Renk",
      "displayType": "IMAGE_ONLY",
      "values": [
        {
          "name": "Siyah",
          "beautifiedName": "siyah",
          "isSelected": true,
          "products": [
            {
              "id": 1081766367,
              "name": "Redmi Buds 8 Pro Siyah Bluetooth Kulakiçi Kulaklık TWS - ANC BT 5.4",
              "pageUrl": "/xiaomi/redmi-buds-8-pro-siyah-...-p-1081766367",
              "imageUrl": "https://cdn.dsmcdn.com/mnresize/128/192/ty1000319/.../1_org_zoom.jpg",
              "merchantId": 624588,
              "campaignId": 61,
              "isSelected": true
            }
          ]
        }
      ]
    }
  ]
}
```