from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db import Base, engine
from .services.market import history
from .services.strategy import evaluate

app=FastAPI(title=settings.app_name,version="0.1.0")
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins.split(","),allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

@app.on_event("startup")
def startup(): Base.metadata.create_all(engine)

@app.get("/health")
def health(): return {"status":"healthy","version":"0.1.0"}

@app.get("/api/v1/strategy")
def strategy(): return {"name":"Swing Pullback V2","historical_win_rate":60.0,"profit_factor":1.14,"risk_per_trade":0.5,"status":"paper-trading","disclaimer":"Historical results do not guarantee future performance."}

@app.get("/api/v1/analyze/{ticker}")
async def analyze(ticker: str):
    try: return evaluate(ticker,await history(ticker),await history("SPY"))
    except Exception as exc: raise HTTPException(502,f"Market data unavailable: {exc}") from exc

