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
| `channelId` | number | Yes | The sales channel identifier. Use `1` for the web channel. |

## Request Headers

Requires the full browser-style header set; in our tests this endpoint returned `429` for non-browser (curl) clients behind the storefront gateway WAF, though it works when issued from a real browser session. See the main README note about browser-only endpoints.

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

**Response (excerpt):**

``` json
{
  "isSuccess": true,
  "statusCode": 200,
  "result": {
    "id": 624588,
    "name": "VATAN BİLGİSAYAR",
    "officialName": "VATAN BİLGİSAYAR SANAYİ VE TİCARET ANONİM ŞİRKETİ",
    "score": 8.8,
    "productCount": 2959,
    "rankingInfo": { "text": "Elektronik Kategorisinde", "textbold": "En çok satan Mağaza", "type": "topSold" },
    "storeUrl": "https://www.trendyol.com/magaza/vatan-bilgisayar-m-624588",
    "sellerMetrics": [
      { "id": "activationDate", "title": "Trendyol'daki Süresi", "value": "4 Yıl" },
      { "id": "location", "title": "Konum", "value": "İstanbul" }
    ]
  }
}
```