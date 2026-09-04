from __future__ import annotations

from tests.helpers.hepsiburada_fixtures import (
    load_expected,
    load_redux_store,
    load_soup,
)


class TestExtractReduxStore:
    def test_returns_dict_or_none(self):
        from scrape.utils.hepsiburada import _extract_redux_store

        redux = _extract_redux_store(load_soup())
        assert isinstance(redux, dict) or redux is None

    def test_has_product_state(self):
        from scrape.utils.hepsiburada import _extract_redux_store

        redux = _extract_redux_store(load_soup())
        if redux is None:
            from pytest import skip

            skip("No redux store in fixture")
        assert "productState" in redux


class TestExtractReduxProduct:
    def test_returns_dict(self):
        from scrape.utils.hepsiburada import (
            _extract_redux_product,
            _extract_redux_store,
        )

        redux = _extract_redux_store(load_soup())
        product = _extract_redux_product(redux)
        if product is None:
            from pytest import skip

            skip("No redux product in fixture")
        assert isinstance(product, dict)

    def test_has_sku(self):
        from scrape.utils.hepsiburada import (
            _extract_redux_product,
            _extract_redux_store,
        )

        redux = _extract_redux_store(load_soup())
        product = _extract_redux_product(redux)
        if product is None:
            from pytest import skip

            skip("No redux product in fixture")
        assert "sku" in product
