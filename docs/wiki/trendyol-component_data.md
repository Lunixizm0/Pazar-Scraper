# Get Component Data

Retrieves component data for a specific product listing on the Trendyol storefront. Returns product description blocks, seller info, return policy, and promotional notices for a given product component to display on the product detail page.

## Endpoint

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/component-read/component/{componentId}
```

## Path Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `componentId` | number | Yes | The unique identifier of the product/component (e.g. `1081766367`). |

## Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `channelId` | number | Yes | The sales channel identifier. Use `1` for the web channel. |

## Request Headers

| Header | Description |
| --- | --- |
| `User-Agent` | Browser user-agent string to mimic a real browser request. |
| `Cookie` | Session/preference cookies (e.g. `platform`, `countryCode`, `language`). |
| `x-web-req-source` | Internal routing header identifying the request source (`StorefrontProductGateway`). |
| `x-agentname` | Internal agent name header (`StorefrontProductGateway`). |
| `Origin` | The origin of the request (`https://www.trendyol.com`). |

## Response

Returns a JSON object with the following fields:

- **`isSuccess`** - Boolean indicating whether the request was successful.

- **`statusCode`** - HTTP-style status code from the internal service.

- **`result`** - Object containing:
    - `descriptions` - An array of product description blocks, each with:
        - `text` - The description text content.

        - `priority` - Display priority order.

        - `viewType` - How the block is rendered: `inline`, `popover`, or `modal`.

        - `textComponents` _(optional)_ - Array of rich-text components for advanced rendering.

## Example

**Request:**

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/component-read/component/1081766367?channelId=1
```

**Response (excerpt):**

``` json
{
  "isSuccess": true,
  "statusCode": 200,
  "result": {
    "descriptions": [
      {
        "text": "Ürün açıklaması...",
        "priority": 1,
        "viewType": "inline"
      }
    ]
  }
}
```
