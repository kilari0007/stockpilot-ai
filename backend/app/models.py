from datetime import datetime
from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class Signal(Base):
    __tablename__ = "signals"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(12), index=True)
    label: Mapped[str] = mapped_column(String(20))
    confidence: Mapped[float] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float)
    entry_low: Mapped[float] = mapped_column(Float)
    entry_high: Mapped[float] = mapped_column(Float)
    stop: Mapped[float] = mapped_column(Float)
    target: Mapped[float] = mapped_column(Float)
    rationale: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

