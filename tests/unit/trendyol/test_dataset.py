from __future__ import annotations

import json

from scrape.dataset import ProductDataset


class TestProductDatasetToJson:
    def test_returns_valid_json(self):
        from scrape.utils.trendyol import product_dataset_to_json

        ds = ProductDataset(source="trendyol", name="Test", price="100.00 TL")
        result = product_dataset_to_json(ds)
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["source"] == "trendyol"

    def test_preserves_unicode(self):
        from scrape.utils.trendyol import product_dataset_to_json

        ds = ProductDataset(source="trendyol", name="Ürün Testi İçi")
        result = product_dataset_to_json(ds)
        parsed = json.loads(result)
        assert parsed["name"] == "Ürün Testi İçi"

    def test_empty_custom_data(self):
        from scrape.utils.trendyol import product_dataset_to_json

        ds = ProductDataset(source="trendyol")
        result = product_dataset_to_json(ds)
        parsed = json.loads(result)
        assert parsed["custom_data"] == {}

    def test_roundtrip(self):
        from scrape.utils.trendyol import product_dataset_to_json

        ds = ProductDataset(
            source="trendyol",
            name="Test Product",
            price="99.99 TL",
            currency="TRY",
            custom_data={"key": "value"},
        )
        result = product_dataset_to_json(ds)
        ds2 = ProductDataset(**json.loads(result))
        assert ds2.source == ds.source
        assert ds2.name == ds.name
        assert ds2.price == ds.price
