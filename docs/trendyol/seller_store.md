# Satıcı Mağaza Bilgisi

Retrieves the storefront header information for a merchant/seller: official name, brand color, score, product count, ranking badge, and a set of seller metrics (tenure, location, corporate invoice, shipping time, response time, ratings).

## Endpoint

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/seller-store/{sellerId}/header-information
```

## Path Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `sellerId` | number | Yes | The merchant/seller id (e.g. `624588`). |

## Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `channelId` | number | NO | The sales channel identifier. Use `1` for the web channel. |

## Response

Top-level wrapper: `{ "isSuccess", "statusCode", "result" }`. The `result` object contains:

- **`id`** - seller id.
- **`name`** - display name (e.g. `VATAN BİLGİSAYAR`).
- **`officialName`** - legal/official company name.
- **`score`** - seller score (e.g. `8.8`).
- **`color` / `fontColor` / `alpha`** - brand color styling.
- **`icon` / `image` / `webImage`** - brand image URLs.
- **`productCount`** - number of products sold.
- **`rankingInfo`** - `{ text, textbold, type }` ranking badge (e.g. `En çok satan Mağaza`).
- **`storeUrl`** - link to the store page.
- **`sellerMetrics`** - array of `{ id, title, value, icon, tooltip, textColor, backgroundColor }`, e.g.:
    - `Trendyol'daki Süresi` - `4 Yıl`
    - `Konum` - `İstanbul`
    - `Kurumsal Fatura` - `Uygun`
    - `Ortalama Kargolama Süresi` - `18 Saat`
    - `Soru Cevaplama Süresi` - `45-60 Dk`
    - `Ürün Değerlendirmeleri` - `4.5`
    - `Satıcı Değerlendirmeleri`

## Example

**Request:**

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/seller-store/624588/header-information?channelId=1
```

**Response:**

``` json
{
    "isSuccess": true,
    "statusCode": 200,
    "result": {
        "id": 624588,
        "name": "VATAN BİLGİSAYAR",
        "officialName": "VATAN BİLGİSAYAR SANAYİ VE TİCARET ANONİM ŞİRKETİ",
        "score": 8.8,
        "fontColor": "#FFFFFF",
        "color": "#002760",
        "alpha": 0.5,
        "icon": "https://cdn.dsmcdn.com/seller-store/uploads/624588/f5c05fed-cd22-43f2-9dc4-9b5d08f194e2.jpg",
        "image": "https://cdn.dsmcdn.com/seller-store/uploads/624588/852a7819-a185-42bf-8858-9b616aa2d9c9.jpg",
        "webImage": {
            "image": "https://cdn.dsmcdn.com/seller-store/uploads/624588/fd15dda7-04d9-4218-932d-3b9184136808.jpg",
            "overlayColor": "#000000",
            "alpha": 0.5,
            "fontColor": "#FFFFFF"
        },
        "productCount": 2954,
        "rankingInfo": {
            "text": "Elektronik Kategorisinde",
            "textbold": "En çok satan Mağaza",
            "type": "topSold"
        },
        "storeUrl": "https://www.trendyol.com/magaza/vatan-bilgisayar-m-624588",
        "sellerMetrics": [
            {
                "id": "activationDate",
                "title": "Trendyol'daki Süresi",
                "value": "4 Yıl",
                "icon": "https://cdn.dsmcdn.com/seller-store/resources/activation-date-web-icon.svg",
                "tooltip": "",
                "textColor": "#333333",
                "backgroundColor": "#FFFFFF"
            },
            {
                "id": "location",
                "title": "Konum",
                "value": "İstanbul",
                "icon": "https://cdn.dsmcdn.com/seller-store/resources/location-web-icon.svg",
                "tooltip": "",
                "textColor": "#333333",
                "backgroundColor": "#FFFFFF"
            },
            {
                "id": "corporateInvoice",
                "title": "Kurumsal Fatura",
                "value": "Uygun",
                "icon": "https://cdn.dsmcdn.com/seller-store/resources/corporate-invoice-web-icon.svg",
                "tooltip": "",
                "textColor": "#333333",
                "backgroundColor": "#FFFFFF"
            },
            {
                "id": "deliveryTime",
                "title": "Ortalama Kargolama Süresi",
                "value": "18 Saat",
                "icon": "https://cdn.dsmcdn.com/seller-store/resources/delivery-time-web-icon.svg",
                "tooltip": "Satıcının siparişlerini kargoya teslim ettiği sürenin son 1 aylık ortalamasıdır.",
                "textColor": "#333333",
                "backgroundColor": "#FFFFFF"
            },
            {
                "id": "averageResponseTime",
                "title": "Soru Cevaplama Süresi",
                "value": "45-60 Dk",
                "icon": "https://cdn.dsmcdn.com/seller-store/resources/response-time-rate-web-icon.svg",
                "textColor": "#333333",
                "backgroundColor": "#FFFFFF",
                "tooltip": "Satıcının ürün ve sipariş sorularını cevaplama süresinin son 1 aylık ortalamasıdır.."
            },
            {
                "id": "avgProductScore",
                "title": "Ürün Değerlendirmeleri",
                "value": "4.5",
                "icon": "",
                "textColor": "#333333",
                "backgroundColor": "#FFFFFF",
                "tooltip": "Satıcıya son 3 ayda gelen ürün değerlendirmelerinin ortalama puanıdır."
            },
            {
                "id": "avgSellerReviewScore",
                "title": "Satıcı Değerlendirmeleri",
                "value": "",
                "icon": "",
                "textColor": "#333333",
                "backgroundColor": "#FFFFFF",
                "tooltip": "Satıcıya son 3 ayda gelen satıcı değerlendirmelerinin ortalama puanıdır."
            }
        ]
    }
}
```