from pydantic import BaseModel
from typing import Optional

class CustomerResponse(BaseModel):
    id: int
    full_name: str
    sex: str
    age: int
    marital_status: str
    income: float
    telephone: str
    email: Optional[str]
    mobile: Optional[str]
    foreign_worker: str

    class Config:
        orm_mode = True
