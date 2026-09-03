# Shipping Due Date (Shipping Delivery Date)

External service that returns the product's estimated shipping delivery date, the "ships tomorrow" info, the cargo company, and the delivery options. It feeds Hepsiburada's PDP block that shows when the cargo will reach you.

## Endpoint

```
POST https://shipping-external.hepsiburada.com/duedateapi/querymodel/withtext/v2
```

It lives on a different host (`shipping-external.hepsiburada.com`), not `www.hepsiburada.com`.

## Request Headers

| Header | Value |
| --- | --- |
| `accept` | `application/json, text/plain, */*` |
| `content-type` | `application/json` |
| `origin` | `https://www.hepsiburada.com` |
| `referer` | the product page URL |
| `cookie` | `hbus_anonymousId` and Akamai cookies |

## Request Body

```json
{
  "queryModels": [
    {
      "sku": "HBCV0000EBN5K8",
      "listingId": "0f6040d3-dda6-43af-bbf0-0eb838c800b2",
      "definitionName": "Pike Takımları",
      "warehouseId": "BIRINCIL",
      "shipmentDay": 1,
      "shippingProfileId": "5d8509ce-e834-4cfc-be1b-73c107e9f818",
      "deci": 1,
      "inStockDate": "",
      "tags": ["1200-300-home-kuponu", "..."],
      "isBuyBoxWinner": true,
      "quantity": 1,
      "merchantId": "9040f2fb-b962-4d99-bc4d-27626d64ad92",
      "merchantCity": "BURSA",
      "merchantCountry": "TÜRKİYE",
      "shipmentDaysPredictedByHb": 2,
      "customerId": "d0965061-6de7-4275-9138-7bbe5f942d90",
      "availableWarehouses": []
    }
  ],
  "customerId": "d0965061-6de7-4275-9138-7bbe5f942d90",
  "customerLocation": "",
  "customerCity": "",
  "customerTown": "",
  "customerTownCode": "",
  "customerDistrict": "",
  "customerDistrictCode": "",
  "anonymousId": "d0965061-6de7-4275-9138-7bbe5f942d90",
  "locationDeliveryUnavailableDays": [],
  "merchantSortingEnabled": true
}
```

Note: `queryModels` is an array; each element carries the shipping info of a listing. The `shippingProfileId`, `warehouseId`, `shipmentDay`, `merchantId`, `sku`, `listingId`, and `definitionName` values are taken from the `product/listings` API. `customerId`/`anonymousId` = `hbus_anonymousId`.

## Response

The top-level container is a JSON **array** (one element for a single listing):

| Field | Type | Example Value |
| --- | --- | --- |
| `dtDueDate` | string (ISO) | `2026-09-04T15:30:00.000Z` |
| `dueDate` | string | `/Date(1788535800000+0300)/` (milliseconds + tz) |
| `dueDateFormatted` | string | `04.09.2026` |
| `dueText` | string | `dakika içinde sipariş verirsen yarın kargoda` |
| `cutOffTime` | number | `18` |
| `checkoutDueText` | string | `Yarın Kargoda` |
| `checkoutDueText2` | string | `Yarın Kargoda` |
| `shipmentTimeText` | string | `<b>19 saat 13dk</b> içinde sipariş verirsen yarın kargoda` |
| `shipmentTimeAsDays` | number | `1` |
| `warehouseId` | string | `BIRINCIL` |
| `merchantId` | string (UUID) | `9040f2fb-...` |
| `listingId` | string (UUID) | `0f6040d3-...` |
| `isBuyBoxWinner` | boolean | `true` |
| `isFasterMerchant` | boolean | `false` |
| `isJetDelivery` | boolean | `false` |
| `isNextDayDelivery` | boolean | `false` |
| `cargoFirmId` | number | `27` |
| `checkoutOptionType` | string | `StandardDelivery` |
| `deliveryOptions` | array | Shipping delivery options (see below) |
| `additionalFields` | string (JSON) | ShipmentDays, EstimatedDelivery etc. meta info |

### each `deliveryOptions[]` item

| Field | Type | Example Value |
| --- | --- | --- |
| `optionName` / `rawOptionName` | string | `Yarın kargoda` |
| `text` | string | `<b>19 saat 13dk</b> içinde sipariş verirsen yarın kargoda` |
| `imageUrl` | string | Cargo company logo URL |
| `type` | string | `StandardDelivery` |
| `cargoFirmId` | number | `27` |
| `infoList` | array | `[]` |

There are also `deliveryOptionsMobile` and `deliveryOptionsMobileV2` (mobile variants); they have the same structure.

## Example (structural)

```json
[
  {
    "dtDueDate": "2026-09-04T15:30:00.000Z",
    "dueDateFormatted": "04.09.2026",
    "dueText": "dakika içinde sipariş verirsen yarın kargoda",
    "checkoutDueText": "Yarın Kargoda",
    "shipmentTimeText": "<b>19 saat 13dk</b> içinde sipariş verirsen yarın kargoda",
    "merchantId": "9040f2fb-b962-4d99-bc4d-27626d64ad92",
    "listingId": "0f6040d3-dda6-43af-bbf0-0eb838c800b2",
    "isBuyBoxWinner": true,
    "cargoFirmId": 27,
    "deliveryOptions": [
      {
        "optionName": "Yarın kargoda",
        "text": "<b>19 saat 13dk</b> içinde sipariş verirsen yarın kargoda",
        "imageUrl": "https://images.hepsiburada.net/shipping/assets/cargo-logo/27.png",
        "type": "StandardDelivery",
        "cargoFirmId": 27,
        "infoList": []
      }
    ]
  }
]
```

## Notes

- `dueDateFormatted` (e.g. `04.09.2026`) is the directly usable estimated delivery date.
- `cargoFirmId` identifies the cargo company; the logo is fetched from `https://images.hepsiburada.net/shipping/assets/cargo-logo/{id}.png`.
- `additionalFields` contains embedded meta data as a JSON string (`ShipmentDays`, `EstimatedDeliveryDays`, etc.).
- Since this endpoint is on a different host, there may be CORS/cookie restrictions; it works through the browser.
