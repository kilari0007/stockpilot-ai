import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session
from .config import settings
from .db import Base, SessionLocal, engine
from .models import PaperPosition, Signal
from .schemas import PositionClose, PositionCreate, PositionOut, ScanRequest, SignalOut
from .services.market import history
from .services.strategy import evaluate

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine); yield

app=FastAPI(title=settings.app_name,version="0.2.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins.split(","),allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

def db():
    session=SessionLocal()
    try: yield session
    finally: session.close()

def persist_signal(result:dict,session:Session):
    keys=("ticker","label","confidence","price","entry_low","entry_high","stop","target","rationale")
    row=Signal(**{k:result[k] for k in keys}); session.add(row); session.commit(); session.refresh(row); return row

@app.get("/health")
def health(): return {"status":"healthy","version":"0.2.0"}

@app.get("/api/v1/strategy")
def strategy(): return {"name":"Swing Pullback V2","historical_win_rate":60.0,"profit_factor":1.14,"risk_per_trade":0.5,"status":"paper-trading","disclaimer":"Historical results do not guarantee future performance."}

@app.get("/api/v1/analyze/{ticker}")
async def analyze(ticker:str,session:Session=Depends(db)):
    try: return persist_signal(evaluate(ticker,await history(ticker),await history("SPY")),session)
    except Exception as exc: raise HTTPException(502,f"Market data unavailable: {exc}") from exc

@app.post("/api/v1/scan")
async def scan(body:ScanRequest,session:Session=Depends(db)):
    tickers=list(dict.fromkeys(t.upper().strip() for t in body.tickers if t.strip()))[:25]
    if not tickers: raise HTTPException(400,"At least one ticker is required")
    try:
        spy=await history("SPY"); data=await asyncio.gather(*(history(t) for t in tickers),return_exceptions=True); results=[]
        for ticker,bars in zip(tickers,data):
            if isinstance(bars,Exception): results.append({"ticker":ticker,"error":str(bars)}); continue
            result=evaluate(ticker,bars,spy,body.earnings_dates.get(ticker)); persist_signal(result,session); results.append(result)
        return {"count":len(results),"results":results}
    except Exception as exc: raise HTTPException(502,f"Scanner unavailable: {exc}") from exc

@app.get("/api/v1/signals",response_model=list[SignalOut])
def signals(limit:int=50,session:Session=Depends(db)):
    return session.scalars(select(Signal).order_by(Signal.created_at.desc()).limit(min(limit,200))).all()

@app.post("/api/v1/positions",response_model=PositionOut)
def open_position(body:PositionCreate,session:Session=Depends(db)):
    if body.quantity<=0 or not body.stop<body.entry<body.target: raise HTTPException(400,"Require quantity > 0 and stop < entry < target")
    if len(session.scalars(select(PaperPosition).where(PaperPosition.status=="OPEN")).all())>=5: raise HTTPException(409,"Maximum five open paper positions")
    values=body.model_dump(); values["ticker"]=body.ticker.upper(); row=PaperPosition(**values)
    session.add(row); session.commit(); session.refresh(row); return row

@app.get("/api/v1/positions",response_model=list[PositionOut])
def positions(session:Session=Depends(db)): return session.scalars(select(PaperPosition).order_by(PaperPosition.opened_at.desc())).all()

@app.post("/api/v1/positions/{position_id}/close",response_model=PositionOut)
def close_position(position_id:int,body:PositionClose,session:Session=Depends(db)):
    row=session.get(PaperPosition,position_id)
    if not row or row.status!="OPEN": raise HTTPException(404,"Open position not found")
    row.exit_price=body.exit_price; row.status="CLOSED"; row.closed_at=datetime.utcnow(); session.commit(); session.refresh(row); return row

@app.get("/api/v1/performance")
def performance(session:Session=Depends(db)):
    rows=session.scalars(select(PaperPosition).where(PaperPosition.status=="CLOSED")).all(); pnl=[(r.exit_price-r.entry)*r.quantity for r in rows]
    wins=[x for x in pnl if x>0]; losses=[x for x in pnl if x<=0]
    return {"closed_trades":len(rows),"win_rate":round(100*len(wins)/len(rows),1) if rows else 0,"realized_pnl":round(sum(pnl),2),"profit_factor":round(sum(wins)/abs(sum(losses)),2) if losses and sum(losses) else None}
