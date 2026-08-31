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
| `channelId` | number | NO | The sales channel identifier. Use `1` for the web channel. |

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
                            "name": "Redmi Buds 8 Pro Siyah Bluetooth Kulakiçi Kulaklık TWS - ANC BT 5.4 (Xiaomi TR Garantili)",
                            "pageUrl": "/xiaomi/redmi-buds-8-pro-siyah-bluetooth-kulakici-kulaklik-tws-anc-bt-5-4-xiaomi-tr-garantili-p-1081766367",
                            "imageUrl": "https://cdn.dsmcdn.com/mnresize/128/192/ty1000319/product/media/images/prod/PIM/20260227/12/a9dc7313-301e-4256-babd-8e0d08ee7623/1_org_zoom.jpg",
                            "merchantId": 968,
                            "campaignId": 689770,
                            "isSelected": true
                        }
                    ]
                },
                {
                    "name": "Mavi",
                    "beautifiedName": "mavi-c",
                    "isSelected": false,
                    "products": [
                        {
                            "id": 1081766366,
                            "name": "Redmi Buds 8 Pro Mavi Bluetooth Kulakiçi Kulaklık TWS - ANC BT 5.4 (Xiaomi TR Garantili)",
                            "pageUrl": "/xiaomi/redmi-buds-8-pro-mavi-bluetooth-kulakici-kulaklik-tws-anc-bt-5-4-xiaomi-tr-garantili-p-1081766366",
                            "imageUrl": "https://cdn.dsmcdn.com/mnresize/128/192/ty1000314/product/media/images/prod/PIM/20260227/12/387739a4-5872-40ae-8f53-c42590af6f72/1_org_zoom.jpg",
                            "merchantId": 984136,
                            "campaignId": 61,
                            "isSelected": false
                        }
                    ]
                },
                {
                    "name": "Beyaz",
                    "beautifiedName": "beyaz",
                    "isSelected": false,
                    "products": [
                        {
                            "id": 1081766368,
                            "name": "Redmi Buds 8 Pro Beyaz Bluetooth Kulakiçi Kulaklık TWS - ANC BT 5.4 (Xiaomi TR Garantili)",
                            "pageUrl": "/xiaomi/redmi-buds-8-pro-beyaz-bluetooth-kulakici-kulaklik-tws-anc-bt-5-4-xiaomi-tr-garantili-p-1081766368",
                            "imageUrl": "https://cdn.dsmcdn.com/mnresize/128/192/ty1000057/product/media/images/prod/PIM/20260108/14/9cd8faab-d1e4-4258-be29-9473c8fffedd/1_org_zoom.jpg",
                            "merchantId": 968,
                            "campaignId": 689770,
                            "isSelected": false
                        }
                    ]
                }
            ]
        }
    ]
}
```