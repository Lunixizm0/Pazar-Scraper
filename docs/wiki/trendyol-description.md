# Product Description

Trendyol builds the product description from the internal **component-read** API rather than the DOM. The page JSON-LD `description` is only a short marketing sentence, so real description text is fetched per product.

## API

`get_product_descriptions_from_api(product_id)` (`src/scrape/utils/trendyol.py`):

```
GET https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/component-read/component/{product_id}
```

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `product_id` | number | Yes | The content/product id (e.g. `1081766367`). |
| `channelId` | number | No | The sales channel. Use `1` for web. |

Response wrapper: `{ "isSuccess", "result" }`. The description lives at `result.descriptions[]`, each entry a dict with a `text` field. The function joins all non-empty entries with spaces.

Sent through the standard API headers (`get_common_api_headers`), with a 20s timeout. Non-200 responses, failed parses, and empty result sets return `None`.

## The `[page=...]` marker syntax

Descriptions embed merchant/section markup:

``` text
Bu ürün [page="merchant_info"]Xiaomi Resmi Mağazası[/page] tarafından gönderilecektir. ...
```

- `[page="merchant_info"]<NAME>[/page]` - merchant display name inside a "Bu ürün ... tarafından gönderilecektir" intro sentence.
- These sentences are shipping/returns boilerplate (see below) and are dropped before the description is stored.

### Captured sample

Fixture: `component_read.json` - the **joined raw description string** (the function's return value, not the response wrapper). It starts:

``` text
Bu ürün [page="merchant_info"]Xiaomi Resmi Mağazası[/page] tarafından gönderilecektir.
Kampanya fiyatından satılmak üzere 10 adetten fazla stok sunulmuştur.
Bir ürün, birden fazla satıcı tarafından satılabilir. ...
```

and ends with the SEO keyword block:

``` text
... bluetooth kulaklık, kablosuz kulaklık, tws kulaklık, anc kulaklık, gürültü engelleme,
kulak içi kulaklık, mikrofonlu kulaklık, ... redmi buds 8 pro, şarjlı kulaklık, ...
```

## Cleaning pipeline

`_build_description(product_data)` (`src/scrape/utils/trendyol.py`) tries, in order:

1. **API text** - `get_product_descriptions_from_api(sku)` (sku = `product_data.sku`), cleaned via `_strip_sentences_before_marker`; accepted when `len > 10`. This is the preferred source.
2. **JSON-LD clean** - `_extract_description_clean(product_data)` (`:823`) applies the same sentence-strip to `product_data.description`.
3. **Attributes** - up to 10 `key: value` snippets from `_extract_attributes_dict`, prefixed with the product name when available (`"{name}. Features: {k1}: {v1}. {k2}: {v2}..."`).
4. **JSON-LD fallback** - the raw `product_data.description` string. Last resort.

### Sentence stripping

`_strip_sentences_before_marker(text)`:

1. Splits text on `(?<=[.!?])\s+` into sentences.
2. Drops any sentence that `_contains_boilerplate` (`:795`): matches one of the `_BOILERPLATE_MARKERS` (`:760`, e.g. `"tarafından gönderilecektir"`, `"kampanya fiyatından satılmak üzere"`, `"satış fiyatını satıcı belirlemektedir"`, `"birden fazla satıcı tarafından satılabilir"`, `"adet sipariş verilebilir"`, `"ücretsiz iade"`, `"15 gün içinde"`, `"stok sunulmuştur"`, ...) **or** contains a `[page` marker.
3. Strips any remaining `[page="..."]...[/page]` / `[page=...]` markup from otherwise-kept sentences.
4. Joins the kept sentences with spaces.

Thus the stored description is the bullet/feature text ("... uyumludur. • IP54 seviyesinde ... günlük kullanım için uygundur.") minus the merchant guarantees and the trailing keyword dump.

Placeholder guard `_is_placeholder_description_text` (used in step 1 of `_build_description`) skips empty/default texts; debug logs use the `ty.desc.*` prefix (`ok`/`skip`).

## Notes

- The API call is only made when `product_data.sku` exists; otherwise the pipeline falls straight to the JSON-LD/attribute fallbacks.
- The fixture stores the pre-strip raw text (as the API returns it), so the `expected` description for tests goes through `_strip_sentences_before_marker` before comparison.