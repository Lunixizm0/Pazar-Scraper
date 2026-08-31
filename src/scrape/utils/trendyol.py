import json

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
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
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


def _normalize_json_value(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _normalize_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_normalize_json_value(item) for item in value]
    return str(value)

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

def _detect_custom_data(product_data):
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

def _build_description(product_data):
    if not isinstance(product_data, dict):
        return None

    # Try to fetch from API first
    sku = product_data.get("sku")
    if sku:
        api_description = get_product_descriptions_from_api(str(sku))
        if api_description:
            return api_description

    # Fallback to attributes-based description
    attributes = _extract_attributes_dict(product_data)
    name = _extract_first_string(product_data.get("name"))

    if attributes:
        snippets = []
        for key, value in list(attributes.items())[:10]:
            snippets.append(f"{key}: {value}")
        base = ". ".join(snippets)
        if name:
            return f"{name}. Özellikler: {base}."
        return base

    return _extract_first_string(product_data.get("description"))


def build_product_dataset(product_data, category="unknown", custom_data=None):
    if not isinstance(product_data, dict):
        return None

    offers = product_data.get("offers") if isinstance(product_data.get("offers"), dict) else {}
    brand = product_data.get("brand")
    if isinstance(brand, dict):
        brand_name = brand.get("name")
    else:
        brand_name = product_data.get("manufacturer")

    detected_category = category if category and category != "unknown" else _detect_category_from_product_data(product_data)
    merged_custom_data = _detect_custom_data(product_data)
    if isinstance(custom_data, dict):
        merged_custom_data.update(custom_data)

    return ProductDataset(
        source="trendyol",
        category=_normalize_json_value(detected_category),
        name=_normalize_json_value(product_data.get("name")),
        brand=_normalize_json_value(brand_name),
        price=_normalize_json_value(extract_price(product_data)),
        currency=_normalize_json_value(offers.get("priceCurrency")),
        url=_normalize_json_value(offers.get("url")),
        sku=_normalize_json_value(product_data.get("sku")),
        image=_normalize_json_value(product_data.get("image")),
        description=_normalize_json_value(_build_description(product_data)),
        availability=_normalize_json_value(offers.get("availability")),
        item_condition=_normalize_json_value(offers.get("itemCondition")),
        custom_data=_normalize_json_value(merged_custom_data),
    )


def extract_product_dataset(soup, category="unknown", custom_data=None):
    product_data = extract_product_data(soup)
    return build_product_dataset(product_data, category=category, custom_data=custom_data)


def product_dataset_to_json(dataset):
    if hasattr(dataset, "to_json"):
        return dataset.to_json()
    return json.dumps(dataset, ensure_ascii=False)


if __name__ == "__main__":
    url = "https://www.trendyol.com/apple/iphone-16-pro-max-256gb-siyah-titanyum-p-857296077"

    response = get_raw_html(url)

    if response.status_code == 200:
        soup = parse_html(response.content)
        dataset = extract_product_dataset(soup)
        payload = dataset.to_dict() if hasattr(dataset, "to_dict") else dataset
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif response.status_code == 404:
        print(json.dumps({"status": 404, "message": "Ürün bulunamadı"}, ensure_ascii=False))
    elif response.status_code == 403:
        print(json.dumps({"status": 403, "message": "Erişim engellendi"}, ensure_ascii=False))
    else:
        print(json.dumps({"status": response.status_code, "message": "Beklenmeyen durum"}, ensure_ascii=False))