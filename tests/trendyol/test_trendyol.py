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
        urls = get_full_product_urls_from_homepage(limit=5)
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
    assert dataset is not None
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
    assert dataset is not None

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

# TODO: Get the 'hardcoded test data' from a live product instead of using fixed values.
# Test data from a live Xiaomi product page (contentId=1081766367, sellerId=624588, groupId=821600500)
LIVE_PRODUCT_ID = "1081766367"
LIVE_SELLER_ID = "624588"
LIVE_GROUP_ID = "821600500"
LIVE_LISTING_ID = "e6e8fd8c3d61815b470afae19defb73a"
LIVE_ITEM_NUMBER = "1494882815"
LIVE_VIDEO_ID = "6d1ee37d-be18-4bf1-a17f-464d7c2a3643"


# review-read/product-reviews/detailed
def test_real_review_read_api():
    from scrape.utils.trendyol import get_reviews_from_api

    data = get_reviews_from_api(LIVE_PRODUCT_ID)
    assert data is not None, "review-read API returned None"
    assert data.get("isSuccess") is True
    result = data.get("result", {})
    assert "summary" in result
    summary = result["summary"]
    assert "averageRating" in summary
    assert summary["averageRating"] > 0
    assert "totalRatingCount" in summary
    assert "ratingCounts" in summary
    assert isinstance(summary["ratingCounts"], list)
    assert "tags" in summary
    assert "reviews" in result
    assert isinstance(result["reviews"], list)
    if "aiSummary" in result:
        assert isinstance(result["aiSummary"], str)


# component-read/component/{id}
def test_real_component_read_api():
    from scrape.utils.trendyol import get_product_descriptions_from_api

    text = get_product_descriptions_from_api(LIVE_PRODUCT_ID)
    assert text is not None, "component-read API returned no text"
    assert len(text) > 10
    assert isinstance(text, str)


# delivery-date-content/delivery-date/{contentId}/itemNumber/{itemNo}
def test_real_delivery_date_api():
    from scrape.utils.trendyol import get_delivery_date_from_api

    data = get_delivery_date_from_api(
        LIVE_PRODUCT_ID, LIVE_ITEM_NUMBER, LIVE_LISTING_ID
    )
    assert data is not None
    assert data.get("isSuccess") is True
    result = data.get("result", {})
    assert "deliveryDates" in result
    assert isinstance(result["deliveryDates"], list)
    assert len(result["deliveryDates"]) > 0
    first = result["deliveryDates"][0]
    assert "deliveryStartDate" in first
    assert "deliveryEndDate" in first


# installment/
def test_real_installment_api():
    from scrape.utils.trendyol import get_installment_from_api

    data = get_installment_from_api(4199, 1058, "eac211e6-2e86-42fa-a755-87479743934a")
    assert data is not None
    assert data.get("isSuccess") is True
    result = data.get("result", {})
    assert "summary" in result
    assert "installmentOffers" in result
    offers = result["installmentOffers"]
    assert isinstance(offers, list)
    assert len(offers) > 0
    first_bank = offers[0]
    assert "installements" in first_bank
    assert len(first_bank["installements"]) > 0


# 5. merchant-questions/content/{id}/answered
def test_real_merchant_questions_api():
    from scrape.utils.trendyol import get_merchant_questions_from_api

    data = get_merchant_questions_from_api(LIVE_PRODUCT_ID)
    assert data is not None
    assert data.get("isSuccess") is True
    questions = data.get("questions", {})
    assert "content" in questions
    assert "totalElements" in questions


# 6. merchant-questions/seller-acceptance
def test_real_seller_acceptance_api():
    from scrape.utils.trendyol import get_seller_acceptance_from_api

    data = get_seller_acceptance_from_api(LIVE_SELLER_ID)
    assert data is not None
    assert "isSellerAcceptQuestions" in data
    assert isinstance(data["isSellerAcceptQuestions"], bool)


# 7. video-content/{videoId}
def test_real_video_content_api():
    from scrape.utils.trendyol import get_video_content_from_api

    data = get_video_content_from_api(LIVE_VIDEO_ID)
    assert data is not None
    assert data.get("isSuccess") is True
    result = data.get("result", {})
    assert "url" in result
    assert result["url"].endswith(".mp4")
    assert "thumbnail" in result


# 8. currencies
def test_real_currencies_api():
    from scrape.utils.trendyol import get_currencies_from_api

    data = get_currencies_from_api()
    assert data is not None
    assert data.get("isSuccess") is True
    result = data.get("result", [])
    assert isinstance(result, list)
    assert len(result) > 0
    currency_names = {c["currencyName"] for c in result}
    assert "USD" in currency_names
    assert "EUR" in currency_names
    assert "TRY" in currency_names


# 9. stickers/stickers 
def test_real_stickers_api():
    from scrape.utils.trendyol import get_stickers_from_api

    data = get_stickers_from_api("1044")
    assert data is not None
    assert data.get("isSuccess") is True
    result = data.get("result", [])
    assert isinstance(result, list)


# 10. complete-the-look/markers
def test_real_complete_the_look_api():
    from scrape.utils.trendyol import get_complete_the_look_from_api

    data = get_complete_the_look_from_api(LIVE_PRODUCT_ID)
    assert data is not None
    assert data.get("isSuccess") is True
    result = data.get("result", {})
    assert "markers" in result
    assert isinstance(result["markers"], list)


# 11. slicing-attributes/product-group/{gid}/slicing-attributes
def test_real_slicing_attributes_api():
    from scrape.utils.trendyol import get_slicing_attributes_from_api

    data = get_slicing_attributes_from_api(LIVE_GROUP_ID, LIVE_PRODUCT_ID)
    assert data is not None
    assert data.get("isSuccess") is True
    result = data.get("result", [])
    assert isinstance(result, list)
    assert len(result) > 0
    first_group = result[0]
    assert "type" in first_group
    assert "values" in first_group
    assert isinstance(first_group["values"], list)


# 12. social-proof/
def test_real_social_proof_api():
    from scrape.utils.trendyol import get_social_proof_from_api

    data = get_social_proof_from_api(LIVE_PRODUCT_ID)
    assert data is not None
    assert LIVE_PRODUCT_ID in data
    proof = data[LIVE_PRODUCT_ID]
    assert "socialProofs" in proof
    assert isinstance(proof["socialProofs"], list)


    # 13. seller-store/{sid}/header-information ---
def test_real_seller_store_api():
    from scrape.utils.trendyol import get_seller_store_from_api

    data = get_seller_store_from_api(LIVE_SELLER_ID)
    assert data is not None
    assert data.get("isSuccess") is True
    result = data.get("result", {})
    assert "name" in result
    assert "score" in result
    assert "sellerMetrics" in result
    assert isinstance(result["sellerMetrics"], list)


# 14. sellerstore-follow/{sid}/follower-count
def test_real_seller_follower_api():
    from scrape.utils.trendyol import get_seller_follower_from_api

    data = get_seller_follower_from_api(LIVE_SELLER_ID)
    assert data is not None
    assert data.get("isSuccess") is True
    result = data.get("result", {})
    assert "count" in result
    assert isinstance(result["count"], int)
    assert result["count"] > 0


# 15. stamps/
def test_real_stamps_api():
    from scrape.utils.trendyol import get_stamps_from_api

    data = get_stamps_from_api("4905,8581,9637")
    assert data is not None
    assert data.get("isSuccess") is True
    result = data.get("result", {})
    assert isinstance(result, dict)
    assert len(result) > 0
    for stamp_data in result.values():
        assert "name" in stamp_data
        assert "stamps" in stamp_data


# 16. product-eligibility/
def test_real_product_eligibility_api():
    from scrape.utils.trendyol import get_product_eligibility_from_api

    data = get_product_eligibility_from_api(1058, 13, 4199)
    assert data is not None
    assert data.get("isSuccess") is True


# 17. vas/ (POST)
def test_real_vas_api_post_400_or_known_response():
    #TODO: Get the 'hardcoded test data' from a live product instead of using fixed values
    # VAS requires 5 specific body fields Verify endpoint is reachable and returns 400 with valid request format
    from scrape.utils.trendyol import get_vas_from_api

    data = get_vas_from_api()
    assert data is None
