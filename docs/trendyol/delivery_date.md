# Teslimat Tarihi ve Kargo Süresi

Retrieves the estimated delivery date range and cargo/shipping options for a specific product listing. The response lists one delivery entry per merchant/listing that sells the product, including delivery windows, cargo company, and fast-delivery flags.

## Endpoint

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/delivery-date-content/delivery-date/{contentId}/itemNumber/{itemNumber}
```

## Path Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `contentId` | number | Yes | The unique product identifier (e.g. `1081766367`). |
| `itemNumber` | number | Yes | The item number of the specific merchant listing (e.g. `1494882815`). |

## Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `winnerListingId` | string | Yes | The winning listing id (e.g. `e6e8fd8c3d61815b470afae19defb73a`). Typically the currently displayed merchant listing. |
| `channelId` | number | Yes | The sales channel identifier. Use `1` for the web channel. |

## Request Headers

Tested successfully with plain `requests` using the same header set as other storefront endpoints (see `review_read.md` for the full list). The `Cookie` must include `countryCode=TR`.

## Response

Top-level wrapper: `{ "isSuccess", "statusCode", "result" }`. The `result` object contains:

- **`deliveryTimeZone`** - string, e.g. `Europe/Istanbul`.

- **`deliveryDates`** - array of delivery entries, one per listing/merchant. Each entry has:
    - `deliveryStartDate` / `deliveryEndDate` - ISO-8601 delivery window (inclusive).
    - `cargoStartDate` - when the cargo company is expected to pick up.
    - `listingId` - the merchant listing id this entry belongs to.
    - `cargoCompanies` - array of cargo company names (empty on some products).
    - `sourceFastDeliveryOptions` / `fastDeliveryOptions` - array of `{ type, dailyCutoffHour }` (e.g. `TOMORROW_SHIPPING`).
    - `shipmentAddressId` - internal shipment address id.
    - `cargoRemainingDays` - days until cargo handoff.
    - `agreedDeliveryDays` - agreed deadline in days.
    - `rushDeliveryDuration` - rush delivery hours (e.g. `24`).
    - `campaignId` - campaign id this listing belongs to.
    - `isLocalDelivery` - whether local delivery is available.

## Example

**Request:**

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/delivery-date-content/delivery-date/1081766367/itemNumber/1494882815?winnerListingId=e6e8fd8c3d61815b470afae19defb73a&channelId=1
```

**Response (excerpt):**

``` json
{
  "isSuccess": true,
  "statusCode": 200,
  "result": {
    "deliveryTimeZone": "Europe/Istanbul",
    "deliveryDates": [
      {
        "deliveryStartDate": "2026-09-01T19:43:26",
        "deliveryEndDate": "2026-09-04T19:43:26",
        "cargoStartDate": "2026-09-01T23:59:00",
        "listingId": "e6e8fd8c3d61815b470afae19defb73a",
        "cargoCompanies": [],
        "fastDeliveryOptions": [{ "type": "TOMORROW_SHIPPING", "dailyCutoffHour": "00:00" }],
        "cargoRemainingDays": 1,
        "agreedDeliveryDays": 1,
        "rushDeliveryDuration": 24,
        "isLocalDelivery": true
      }
    ]
  }
}
```