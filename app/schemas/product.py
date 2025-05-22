import re

from pydantic import BaseModel, Field, field_validator


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    sku: str = Field(..., min_length=5, max_length=9)
    price: float = Field(..., gt=0)

    @field_validator('sku')
    @classmethod
    def validate_sku(cls, value):
        if not re.match(r'^[A-Z]+-\d+$', value):
            raise ValueError('SKU must be in the format CATEGORY-NUMBER (e.g., TECH-001).')
        return value.upper()

    @field_validator('price')
    @classmethod
    def validate_price(cls, value):
        value = round(value, 2)

        if value > 10000:
            raise ValueError('Price cannot exceed $10,000.')
        return value
