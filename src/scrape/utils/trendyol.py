import json
import re
from typing import Any

import requests
from bs4 import BeautifulSoup

from scrape.dataset import ProductDataset


def get_raw_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:154.0) Gecko/20100101 Firefox/154.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Host": "www.trendyol.com",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }
    response = requests.get(url, headers=headers, timeout=20)
    return response

def _is_placeholder_description_text(value):
    if value is None:
        return True

    cleaned = str(value).strip()
    if not cleaned:
        return True

    normalized = "".join(ch for ch in cleaned if ch.isalnum()).upper()
    if normalized in {"STD", "NAA", "NA", "NONE", "NULL", "UNKNOWN", "UNDEFINED", "N/A"}:
        return True

    return len(normalized) <= 3 and normalized.isalpha()


def get_product_descriptions_from_api(product_id):
    if not product_id:
        return None

    try:
        url = f"https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/component-read/component/{product_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:154.0) Gecko/20100101 Firefox/154.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8",
            "x-agentname": "StorefrontProductGateway",
            "x-web-req-source": "StorefrontProductGateway",
            "Origin": "https://www.trendyol.com",
            "Cookie": "platform=web; AZ_SELECTED=false; countryCode=TR; language=tr",
        }
        params = {"channelId": "1"}

        response = requests.get(url, params=params, headers=headers, timeout=20)
        if response.status_code != 200:
            return None

        data = response.json()
        if not data.get("isSuccess") or not data.get("result"):
            return None

        descriptions = data.get("result", {}).get("descriptions", [])
        if not descriptions:
            return None

        valid_texts = []
        for desc in descriptions:
            text = desc.get("text") if isinstance(desc, dict) else None
            if not text or _is_placeholder_description_text(text):
                continue
            valid_texts.append(text)

        if valid_texts:
            return " ".join(valid_texts)

        return None
    except Exception as e:
        print(f"Error fetching product descriptions from API: {e}")
        return None

def parse_html(html_content):
    return BeautifulSoup(html_content, "html.parser")

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

def extract_product_data(soup):
    for payload in _iter_json_ld_payloads(soup):
        if not isinstance(payload, dict):
            continue

        if payload.get("@type") == "Product":
            return payload

        offers = payload.get("offers")
        if isinstance(offers, dict) and payload.get("name"):
            return payload

    return None


def _format_price_value(value):
    if value is None:
        return None
    try:
        return f"{float(value):.2f} TL"
    except (TypeError, ValueError):
        return None


def extract_price(product_data_or_soup):
    if isinstance(product_data_or_soup, dict):
        product_data = product_data_or_soup
    else:
        product_data = extract_product_data(product_data_or_soup)

    if not isinstance(product_data, dict):
        return None

    offers = product_data.get("offers")
    if isinstance(offers, dict):
        price = offers.get("price")
        if price is not None:
            return _format_price_value(price)

    price = product_data.get("price")
    if price is not None:
        return _format_price_value(price)

    return None


def extract_price_from_product_data(product_data):
    return extract_price(product_data)


def _normalize_json_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _normalize_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_normalize_json_value(item) for item in value]
    return str(value)


def _str(value: Any) -> str | None:
    normalized = _normalize_json_value(value)
    if normalized is None or isinstance(normalized, str):
        return normalized
    return str(normalized)

def _extract_first_string(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, dict):
        for key in ("name", "text", "value", "label"):
            candidate = _extract_first_string(value.get(key))
            if candidate:
                return candidate
        return None
    if isinstance(value, (list, tuple, set)):
        for item in value:
            candidate = _extract_first_string(item)
            if candidate:
                return candidate
    return str(value)


def _detect_category_from_product_data(product_data):
    if not isinstance(product_data, dict):
        return "unknown"

    for key in ("category", "categoryName", "itemCategory", "productCategory"):
        candidate = _extract_first_string(product_data.get(key))
        if candidate:
            return candidate

    for key in ("pattern", "type", "kind"):
        candidate = _extract_first_string(product_data.get(key))
        if candidate:
            return candidate

    return "unknown"

def _extract_shared_props(soup):
    if not isinstance(soup, BeautifulSoup):
        return None

    for script in soup.select("script"):
        text = script.string or ""
        if '__envoy__SHARED_PROPS' not in text:
            continue

        marker = 'window["__envoy__SHARED_PROPS"]='
        start = text.find(marker)
        if start == -1:
            start = text.find("__envoy__SHARED_PROPS")
            start = text.find("=", start) + 1

        brace = text.find("{", start)
        if brace == -1:
            continue

        depth = 0
        i = brace
        in_str = False
        while i < len(text):
            ch = text[i]
            if in_str:
                if ch == "\\":
                    i += 2
                    continue
                if ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        break
            i += 1

        try:
            payload = json.loads(text[brace : i + 1])
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict):
            return payload

    return None


def _extract_reviews_custom(product_data, shared_props):
    if isinstance(shared_props, dict):
        product = shared_props.get("product")
        if isinstance(product, dict):
            rating = product.get("ratingScore")
            if isinstance(rating, dict):
                review_data = {}
                if rating.get("averageRating") is not None:
                    review_data["score"] = rating["averageRating"]
                if rating.get("commentCount") is not None:
                    review_data["count"] = rating["commentCount"]
                if review_data:
                    return review_data

    aggregate_rating = product_data.get("aggregateRating")
    if isinstance(aggregate_rating, dict):
        review_data = {}
        if aggregate_rating.get("ratingValue") is not None:
            review_data["score"] = aggregate_rating["ratingValue"]
        count = aggregate_rating.get("reviewCount") or aggregate_rating.get("ratingCount")
        if count is not None:
            review_data["count"] = count
        if review_data:
            return review_data

    return None


def _extract_listing_entry(merchant_dict):
    if not isinstance(merchant_dict, dict):
        return None

    entry = {"merchant": merchant_dict.get("name")}

    variants = merchant_dict.get("variants")
    if isinstance(variants, list) and variants:
        variant = variants[0]
        if isinstance(variant, dict):
            price = variant.get("price")
            if isinstance(price, dict):
                discounted = price.get("discountedPrice") or price.get("sellingPrice")
                if isinstance(discounted, dict) and discounted.get("value") is not None:
                    entry["price"] = discounted["value"]
                original = price.get("originalPrice")
                if isinstance(original, dict) and original.get("value") is not None:
                    entry["original_price"] = original["value"]
    return entry


def _extract_listings_custom(shared_props):
    if not isinstance(shared_props, dict):
        return None

    product = shared_props.get("product")
    if not isinstance(product, dict):
        return None

    merchant_listing = product.get("merchantListing")
    if not isinstance(merchant_listing, dict):
        return None

    listings = []

    merchant = merchant_listing.get("merchant")
    if isinstance(merchant, dict) and merchant.get("name"):
        entry = _extract_listing_entry(
            {
                "name": merchant.get("name"),
                "variants": [merchant_listing.get("winnerVariant")] if merchant_listing.get("winnerVariant") else None,
            }
        )
        if entry:
            listings.append(entry)

    other_merchants = merchant_listing.get("otherMerchants")
    if isinstance(other_merchants, list):
        for other in other_merchants:
            entry = _extract_listing_entry(other)
            if entry:
                listings.append(entry)

    if not listings:
        return None
    return listings


def _find_category_path_in_shared_props(node, depth=0):
    if depth > 8 or node is None:
        return None
    if isinstance(node, dict):
        for key in ("categoryTree", "webCategoryTree"):
            cand = node.get(key)
            if isinstance(cand, list):
                path = [c.get("name") for c in cand if isinstance(c, dict) and c.get("name")]
                if path:
                    return path
        for value in node.values():
            found = _find_category_path_in_shared_props(value, depth + 1)
            if found:
                return found
    elif isinstance(node, list):
        for item in node:
            found = _find_category_path_in_shared_props(item, depth + 1)
            if found:
                return found
    return None


def _detect_custom_data(product_data, shared_props=None):
    custom = {}

    if not isinstance(product_data, dict):
        return custom

    pattern = _extract_first_string(product_data.get("pattern"))
    if pattern:
        custom["pattern"] = pattern

    additional_properties = product_data.get("additionalProperty")
    if isinstance(additional_properties, list):
        attributes = {}
        for entry in additional_properties:
            if not isinstance(entry, dict):
                continue
            name = _extract_first_string(entry.get("name"))
            value = _extract_first_string(entry.get("value")) or _extract_first_string(entry.get("unitText"))
            if not name or not value:
                continue
            lowered = name.lower()
            if "renk" in lowered or "brand" in lowered or "marka" in lowered:
                continue
            attributes[name] = value
        if attributes:
            custom["attributes"] = attributes

    reviews = _extract_reviews_custom(product_data, shared_props)
    if reviews:
        custom["reviews"] = reviews

    listings = _extract_listings_custom(shared_props)
    if listings:
        custom["listings"] = listings
        if not custom.get("merchant") and isinstance(listings[0], dict):
            merchant = listings[0].get("merchant")
            if merchant:
                custom["merchant"] = merchant

    if isinstance(shared_props, dict):
        path = _find_category_path_in_shared_props(shared_props)
        if not path:
            category = shared_props.get("category") if isinstance(shared_props.get("category"), dict) else None
            if category:
                hierarchy = category.get("hierarchy")
                if hierarchy:
                    path = [p.strip() for p in str(hierarchy).split("/") if p.strip()]
        if path:
            custom["category_path"] = path

    return custom

def _extract_attributes_dict(product_data):
    attributes = {}
    if not isinstance(product_data, dict):
        return attributes

    for field_name in ("additionalProperty", "attributes"):
        items = product_data.get(field_name)
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict) and "key" in item and "value" in item:
                key = _extract_first_string(item.get("key"))
                value = _extract_first_string(item.get("value"))
            elif isinstance(item, dict):
                key = _extract_first_string(item.get("name"))
                value = _extract_first_string(item.get("value")) or _extract_first_string(item.get("unitText"))
            else:
                continue
            if key and value:
                attributes[key] = value
    return attributes

_BOILERPLATE_MARKERS = (
    "tarafından gönderilecektir",
    "kampanya fiyatından satılmak üzere",
    "satış fiyatını satıcı belirlemektedir",
    "birden fazla satıcı tarafından satılabilir",
    "adet sipariş verilebilir",
    "siparişinizi iptal etmek istemeniz durumunda",
    "ürünün satıcıları ürün için belirledikleri fiyata",
    "göre sıralanmaktadır",
    "ücretsiz iade",
    "incelemiş olduğunuz ürünün",
    "stok sunulmuştur",
    "limit kurumsal siparişlerde",
    "saklı tutar",
    "15 gün içinde",
    "bu üründen",
    "farklı limitler belirlenebilmektedir",
    "satıcı puanlarına",
    "teslimat statülerine",
    "kargonun bedava olup olmamasına",
    "hızlı teslimat ile teslim edilip edilememesine",
    "stok ve kategorileri bilgilerine",
    "gerçekleştirilen indirimler",
    "iade koşulları",
    "söz konusu ürün",
    "satın alındıktan sonra",
    "iptal etmek istemeniz durumunda",
    "adedin hepsi",
    "iptal edilecektir",
    "stoklarımıza",
    "siparişiniz onaylandıktan",
    "satılmak üzere",
)


def _contains_boilerplate(text: str) -> bool:
    lower = " ".join(text.split()).lower()
    for marker in _BOILERPLATE_MARKERS:
        if marker in lower:
            return True
    return bool(re.search(r"\[page", text))


def _strip_sentences_before_marker(text: str) -> str:
    if not text:
        return ""

    parts = re.split(r"(?<=[.!?])\s+", text)
    kept = []
    for part in parts:
        if not part.strip():
            continue
        if _contains_boilerplate(part):
            continue
        cleaned = re.sub(r"\[page(?:=\"[^\"]*\")?=[^\]]*\][^\[]*\[/page\]", "", part)
        cleaned = re.sub(r"\[page(?:=\"[^\"]*\")?=[^\]]*\]", "", cleaned)
        cleaned = cleaned.strip()
        if cleaned:
            kept.append(cleaned)

    return " ".join(kept).strip()


def _extract_description_clean(product_data):
    raw = product_data.get("description")
    if isinstance(raw, str):
        cleaned = _strip_sentences_before_marker(raw)
        return cleaned or None
    return None


def _build_description(product_data):
    if not isinstance(product_data, dict):
        return None

    sku = product_data.get("sku")
    if sku:
        api_description = get_product_descriptions_from_api(str(sku))
        if api_description:
            cleaned_api = _strip_sentences_before_marker(api_description).strip()
            if cleaned_api and len(cleaned_api) > 10:
                return cleaned_api

    clean_description = _extract_description_clean(product_data)
    if clean_description and len(clean_description) > 10:
        return clean_description

    attributes = _extract_attributes_dict(product_data)
    name = _extract_first_string(product_data.get("name"))

    if attributes:
        snippets = []
        for key, value in list(attributes.items())[:10]:
            snippets.append(f"{key}: {value}")
        base = ". ".join(snippets)
        if name:
            return f"{name}. Features: {base}."
        return base

    return _extract_first_string(product_data.get("description"))


def _extract_image(product_data):
    image = product_data.get("image")
    if isinstance(image, list):
        image = image[0] if image else None
    if isinstance(image, dict):
        content_url = image.get("contentUrl")
        if isinstance(content_url, str):
            return content_url
        if isinstance(content_url, list) and content_url:
            return str(content_url[0])
        return None
    if isinstance(image, str):
        return image
    return None


def build_product_dataset(product_data, category="unknown", custom_data=None, soup=None):
    if not isinstance(product_data, dict):
        return None

    shared_props = _extract_shared_props(soup) if soup is not None else None

    offers_raw = product_data.get("offers")
    offers = offers_raw if isinstance(offers_raw, dict) else {}

    brand = product_data.get("brand")
    if isinstance(brand, dict):
        brand_name = brand.get("name")
    else:
        brand_name = product_data.get("manufacturer")

    detected_category = category if category and category != "unknown" else _detect_category_from_product_data(product_data)
    merged_custom_data = _detect_custom_data(product_data, shared_props=shared_props)
    if isinstance(custom_data, dict):
        merged_custom_data.update(custom_data)

    return ProductDataset(
        source="trendyol",
        category=str(detected_category),
        name=_str(product_data.get("name")),
        brand=_str(brand_name),
        price=_str(extract_price(product_data)),
        currency=_str(offers.get("priceCurrency")),
        url=_str(offers.get("url")),
        sku=_str(product_data.get("sku")),
        image=_extract_image(product_data),
        description=_build_description(product_data),
        availability=_str(offers.get("availability")),
        item_condition=_str(offers.get("itemCondition")),
        custom_data=merged_custom_data if isinstance(merged_custom_data, dict) else {},
    )


def extract_product_dataset(soup, category="unknown", custom_data=None):
    product_data = extract_product_data(soup)
    return build_product_dataset(product_data, category=category, custom_data=custom_data, soup=soup)


def product_dataset_to_json(dataset):
    if hasattr(dataset, "to_json"):
        return dataset.to_json()
    return json.dumps(dataset, ensure_ascii=False)


if __name__ == "__main__":
    url = "https://www.trendyol.com/xiaomi/redmi-buds-8-pro-siyah-bluetooth-kulakici-kulaklik-tws-anc-bt-5-4-xiaomi-tr-garantili-p-1081766367"

    response = get_raw_html(url)

    if response.status_code == 200:
        soup = parse_html(response.content)
        dataset = extract_product_dataset(soup)
        payload = dataset.to_dict() if isinstance(dataset, ProductDataset) else dataset
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif response.status_code == 404:
        print(json.dumps({"status": 404, "message": "Product not found"}, ensure_ascii=False))
    elif response.status_code == 403:
        print(json.dumps({"status": 403, "message": "Access denied"}, ensure_ascii=False))
    else:
        print(json.dumps({"status": response.status_code, "message": "Unexpected status"}, ensure_ascii=False))