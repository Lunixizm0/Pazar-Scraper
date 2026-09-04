from __future__ import annotations

import pytest


class TestGetFullProductUrlsFromHomepage:
    def test_uses_best_seller_api(self, monkeypatch):
        from tests.helpers._live_helpers import get_trendyol_product_urls

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

        urls = get_trendyol_product_urls(limit=2)

        assert urls == [
            "https://www.trendyol.com/kontes/kadin-fularli-fermuarli-shopper-el-ve-omuz-cantasi-p-898198883",
            "https://www.trendyol.com/c-e-design/ultra-esnek-kopmaz-siyah-seffaf-sac-orgu-lastigi-100-adet-p-1106980689",
        ]
