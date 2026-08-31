import json

import requests
from bs4 import BeautifulSoup


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


def parse_html(html_content):
    return BeautifulSoup(html_content, "html.parser")


def extract_price(soup):
    selectors = [
        'button[data-testid="lowest-price"]',
        'div[data-testid="normal-price"]',
        '.price.normal-price',
        '.price-wrapper .price',
        '.price',
    ]

    for selector in selectors:
        price_block = soup.select_one(selector)
        if not price_block:
            continue

        discounted = price_block.select_one(".discounted")
        if discounted:
            return discounted.get_text(strip=True)

        price_view = price_block.select_one(".price-view")
        if price_view:
            for candidate in price_view.select(".discounted, .price"):
                text = candidate.get_text(strip=True)
                if text:
                    return text

        for candidate in price_block.select(".discounted, .price, .price-container"):
            text = candidate.get_text(strip=True)
            if text:
                return text

        text = price_block.get_text(" ", strip=True)
        if text:
            if "!" in text:
                return text.split("!")[-1].strip()
            return text

    for script in soup.select("script[type='application/ld+json']"):
        try:
            payload = json.loads(script.string or "")
        except (TypeError, json.JSONDecodeError):
            continue

        offers = payload.get("offers") if isinstance(payload, dict) else None
        if isinstance(offers, dict):
            price = offers.get("price")
            if price:
                return f"{float(price):.2f} TL"

        if isinstance(payload, dict):
            price = payload.get("price")
            if price:
                return f"{float(price):.2f} TL"

    return None


if __name__ == "__main__":
    url = "https://www.trendyol.com/xiaomi/redmi-buds-8-pro-siyah-bluetooth-kulakici-kulaklik-tws-anc-bt-5-4-xiaomi-tr-garantili-p-1081766367"

    response = get_raw_html(url)

    if response.status_code == 200:
        soup = parse_html(response.content)
        price = extract_price(soup)

        if price:
            print(price)
        else:
            print("Price bulunamadı")