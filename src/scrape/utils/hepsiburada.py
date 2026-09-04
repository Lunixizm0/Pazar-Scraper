import json

import requests as _requests
from bs4 import BeautifulSoup

from scrape.dataset import ProductDataset
from scrape.debug import DebugRequests, debug, error, info, request_get, warn
from scrape.utils.trendyol import (
    _extract_first_string,
    _format_price_value,
    _is_placeholder_description_text,
    extract_price,
    parse_html,
)

requests = DebugRequests(_requests)


def get_raw_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:154.0) Gecko/20100101 Firefox/154.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US",
        "Accept-Encoding": "gzip, deflate",
        "Host": "www.hepsiburada.com",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }
    response = request_get(_requests, url, headers=headers, timeout=30)
    return response


def _iter_json_ld_payloads(soup):
    for script in soup.select("script[type='application/ld+json']"):
        script_text = script.string or ""
        if not script_text.strip():
            continue
        try:
            payload = json.loads(script_text)
        except (TypeError, json.JSONDecodeError):
            continue
        yield payload


def _extract_product_from_json_ld(payload):
    if not isinstance(payload, dict):
        return None

    if payload.get("@type") == "Product":
        return payload

    graph = payload.get("@graph")
    if isinstance(graph, list):
        for item in graph:
            if isinstance(item, dict) and item.get("@type") == "Product":
                return item

    return None


def extract_product_data(soup):
    if isinstance(soup, dict):
        return soup
    for payload in _iter_json_ld_payloads(soup):
        product = _extract_product_from_json_ld(payload)
        if product is not None:
            debug("product_data.found", source="json_ld", provider="hepsiburada")
            return product
    warn("product_data.missing", source="json_ld", provider="hepsiburada")
    return None


def _extract_redux_store(soup):
    if not isinstance(soup, BeautifulSoup):
        return None
    script = soup.select_one("script#reduxStore")
    if script is None:
        return None
    text = (script.string or "").strip()
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        store = json.loads(text[start : end + 1])
        debug("redux_store.found", provider="hepsiburada")
        return store
    except (TypeError, ValueError):
        warn("redux_store.invalid", provider="hepsiburada")
        return None


def _extract_description_from_dom(soup):
    if not isinstance(soup, BeautifulSoup):
        return None

    candidates = []

    product_desc = soup.select_one("div#ProductDescription")
    if product_desc is not None:
        candidates.append(product_desc)

    for element in soup.select("[class*='ProductDescription']"):
        if any(elem is element for elem in candidates):
            continue
        candidates.append(element)

    best = None
    for element in candidates:
        text = " ".join(element.get_text(" ", strip=True).split())
        if not text:
            continue
        if _is_placeholder_description_text(text):
            continue
        if _is_generic_hepsiburada_description(text):
            continue
        if best is None or len(text) > len(best):
            best = text

    return best


def _clean_description_text(value):
    if not value:
        return None
    cleaned = " ".join(str(value).split())
    return cleaned or None


def _strip_placeholder_tokens(text):
    import re

    cleaned = " ".join(str(text).split())
    cleaned = re.sub(
        r"\s+(?:STD|N/?A|NONE|NA|NUL)\s*$", "", cleaned, flags=re.IGNORECASE
    )
    return cleaned.strip()


_META_FIELDS = {
    "name",
    "url",
    "image",
    "offers",
    "brand",
    "description",
    "category",
    "@id",
    "@type",
    "@context",
    "aggregateRating",
    "review",
    "hasMerchantReturnPolicy",
    "merchantReturnPolicy",
    "shippingDetails",
    "mainEntityOfPage",
    "potentialAction",
    "additionalType",
}


def _extract_attribute_fallback_description(product_data):
    if not isinstance(product_data, dict):
        return None

    name = _extract_first_string(product_data.get("name")) or ""
    name_lower = name.lower()

    snippets = []
    for key, value in product_data.items():
        normalized_key = str(key).lower()
        if normalized_key in _META_FIELDS or normalized_key.startswith("@"):
            continue
        if isinstance(value, (dict, list, tuple, bool)) or value is None:
            continue
        text = _extract_first_string(value)
        if not text or _is_placeholder_description_text(text):
            continue
        if text.lower() in name_lower:
            continue
        snippets.append(f"{key}: {text}")

    if snippets:
        heading = f"{name}." if name else ""
        return f"{heading} {'. '.join(snippets)}.".strip()
    return None


def _build_description(soup, product_data):
    parts = []
    dom_description = _extract_description_from_dom(soup)
    dom_description = (
        _strip_placeholder_tokens(dom_description) if dom_description else None
    )

    name = _extract_first_string(product_data.get("name")) or ""
    if dom_description:
        rest = dom_description
        if name and rest.lower().startswith(name.lower()):
            rest = rest[len(name) :].strip()
        if rest and len(rest) > 10:
            parts.append(dom_description)

    json_ld_description = _extract_first_string(product_data.get("description"))
    if json_ld_description and not _is_placeholder_description_text(
        json_ld_description
    ):
        if _is_generic_hepsiburada_description(json_ld_description):
            if not dom_description:
                parts.append(json_ld_description)
        else:
            parts.append(json_ld_description)

    if not parts:
        fallback = _extract_attribute_fallback_description(product_data)
        if fallback:
            return fallback
        return None
    return " ".join(parts)


def _is_generic_hepsiburada_description(value):
    if not value:
        return False
    normalized = "".join(ch for ch in str(value) if ch.isalnum()).lower()
    markers = (
        "eniyifiyatlahepsiburadadan",
        "satinalabilirsiniz",
        "ayağınızagelsin",
        "eniyifiyatlahepsiburada",
        "avantajlıfiyatlarla",
    )
    return any(marker in normalized for marker in markers)


def _extract_redux_product(redux):
    if not isinstance(redux, dict):
        return None
    product_state = redux.get("productState")
    if not isinstance(product_state, dict):
        return None
    product = product_state.get("product")
    if not isinstance(product, dict):
        return None
    return product


def _extract_image(product_data):
    image = product_data.get("image")
    if isinstance(image, list):
        image = image[0] if image else None
    if isinstance(image, dict):
        image = image.get("url")
    if isinstance(image, str):
        return image.replace("{size}", "375")
    return None


def _detect_category(product_data, redux_product):
    if isinstance(redux_product, dict):
        categories = redux_product.get("categories")
        if isinstance(categories, list) and categories:
            last = categories[-1]
            name = (
                _extract_first_string(last.get("categoryName"))
                if isinstance(last, dict)
                else None
            )
            if name:
                return name
    category = product_data.get("category")
    if category:
        return category
    return "unknown"


def _extract_availability(product_data, redux_product):
    offers = product_data.get("offers")
    if isinstance(offers, dict) and offers.get("availability"):
        return offers.get("availability")
    if isinstance(redux_product, dict):
        if redux_product.get("isInStock"):
            return "https://schema.org/InStock"
        return "https://schema.org/OutOfStock"
    return None


def _extract_custom_data(product_data, redux_product):
    custom = {}

    if isinstance(redux_product, dict):
        merchant = redux_product.get("merchantName")
        if merchant:
            custom["merchant"] = merchant
        product_id = redux_product.get("productId")
        if product_id:
            custom["product_id"] = product_id

        categories = redux_product.get("categories")
        if isinstance(categories, list) and categories:
            names = [
                c.get("categoryName")
                for c in categories
                if isinstance(c, dict) and c.get("categoryName")
            ]
            if names:
                custom["category_path"] = names

        listings = redux_product.get("listings")
        if isinstance(listings, list) and listings:
            listing_data = []
            for listing in listings[:3]:
                if not isinstance(listing, dict):
                    continue
                entry = {}
                if listing.get("merchantName"):
                    entry["merchant"] = listing["merchantName"]
                price = listing.get("price")
                if price is None:
                    prices = listing.get("prices")
                    if isinstance(prices, list) and prices:
                        first = prices[0]
                        if isinstance(first, dict):
                            price = first.get("value")
                if price is None:
                    price = listing.get("unitPrice")
                if price is not None:
                    entry["price"] = price
                original_price = listing.get("originalPrice")
                if original_price is None:
                    original_price = listing.get("minimumPrice")
                if original_price is not None:
                    entry["original_price"] = original_price
                if entry:
                    listing_data.append(entry)
            if listing_data:
                custom["listings"] = listing_data

        reviews = redux_product.get("reviews")
        if isinstance(reviews, dict):
            review_data = {}
            if reviews.get("customerReviewScore") is not None:
                review_data["score"] = reviews["customerReviewScore"]
            if reviews.get("customerReviewCount") is not None:
                review_data["count"] = reviews["customerReviewCount"]
            if review_data:
                custom["reviews"] = review_data

    return custom


DEFAULT_ANONYMOUS_ID = "d0965061-6de7-4275-9138-7bbe5f942d90" #i get ts from incognito. probably will expire. tryna fix it soon.
_HEPB_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:152.0) Gecko/20100101 Firefox/152.0"


def _goto_referer(product_url):
    return product_url if product_url else "https://www.hepsiburada.com"


def _to_int_list(values):
    out = []
    for v in values or []:
        try:
            out.append(int(v))
        except (TypeError, ValueError):
            pass
    return out


def _api_headers(product_url=None, is_post=False):
    headers = {
        "User-Agent": _HEPB_UA,
        "Accept": "application/json, text/plain, */*",
        "Referer": _goto_referer(product_url),
    }
    if is_post:
        headers["Content-Type"] = "application/json"
        headers["Origin"] = "https://www.hepsiburada.com"
    return headers


def _extract_product_ctx(soup, product_data):
    ctx = {}

    if isinstance(product_data, dict):
        ctx["sku"] = product_data.get("sku")
        offers = product_data.get("offers")
        if isinstance(offers, dict):
            ctx["url"] = offers.get("url")

    if isinstance(soup, BeautifulSoup):
        script = soup.select_one("script#reduxStore")
        text = (script.string or "").strip() if script is not None else ""
        if text:
            try:
                store = json.loads(text[text.find("{") : text.rfind("}") + 1])
            except (TypeError, ValueError, json.JSONDecodeError):
                store = None
            if isinstance(store, dict):
                product_state = store.get("productState")
                if isinstance(product_state, dict):
                    product = product_state.get("product")
                    if isinstance(product, dict):
                        if ctx.get("sku") is None:
                            ctx["sku"] = product.get("sku")
                        if ctx.get("url") is None:
                            ctx["url"] = product.get("url")
                        if ctx.get("url") is None and product.get("slugName"):
                            _sku = ctx.get("sku") or product.get("sku")
                            if _sku:
                                ctx["url"] = (
                                    "https://www.hepsiburada.com/"
                                    f'{product.get("slugName")}-p-{_sku}'
                                )
                        if ctx.get("product_id") is None:
                            ctx["product_id"] = product.get("productId")
                        if ctx.get("definition_id") is None:
                            ctx["definition_id"] = product.get("definitionId")
                        if ctx.get("definition_name") is None:
                            ctx["definition_name"] = product.get("definitionName")
                        if ctx.get("tax_vat_rate") is None:
                            ctx["tax_vat_rate"] = product.get("taxVatRate")
                        listings = product.get("listings")
                        if isinstance(listings, list) and listings:
                            first = listings[0]
                            if isinstance(first, dict):
                                if ctx.get("merchant_id") is None:
                                    ctx["merchant_id"] = first.get("merchantId")
                                if ctx.get("listing_id") is None:
                                    ctx["listing_id"] = first.get("listingId")
                                if ctx.get("merchant_name") is None:
                                    ctx["merchant_name"] = first.get("merchantName")
                                if ctx.get("warehouse_id") is None:
                                    ctx["warehouse_id"] = first.get("warehouseId")
                                if ctx.get("shipment_day") is None:
                                    ctx["shipment_day"] = first.get("shipmentDay")
                                if ctx.get("shipping_profile_id") is None:
                                    ctx["shipping_profile_id"] = first.get(
                                        "shippingProfileId"
                                    )
                                if ctx.get("merchant_city") is None:
                                    ctx["merchant_city"] = first.get("merchantCity")
                                if ctx.get("merchant_country") is None:
                                    ctx["merchant_country"] = first.get(
                                        "merchantCountry"
                                    )
                        # categories from redux product
                        if not ctx.get("root_category_list"):
                            categories = product.get("categories")
                            if isinstance(categories, list) and categories:
                                ids = [
                                    c.get("categoryId")
                                    for c in categories
                                    if isinstance(c, dict) and c.get("categoryId")
                                ]
                                if ids:
                                    ctx["root_category_list"] = ids
                                    ctx["root_buying_category_list"] = [ids[-1]]

        # backfill from raw HTML regardless of redux presence
        html = str(soup)
        try:
            import re
            if ctx.get("definition_id") is None:
                md = re.search(r'"definitionId":(\d+)', html)
                if md:
                    ctx["definition_id"] = int(md.group(1))
            if ctx.get("definition_name") is None:
                mn = re.search(r'"definitionName":"([^"]+)"', html)
                if mn:
                    ctx["definition_name"] = mn.group(1)
            if ctx.get("tax_vat_rate") is None:
                mt = re.search(r'"taxVatRate":(\d+)', html)
                if mt:
                    ctx["tax_vat_rate"] = int(mt.group(1))
            if ctx.get("product_id") is None:
                mp = re.search(r'"productId":"([^"]+)"', html)
                if mp:
                    ctx["product_id"] = mp.group(1)
            if not ctx.get("root_category_list"):
                mr = re.search(r'"rootCategoryList":(\[.*?\])', html)
                if mr:
                    ids = [
                        int(x)
                        for x in re.findall(r'categoryId":"(\d+)"', mr.group(1))
                        if int(x) != 0
                    ]
                    if ids:
                        ctx["root_category_list"] = ids
                        ctx["root_buying_category_list"] = [ids[-1]]
        except Exception:
            pass

    if ctx.get("sku") is None and isinstance(product_data, dict):
        ctx["sku"] = product_data.get("sku")

    return ctx


class _HepbAPIContext:
    def __init__(self, soup=None, product_data=None, anonymous_id=DEFAULT_ANONYMOUS_ID, product_url=None):
        self.ctx = _extract_product_ctx(soup, product_data)
        self.soup = soup
        self.product_data = product_data or {}
        self.anonymous_id = anonymous_id
        self.product_url = (
            product_url
            or self.ctx.get("url")
            or (
                f'https://www.hepsiburada.com/-p-{self.ctx["sku"]}'
                if self.ctx.get("sku")
                else "https://www.hepsiburada.com"
            )
        )
        if not self.ctx.get("sku") and isinstance(product_data, dict):
            self.ctx["sku"] = product_data.get("sku")


def get_listings_from_api(sku, product_url=None):
    ctx = _HepbAPIContext(product_data={"sku": sku}, product_url=product_url)
    url = f"https://www.hepsiburada.com/api/v1/product/listings/{sku}"
    resp = requests.get(url, headers=_api_headers(ctx.product_url), timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    data = payload.get("data") if isinstance(payload, dict) else None
    listings = data.get("listings") if isinstance(data, dict) else None
    if isinstance(listings, list):
        filtered = []
        for listing in listings:
            if not isinstance(listing, dict):
                filtered.append(listing)
                continue
            item = dict(listing)
            item.pop("pbs", None)
            filtered.append(item)
        listings = filtered
    return listings


def get_installment_from_api(
    sku,
    amount=None,
    definition_id=None,
    tax_ratio=None,
    merchant_id=None,
    is_fashion="false",
    product_url=None,
):
    params = {
        "maxInstallment": 12,
        "amount": str(amount or 0),
        "definitionId": str(definition_id or ""),
        "isFashion": str(is_fashion or "false"),
        "consumerFinanceTag": "",
        "paymentTag": "",
        "sku": sku,
        "merchantId": str(merchant_id or ""),
        "taxRatio": str(tax_ratio or ""),
    }
    resp = requests.get(
        "https://www.hepsiburada.com/api/v1/product/installment",
        params=params,
        headers=_api_headers(product_url),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _merge_product_meta(ctx, product_tags=None, **overrides):
    root_category_list = ctx.ctx.get("root_category_list") or []
    root_buying_category_list = ctx.ctx.get("root_buying_category_list") or []

    body = {
        "userId": ctx.anonymous_id,
        "product": {
            "productTags": product_tags if product_tags is not None else [],
            "sku": ctx.ctx.get("sku"),
            "productId": ctx.ctx.get("product_id"),
            "brand": ctx.ctx.get("merchant_name"),
            "merchantId": ctx.ctx.get("merchant_id"),
            "listingId": ctx.ctx.get("listing_id"),
            "rootCategoryList": _to_int_list(root_category_list),
            "rootBuyingCategoryList": _to_int_list(root_buying_category_list),
            "definitionName": ctx.ctx.get("definition_name"),
            "definitionId": str(ctx.ctx.get("definition_id") or ""),
            "taxVatRate": ctx.ctx.get("tax_vat_rate"),
            "campaignIds": [],
        },
    }
    if overrides:
        for key, value in overrides.items():
            if value is not None:
                body["product"][key] = value
    return body


def get_without_affordability_from_api(
    sku,
    product_tags,
    product_url=None,
    anonymous_id=DEFAULT_ANONYMOUS_ID,
    product_data=None,
    soup=None,
    ctx_dict=None,
    **overrides,
):
    ctx = _HepbAPIContext(
        soup=soup,
        product_data={"sku": sku},
        product_url=product_url,
        anonymous_id=anonymous_id,
    )
    if isinstance(ctx_dict, dict):
        ctx.ctx.update(ctx_dict)
    body = _merge_product_meta(ctx, product_tags=product_tags, **overrides)
    body["affordabilityRequest"] = {
        "product": None,
        "additionalData": None,
        "definitionId": str(ctx.ctx.get("definition_id") or ""),
    }
    headers = _api_headers(ctx.product_url, is_post=True)
    headers.update(
        {
            "x-gotham_is_include_premium_clubs": "true",
            "x-gotham_is_include_payment_campaigns": "true",
            "x-gotham_is_enabled_next_eligible_campaign": "true",
            "x-gotham_is_enabled_evaluate_coupon": "true",
            "x-gotham_app-key": "All",
        }
    )
    resp = requests.post(
        "https://www.hepsiburada.com/api/v1/withoutAffordability",
        headers=headers,
        data=json.dumps(body),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_vas_from_api(
    sku,
    product_url=None,
    product_data=None,
    soup=None,
    ctx_dict=None,
    **overrides,
):
    ctx = _HepbAPIContext(
        soup=soup,
        product_data={"sku": sku},
        product_url=product_url,
    )
    if isinstance(ctx_dict, dict):
        ctx.ctx.update(ctx_dict)
    definition_name = (
        ctx.ctx.get("definition_name")
        or ctx.ctx.get("name")
        or (
            product_data.get("name")
            if isinstance(product_data, dict)
            else None
        )
    )
    root_categories = _to_int_list(ctx.ctx.get("root_category_list"))
    price = ctx.ctx.get("price")
    if price is None and isinstance(product_data, dict):
        offers = product_data.get("offers")
        if isinstance(offers, dict):
            price = offers.get("price")
    body = {
        "definationName": definition_name or "",
        "merchantName": ctx.ctx.get("merchant_name") or "",
        "price": price,
        "rootCategories": root_categories,
        "sku": sku,
    }
    if overrides:
        for key, value in overrides.items():
            if value is not None:
                body[key] = value
    resp = requests.post(
        "https://customer-voltran-gw.hepsiburada.com/api/vas/evaluate",
        headers=_api_headers(ctx.product_url, is_post=True),
        data=json.dumps(body),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_payment_options_from_api(
    sku,
    product_url=None,
    anonymous_id=DEFAULT_ANONYMOUS_ID,
    definition_id=None,
    **overrides,
):
    body = {
        "userId": anonymous_id,
        "affordabilityRequest": {
            "product": None,
            "additionalData": None,
            "definitionId": str(definition_id or ""),
        },
    }
    if overrides:
        body["userId"] = anonymous_id
        for key, value in overrides.items():
            if value is not None:
                body[key] = value
    headers = _api_headers(product_url, is_post=True)
    headers.update(
        {
            "x-gotham_is_include_premium_clubs": "true",
            "x-gotham_is_include_payment_campaigns": "true",
            "x-gotham_is_enabled_next_eligible_campaign": "true",
            "x-gotham_is_enabled_evaluate_coupon": "true",
            "x-gotham_app-key": "All",
        }
    )
    resp = requests.post(
        "https://www.hepsiburada.com/api/v1/paymentOptions",
        headers=headers,
        data=json.dumps(body),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_other_merchants_from_api(
    sku,
    product_tags,
    product_url=None,
    anonymous_id=DEFAULT_ANONYMOUS_ID,
    merchant_id=None,
    merchant_name=None,
    listing_id=None,
    final_price_on_sale=None,
    minimum_price=None,
    product_data=None,
    soup=None,
    ctx_dict=None,
    **overrides,
):
    ctx = _HepbAPIContext(
        soup=soup,
        product_data={"sku": sku},
        product_url=product_url,
        anonymous_id=anonymous_id,
    )
    if isinstance(ctx_dict, dict):
        ctx.ctx.update(ctx_dict)
    body = _merge_product_meta(ctx, product_tags=product_tags)
    body["product"]["otherMerchants"] = [
        {
            "productTags": product_tags if product_tags is not None else [],
            "campaignIds": [],
            "finalPriceOnSale": final_price_on_sale or 0,
            "minimumPriceForNLastDays": minimum_price or 0,
            "merchantId": merchant_id or ctx.ctx.get("merchant_id"),
            "merchantName": merchant_name or ctx.ctx.get("merchant_name"),
            "listingId": listing_id or ctx.ctx.get("listing_id"),
        }
    ]
    if overrides:
        for key, value in overrides.items():
            if value is not None:
                body[key] = value
    resp = requests.post(
        "https://www.hepsiburada.com/api/v1/otherMerchants",
        headers=_api_headers(ctx.product_url, is_post=True),
        data=json.dumps(body),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_shipping_due_date_from_api(
    ctx,
    product_url=None,
    anonymous_id=DEFAULT_ANONYMOUS_ID,
):
    sku = ctx.ctx.get("sku")
    listing = ctx.ctx.get("_listing") or {}
    query_model = {
        "sku": sku,
        "listingId": listing.get("listingId") or ctx.ctx.get("listing_id"),
        "definitionName": ctx.ctx.get("definition_name"),
        "warehouseId": listing.get("warehouseId") or ctx.ctx.get("warehouse_id"),
        "shipmentDay": listing.get("shipmentDay") or ctx.ctx.get("shipment_day"),
        "shippingProfileId": listing.get("shippingProfileId")
        or ctx.ctx.get("shipping_profile_id"),
        "deci": 1,
        "inStockDate": "",
        "tags": ctx.ctx.get("product_tags") or [],
        "isBuyBoxWinner": True,
        "quantity": 1,
        "merchantId": listing.get("merchantId") or ctx.ctx.get("merchant_id"),
        "merchantCity": listing.get("merchantCity") or ctx.ctx.get("merchant_city"),
        "merchantCountry": listing.get("merchantCountry")
        or ctx.ctx.get("merchant_country"),
        "shipmentDaysPredictedByHb": 2,
        "customerId": anonymous_id,
        "availableWarehouses": [],
    }
    body = {
        "queryModels": [query_model],
        "customerId": anonymous_id,
        "customerLocation": "",
        "customerCity": "",
        "customerTown": "",
        "customerTownCode": "",
        "customerDistrict": "",
        "customerDistrictCode": "",
        "anonymousId": anonymous_id,
        "locationDeliveryUnavailableDays": [],
        "merchantSortingEnabled": True,
    }
    resp = requests.post(
        "https://shipping-external.hepsiburada.com/duedateapi/querymodel/withtext/v2",
        headers=_api_headers(product_url or ctx.product_url, is_post=True),
        data=json.dumps(body),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_ask_to_seller_from_api(sku, product_url=None):
    ctx = _HepbAPIContext(product_data={"sku": sku}, product_url=product_url)
    resp = requests.get(
        f"https://api-asktoseller.hepsiburada.com/api/v2.0/products/{sku}/merchants/accept-questions",
        headers=_api_headers(ctx.product_url),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _safe_api_call(fn, *args, **kwargs):
    api_name = getattr(fn, "__name__", str(fn))
    info("api.builder.start", builder=api_name)
    try:
        result = fn(*args, **kwargs)
        info("api.builder.complete", builder=api_name, available=result is not None)
        return result
    except Exception as e:
        error("api.builder.error", builder=api_name, error=f"{type(e).__name__}: {e}")
        return None


def _is_hepb_response_dict(data):
    return isinstance(data, dict) and data.get("statusCode") == 200


def _listing_price_value(listing, key):
    if isinstance(listing, dict):
        v = listing.get(key)
        if isinstance(v, dict):
            return v.get("value")
        return v
    return None


def _kurus_amount(value):
    try:
        return int(round(float(value) * 100))
    except (TypeError, ValueError):
        return 0


def _build_pricing(pricing_data, promo_data):
    if not isinstance(pricing_data, dict):
        return None
    out = {}
    if pricing_data.get("rawPrice") is not None:
        out["original_price"] = pricing_data["rawPrice"]
    if pricing_data.get("discountedPrice") is not None:
        out["price"] = pricing_data["discountedPrice"]
    if pricing_data.get("priceText"):
        out["price_text"] = pricing_data["priceText"]
    if not out and pricing_data.get("price") is not None:
        out["price"] = pricing_data["price"]
    if isinstance(promo_data, dict) and promo_data.get("price"):
        promo = promo_data["price"]
        if isinstance(promo, dict):
            if promo.get("price") is not None:
                out["price"] = promo["price"]
            if promo.get("discountedPrice") is not None:
                out["price"] = promo["discountedPrice"]
    return out if out else None


def _build_discount_rate(discount_data):
    if not isinstance(discount_data, dict):
        return None
    out = {}
    if discount_data.get("discountRate") is not None:
        out["rate"] = discount_data["discountRate"]
    if discount_data.get("text"):
        out["text"] = discount_data["text"]
    if discount_data.get("type"):
        out["type"] = discount_data["type"]
    return out if out else None


def _build_installment_offer(data):
    if not _is_hepb_response_dict(data):
        return None
    detail = data.get("data", {}).get("instalmentDetail") if isinstance(data.get("data"), dict) else None
    if not isinstance(detail, dict):
        return None
    out = {}
    for key, label in (
        ("cardAmount", "card_amount"),
        ("cardInstallment", "card_installment"),
        ("loanAmount", "loan_amount"),
        ("loanInstallment", "loan_installment"),
    ):
        if detail.get(key) is not None:
            out[label] = detail[key]
    return out if out else None


def _build_ask_to_seller(data):
    if not isinstance(data, dict):
        return None
    out = {}
    if data.get("questionCount") is not None:
        out["question_count"] = data["questionCount"]
    merchants = data.get("merchants")
    if isinstance(merchants, list) and merchants:
        entries = []
        for m in merchants:
            if not isinstance(m, dict):
                continue
            entry = {}
            if m.get("name"):
                entry["merchant"] = m["name"]
            if m.get("rating") is not None:
                entry["rating"] = m["rating"]
            if entry:
                entries.append(entry)
        if entries:
            out["merchants"] = entries
    return out if out else None


def _build_shipping(data):
    if not isinstance(data, list) or not data:
        return None
    first = data[0]
    if not isinstance(first, dict):
        return None
    out = {}
    for key, label in (
        ("dueDateFormatted", "due_date"),
        ("dueText", "due_text"),
        ("checkoutDueText", "checkout_due_text"),
        ("shipmentTimeText", "shipment_time_text"),
        ("cargoFirmId", "cargo_firm_id"),
        ("cutOffTime", "cut_off_time"),
    ):
        if first.get(key) is not None:
            out[label] = first[key]
    delivery_options = first.get("deliveryOptions")
    if isinstance(delivery_options, list) and delivery_options:
        opts = []
        for d in delivery_options:
            if not isinstance(d, dict):
                continue
            entry = {}
            if d.get("optionName"):
                entry["name"] = d["optionName"]
            if d.get("text"):
                entry["text"] = d["text"]
            if d.get("type"):
                entry["type"] = d["type"]
            if d.get("cargoFirmId") is not None:
                entry["cargo_firm_id"] = d["cargoFirmId"]
            if d.get("imageUrl"):
                entry["image_url"] = d["imageUrl"]
            if entry:
                opts.append(entry)
        if opts:
            out["delivery_options"] = opts
    return out if out else None


def _build_without_affordability(data):
    if not _is_hepb_response_dict(data):
        return None
    result = data.get("data", {}).get("result") if isinstance(data.get("data"), dict) else None
    product = result.get("product") if isinstance(result, dict) else None
    if not isinstance(product, dict):
        return None
    out = {}
    price = _build_pricing(product.get("priceData"), product.get("promoData"))
    if price:
        out["price"] = price
    rate = _build_discount_rate(product.get("discountRateData"))
    if rate:
        out["discount_rate"] = rate
    promo_data = product.get("promoData")
    if isinstance(promo_data, dict) and isinstance(promo_data.get("data"), dict):
        campaign_data = promo_data["data"]
        campaigns = campaign_data.get("campaigns")
        if isinstance(campaigns, dict):
            tab = campaigns.get("campaignTabDetailList")
            if isinstance(tab, dict):
                for section_name, label in (
                    ("freeShippingCampaignList", "free_shipping_campaigns"),
                    ("specialCampaignList", "special_campaigns"),
                    ("couponCampaignList", "coupon_campaigns"),
                ):
                    section = tab.get(section_name)
                    if isinstance(section, list) and section:
                        entries = []
                        for item in section:
                            if not isinstance(item, dict):
                                continue
                            entry = {}
                            if item.get("name"):
                                entry["name"] = item["name"]
                            if item.get("conditionAmount") is not None:
                                entry["condition_amount"] = item["conditionAmount"]
                            if item.get("endDateTime"):
                                entry["end_date"] = item["endDateTime"]
                            if entry:
                                entries.append(entry)
                        if entries:
                            out.setdefault("campaigns", {})[label] = entries
    return out if out else None


def _build_payment_options(data):
    if not _is_hepb_response_dict(data):
        return None
    result = data.get("data", {}).get("result") if isinstance(data.get("data"), dict) else None
    product = result.get("product") if isinstance(result, dict) else None
    if not isinstance(product, dict):
        return None
    options = product.get("paymentOptions")
    if not isinstance(options, list) or not options:
        return None
    entries = []
    for opt in options:
        if not isinstance(opt, dict):
            continue
        entry = {}
        if opt.get("title"):
            entry["title"] = opt["title"]
        if opt.get("text"):
            entry["text"] = opt["text"]
        if opt.get("paymentType") is not None:
            entry["payment_type"] = opt["paymentType"]
        if opt.get("isCashPrice") is not None:
            entry["is_cash_price"] = opt["isCashPrice"]
        if opt.get("iconUrl"):
            entry["icon_url"] = opt["iconUrl"]
        if entry:
            entries.append(entry)
    return entries if entries else None


def _build_other_merchants(data):
    if not _is_hepb_response_dict(data):
        return None
    result = data.get("data", {}).get("result") if isinstance(data.get("data"), dict) else None
    products = result.get("products") if isinstance(result, dict) else None
    merchants = products.get("otherMerchants") if isinstance(products, dict) else None
    if not isinstance(merchants, list) or not merchants:
        return None
    entries = []
    for m in merchants:
        if not isinstance(m, dict):
            continue
        entry = {}
        if m.get("merchantName"):
            entry["merchant"] = m["merchantName"]
        if m.get("merchantId"):
            entry["merchant_id"] = m["merchantId"]
        price = _build_pricing(m.get("priceData"), m.get("promoData"))
        if price:
            entry["price"] = price
        if m.get("couponCount") is not None:
            entry["coupon_count"] = m["couponCount"]
        campaigns = m.get("campaigns")
        if isinstance(campaigns, list) and campaigns:
            texts = [
                c.get("text")
                for c in campaigns
                if isinstance(c, dict) and c.get("text")
            ]
            if texts:
                entry["campaigns"] = texts
        if entry:
            entries.append(entry)
    return entries if entries else None


def _build_vas(data):
    if not isinstance(data, dict):
        return None
    suggested = data.get("suggestedProducts")
    if not isinstance(suggested, list) or not suggested:
        return None
    entries = []
    for s in suggested:
        if not isinstance(s, dict):
            continue
        entry = {}
        if s.get("suggestedSku"):
            entry["suggested_sku"] = s["suggestedSku"]
        if s.get("title"):
            entry["title"] = s["title"]
        if s.get("subTitle"):
            entry["sub_title"] = s["subTitle"]
        if s.get("description"):
            entry["description"] = s["description"]
        if s.get("name_mobile"):
            entry["name_mobile"] = s["name_mobile"]
        if s.get("price") is not None:
            entry["price"] = s["price"]
        if s.get("brand"):
            entry["brand"] = s["brand"]
        if s.get("listingId"):
            entry["listing_id"] = s["listingId"]
        if s.get("logo"):
            entry["logo"] = s["logo"]
        if s.get("detailLink"):
            entry["detail_link"] = s["detailLink"]
        if s.get("staticPage"):
            entry["static_page"] = s["staticPage"]
        items = s.get("items_mobile")
        if isinstance(items, list) and items:
            item_entries = []
            for item in items:
                if not isinstance(item, dict):
                    continue
                ie = {}
                if item.get("title"):
                    ie["title"] = item["title"]
                if item.get("description"):
                    ie["description"] = item["description"]
                if item.get("image"):
                    ie["image"] = item["image"]
                if ie:
                    item_entries.append(ie)
            if item_entries:
                entry["items"] = item_entries
        if entry:
            entries.append(entry)
    return entries if entries else None


def build_product_dataset(
    product_data, category="unknown", custom_data=None, soup=None
):
    if not isinstance(product_data, dict):
        warn("dataset.skipped", provider="hepsiburada", reason="product_data_missing")
        return None

    redux = _extract_redux_store(soup) if soup is not None else None
    redux_product = _extract_redux_product(redux)
    debug("dataset.build.start", provider="hepsiburada", redux_product_found=redux_product is not None)

    offers = product_data.get("offers")
    if not isinstance(offers, dict):
        offers = {}

    brand = product_data.get("brand")
    if isinstance(brand, dict):
        brand_name = brand.get("name")
    else:
        brand_name = brand

    custom_data = _extract_custom_data(product_data, redux_product)

    sku = product_data.get("sku")
    merchant_id = None
    listing_id = None
    product_tags = []
    merchant_name = None
    listing = {}
    if isinstance(redux_product, dict):
        listings = redux_product.get("listings")
        if isinstance(listings, list) and listings:
            listing = listings[0] if isinstance(listings[0], dict) else {}
        if not listing and isinstance(redux_product.get("listings"), list):
            listing = {}
        merchant_id = listing.get("merchantId")
        listing_id = listing.get("listingId")
        merchant_name = listing.get("merchantName")
        product_id = listing.get("productId") or redux_product.get("productId")
        payment_tag = listing.get("paymentTag")
        if isinstance(payment_tag, str) and payment_tag:
            product_tags = [t.strip() for t in payment_tag.split(",") if t.strip()]
        if not product_tags:
            tag_list = listing.get("tagList")
            if isinstance(tag_list, list):
                product_tags = [
                    t.get("tagId")
                    for t in tag_list
                    if isinstance(t, dict) and t.get("tagId")
                ]

    if sku is None:
        sku = (redux_product or {}).get("sku")

    api_data = {}

    if sku:
        listings = _safe_api_call(get_listings_from_api, sku)
        if isinstance(listings, list) and listings:
            first_listing = listings[0]
            listing = first_listing if isinstance(first_listing, dict) else {}
            if isinstance(first_listing, dict):
                if merchant_id is None:
                    merchant_id = first_listing.get("merchantId")
                if listing_id is None:
                    listing_id = first_listing.get("listingId")
                if merchant_name is None:
                    merchant_name = first_listing.get("merchantName")
                if not product_tags:
                    payment_tag = first_listing.get("paymentTag")
                    if isinstance(payment_tag, str) and payment_tag:
                        product_tags = [
                            t.strip()
                            for t in payment_tag.split(",")
                            if t.strip()
                        ]
                    if not product_tags:
                        tag_list = first_listing.get("tagList")
                        if isinstance(tag_list, list):
                            product_tags = [
                                t.get("tagId")
                                for t in tag_list
                                if isinstance(t, dict) and t.get("tagId")
                            ]
            api_data["listings"] = listings

    api_ctx = _HepbAPIContext(soup=soup, product_data=product_data)
    api_ctx.ctx["merchant_id"] = api_ctx.ctx.get("merchant_id") or merchant_id
    api_ctx.ctx["listing_id"] = api_ctx.ctx.get("listing_id") or listing_id
    api_ctx.ctx["merchant_name"] = api_ctx.ctx.get("merchant_name") or merchant_name
    api_ctx.ctx["product_tags"] = product_tags
    api_ctx.ctx["_listing"] = listing

    definition_id = api_ctx.ctx.get("definition_id")
    tax_ratio = api_ctx.ctx.get("tax_vat_rate")
    product_url = api_ctx.product_url

    installment = _safe_api_call(
        get_installment_from_api,
        sku,
        amount=_kurus_amount(_listing_price_value(listing, "price")),
        definition_id=definition_id,
        tax_ratio=tax_ratio,
        merchant_id=merchant_id,
        product_url=product_url,
    )
    built_installment = _build_installment_offer(installment)
    if built_installment:
        api_data["installment"] = built_installment

    ask_to_seller = _safe_api_call(get_ask_to_seller_from_api, sku, product_url=product_url)
    built_ask = _build_ask_to_seller(ask_to_seller)
    if built_ask:
        api_data["ask_to_seller"] = built_ask

    if product_tags:
        without_aff = _safe_api_call(
            get_without_affordability_from_api,
            sku,
            product_tags,
            finalPrice=_listing_price_value(listing, "price"),
            finalPriceOnSale=_listing_price_value(listing, "price"),
            taxVatRate=tax_ratio,
            product_url=product_url,
            product_data=product_data,
            soup=soup,
            ctx_dict=api_ctx.ctx,
        )
        built_without_aff = _build_without_affordability(without_aff)
        if built_without_aff:
            api_data["affordability"] = built_without_aff

        other_merchants = _safe_api_call(
            get_other_merchants_from_api,
            sku,
            product_tags,
            merchant_id=merchant_id,
            merchant_name=merchant_name,
            listing_id=listing_id,
            final_price_on_sale=_listing_price_value(listing, "price"),
            minimum_price=_listing_price_value(listing, "minimumPrice"),
            product_url=product_url,
            product_data=product_data,
            soup=soup,
            ctx_dict=api_ctx.ctx,
        )
        built_other = _build_other_merchants(other_merchants)
        if built_other:
            api_data["other_merchants"] = built_other

    shipping = _safe_api_call(get_shipping_due_date_from_api, api_ctx)
    built_shipping = _build_shipping(shipping)
    if built_shipping:
        api_data["shipping"] = built_shipping

    payment_options = _safe_api_call(
        get_payment_options_from_api,
        sku,
        definition_id=definition_id,
        product_url=product_url,
    )
    built_payment = _build_payment_options(payment_options)
    if built_payment:
        api_data["payment_options"] = built_payment

    vas = _safe_api_call(
        get_vas_from_api,
        sku,
        price=_listing_price_value(listing, "price"),
        product_url=product_url,
        product_data=product_data,
        soup=soup,
        ctx_dict=api_ctx.ctx,
    )
    built_vas = _build_vas(vas)
    if built_vas:
        api_data["vas"] = built_vas

    if api_data:
        custom_data["api_data"] = api_data

    dataset = ProductDataset(
        source="hepsiburada",
        category=_detect_category(product_data, redux_product)
        if category in (None, "", "unknown")
        else category,
        name=_extract_first_string(product_data.get("name")),
        brand=_extract_first_string(brand_name),
        price=extract_price(product_data),
        currency=offers.get("priceCurrency"),
        url=offers.get("url"),
        sku=sku,
        image=_extract_image(product_data),
        description=_build_description(soup, product_data)
        if soup is not None
        else _extract_first_string(product_data.get("description")),
        availability=_extract_availability(product_data, redux_product),
        item_condition=offers.get("itemCondition"),
        reviews=custom_data.get("reviews"),
        installments=api_data.get("installment"),
        vas=api_data.get("vas"),
        custom_data=custom_data,
    )
    debug(
        "dataset.build.complete",
        provider="hepsiburada",
        api_sections=list(api_data),
        populated_fields=sum(
            value is not None
            for value in (
                dataset.name,
                dataset.brand,
                dataset.price,
                dataset.sku,
                dataset.description,
                dataset.availability,
            )
        ),
    )
    return dataset


def extract_product_dataset(soup, category="unknown", custom_data=None):
    product_data = extract_product_data(soup)
    debug("dataset.extract", provider="hepsiburada", product_data_found=product_data is not None)
    return build_product_dataset(
        product_data, category=category, custom_data=custom_data, soup=soup
    )


def product_dataset_to_json(dataset):
    if hasattr(dataset, "to_json"):
        return dataset.to_json()
    return json.dumps(dataset, ensure_ascii=False)


if __name__ == "__main__":
    url = "https://www.hepsiburada.com/karaca-tea-break-inox-siyah-celik-su-isitici-cay-makinesi-pm-HBC00002JH1M2"

    response = get_raw_html(url)

    if response.status_code == 200:
        soup = parse_html(response.content)
        dataset = extract_product_dataset(soup)
        payload = dataset.to_dict() if isinstance(dataset, ProductDataset) else dataset
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif response.status_code == 404:
        print(
            json.dumps(
                {"status": 404, "message": "Product not found"}, ensure_ascii=False
            )
        )
    elif response.status_code == 403:
        print(
            json.dumps({"status": 403, "message": "Access denied"}, ensure_ascii=False)
        )
    else:
        print(
            json.dumps(
                {"status": response.status_code, "message": "Unexpected status"},
                ensure_ascii=False,
            )
        )
