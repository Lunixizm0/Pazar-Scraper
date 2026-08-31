import argparse
import json
from urllib.parse import urlparse

from scrape.dataset import ProductDataset
from scrape.utils.hepsiburada import (
    extract_product_dataset as extract_hepsiburada_dataset,
)
from scrape.utils.hepsiburada import (
    get_raw_html as get_hepsiburada_html,
)
from scrape.utils.trendyol import extract_product_dataset, get_raw_html, parse_html


def detect_provider(url: str) -> str:
    hostname = urlparse(url).netloc.lower()
    if "trendyol.com" in hostname:
        return "trendyol"
    if "hepsiburada.com" in hostname:
        return "hepsiburada"
    raise ValueError(f"Unsupported site: {url}")


def scrape_trendyol(url: str) -> dict:
    response = get_raw_html(url)
    if response.status_code != 200:
        raise RuntimeError(f"Trendyol request failed: {response.status_code}")

    soup = parse_html(response.content)
    dataset = extract_product_dataset(soup)
    if dataset is None:
        raise RuntimeError(f"Trendyol product data not found: {url}")

    if isinstance(dataset, ProductDataset):
        return dataset.to_dict()
    return json.loads(json.dumps(dataset, ensure_ascii=False))


def scrape_hepsiburada(url: str) -> dict:
    response = get_hepsiburada_html(url)
    if response.status_code != 200:
        raise RuntimeError(f"Hepsiburada request failed: {response.status_code}")

    soup = parse_html(response.content)
    dataset = extract_hepsiburada_dataset(soup)
    if dataset is None:
        raise RuntimeError(f"Hepsiburada product data not found: {url}")

    if isinstance(dataset, ProductDataset):
        return dataset.to_dict()
    return json.loads(json.dumps(dataset, ensure_ascii=False))


def _dispatch(url: str) -> dict:
    provider = detect_provider(url)
    if provider == "trendyol":
        return scrape_trendyol(url)
    if provider == "hepsiburada":
        return scrape_hepsiburada(url)
    raise ValueError(f"Unsupported provider: {provider}")


def main() -> None:
    parser = argparse.ArgumentParser(description="URL-based product scraper CLI")
    parser.add_argument("url", help="Product URL to scrape")
    args = parser.parse_args()

    try:
        payload = _dispatch(args.url)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    except Exception as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
