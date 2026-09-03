# Satıcı Soru-Cevap (Cevaplanmış Sorular)

Retrieves the answered questions (ürün ve satıcı soruları) for a product, including the question, the masked user, the answering seller, and the seller's answer. Supports pagination.

## Endpoint

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/merchant-questions/content/{contentId}/answered
```

## Path Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `contentId` | number | Yes | The unique product identifier (e.g. `1081766367`). |

## Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `fulfilmentType` | string | NO | Fulfillment type of the listing, e.g. `mp` (marketplace). |
| `excludeTag` | boolean | NO | e.g. `false`. |
| `page` | number | NO | Zero-based page index (e.g. `0`). |
| `size` | number | NO | Questions per page (e.g. `4`). |
| `isMobile` | boolean | Yes | e.g. `false`. |
| `channelId` | number | NO | The sales channel identifier. Use `1` for the web channel. |

## Request Headers

Same header set as the other storefront endpoints (see [`review_read.md`](trendyol-review_read)).

## Response

Response fields are at the top level (not nested under `result`):

- **`questions`** - Object with pagination info and content:
    - `page`, `size`, `totalPages`, `totalElements`.
    - `content` - array of question objects, each with:
        - `id` - question id.
        - `text` / `originalText` - the question text.
        - `userName` - masked username (e.g. `**** ****`).
        - `answeredDateMessage` - human-readable response latency (e.g. `6 saat içinde cevaplandı.`).
        - `sellerName`, `sellerId` - answering merchant.
        - `isTranslated`, `trusted`, `sourceChannelId`.
        - `creationDate` - epoch millis.
        - `answer` - `{ text, isTranslated, originalText }`.

- **`sellerScore`** - object (may be empty `{}` on non-eligible sellers).

- **`contentSummary`** - `{ totalCount, tags[] }` total number of questions and tags.

- **`isSuccess`**, **`statusCode`**.

## Example

**Request:**

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/merchant-questions/content/1081766367/answered?fulfilmentType=mp&excludeTag=false&page=0&size=4&isMobile=false&channelId=1
```

**Response (excerpt):**

``` json
{
  "questions": {
    "page": 0,
    "size": 4,
    "totalPages": 1,
    "totalElements": 2,
    "content": [
      {
        "id": 445821784,
        "text": "1 tanesini kaybettim nasıl yapabiliriz",
        "userName": "**** ****",
        "answeredDateMessage": "6 saat içinde cevaplandı.",
        "sellerName": "VATAN BİLGİSAYAR",
        "sellerId": 624588,
        "creationDate": 1787873642215,
        "answer": { "text": "Değerli müşterimiz, yedek parça satışımız bulunmamaktadır.", "isTranslated": false, "originalText": "..." }
      }
    ]
  },
  "contentSummary": { "totalCount": 24, "tags": [] },
  "isSuccess": true,
  "statusCode": 200
}
```