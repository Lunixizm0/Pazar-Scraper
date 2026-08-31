import argparse
import json
from urllib.parse import urlparse

from scrape.utils.trendyol import extract_product_dataset, get_raw_html, parse_html


def detect_provider(url: str) -> str:
    hostname = urlparse(url).netloc.lower()
    if "trendyol.com" in hostname:
        return "trendyol"
    if "hepsiburada.com" in hostname:
        return "hepsiburada"
    raise ValueError(f"Desteklenmeyen site: {url}")


def scrape_trendyol(url: str) -> dict:
    response = get_raw_html(url)
    if response.status_code != 200:
        raise RuntimeError(f"Trendyol URL isteği başarısız: {response.status_code}")

    soup = parse_html(response.content)
    dataset = extract_product_dataset(soup)
    if dataset is None:
        raise RuntimeError(f"Trendyol ürün verisi bulunamadı: {url}")

    if hasattr(dataset, "to_dict"):
        return dataset.to_dict()
    return json.loads(json.dumps(dataset, ensure_ascii=False))


def scrape_hepsiburada(url: str) -> dict:
    raise NotImplementedError(
        f"Hepsiburada desteği henüz yok: {url}. Şimdilik sadece Trendyol destekleniyor.")


def _dispatch(url: str) -> dict:
    provider = detect_provider(url)
    if provider == "trendyol":
        return scrape_trendyol(url)
    if provider == "hepsiburada":
        return scrape_hepsiburada(url)
    raise ValueError(f"Desteklenmeyen provider: {provider}")


def main() -> None:
    parser = argparse.ArgumentParser(description="URL bazlı ürün scraper CLI")
    parser.add_argument("url", help="Scrape edilecek ürün URL'si")
    args = parser.parse_args()

    try:
        payload = _dispatch(args.url)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    except Exception as exc:
        raise SystemExit(str(exc)) from exc

if __name__ == "__main__":
    main()