from pydantic import BaseModel, Field
from typing import Optional


class TransportBase(BaseModel):
    name: str
    description: str
    category: str
    location: str
    price_per_day: float = Field(..., gt=0)
    year: Optional[int] = None
    model: Optional[str] = None
    capacity: Optional[str] = None
    image_url: Optional[str] = None


class TransportCreate(TransportBase):
    pass


class TransportUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    price_per_day: Optional[float] = Field(None, gt=0)
    available: Optional[bool] = None
    year: Optional[int] = None
    model: Optional[str] = None
    capacity: Optional[str] = None
    image_url: Optional[str] = None


class TransportResponse(TransportBase):
    id: int
    available: bool
    owner_id: int

    class Config:
        from_attributes = True


class TransportFilter(BaseModel):
    location: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None 