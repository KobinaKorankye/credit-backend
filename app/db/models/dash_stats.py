from sqlalchemy import Column, Integer, String, Date, DateTime, func, Boolean, event, Numeric, select
from sqlalchemy.dialects.postgresql import JSONB

from app.db.database import Base

class DashStats(Base):
    __tablename__ = 'dash_stats'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    processing = Column(Boolean, default=False, nullable=False)
    stats = Column(JSONB, nullable=True)

    # New fields for tracking creation and update times
    date_created = Column(DateTime, default=func.now(), nullable=False)
    date_updated = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)