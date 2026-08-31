# Döviz Kurları (TCMB)

Retrieves the current and historical TCMB (Turkish Central Bank) exchange rates used across the Trendyol storefront for currency display/conversion.

## Endpoint

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/currencies
```

## Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `storefrontId` | number | Yes | e.g. `1`. |
| `culture` | string | Yes | e.g. `tr-TR`. |
| `channelId` | number | Yes | The sales channel identifier. Use `1` for the web channel. |

## Request Headers

Same header set as the other storefront endpoints (see `review_read.md`).

## Response

Top-level wrapper: `{ "isSuccess", "statusCode", "result" }`. The `result` is an array of currency entries, each with:

- **`currencyDate`** - ISO-8601 date of the rate (some entries are older than others).
- **`currencyName`** - ISO 4217 currency code (e.g. `EUR`, `TRY`, `USD`).
- **`tcmbRate`** - TCMB rate (value of one unit of that currency in TRY; `TRY` itself is `1`).

## Example

**Request:**

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/currencies?storefrontId=1&culture=tr-TR&channelId=1
```

**Response (excerpt):**

``` json
{
  "isSuccess": true,
  "statusCode": 200,
  "result": [
    { "currencyDate": "2026-08-28T00:00:00Z", "currencyName": "EUR", "tcmbRate": 55.9845 },
    { "currencyDate": "2025-08-05T00:00:00Z", "currencyName": "TRY", "tcmbRate": 1 },
    { "currencyDate": "2026-08-28T00:00:00Z", "currencyName": "USD", "tcmbRate": 48.0732 }
  ]
}
```