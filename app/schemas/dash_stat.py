from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime, date

class DashStatBase(BaseModel):
    name: str
    start_date: date
    end_date: date

class DashStatCreate(DashStatBase):
    pass

class DashStatUpdate(DashStatBase):
    id: int
    stats: Dict
    date_created: datetime
    date_updated: datetime

class DashStatResponse(DashStatBase):
    id: int
    processing: bool
    stats: Optional[Dict] = None
    date_created: datetime
    date_updated: datetime

    class Config:
        orm_mode = True