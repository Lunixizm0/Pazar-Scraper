import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProductDataset:
    source: str
    category: str = "unknown"
    name: str | None = None
    brand: str | None = None
    price: str | None = None
    currency: str | None = None
    url: str | None = None
    sku: str | None = None
    image: str | None = None
    description: str | None = None
    availability: str | None = None
    item_condition: str | None = None
    reviews: dict[str, Any] | None = None
    vas: list[Any] | None = None
    installments: dict[str, Any] | None = None
    custom_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "category": self.category,
            "name": self.name,
            "brand": self.brand,
            "price": self.price,
            "currency": self.currency,
            "url": self.url,
            "sku": self.sku,
            "image": self.image,
            "description": self.description,
            "availability": self.availability,
            "item_condition": self.item_condition,
            "reviews": self.reviews,
            "vas": self.vas,
            "installments": self.installments,
            "custom_data": self.custom_data,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)
