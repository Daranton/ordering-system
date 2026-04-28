from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from src.utils.models import OrderStatus

# Sits at API boundary layer - how orders enter & leave the API.
# answers the question: "is this valid status and data structure?"
class OrderItemSchema(BaseModel):
    product_name: str = Field(min_length=1, max_length=200)
    quantity: int = Field(gt=0) # gt - greater than
    unit_price: float = Field(gt=0)

# POST request
class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=100)
    items: list[OrderItemSchema] = Field(min_length=1)
    
# PATCH request
class OrderUpdate(BaseModel):
    status: OrderStatus | None = None

    @field_validator("status", mode="before")
    @classmethod
    def normalise_status(cls, v: str | OrderStatus | None) -> str | OrderStatus | None:
        if isinstance(v, str):
            return v.lower()
        return v

class OrderResponse(BaseModel):
    id: str
    customer_name: str
    items: list[OrderItemSchema]
    status: OrderStatus
    total: float
    created_at: datetime
