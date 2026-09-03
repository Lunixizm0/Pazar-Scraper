# Ürün Uygunluk Kontrolü (Product Eligibility)

Checks product-level eligibility flags (e.g. participation-bank eligibility) for a given product price and category. Likely consumed to toggle payment/shopping options in the UI.

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
| `storefrontId` | number | NO | e.g. `1`. |
| `channelId` | number | Yes | The sales channel identifier. Use `1` for the web channel. |

## Request Headers

Same header set as the other storefront endpoints (see [`review_read.md`](trendyol-review_read)); browser session required.

## Example Request

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/product-eligibility/?categoryId=1058&bankCategoryId=13&price=4199&culture=tr-TR&storefrontId=1&channelId=1
```

## Example Response

```
{
    "isSuccess": true,
    "statusCode": 200,
    "result": {
        "eligible": true,
        "maxLoanTerm": 36,
        "productDetailSlogan": "Alışveriş Kredisiyle 36 Aya Varan Taksit!",
        "banners": [
            {
                "title": "Alışveriş Kredisi",
                "content": "36 ay 244 TL'den başlayan ödeme fırsatları",
                "logo": "/ty667/retailfs-banner/default_banner.png",
                "redirectUrl": "https://coc-webview.trendyol.com/retailfs/pdp-landing-page?price=4199.0&maxTerm=36&bankCategoryId=13&showMonthlyPayments=true",
                "zeroInterest": false,
                "color": {
                    "titleCode": "#F27A1A",
                    "backgroundCode": "#FEF1E8"
                }
            }
        ]
    }
}
```