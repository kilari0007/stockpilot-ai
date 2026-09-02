import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from .config import settings
from .db import Base, SessionLocal, engine
from .models import PaperPosition, Signal, WatchlistItem
from .schemas import PositionClose, PositionCreate, PositionOut, ScanRequest, SignalOut, UniverseScanRequest, WatchlistUpdate
from .services.earnings import upcoming_earnings
from .services.market import history
from .services.strategy import evaluate
from .universes import UNIVERSES

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    scheduler=AsyncIOScheduler(timezone="America/New_York")
    scheduler.add_job(scheduled_scan,CronTrigger(day_of_week="mon-fri",hour=16,minute=30),id="daily-watchlist-scan",replace_existing=True)
    scheduler.start(); yield; scheduler.shutdown(wait=False)

app=FastAPI(title=settings.app_name,version="0.2.0",lifespan=lifespan)
allowed_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials="*" not in allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

def db():
    session=SessionLocal()
    try: yield session
    finally: session.close()

def persist_signal(result:dict,session:Session):
    keys=("ticker","label","confidence","price","entry_low","entry_high","stop","target","rationale")
    row=Signal(**{k:result[k] for k in keys}); session.add(row); session.commit(); session.refresh(row); return row

async def run_scan(tickers:list[str],session:Session,provided:dict|None=None):
    earnings=provided or await upcoming_earnings(tickers)
    spy=await history("SPY"); data=await asyncio.gather(*(history(t) for t in tickers),return_exceptions=True); results=[]
    for ticker,bars in zip(tickers,data):
        if isinstance(bars,Exception): results.append({"ticker":ticker,"error":str(bars)}); continue
        result=evaluate(ticker,bars,spy,earnings.get(ticker)); persist_signal(result,session); results.append(result)
    return results

async def scheduled_scan():
    session=SessionLocal()
    try:
        tickers=[x.ticker for x in session.scalars(select(WatchlistItem)).all()]
        if tickers: await run_scan(tickers,session)
    finally: session.close()

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
        results=await run_scan(tickers,session,body.earnings_dates or None)
        return {"count":len(results),"results":results}
    except Exception as exc: raise HTTPException(502,f"Scanner unavailable: {exc}") from exc

@app.get("/api/v1/universes")
def universes():
    return [{"id":key,"name":value["name"],"description":value["description"],"size":len(value["tickers"])} for key,value in UNIVERSES.items()]

@app.post("/api/v1/scan/universe")
async def scan_universe(body:UniverseScanRequest,session:Session=Depends(db)):
    universe=UNIVERSES.get(body.universe)
    if not universe: raise HTTPException(404,"Unknown scanner universe")
    tickers=universe["tickers"]
    try:
        results=await run_scan(tickers,session)
        valid=[item for item in results if not item.get("error")]
        rank={"STRONG BUY":3,"BUY":2,"WATCH":1,"AVOID":0}
        ranked=sorted(valid,key=lambda item:(rank.get(item["label"],0),item["confidence"]),reverse=True)[:body.top_n]
        return {"universe":body.universe,"universe_name":universe["name"],"scanned":len(tickers),"successful":len(valid),"count":len(ranked),"results":ranked}
    except Exception as exc: raise HTTPException(502,f"Universe scanner unavailable: {exc}") from exc

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

@app.get("/api/v1/watchlist")
def get_watchlist(session:Session=Depends(db)): return {"tickers":[x.ticker for x in session.scalars(select(WatchlistItem).order_by(WatchlistItem.ticker)).all()]}

@app.put("/api/v1/watchlist")
def save_watchlist(body:WatchlistUpdate,session:Session=Depends(db)):
    tickers=list(dict.fromkeys(t.upper().strip() for t in body.tickers if t.strip()))[:25]
    for row in session.scalars(select(WatchlistItem)).all(): session.delete(row)
    session.add_all([WatchlistItem(ticker=t) for t in tickers]); session.commit()
    return {"tickers":tickers,"scheduled_scan":"4:30 PM America/New_York, weekdays"}

@app.get("/api/v1/earnings")
async def earnings(tickers:str):
    symbols=[x.strip().upper() for x in tickers.split(",") if x.strip()][:25]
    return {k:v.isoformat() for k,v in (await upcoming_earnings(symbols)).items()}
