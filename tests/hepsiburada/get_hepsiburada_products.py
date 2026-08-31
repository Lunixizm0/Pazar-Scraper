import re

import requests


def _normalize_hepsiburada_product_url(value):
    value = (value or "").strip()
    if not value:
        return None

    value = value.split("#", 1)[0].split("?", 1)[0].strip("\"'")

    if value.startswith(("http://", "https://")):
        url = value
    elif value.startswith("/"):
        url = f"https://www.hepsiburada.com{value}"
    else:
        url = f"https://www.hepsiburada.com/{value.lstrip('/')}"

    url = url.replace("https://www.hepsiburada.com:443", "https://www.hepsiburada.com")
    return url.rstrip("/")


def _is_product_url(url):
    return bool(re.search(r"[-/](?:p|pm)-[A-Za-z0-9]+$", url))


def get_full_product_urls_from_homepage(limit=5):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:154.0) Gecko/20100101 Firefox/154.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        response = requests.get(
            "https://www.hepsiburada.com", headers=headers, timeout=30
        )
        if response.status_code != 200:
            return []

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(response.text, "html.parser")
        seen = set()
        urls = []
        for a in soup.find_all("a", href=True):
            normalized = _normalize_hepsiburada_product_url(a["href"])
            if not normalized or not _is_product_url(normalized):
                continue
            if normalized in seen:
                continue
            seen.add(normalized)
            urls.append(normalized)
            if len(urls) >= limit:
                break

        return urls
    except Exception as e:
        print(f"Error fetching product URLs from homepage: {e}")
        return []


if __name__ == "__main__":
    print("Fetching products from Hepsiburada homepage...\n")
    urls = get_full_product_urls_from_homepage(limit=5)
    if urls:
        print(f"Found {len(urls)} full product URLs:")
        for url in urls:
            print(f"  - {url}")
    else:
        print("No product URLs found")
