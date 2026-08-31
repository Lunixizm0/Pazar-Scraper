import re

import requests


def _normalize_trendyol_product_url(value):
    value = (value or "").strip()
    if not value:
        return None

    value = value.split("#", 1)[0].split("?", 1)[0].strip("\"'")

    if value.startswith(("http://", "https://")):
        return value
    if value.startswith("/"):
        return f"https://www.trendyol.com{value}"
    return f"https://www.trendyol.com/{value.lstrip('/')}"


def _best_seller_products_response(limit=5):
    page_url = "https://www.trendyol.com/cok-satanlar?type=bestSeller&webGenderId=1"
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:154.0) Gecko/20100101 Firefox/154.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://www.trendyol.com/",
    }
    session.get(page_url, headers=headers, timeout=30)

    api_url = "https://apigw.trendyol.com/discovery-sfint-browsing-service/api/top-rankings-v2/top-ranking-contents"
    params = {
        "rankingType": "bestSeller",
        "webGenderId": "1",
        "page": "1",
        "pageSize": str(limit),
        "categoryId": "27",
        "channelId": "1",
    }
    api_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:154.0) Gecko/20100101 Firefox/154.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
        "Referer": page_url,
        "Origin": "https://www.trendyol.com",
        "x-device-type": "desktop",
        "x-device-platform": "web",
    }

    response = session.get(api_url, params=params, headers=api_headers, timeout=30)
    if response.status_code != 200:
        return []

    payload = response.json()
    products = payload.get("products") or []
    if not isinstance(products, list):
        return []
    return products


def get_product_ids_from_homepage(limit=10):
    urls = get_full_product_urls_from_homepage(limit=limit)
    ids = set()
    for url in urls:
        match = re.search(r"-p-(\d+)(?:[/?#]|$)", url)
        if match:
            ids.add(match.group(1))
    return list(ids)[:limit]


def get_full_product_urls_from_homepage(limit=10):
    try:
        products = _best_seller_products_response(limit=limit)
        seen = set()
        urls = []
        for product in products:
            candidate = (product or {}).get("url")
            normalized = _normalize_trendyol_product_url(candidate)
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            urls.append(normalized)

        return urls[:limit]
    except Exception as e:
        print(f"Error fetching product URLs: {e}")
        return []


if __name__ == "__main__":
    print("Fetching products from Trendyol best sellers page...\n")

    print("Method 1: Full Product URLs")
    urls = get_full_product_urls_from_homepage(limit=5)
    if urls:
        print(f"Found {len(urls)} full product URLs:")
        for url in urls:
            print(f"  - {url}")
    else:
        print("No full URLs found")

    print("\nMethod 2: Product IDs (for API use)")
    product_ids = get_product_ids_from_homepage(limit=5)
    if product_ids:
        print(f"Found {len(product_ids)} product IDs:")
        for pid in product_ids:
            print(f"  - {pid}")
            print(f"    API: https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/component-read/component/{pid}")
    else:
        print("No product IDs found")
