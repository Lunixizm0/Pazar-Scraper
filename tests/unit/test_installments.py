from scrape.utils import trendyol


def test_installment_plan_uses_trendyol_response_field_names(monkeypatch):
    monkeypatch.setattr(
        "scrape.utils.trendyol.api.get_installment_from_api",
        lambda *args: {
            "result": {
                "installmentOffers": [
                    {
                        "issuerName": "Test Bank",
                        "installements": [
                            {
                                "term": 12,
                                "interestRate": 29.16,
                                "totalTermPrice": 181.8,
                                "totalPrice": 2181.61,
                            }
                        ],
                    }
                ]
            }
        },
    )
    shared_props = {
        "product": {
            "category": {"id": 448},
            "merchantListing": {
                "winnerVariant": {"price": {"sellingPrice": {"value": 1689}}}
            },
        }
    }

    result = trendyol._build_installments({}, shared_props)

    assert result == {
        "offers": [
            {
                "bank": "Test Bank",
                "plans": [
                    {
                        "term": 12,
                        "monthly_fee": 181.8,
                        "total_price": 2181.61,
                        "interest_rate": 29.16,
                    }
                ],
            }
        ]
    }
