# Ürün Uygunluk Kontrolü (Product Eligibility)

Checks product-level eligibility flags (e.g. participation-bank eligibility) for a given product price and category. Likely consumed to toggle payment/shopping options in the UI.

In our tests this endpoint repeatedly returned `429` for non-browser (curl) clients behind the storefront WAF. The request parameters are documented below from the observed request; the response schema is not yet captured.

## Endpoint

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/product-eligibility/
```

## Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `categoryId` | number | Yes | Product category id (e.g. `1058`). |
| `bankCategoryId` | number | Yes | Bank category id (e.g. `13` = participation banks). |
| `price` | number | Yes | Product price (e.g. `4199`). |
| `culture` | string | Yes | e.g. `tr-TR`. |
| `storefrontId` | number | Yes | e.g. `1`. |
| `channelId` | number | Yes | The sales channel identifier. Use `1` for the web channel. |

## Request Headers

Same header set as the other storefront endpoints (see `review_read.md`); browser session required.

## Example Request

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/product-eligibility/?categoryId=1058&bankCategoryId=13&price=4199&culture=tr-TR&storefrontId=1&channelId=1
```