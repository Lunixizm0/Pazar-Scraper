# Pazar-Scraper Documentation

Documentation for the internal (storefront) APIs that the Pazar-Scraper project discovers and consumes.

## Trendyol

- [Trendyol API Documentation](trendyol-README) - overview, base URL, common request headers, and the full endpoint list
- Exchange rates: [currencies](trendyol-currencies)
- Credit offers (Cloudflare protected): [kredi-teklifleri](trendyol-kredi_teklifleri)
- Variants: [slicing-attributes](trendyol-slicing_attributes)
- Product eligibility: [product-eligibility](trendyol-product_eligibility)
- JSON-LD structured data: [jsonld](trendyol-jsonld)
- Embedded state (`__envoy__SHARED_PROPS`): [shared-props](trendyol-shared_props)
- Product description (component-read API): [description](trendyol-description)

## Hepsiburada

- [Hepsiburada API Documentation](hepsiburada-README) - overview, base URL, common request headers, and the full endpoint list
- Product listings: [product-listings](hepsiburada-product_listings)
- Installment: [installment](hepsiburada-installment)
- Other merchants: [other-merchants](hepsiburada-other_merchants)
- Payment options: [payment-options](hepsiburada-payment_options)
- Shipping due date: [shipping-due-date](hepsiburada-shipping_due_date)
- Ask to seller: [ask-to-seller](hepsiburada-ask_to_seller)
- JSON-LD structured data: [jsonld](hepsiburada-jsonld)
- Embedded state (`script#reduxStore`): [redux-store](hepsiburada-redux_store)
- Product description (DOM): [description](hepsiburada-description)

## Shared

- Product dataset (output schema): [dataset-schema](dataset-schema)

### Note

- If you want to get the *.json files mentioned, you need to run `tests/fixtures/capture_fixtures.py`