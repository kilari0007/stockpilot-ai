from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SignalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int | None = None
    ticker: str; label: str; confidence: float; price: float
    entry_low: float; entry_high: float; stop: float; target: float
    rationale: str; created_at: datetime | None = None

class ScanRequest(BaseModel):
    tickers: list[str]
    earnings_dates: dict[str, datetime] = {}

class PositionCreate(BaseModel):
    ticker: str; entry: float; quantity: float; stop: float; target: float

class PositionClose(BaseModel):
    exit_price: float

class PositionOut(PositionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int; status: str; exit_price: float | None = None
    opened_at: datetime; closed_at: datetime | None = None
