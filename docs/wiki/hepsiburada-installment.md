# Installment (Installment / Credit Options)

Internal service that returns card/non-card installment options, the number of installments, and the installment amounts for a product amount. It is Hepsiburada's equivalent of the `installment` API in Trendyol.

## Endpoint

```
GET https://www.hepsiburada.com/api/v1/product/installment
```

## Query Parameters

| Parameter | Type | Example Value |
| --- | --- | --- |
| `maxInstallment` | number | `12` |
| `amount` | number | `94200` (in kuruş: 942.00 TL = 94200) |
| `definitionId` | string | `559` |
| `isFashion` | boolean | `false` |
| `consumerFinanceTag` | string | `` (empty) |
| `paymentTag` | string | Comma-separated tag list (the `paymentTag` value from the listings API) |
| `sku` | string | `HBCV0000EBN5K8` |
| `merchantId` | string (UUID) | `9040f2fb-b962-4d99-bc4d-27626d64ad92` |
| `taxRatio` | number | `10` |

Note: the `amount` value is **in kuruş** (94200 = 942.00 TL). The `paymentTag`, `sku`, `merchantId`, `definitionId`, and `taxRatio` values are taken from the `product/listings` API and the meta tags.

## Request Headers

| Header | Value |
| --- | --- |
| `accept` | `application/json, text/plain, */*` |
| `referer` | the product page URL |
| `cookie` | `hbus_anonymousId` and Akamai cookies |

No auth header is required.

## Response

Top-level container: `{ "statusCode": 200, "data": { "result": {...} }, "redirection": {...} }`.

### `result` fields

| Field | Type | Example Value |
| --- | --- | --- |
| `cardAmount` | number | `10295` (kuruş; 102.95 TL) |
| `cardInstallment` | number | `12` (credit card installment count) |
| `loanAmount` | number | `37272` (kuruş; 372.72 TL) |
| `loanInstallment` | number | `36` (shopping loan/debt installment count) |

## Example

**Request:**
```
GET https://www.hepsiburada.com/api/v1/product/installment?maxInstallment=12&amount=94200&definitionId=559&isFashion=false&consumerFinanceTag=&paymentTag=1200-300-home-kuponu,...&sku=HBCV0000EBN5K8&merchantId=9040f2fb-b962-4d99-bc4d-27626d64ad92&taxRatio=10
```

**Response:**
```json
{
  "statusCode": 200,
  "data": {
    "result": {
      "cardAmount": 10295,
      "cardInstallment": 12,
      "loanAmount": 37272,
      "loanInstallment": 36
    }
  }
}
```

## Notes

- The response is quite compact: it returns only 4 numeric fields.
- `cardAmount` - monthly card payment over 12 installments (102.95 TL). `cardInstallment` - card installment count.
- `loanAmount` - monthly loan payment over 36 installments (372.72 TL). `loanInstallment` - loan installment count.
- It is important to send the `amount` query in kuruş; if sent in TL, an incorrect result is returned.
- There is no bank-specific installment detail in this API; it only provides summary installment/loan information.
