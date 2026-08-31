import re

import pytest

from scrape.utils.trendyol import extract_price, get_raw_html, parse_html


@pytest.mark.parametrize(
    "url",
    [
        "https://www.trendyol.com/xiaomi/redmi-buds-8-pro-siyah-bluetooth-kulakici-kulaklik-tws-anc-bt-5-4-xiaomi-tr-garantili-p-1081766367",
        "https://www.trendyol.com/xiaomi/redmi-buds-6-play-siyah-kulakici-kulaklik-gurultu-onleme-bt5-4-ios-android-xiaomi-tr-garantili-p-855229295",
    ],
)
def test_extracts_price_from_live_trendyol_product(url):
    response = get_raw_html(url)
    assert response.status_code == 200, f"Request failed for {url}: {response.status_code}"

    soup = parse_html(response.content)
    price = extract_price(soup)

    assert price is not None, f"No price found on {url}"
    assert re.search(r"\d[\d.,]*\s*TL", price), f"Unexpected price format for {url}: {price}"
