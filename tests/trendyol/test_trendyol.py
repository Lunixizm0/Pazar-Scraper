import json
import re
import sys
from pathlib import Path

import pytest

from scrape.utils.trendyol import (
    extract_price,
    extract_price_from_product_data,
    extract_product_data,
    extract_product_dataset,
    get_raw_html,
    parse_html,
    product_dataset_to_json,
)

sys.path.insert(0, str(Path(__file__).parent))
from get_products import (
    get_full_product_urls_from_homepage,
)


def test_get_full_product_urls_from_homepage_uses_best_seller_api(monkeypatch):
    class DummySession:
        def __init__(self):
            self.cookies = {"countryCode": "TR", "language": "tr"}

        def get(self, url, *args, **kwargs):
            if (
                url
                == "https://www.trendyol.com/cok-satanlar?type=bestSeller&webGenderId=1"
            ):

                class DummyHTMLResponse:
                    status_code = 200
                    text = "<html><body><a href='/not-a-product'>skip</a></body></html>"

                return DummyHTMLResponse()

            if (
                url
                == "https://apigw.trendyol.com/discovery-sfint-browsing-service/api/top-rankings-v2/top-ranking-contents"
            ):

                class DummyJSONResponse:
                    status_code = 200

                    def json(self):
                        return {
                            "products": [
                                {
                                    "url": "/kontes/kadin-fularli-fermuarli-shopper-el-ve-omuz-cantasi-p-898198883"
                                },
                                {
                                    "url": "/c-e-design/ultra-esnek-kopmaz-siyah-seffaf-sac-orgu-lastigi-100-adet-p-1106980689"
                                },
                            ]
                        }

                return DummyJSONResponse()

            raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr("requests.Session", lambda: DummySession())

    urls = get_full_product_urls_from_homepage(limit=2)

    assert urls == [
        "https://www.trendyol.com/kontes/kadin-fularli-fermuarli-shopper-el-ve-omuz-cantasi-p-898198883",
        "https://www.trendyol.com/c-e-design/ultra-esnek-kopmaz-siyah-seffaf-sac-orgu-lastigi-100-adet-p-1106980689",
    ]


def pytest_generate_tests(metafunc):
    if "url" in metafunc.fixturenames:
        urls = get_full_product_urls_from_homepage(limit=20)
        metafunc.parametrize("url", urls)


def test_extracts_price_from_live_trendyol_product(url):
    response = get_raw_html(url)
    assert response.status_code == 200, (
        f"Request failed for {url}: {response.status_code}"
    )

    soup = parse_html(response.content)
    product_data = extract_product_data(soup)
    assert product_data is not None, f"No product JSON found on {url}"

    price = extract_price_from_product_data(product_data)
    assert price is not None, f"No price found on {url}"
    assert re.search(r"\d[\d.,]*\s*TL", price), (
        f"Unexpected price format for {url}: {price}"
    )

    assert extract_price(soup) == price, f"DOM and JSON price mismatch for {url}"

    dataset = extract_product_dataset(soup)
    assert dataset.source == "trendyol"
    assert dataset.category is not None
    assert dataset.price is not None
    assert "brand" not in dataset.custom_data
    assert "color" not in dataset.custom_data
    assert dataset.description is not None and len(dataset.description) > 10, (
        f"Description too short: {dataset.description}"
    )
    json.loads(product_dataset_to_json(dataset))


def test_live_trendyol_product_has_reviews_and_listings(url):
    response = get_raw_html(url)
    assert response.status_code == 200, (
        f"Request failed for {url}: {response.status_code}"
    )

    soup = parse_html(response.content)
    dataset = extract_product_dataset(soup)

    reviews = dataset.custom_data.get("reviews")
    assert reviews is not None, f"No reviews found on {url}"
    assert isinstance(reviews, dict), f"Unexpected reviews type on {url}: {reviews}"
    assert "score" in reviews or "count" in reviews

    listings = dataset.custom_data.get("listings")
    assert listings is not None, f"No listings found on {url}"
    assert isinstance(listings, list) and len(listings) > 0, f"Empty listings on {url}"
    assert all("merchant" in listing for listing in listings), (
        f"Listing missing merchant on {url}"
    )

    json.loads(product_dataset_to_json(dataset))
