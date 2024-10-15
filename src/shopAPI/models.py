from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import ConfigDict
from sqlmodel import Field, SQLModel
from shopAPI.database import IdMixin


class ApiStatus(SQLModel):
    name: str = Field(...)
    version: str = Field(...)
    status: str = Field(...)
    message: str = Field(...)
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "ShopAPI",
                    "version": "1.0.0",
                    "status": "OK",
                    "message": "Visit /swagger for documentation.",
                },
            ]
        }
    )


class ResponseMessage(SQLModel):
    detail: str


def field_example(param: Any) -> Dict[str, Dict[str, Any]]:
    """
    Returns field example for swagger documentation

    It's a workaround for SQLModel bug,
    see https://github.com/tiangolo/sqlmodel/discussions/833
    """
    return {"schema_extra": {"json_schema_extra": {"example": param}}}


class ProductBase(SQLModel):
    name: str = Field(nullable=False, **field_example("Product"))
    description: str = Field(nullable=False, **field_example("A simple product"))
    price: float = Field(nullable=False, **field_example(128.99))
    amount: int = Field(nullable=False, **field_example(100))

    model_config = ConfigDict(extra="forbid")


class Product(IdMixin, ProductBase, table=True):
    __tablename__ = "product"


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    # TODO check examples with https://fastapi.tiangolo.com/tutorial/schema-extra-example/#body-with-examples
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Updated product",
                    "description": "A simple updated product",
                    "price": 256.99,
                    "amount": 200,
                }
            ]
        }
    )


class ProductResponse(ProductBase):
    id: UUID
