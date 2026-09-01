import json
import re
from typing import Any

import requests as _requests
from bs4 import BeautifulSoup

from scrape.dataset import ProductDataset
from scrape.debug import DebugRequests, debug, request_get

requests = DebugRequests(_requests)


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
    response = request_get(_requests, url, headers=headers, timeout=20)
    return response


def _is_placeholder_description_text(value):
    if value is None:
        return True

    cleaned = str(value).strip()
    if not cleaned:
        return True

    normalized = "".join(ch for ch in cleaned if ch.isalnum()).upper()
    if normalized in {
        "STD",
        "NAA",
        "NA",
        "NONE",
        "NULL",
        "UNKNOWN",
        "UNDEFINED",
        "N/A",
    }:
        return True

    return len(normalized) <= 3 and normalized.isalpha()


def get_common_api_headers():
    return {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:154.0) Gecko/20100101 Firefox/154.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8",
        "x-agentname": "StorefrontProductGateway",
        "x-web-req-source": "StorefrontProductGateway",
        "Origin": "https://www.trendyol.com",
        "Cookie": "platform=web; AZ_SELECTED=false; storefrontId=1; countryCode=TR; language=tr",
    }


def get_product_descriptions_from_api(product_id):
    if not product_id:
        return None

    try:
        url = f"https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/component-read/component/{product_id}"
        headers = get_common_api_headers()
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
        debug("api.error", api="product_descriptions", error=f"{type(e).__name__}: {e}")
        return None


def get_reviews_from_api(product_id, page=0, page_size=5):
    #Fetch product reviews, AI summary, and rating stats via review-read API
    try:
        url = "https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/review-read/product-reviews/detailed"
        params = {"contentId": product_id, "page": page, "pageSize": page_size, "channelId": "1"}
        response = requests.get(url, params=params, headers=get_common_api_headers(), timeout=20)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        debug("api.error", api="reviews", error=f"{type(e).__name__}: {e}")
        return None


def get_delivery_date_from_api(content_id, item_number, winner_listing_id):
    #Fetch delivery dates and shipping info via delivery-date-content API
    try:
        url = f"https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/delivery-date-content/delivery-date/{content_id}/itemNumber/{item_number}"
        params = {"winnerListingId": winner_listing_id, "channelId": "1"}
        response = requests.get(url, params=params, headers=get_common_api_headers(), timeout=20)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        debug("api.error", api="delivery_date", error=f"{type(e).__name__}: {e}")
        return None


def get_installment_from_api(amount, category_id, group_tag_ids, total_amount=None):
    #Fetch per-bank installment plans via installment API
    try:
        url = "https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/installment/"
        params = {
            "amount": amount,
            "totalAmount": total_amount or amount,
            "categoryId": category_id,
            "categoryIds": str(category_id),
            "codEligible": "true",
            "clientPage": "PDP",
            "isUserTyPlusActive": "false",
            "groupTagIds": group_tag_ids,
            "channelId": "1",
        }
        response = requests.get(url, params=params, headers=get_common_api_headers(), timeout=20)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching installment API: {e}")
        return None


def get_merchant_questions_from_api(content_id, page=0, size=4, fulfilment_type="mp"):
    #Fetch answered Q&A via merchant-questions API.
    try:
        url = f"https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/merchant-questions/content/{content_id}/answered"
        params = {
            "fulfilmentType": fulfilment_type,
            "excludeTag": "false",
            "page": page,
            "size": size,
            "isMobile": "false",
            "channelId": "1",
        }
        response = requests.get(url, params=params, headers=get_common_api_headers(), timeout=20)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching merchant questions API: {e}")
        return None


def get_seller_acceptance_from_api(seller_id):
    #Check seller question acceptance status via seller-acceptance API.
    try:
        url = "https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/merchant-questions/seller-acceptance"
        params = {"sellerId": seller_id, "isMobile": "false", "channelId": "1"}
        response = requests.get(url, params=params, headers=get_common_api_headers(), timeout=20)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching seller acceptance API: {e}")
        return None


def get_video_content_from_api(video_id):
    #Fetch video metadata (MP4 URL, thumbnail) via video-content API.
    try:
        url = f"https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/video-content/{video_id}"
        params = {"channelId": "1"}
        response = requests.get(url, params=params, headers=get_common_api_headers(), timeout=20)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching video content API: {e}")
        return None


def get_currencies_from_api(culture="tr-TR", storefront_id=1):
    #Fetch TCMB exchange rates via currencies API.
    try:
        url = "https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/currencies"
        params = {"storefrontId": storefront_id, "culture": culture, "channelId": "1"}
        response = requests.get(url, params=params, headers=get_common_api_headers(), timeout=20)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching currencies API: {e}")
        return None


def get_stickers_from_api(sticker_ids, platform="WEB"):
    #Fetch decorative/promotional stickers via stickers API
    try:
        url = "https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/stickers/stickers"
        params = {"stickerIds": sticker_ids, "platform": platform, "channelId": "1"}
        response = requests.get(url, params=params, headers=get_common_api_headers(), timeout=20)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching stickers API: {e}")
        return None


def get_complete_the_look_from_api(content_id, culture="tr-TR"):
    #Fetch complete-the-look markers via complete-the-look API.
    try:
        url = "https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/complete-the-look/markers"
        params = {
            "contentId": content_id,
            "intersactionAreaPadding": 5,
            "pointLabelGap": 30,
            "labelsGap": 4,
            "labelHeight": 28,
            "imageSize": "398x597",
            "labelPrefix": "+",
            "culture": culture,
            "channelId": "1",
        }
        response = requests.get(url, params=params, headers=get_common_api_headers(), timeout=20)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching complete the look API: {e}")
        return None


def get_slicing_attributes_from_api(group_id, content_id):
    #Fetch product variant options (colors, sizes) via slicing-attributes API.
    try:
        url = f"https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/slicing-attributes/product-group/{group_id}/slicing-attributes"
        params = {"contentId": content_id, "channelId": "1"}
        response = requests.get(url, params=params, headers=get_common_api_headers(), timeout=20)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching slicing attributes API: {e}")
        return None


def get_social_proof_from_api(content_ids):
    #Fetch favorite count / social proof badges via social-proof API.
    try:
        url = "https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/social-proof/"
        params = {"contentIds": content_ids, "channelId": "1"}
        response = requests.get(url, params=params, headers=get_common_api_headers(), timeout=20)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching social proof API: {e}")
        return None


def get_seller_store_from_api(seller_id):
    #Fetch merchant store info (score, metrics, tenure) via seller-store API.
    try:
        url = f"https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/seller-store/{seller_id}/header-information"
        params = {"channelId": "1"}
        response = requests.get(url, params=params, headers=get_common_api_headers(), timeout=20)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching seller store API: {e}")
        return None


def get_seller_follower_from_api(seller_id, culture="tr-TR"):
    #Fetch merchant store follower count via sellerstore-follow API.
    try:
        url = f"https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/sellerstore-follow/{seller_id}/follower-count"
        params = {"culture": culture, "channelId": "1", "checkCoupon": "true"}
        response = requests.get(url, params=params, headers=get_common_api_headers(), timeout=20)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching seller follower API: {e}")
        return None


def get_stamps_from_api(tag_ids, platform="WEB"):
    #Fetch promotional stamps / badges via stamps API.
    try:
        url = "https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/stamps/"
        params = {"tagIds": tag_ids, "platform": platform, "channelId": "1"}
        response = requests.get(url, params=params, headers=get_common_api_headers(), timeout=20)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching stamps API: {e}")
        return None


def get_product_eligibility_from_api(category_id, bank_category_id, price, culture="tr-TR", storefront_id=1):
    #Fetch product eligibility status via product-eligibility API.
    try:
        url = "https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/product-eligibility/"
        params = {
            "categoryId": category_id,
            "bankCategoryId": bank_category_id,
            "price": price,
            "culture": culture,
            "storefrontId": storefront_id,
            "channelId": "1",
        }
        response = requests.get(url, params=params, headers=get_common_api_headers(), timeout=20)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching product eligibility API: {e}")
        return None

def _flatten_vas_attributes(attributes):
    if isinstance(attributes, dict):
        return [
            {"key": str(k), "value": str(v) if not isinstance(v, dict) else str(v.get("name") or v.get("name") or v)}
            for k, v in attributes.items()
        ]
    if isinstance(attributes, list):
        flat = []
        for attr in attributes:
            if not isinstance(attr, dict):
                continue
            key = attr.get("key")
            if isinstance(key, dict):
                key = key.get("name")
            value = attr.get("value")
            if isinstance(value, dict):
                value = value.get("name")
            if key or value:
                flat.append({"key": str(key) if key else "", "value": str(value) if value else ""})
        return flat
    return None


def get_vas_from_api(product_id=None, storefront_id=1, language="tr", shared_props=None):
    sp = shared_props.get("product") if isinstance(shared_props, dict) else None
    if not isinstance(sp, dict):
        return None

    category_id = (sp.get("category") or {}).get("id")
    brand_id = (sp.get("brand") or {}).get("id")
    merchant_listing = sp.get("merchantListing") or {}
    seller_id = (merchant_listing.get("merchant") or {}).get("id")
    price_info = (merchant_listing.get("winnerVariant") or {}).get("price") or {}
    selling_price = (
        (price_info.get("sellingPrice") or {}).get("value")
        or (price_info.get("discountedPrice") or {}).get("value")
    )
    attributes = _flatten_vas_attributes(sp.get("attributes"))
    pid = product_id or sp.get("id")

    if not all([pid, category_id, brand_id, seller_id, selling_price, attributes]):
        return None

    try:
        url = "https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/vas/"
        params = {"storefrontId": storefront_id, "language": language, "channelId": "1"}
        payload = {
            "categoryId": category_id,
            "brandId": brand_id,
            "sellerId": seller_id,
            "sellingPrice": selling_price,
            "attributes": attributes,
        }
        response = requests.post(url, params=params, json=payload, headers=get_common_api_headers(), timeout=20)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        debug("api.error", api="vas", error=f"{type(e).__name__}: {e}")
        return None


def parse_html(html_content):
    debug("html.parse", bytes=len(html_content or b""))
    soup = BeautifulSoup(html_content, "html.parser")
    debug("html.parsed", scripts=len(soup.select("script")))
    return soup


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
            debug("product_data.found", source="json_ld", match="@type")
            return payload

        offers = payload.get("offers")
        if isinstance(offers, dict) and payload.get("name"):
            debug("product_data.found", source="json_ld", match="offers_and_name")
            return payload

    debug("product_data.missing", source="json_ld")
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
        if "__envoy__SHARED_PROPS" not in text:
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
        count = aggregate_rating.get("reviewCount") or aggregate_rating.get(
            "ratingCount"
        )
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
                "variants": [merchant_listing.get("winnerVariant")]
                if merchant_listing.get("winnerVariant")
                else None,
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
                path = [
                    c.get("name") for c in cand if isinstance(c, dict) and c.get("name")
                ]
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
            value = _extract_first_string(entry.get("value")) or _extract_first_string(
                entry.get("unitText")
            )
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
            category = (
                shared_props.get("category")
                if isinstance(shared_props.get("category"), dict)
                else None
            )
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
                value = _extract_first_string(
                    item.get("value")
                ) or _extract_first_string(item.get("unitText"))
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


def _sp_product(shared_props):
    if not isinstance(shared_props, dict):
        return None
    product = shared_props.get("product")
    return product if isinstance(product, dict) else None


def _sp_product_id(product_data, shared_props):
    pid = product_data.get("sku") if isinstance(product_data, dict) else None
    if pid is None:
        sp = _sp_product(shared_props)
        if sp:
            pid = sp.get("id")
    return pid


def _sp_seller_id(shared_props):
    sp = _sp_product(shared_props)
    if not sp:
        return None
    listing = sp.get("merchantListing")
    if isinstance(listing, dict):
        merchant = listing.get("merchant")
        if isinstance(merchant, dict):
            return merchant.get("id")
    return None


def _sp_category_id(shared_props):
    sp = _sp_product(shared_props)
    if not sp:
        return None
    category = sp.get("category")
    if isinstance(category, dict):
        return category.get("id")
    return None


def _sp_selling_price(shared_props):
    sp = _sp_product(shared_props)
    if not sp:
        return None
    listing = sp.get("merchantListing")
    if not isinstance(listing, dict):
        return None
    winner = listing.get("winnerVariant")
    if not isinstance(winner, dict):
        return None
    price = winner.get("price")
    if not isinstance(price, dict):
        return None
    selling = price.get("sellingPrice")
    if isinstance(selling, dict) and selling.get("value") is not None:
        return selling["value"]
    discounted = price.get("discountedPrice")
    if isinstance(discounted, dict) and discounted.get("value") is not None:
        return discounted["value"]
    return None


def _sp_group_tag_ids(shared_props):
    sp = _sp_product(shared_props)
    if not sp:
        return None
    for key in ("groupTagIds", "groupIdList", "groupTagId"):
        val = sp.get(key)
        if val:
            return val
    return None


def _sp_video_id(shared_props):
    sp = _sp_product(shared_props)
    if not sp:
        return None
    for key in ("videoContentId", "videoId", "videoContents"):
        val = sp.get(key)
        if isinstance(val, dict):
            vid = val.get("id") or val.get("videoId")
            if vid:
                return vid
        elif val:
            return val
    return None


def _sp_p_group_id(shared_props):
    sp = _sp_product(shared_props)
    if not sp:
        return None
    for key in ("pGroupId", "productGroupId", "group_id"):
        val = sp.get(key)
        if val:
            return val
    return None


def _sp_sticker_ids(shared_props):
    sp = _sp_product(shared_props)
    if not sp:
        return None
    for key in ("stickerIds", "stickers"):
        val = sp.get(key)
        if val:
            return val
    return None


def _sp_tag_ids(shared_props):
    sp = _sp_product(shared_props)
    if not sp:
        return None
    for key in ("tagIds", "tags", "filterableLabelIds"):
        val = sp.get(key)
        if val:
            return val
    return None


def _sp_delivery(shared_props):
    sp = _sp_product(shared_props)
    if not sp:
        return (None, None, None)
    listing = sp.get("merchantListing")
    if not isinstance(listing, dict):
        return (None, None, None)
    winner = listing.get("winnerVariant")
    item_number = None
    listing_id = None
    if isinstance(winner, dict):
        item_number = winner.get("itemNumber")
        if item_number is None:
            item_number = winner.get("item")
        listing_id = winner.get("listingId") or winner.get("id")
    if listing_id is None:
        listing_id = listing.get("listingId")
    return (item_number, listing_id)


def _safe_api_call(fn, *args, **kwargs):
    api_name = getattr(fn, "__name__", str(fn))
    debug("api.builder.start", builder=api_name)
    try:
        result = fn(*args, **kwargs)
        debug("api.builder.complete", builder=api_name, available=result is not None)
        return result
    except Exception as e:
        debug("api.builder.error", builder=api_name, error=f"{type(e).__name__}: {e}")
        return None


def _build_reviews(product_data, shared_props):
    pid = _sp_product_id(product_data, shared_props)
    if pid is None:
        return None
    data = _safe_api_call(get_reviews_from_api, pid)
    if not isinstance(data, dict):
        return None
    result = data.get("result")
    if not isinstance(result, dict):
        return None
    summary = result.get("summary") if isinstance(result.get("summary"), dict) else {}
    reviews = []
    for r in (result.get("reviews") or []):
        if not isinstance(r, dict):
            continue
        entry = {}
        if r.get("rate") is not None:
            entry["rating"] = r["rate"]
        text = r.get("comment") or r.get("originalText")
        if text:
            entry["comment"] = text
        seller = r.get("seller")
        if isinstance(seller, dict) and seller.get("name"):
            entry["seller"] = seller["name"]
        if r.get("trusted") is not None:
            entry["trusted"] = r["trusted"]
        if entry:
            reviews.append(entry)
    out = {}
    if summary.get("averageRating") is not None:
        out["score"] = summary["averageRating"]
    if summary.get("totalRatingCount") is not None:
        out["total_rating_count"] = summary["totalRatingCount"]
    if result.get("aiSummary"):
        out["ai_summary"] = result["aiSummary"]
    if reviews:
        out["reviews"] = reviews[:5]
    return out if out else None


def _build_vas(product_data, shared_props):
    pid = _sp_product_id(product_data, shared_props)
    data = _safe_api_call(get_vas_from_api, product_id=pid, shared_props=shared_props)
    if not isinstance(data, dict) or not data.get("isSuccess"):
        debug(
            "api.builder.skip",
            builder="_build_vas",
            reason="response_not_successful",
            response_type=type(data).__name__,
            is_success=data.get("isSuccess") if isinstance(data, dict) else None,
        )
        return None
    result = data.get("result")
    if not isinstance(result, list):
        debug("api.builder.skip", builder="_build_vas", reason="result_not_a_list")
        return None
    offers = []
    for offer in result:
        if not isinstance(offer, dict):
            continue
        entry = {
            "name": offer.get("subCategory")
            or offer.get("category")
            or offer.get("variant", {}).get("name"),
            "price": offer.get("calculatedPrice")
            or offer.get("calculatedPriceText"),
            "user_friendly_price": offer.get("calculatedPriceTextWithCurrency"),
            "currency": offer.get("currency"),
            "category": offer.get("category"),
            "seller": offer.get("sellerName"),
        }
        entry = {k: v for k, v in entry.items() if v is not None}
        if offer.get("description"):
            entry["description"] = offer["description"]
        if entry:
            offers.append(entry)
    if not offers:
        debug("api.builder.skip", builder="_build_vas", reason="no_usable_offers")
        return None
    return offers


def _build_installments(product_data, shared_props):
    amount = _sp_selling_price(shared_props)
    category_id = _sp_category_id(shared_props)
    if amount is None or category_id is None:
        return None
    group_tag_ids = _sp_group_tag_ids(shared_props) or ""
    data = _safe_api_call(
        get_installment_from_api, amount, category_id, group_tag_ids
    )
    if not isinstance(data, dict):
        return None
    result = data.get("result")
    if not isinstance(result, dict):
        return None
    out = {}
    summary = result.get("summary")
    if isinstance(summary, dict):
        zero = summary.get("zeroInstallment")
        if isinstance(zero, dict):
            out["zero_installment"] = {
                "term": zero.get("term"),
                "banks": zero.get("bankDetails"),
            }
        max_inst = summary.get("maxInstallment")
        if isinstance(max_inst, dict):
            out["max_installment"] = {
                "term": max_inst.get("term"),
                "monthly_fee": max_inst.get("monthlyFee"),
            }
    offers = []
    for offer in (result.get("installmentOffers") or []):
        if not isinstance(offer, dict):
            continue
        issuer = offer.get("issuerName") or offer.get("displayName")
        plans = []
        for inst in (offer.get("installements") or []):
            if not isinstance(inst, dict):
                continue
            plans.append(
                {
                    "term": inst.get("term"),
                    "monthly_fee": inst.get("totalTermPrice"),
                    "total_price": inst.get("totalPrice"),
                    "interest_rate": inst.get("interestRate"),
                }
            )
        plans = [p for p in plans if p.get("term") is not None]
        if issuer and plans:
            offers.append({"bank": issuer, "plans": plans})
    if offers:
        out["offers"] = offers
    return out if out else None


def _build_delivery(product_data, shared_props):
    pid = _sp_product_id(product_data, shared_props)
    if pid is None:
        return None
    item_number, listing_id = _sp_delivery(shared_props)
    if item_number is None or listing_id is None:
        return None
    data = _safe_api_call(get_delivery_date_from_api, pid, item_number, listing_id)
    if not isinstance(data, dict):
        return None
    result = data.get("result")
    if not isinstance(result, dict):
        return None
    dates = result.get("deliveryDates")
    if not isinstance(dates, list) or not dates:
        return None
    entry = dates[0]
    out = {
        "delivery_start": entry.get("deliveryStartDate"),
        "delivery_end": entry.get("deliveryEndDate"),
        "cargo_start": entry.get("cargoStartDate"),
        "cargo_companies": entry.get("cargoCompanies") or [],
    }
    out = {k: v for k, v in out.items() if v is not None}
    fast = entry.get("fastDeliveryOptions")
    if isinstance(fast, list) and fast:
        out["fast_delivery_options"] = fast
    return out if out else None


def _build_merchant_questions(product_data, shared_props):
    pid = _sp_product_id(product_data, shared_props)
    if pid is None:
        return None
    data = _safe_api_call(get_merchant_questions_from_api, pid)
    if not isinstance(data, dict):
        return None
    questions = data.get("questions")
    if not isinstance(questions, dict):
        questions = data.get("result", {}).get("questions") if isinstance(data.get("result"), dict) else None
    if not isinstance(questions, dict):
        return None
    out = {}
    if questions.get("totalElements") is not None:
        out["total"] = questions["totalElements"]
    entries = []
    for q in (questions.get("content") or []):
        if not isinstance(q, dict):
            continue
        entry = {"question": q.get("text")}
        answer = q.get("answer")
        if isinstance(answer, dict):
            ans_text = answer.get("text") or answer.get("originalText")
            if ans_text:
                entry["answer"] = ans_text
        if q.get("sellerName"):
            entry["seller"] = q["sellerName"]
        if q.get("answeredDateMessage"):
            entry["answered"] = q["answeredDateMessage"]
        if entry:
            entries.append(entry)
    if entries:
        out["questions"] = entries[:4]
    return out if out else None


def _build_seller_store(product_data, shared_props):
    seller_id = _sp_seller_id(shared_props)
    if seller_id is None:
        return None
    data = _safe_api_call(get_seller_store_from_api, seller_id)
    if not isinstance(data, dict):
        return None
    result = data.get("result")
    if not isinstance(result, dict):
        return None
    out = {
        "name": result.get("name") or result.get("officialName"),
        "score": result.get("score"),
        "product_count": result.get("productCount"),
        "official_name": result.get("officialName"),
        "store_url": result.get("storeUrl"),
    }
    out = {k: v for k, v in out.items() if v is not None}
    ranking = result.get("rankingInfo")
    if isinstance(ranking, dict) and ranking.get("text"):
        out["ranking"] = ranking["text"]
    metrics = []
    for m in (result.get("sellerMetrics") or []):
        if isinstance(m, dict) and m.get("title") is not None:
            metrics.append(
                {"title": m.get("title"), "value": m.get("value"), "id": m.get("id")}
            )
    if metrics:
        out["metrics"] = metrics
    return out if out else None


def _build_seller_follower(product_data, shared_props):
    seller_id = _sp_seller_id(shared_props)
    if seller_id is None:
        return None
    data = _safe_api_call(get_seller_follower_from_api, seller_id)
    if not isinstance(data, dict):
        return None
    result = data.get("result")
    if not isinstance(result, dict):
        return None
    out = {}
    if result.get("count") is not None:
        out["count"] = result["count"]
    if result.get("text"):
        out["text"] = result["text"]
    if result.get("hasCoupon") is not None:
        out["has_coupon"] = result["hasCoupon"]
    return out if out else None


def _build_seller_acceptance(product_data, shared_props):
    seller_id = _sp_seller_id(shared_props)
    if seller_id is None:
        return None
    data = _safe_api_call(get_seller_acceptance_from_api, seller_id)
    if not isinstance(data, dict):
        return None
    if data.get("isSellerAcceptQuestions") is not None:
        return {"accepts_questions": data["isSellerAcceptQuestions"]}
    return None


def _build_product_eligibility(product_data, shared_props):
    category_id = _sp_category_id(shared_props)
    price = _sp_selling_price(shared_props)
    if category_id is None or price is None:
        return None
    data = _safe_api_call(
        get_product_eligibility_from_api, category_id, 13, price
    )
    if not isinstance(data, dict):
        return None
    result = data.get("result")
    if not isinstance(result, dict):
        return None
    out = {}
    if result.get("eligible") is not None:
        out["eligible"] = result["eligible"]
    if result.get("maxLoanTerm") is not None:
        out["max_loan_term"] = result["maxLoanTerm"]
    if result.get("productDetailSlogan"):
        out["slogan"] = result["productDetailSlogan"]
    banners = result.get("banners")
    if isinstance(banners, list) and banners:
        clean = []
        for b in banners:
            if isinstance(b, dict) and b.get("title"):
                clean.append({"title": b["title"], "content": b.get("content")})
        if clean:
            out["banners"] = clean
    return out if out else None


def _build_slicing_attributes(product_data, shared_props):
    pid = _sp_product_id(product_data, shared_props)
    group_id = _sp_p_group_id(shared_props)
    if pid is None or group_id is None:
        return None
    data = _safe_api_call(get_slicing_attributes_from_api, group_id, pid)
    if not isinstance(data, dict):
        return None
    result = data.get("result")
    if not isinstance(result, list) or not result:
        return None
    attrs = []
    for attr in result:
        if not isinstance(attr, dict):
            continue
        values = []
        for v in (attr.get("values") or []):
            if not isinstance(v, dict):
                continue
            values.append(
                {
                    "name": v.get("name") or v.get("beautifiedName"),
                    "is_selected": v.get("isSelected"),
                    "product_count": len(v.get("products") or [])
                    if isinstance(v.get("products"), list)
                    else None,
                }
            )
        values = [x for x in values if x.get("name")]
        if attr.get("title") and values:
            attrs.append({"title": attr["title"], "type": attr.get("type"), "values": values})
    return attrs if attrs else None


def _build_complete_the_look(product_data, shared_props):
    pid = _sp_product_id(product_data, shared_props)
    if pid is None:
        return None
    data = _safe_api_call(get_complete_the_look_from_api, pid)
    if not isinstance(data, dict):
        return None
    result = data.get("result")
    if isinstance(result, dict) and isinstance(result.get("markers"), list):
        return result["markers"]
    if isinstance(result, list):
        return result
    return None


def _build_social_proof(product_data, shared_props):
    pid = _sp_product_id(product_data, shared_props)
    if pid is None:
        return None
    data = _safe_api_call(get_social_proof_from_api, str(pid))
    if not isinstance(data, dict):
        return None
    out = {}
    for val in data.values():
        if not isinstance(val, dict):
            continue
        for proof in (val.get("socialProofs") or []):
            if isinstance(proof, dict) and proof.get("id"):
                out[proof["id"]] = proof.get("count")
    return out if out else None


def _build_video(product_data, shared_props):
    video_id = _sp_video_id(shared_props)
    if video_id is None:
        debug("api.builder.skip", builder="_build_video", reason="video_id_missing")
        return None
    data = _safe_api_call(get_video_content_from_api, video_id)
    if not isinstance(data, dict):
        return None
    result = data.get("result")
    if not isinstance(result, dict):
        return None
    out = {
        "url": result.get("url"),
        "thumbnail": result.get("thumbnail"),
        "duration": result.get("duration"),
        "view_count": result.get("viewCount"),
    }
    out = {k: v for k, v in out.items() if v is not None}
    return out if out else None


def _build_stickers(product_data, shared_props):
    sticker_ids = _sp_sticker_ids(shared_props)
    if sticker_ids is None:
        debug("api.builder.skip", builder="_build_stickers", reason="sticker_ids_missing")
        return None
    if isinstance(sticker_ids, (list, tuple)):
        sticker_ids = ",".join(str(x) for x in sticker_ids)
    data = _safe_api_call(get_stickers_from_api, sticker_ids)
    if not isinstance(data, dict):
        return None
    result = data.get("result")
    if not isinstance(result, list) or not result:
        return None
    stickers = []
    for s in result:
        if isinstance(s, dict) and (s.get("stickerImageUrl") or s.get("description")):
            stickers.append(
                {
                    "image": s.get("stickerImageUrl"),
                    "description": s.get("description"),
                    "is_authorized_seller": s.get("isAuthorizedSellerSticker"),
                }
            )
    return stickers if stickers else None


def _build_stamps(product_data, shared_props):
    tag_ids = _sp_tag_ids(shared_props)
    if tag_ids is None:
        return None
    if isinstance(tag_ids, (list, tuple)):
        tag_ids = ",".join(str(x) for x in tag_ids)
    data = _safe_api_call(get_stamps_from_api, tag_ids)
    if not isinstance(data, dict):
        debug("api.builder.skip", builder="_build_stamps", reason="response_not_an_object")
        return None
    result = data.get("result")
    if not isinstance(result, dict) or not result:
        debug("api.builder.skip", builder="_build_stamps", reason="result_empty_or_not_an_object")
        return None
    stamps = []
    for info in result.values():
        if not isinstance(info, dict):
            continue
        display = info.get("displayName") or info.get("name")
        for stamp in (info.get("stamps") or []):
            if isinstance(stamp, dict) and stamp.get("stampUrl"):
                stamps.append(
                    {
                        "image": stamp["stampUrl"],
                        "display_name": display,
                        "position": stamp.get("position"),
                        "type": stamp.get("stampType") or stamp.get("type"),
                    }
                )
    if not stamps:
        debug("api.builder.skip", builder="_build_stamps", reason="no_stamp_url_in_response")
        return None
    return stamps


def _build_currencies(product_data, shared_props):
    data = _safe_api_call(get_currencies_from_api)
    if not isinstance(data, dict):
        return None
    result = data.get("result")
    if not isinstance(result, list) or not result:
        return None
    currencies = []
    for c in result:
        if isinstance(c, dict) and c.get("currencyName"):
            currencies.append(
                {"name": c["currencyName"], "rate": c.get("tcmbRate")}
            )
    return currencies if currencies else None


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


def build_product_dataset(
    product_data, category="unknown", custom_data=None, soup=None
):
    if not isinstance(product_data, dict):
        debug("dataset.skipped", provider="trendyol", reason="product_data_missing")
        return None

    shared_props = _extract_shared_props(soup) if soup is not None else None
    debug("dataset.build.start", provider="trendyol", shared_props_found=shared_props is not None)

    offers_raw = product_data.get("offers")
    offers = offers_raw if isinstance(offers_raw, dict) else {}

    brand = product_data.get("brand")
    if isinstance(brand, dict):
        brand_name = brand.get("name")
    else:
        brand_name = product_data.get("manufacturer")

    detected_category = (
        category
        if category and category != "unknown"
        else _detect_category_from_product_data(product_data)
    )
    merged_custom_data = _detect_custom_data(product_data, shared_props=shared_props)
    if isinstance(custom_data, dict):
        merged_custom_data.update(custom_data)

    reviews = _build_reviews(product_data, shared_props)
    vas = _build_vas(product_data, shared_props)
    installments = _build_installments(product_data, shared_props)

    api_data = {}
    for name, builder in (
        ("delivery", _build_delivery),
        ("merchant_questions", _build_merchant_questions),
        ("seller_store", _build_seller_store),
        ("seller_follower", _build_seller_follower),
        ("seller_acceptance", _build_seller_acceptance),
        ("product_eligibility", _build_product_eligibility),
        ("slicing_attributes", _build_slicing_attributes),
        ("complete_the_look", _build_complete_the_look),
        ("social_proof", _build_social_proof),
        ("video", _build_video),
        ("stickers", _build_stickers),
        ("stamps", _build_stamps),
        ("currencies", _build_currencies),
    ):
        value = _safe_api_call(builder, product_data, shared_props)
        if value is not None:
            api_data[name] = value

    if api_data:
        merged_custom_data["api_data"] = api_data

    debug(
        "dataset.build.complete",
        provider="trendyol",
        api_sections=list(api_data),
        reviews=reviews is not None,
        vas=vas is not None,
        installments=installments is not None,
    )

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
        reviews=reviews,
        vas=vas,
        installments=installments,
        custom_data=merged_custom_data if isinstance(merged_custom_data, dict) else {},
    )


def extract_product_dataset(soup, category="unknown", custom_data=None):
    product_data = extract_product_data(soup)
    debug("dataset.extract", provider="trendyol", product_data_found=product_data is not None)
    return build_product_dataset(
        product_data, category=category, custom_data=custom_data, soup=soup
    )


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
