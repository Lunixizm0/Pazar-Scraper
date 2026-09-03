# Ask to Seller (Seller Question Status)

Returns which of the product's sellers can be asked questions and those sellers' ratings. It controls the visibility of the "Satıcıya Sor" (Ask the seller) button on the PDP.

## Endpoint

```
GET https://api-asktoseller.hepsiburada.com/api/v2.0/products/{sku}/merchants/accept-questions
```

`{sku}` - the product's SKU code (e.g. `HBCV0000EBN5K8`). It lives on a different host (`api-asktoseller.hepsiburada.com`).

## Request Headers

| Header | Value |
| --- | --- |
| `accept` | `application/json, text/plain, */*` |
| `referer` | the product page URL |
| `cookie` | `hbus_anonymousId` and Akamai cookies |

No auth header is required.

## Response

```json
{
  "merchants": [
    {
      "id": "9040f2fb-b962-4d99-bc4d-27626d64ad92",
      "name": "ELART",
      "rating": 9.6
    }
  ],
  "questionCount": 1
}
```

### Fields

| Field | Type | Example Value |
| --- | --- | --- |
| `merchants` | array | Sellers that can be asked questions |
| `merchants[].id` | string (UUID) | `9040f2fb-...` |
| `merchants[].name` | string | `ELART` |
| `merchants[].rating` | number | `9.6` (merchant rating) |
| `questionCount` | number | `1` (total number of questions) |

## Example

**Request:**
```
GET https://api-asktoseller.hepsiburada.com/api/v2.0/products/HBCV0000EBN5K8/merchants/accept-questions
```

**Response:**
```json
{
  "merchants": [
    { "id": "9040f2fb-b962-4d99-bc4d-27626d64ad92", "name": "ELART", "rating": 9.6 }
  ],
  "questionCount": 1
}
```

## Notes

- `merchants[].rating` (9.6) - the merchant's overall rating; it differs from the product's own rating (JSON-LD `aggregateRating.ratingValue` = 5).
- `questionCount` - the number of questions asked about the product so far.
- This endpoint also provides info such as the merchant rating (rating) that overlaps with the `ratingSummary.lifetimeRating` in `product/listings`.
