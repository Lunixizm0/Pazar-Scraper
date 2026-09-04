# Product Description

Hepsiburada's description is extracted from the **DOM** (`div#ProductDescription` / `[class*='ProductDescription']`), not from the JSON-LD: the JSON-LD `description` is generic marketing boilerplate and is discarded. The stored description is the visible "Ürün Bilgileri" block text.

Captured from the live product:

``` text
Razer BlackShark V2 Pro 2023 Kablosuz Gaming Kulaklık, Beyaz RZ04-04530200-R3M1
```

(`https://www.hepsiburada.com/razer-blackshark-v2-pro-2023-kablosuz-gaming-kulaklik-beyaz-rz04-04530200-r3m1-p-HBCV00004MW5Q6`, sku `HBCV00004MW5Q6`.)

## DOM extraction

`_extract_description_from_dom(soup)` (`src/scrape/utils/hepsiburada.py`):

1. **Primary**: `div#ProductDescription`.
2. **Fallback**: any `[class*='ProductDescription']` element.
3. Among candidates, picks the text with the longest normalized (whitespace-collapsed) text, skipping:
   - empty text,
   - placeholder text (`_is_placeholder_description_text`),
   - generic marketing text (`_is_generic_hepsiburada_description`).

**Live-sample note:** the captured page does **not** contain `div#ProductDescription`. The match is a CSS-module-hashed class `div.ProductDescription_a2054006-c2a7-4b92-852c-cfaec56a6e2a` (which is why the subclass selector `[class*='ProductDescription']` exists). Its text is the product title line *including* the SKU/model suffix (`RZ04-04530200-R3M1`).

## Why the JSON-LD description is ignored

The JSON-LD `description` for this product is:

``` text
Razer BlackShark V2 Pro 2023 Kablosuz Gaming Kulaklık, Beyaz en iyi fiyatla Hepsiburada'dan satın alın!
Şimdi indirimli fiyatla sipariş verin, ayağınıza gelsin!
```

`_is_generic_hepsiburada_description` (`hepsiburada.py:234`) detects this family of phrases by normalizing text (alphanumeric only, lowercased) and checking markers such as:

- `eniyifiyatlahepsiburadadan`
- `eniyifiyatlahepsiburada`
- `ayağınızagelsin`
- `avantajlıfiyatlarla`
- `satinalabilirsiniz`

"en iyi fiyatla Hepsiburada'dan" normalizes to `eniyifiyatlahepsiburadan`, which matches, so the JSON-LD text is treated as boilerplate and only kept as a last resort (when no DOM text exists).

## Build order

`_build_description(soup, product_data)` (`hepsiburada.py:196`):

1. **DOM text** (`_extract_description_from_dom`), cleaned with `_strip_placeholder_tokens` (`:137`, removes trailing `STD`/`N/A`/`NONE`/`NA`/`NUL` tokens). If it is just the product `name` repeated plus nothing meaningful (`len(rest) <= 10` after stripping the name prefix), it is not used.
   - Here, the DOM title line is `name + " RZ04-04530200-R3M1"`; after stripping the name prefix the remaining `RZ04-04530200-R3M1` is > 10 chars, so the DOM text is kept, model code included.
2. **JSON-LD text** only if non-generic; if generic, only used when there is no DOM text.
3. **Attribute fallback** (`_extract_attribute_fallback_description`, `:169`): when both DOM and JSON-LD are unusable, builds `"{name}. key1: value1. key2: value2."` from non-meta JSON-LD fields (skipping `_META_FIELDS` such as `name`, `url`, `image`, `offers`, `@type`, `aggregateRating`, etc. and values already contained in the name).

## Notes

- Compare with Trendyol, whose description comes from the **component-read API** (with `[page=...]` marker stripping) because the DOM/JSON-LD gives only a one-line marketing sentence.
- The description here is short because the live product's "Ürün Bilgileri" section renders only the title line; longer products include bullet/paragraph text in the same block.
- Places a `desc.*` debug log (`desc.dom`, `desc.json_ld`, `desc.fallback`, `desc.ok`, `desc.none`).