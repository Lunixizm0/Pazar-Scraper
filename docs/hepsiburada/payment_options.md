# Payment Options (Payment Options)

Returns the payment methods shown on the product page (Hepsitaksit card-free installments, credit card, shopping loan).

## Endpoint

```
POST https://www.hepsiburada.com/api/v1/paymentOptions
```

## Request Headers

| Header | Value |
| --- | --- |
| `accept` | `application/json, text/plain, */*` |
| `content-type` | `application/json` |
| `origin` | `https://www.hepsiburada.com` |
| `referer` | the product page URL |
| `sec-fetch-dest` | `empty` |
| `sec-fetch-mode` | `cors` |
| `sec-fetch-site` | `same-origin` |
| `cookie` | `hbus_anonymousId` and Akamai cookies |

## Request Body

```json
{
  "userId": "d0965061-6de7-4275-9138-7bbe5f942d90",
  "affordabilityRequest": {
    "product": null,
    "additionalData": null,
    "definitionId": "559"
  }
}
```

Note: `userId` = `hbus_anonymousId`, `definitionId` is the product's definition id (`559`). `product` and `additionalData` are sent as null.

## Response

Top-level container: `{ "statusCode": 200, "data": { "result": { "product": {...} } }, "redirection": {...} }`.

### `result.product` fields

| Field | Type | Example Value |
| --- | --- | --- |
| `paymentOptions` | array | List of payment options (see below) |
| `cardPrograms` | string | `` (empty) |
| `prioritizedEcomCardProgramNames` | string\|null | `null` |

### each `paymentOptions[]` item

| Field | Type | Description |
| --- | --- | --- |
| `paymentType` | number | 4=card-free installment (Hepsitaksit), 3=credit card, 2=shopping loan, 1=other (cash) |
| `title` | string | Title: `Hepsitaksit`, `Kredi Kartı ile`, `Alışveriş Kredisi` |
| `text` | string | Description text (e.g. `Kartsız taksitle al`, `Peşin fiyatına taksitle al`, `Kartsız {0} taksit`) |
| `iconUrl` | string | Icon URL |
| `isCashPrice` | boolean | `false` |
| `isSelected` | boolean\|null | `null` |

## Example (structural)

```json
{
  "statusCode": 200,
  "data": {
    "result": {
      "product": {
        "paymentOptions": [
          { "paymentType": 4, "text": "Kartsız taksitle al", "title": "Hepsitaksit", "isCashPrice": false, "isSelected": null },
          { "paymentType": 3, "text": "Peşin fiyatına taksitle al", "title": "Kredi Kartı ile", "isCashPrice": false, "isSelected": null },
          { "paymentType": 2, "text": "Kartsız {0} taksit", "title": "Alışveriş Kredisi", "isCashPrice": false, "isSelected": null },
          { "paymentType": 1, "isCashPrice": false, "isSelected": null }
        ],
        "cardPrograms": "",
        "prioritizedEcomCardProgramNames": null
      }
    }
  }
}
```

## Notes

- The `paymentType` values indicate the payment channel: `1` (cash/card - may have no title), `2` (Shopping Loan), `3` (Credit Card), `4` (Hepsitaksit card-free installment).
- The `iconUrl` field may be missing in some items (the `paymentType: 1` item has no title/text either).
- There is no payment/installment count detail here; installment data comes from `/api/v1/product/installment`.
