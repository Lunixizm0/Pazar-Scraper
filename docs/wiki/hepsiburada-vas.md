# VAS (Value-Added Services / Insurance Suggestions)

Internal service that returns Hepsiburada's value-added service suggestions for a product (insurance, protection package, etc.). Optional add-ons such as accidental damage insurance or a protection package come from here.

> **Note:** Not every product has a VAS suggestion. Suggestions are only returned for eligible product categories/price ranges; for ineligible products `suggestedProducts` comes back empty (`[]`) and this field naturally stays empty (it is not a code error).

## Endpoint

```
POST https://customer-voltran-gw.hepsiburada.com/api/vas/evaluate
```

## Request Body

| Field | Type | Example Value |
| --- | --- | --- |
| `definationName` | string | `Kulaklık - Mikrofon` (product definition name) |
| `merchantName` | string | `EMC&BİLİSİM&TEKN` |
| `price` | number | `7890` (TL) |
| `rootCategories` | number[] | `[2147483646, 3013120, 18, 520, 60004548]` (int categories) |
| `sku` | string | `HBCV00004MW5Q6` |

## Request Headers

| Header | Value |
| --- | --- |
| `content-type` | `application/json;charset=utf-8` |
| `origin` | `https://www.hepsiburada.com` |
| `referer` | the product page URL (must not be the root path) |
| `user-agent` | Browser UA |

## Response

Top-level container fields:

| Field | Type | Description |
| --- | --- | --- |
| `vasTypeId` | number | VAS type (`5` = value-added service/insurance) |
| `title` | string | Suggestion group title (e.g. `Ek hizmet önerilerimiz`) |
| `title2` | string | Subtitle |
| `denyText` | string | Decline text (e.g. `Onarım hizmeti istemiyorum`) |
| `checkoutTypeCode` | number | Add-to-cart/checkout type code (`8`) |
| `staticPage` | string | Static explanation page URL |
| `suggestedProducts` | object[] | List of suggested value-added services |

### `suggestedProducts[]` fields

| Field | Type | Description |
| --- | --- | --- |
| `suggestedSku` | string | SKU of the product to be added |
| `title` | string | Service name (e.g. `Kazaen Zarar Sigortası`) |
| `subTitle` | string | Short description (e.g. `1 yıl geçerli kırılma, sıvı teması ve hırsızlık`) |
| `description` | string | Full description / policy coverage |
| `price` | number | Service fee (TL) |
| `brand` | string | Provider (e.g. `Hepsiburada`) |
| `listingId` | string | Listing id of the service product |
| `logo` | string | Image URL |
| `detailLink` / `staticPage` | string | Detail page URLs |
| `items_mobile` | object[] | "How does it work?" steps (`title`, `description`, `image`) |

## Example

**Request:**
```json
{
  "definationName": "Kulaklık - Mikrofon",
  "merchantName": "EMC&BİLİSİM&TEKN",
  "price": 7890,
  "rootCategories": [2147483646, 3013120, 18, 520, 60004548],
  "sku": "HBCV00004MW5Q6"
}
```

**Response:**
```json
{
  "vasTypeId": 5,
  "title": "Ek hizmet önerilerimiz",
  "title2": "Ürününüz için ek hizmet önerilerimiz",
  "denyText": "Onarım hizmeti istemiyorum",
  "checkoutTypeCode": 8,
  "staticPage": "https://www.hepsiburada.com/staticpage/51866692389872",
  "suggestedProducts": [
    {
      "vasTypeId": 5,
      "suggestedSku": "HBCV00003BI5EQ",
      "suggestedMerchantName": "",
      "logo": "https://images.hepsiburada.net/cac/content/images/vas/hb_koruma_paketi.png",
      "detailText": "Hepsiburada koruma paketi ile ilgili detaylı bilgi",
      "detailLink": "https://www.hepsiburada.com/staticPage/960255753068575",
      "overrideLink": false,
      "detailLinkMobile": "https://www.hepsiburada.com/staticPage/960255753068575",
      "description": "Kazaen Kırılma ve Hırsızlık Sigortası Poliçe başlangıç tarihinizden itibaren ...",
      "name_mobile": "Koruma Paketi",
      "title_mobile": "Hepsiburada Koruma Paketi",
      "description_mobile": "Kazaen Kırılma ve Hırsızlık Sigortası ...",
      "items_title_mobile": "Nasıl çalışır?",
      "items_mobile": [
        {
          "image": "https://images.hepsiburada.net/assets/storefront/vas/sepet_bottomsheet.png",
          "title": "SEPETİNİ OLUŞTUR",
          "description": "Seçtiğiniz ürünle birlikte sigorta paketini sepetinize ekleyin."
        },
        {
          "image": "https://images.hepsiburada.net/assets/storefront/vas/randevu_bottomsheet.png",
          "title": "KAYIT OL",
          "description": "Sigorta paketi ve eklediğiniz ürününüzün satın alım işlemini tamamlayın."
        },
        {
          "image": "https://images.hepsiburada.net/assets/storefront/vas/tamam_bottomsheet.png",
          "title": "İŞLEM TAMAM",
          "description": "Siparişiniz teslim edildikten sonra poliçeniz oluşturularak sizinle paylaşılacaktır. Cihazınızı güvenle kullanabilirsiniz."
        }
      ],
      "title": "Kazaen Zarar Sigortası",
      "subTitle": "1 yıl geçerli kırılma, sıvı teması ve hırsızlık",
      "orderType": null,
      "price": 1059.0,
      "listingId": "4a13e5b0-325c-47de-b369-93db616d327d",
      "brand": "Hepsiburada",
      "staticPage": "https://www.hepsiburada.com/staticpage/51866692389872"
    }
  ]
}
```

## Notes

- `price` is an integer/decimal value **in TL** (not kurus/cent).
- `rootCategories` is a list of **int** values taken from the product's category hierarchy (redux `rootCategoryList`, etc.).
- `definationName` ("defination" - Hepsiburada's spelling) is the product definition name; the scraped product's `definition_name` value is used.
- For products without a VAS suggestion (`suggestedProducts: []`) the field is omitted from the output, so the top-level `vas` field stays `null`.
