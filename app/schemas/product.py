from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    duration: int
    purpose: str
    credit_amount: int
    filters: Optional[Dict] = None  # JSONB field for storing array of filter objects
    eligible_customers: Optional[List[Dict]] = None  # JSONB field for storing array of customer objects

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    id: int
    date_created: Optional[datetime] = None
    date_updated: Optional[datetime] = None
    pass

class ProductResponse(ProductBase):
    id: int
    date_created: datetime
    date_updated: datetime
    processing: bool

    class Config:
        orm_mode = True
