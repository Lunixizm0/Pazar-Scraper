# Taksit ve Kredi Teklifleri (Tahmini Ödemeler)

Retrieves the installment (taksit) payment options for a given product price from Trendyol's storefront consumer-lending service. Returns a summary (zero-interest installments, longest term) plus per-bank installment plans with term, interest rate, monthly payment, and total price.

Note: This is a preferred replacement for the external `coc-webview` endpoint documented in [`kredi_teklifleri.md`](trendyol-kredi_teklifleri). The `coc-webview` endpoint sits behind a strict Cloudflare wall (returns 403 for non-browser clients), whereas this storefront `installment` endpoint is reachable with plain `requests`.

## Endpoint

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/installment/
```

## Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `amount` | number | yes | The product price (e.g. `4199`). |
| `totalAmount` | number | NO | Total amount (usually equals `amount`). |
| `categoryId` | number | NO | Product category id (e.g. `1058`). |
| `categoryIds` | string | NO | Comma-separated category ids (e.g. `1058`). |
| `codEligible` | boolean | NO | Whether cash-on-delivery is eligible (e.g. `true`). |
| `clientPage` | string | NO | Client page context, e.g. `PDP`. |
| `isUserTyPlusActive` | boolean | NO | Whether the user has active Ty+ membership (e.g. `false`). |
| `groupTagIds` | string | No | Group tag id (UUID) of the product. |
| `channelId` | number | Yes | The sales channel identifier. Use `1` for the web channel. |

Most of these values are readily available from the product page itself (price, category id) or from other endpoints (groupTagIds can be parsed from Redux/SHARED_PROPS state).

## Request Headers

Tested successfully with plain `requests` (same header set as [`review_read.md`](trendyol-review_read)). May intermittently return `429` under burst rate limits; add a small delay between calls.

## Response

Top-level wrapper: `{ "isSuccess", "statusCode", "result" }`. The `result` object contains:

- **`summary`** - Object with:
    - `zeroInstallment` - `{ term, availableForTyPlus, bankDetails[] }` for 0% installment offers and which banks support them.
    - `maxInstallment` - `{ term, monthlyFee }` for the longest available term and its monthly fee.

- **`installmentOffers`** - Array, one entry per bank:
    - `issuerName` - bank name (e.g. `Garanti BBVA`).
    - `displayName` - combined name (e.g. `Garanti BBVA - BONUS`).
    - `installements` - array of plans, each with:
        - `term` - number of months.
        - `interestRate` - percentage (0 = interest-free).
        - `totalTermPrice` - monthly payment amount (TRY).
        - `totalPrice` - total amount paid over all terms (TRY).

## Example

**Request:**

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/installment/?amount=4199&totalAmount=4199&categoryId=1058&categoryIds=1058&codEligible=true&clientPage=PDP&isUserTyPlusActive=false&groupTagIds=eac211e6-2e86-42fa-a755-87479743934a&channelId=1
```

**Response (excerpt):**

``` json
{
  "isSuccess": true,
  "result": {
    "summary": {
      "zeroInstallment": { "term": 3, "availableForTyPlus": false, "bankDetails": ["Axess", "Bonus", "Maximum"] },
      "maxInstallment": { "term": 9, "monthlyFee": 571.2 }
    },
    "installmentOffers": [
      {
        "issuerName": "İş Bankası",
        "displayName": "İş Bankası - MAXIMUM",
        "installements": [
          { "term": 1, "interestRate": 0, "totalTermPrice": 4199, "totalPrice": 4199 },
          { "term": 3, "interestRate": 0, "totalTermPrice": 1399.67, "totalPrice": 4199 }
        ]
      }
    ]
  }
}
```