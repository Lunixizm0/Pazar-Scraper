import json
import re
import sys
from pathlib import Path

import pytest

from scrape.utils.hepsiburada import (
    extract_product_data,
    extract_product_dataset,
    get_raw_html,
    parse_html,
    product_dataset_to_json,
)

sys.path.insert(0, str(Path(__file__).parent))
from get_hepsiburada_products import get_full_product_urls_from_homepage


def pytest_generate_tests(metafunc):
    if "url" in metafunc.fixturenames:
        urls = get_full_product_urls_from_homepage(limit=20)
        metafunc.parametrize("url", urls)


def test_extracts_product_from_live_hepsiburada_product(url):
    response = get_raw_html(url)
    assert response.status_code == 200, f"Request failed for {url}: {response.status_code}"

    soup = parse_html(response.content)
    product_data = extract_product_data(soup)
    assert product_data is not None, f"No product JSON-LD found on {url}"

    dataset = extract_product_dataset(soup)
    assert dataset is not None

    assert dataset["source"] == "hepsiburada"
    assert dataset["name"] is not None and len(dataset["name"]) > 0, f"No name on {url}"
    assert dataset["brand"] is not None, f"No brand on {url}"
    assert dataset["sku"] is not None, f"No sku on {url}"
    assert dataset["price"] is not None, f"No price on {url}"
    assert re.search(r"\d[\d.,]*\s*TL", dataset["price"]), f"Unexpected price format on {url}: {dataset['price']}"
    assert dataset["currency"] == "TRY", f"Unexpected currency on {url}: {dataset['currency']}"
    assert dataset["category"] not in (None, "unknown"), f"No category on {url}"
    assert dataset["availability"] is not None, f"No availability on {url}"

    assert dataset["description"] is not None and len(dataset["description"]) > 10, (
        f"Description too short on {url}"
    )

    assert "merchant" in dataset["custom_data"], f"No merchant in custom_data on {url}"

    json.loads(product_dataset_to_json(dataset))


def test_live_hepsiburada_product_has_reviews_and_listings(url):
    response = get_raw_html(url)
    assert response.status_code == 200, f"Request failed for {url}: {response.status_code}"

    soup = parse_html(response.content)
    dataset = extract_product_dataset(soup)

    assert dataset["custom_data"].get("reviews") is not None, f"No reviews on {url}"

    listings = dataset["custom_data"].get("listings")
    assert listings is None or (isinstance(listings, list) and len(listings) > 0), (
        f"Unexpected listings on {url}: {listings}"
    )
