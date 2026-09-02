from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SignalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int | None = None
    ticker: str; label: str; confidence: float; price: float
    entry_low: float; entry_high: float; stop: float; target: float
    rationale: str; created_at: datetime | None = None

