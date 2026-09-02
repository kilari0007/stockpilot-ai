import numpy as np
import pandas as pd

def indicators(df: pd.DataFrame) -> pd.DataFrame:
    d=df.copy(); prev=d.close.shift(1)
    tr=pd.concat([d.high-d.low,(d.high-prev).abs(),(d.low-prev).abs()],axis=1).max(axis=1)
    d["atr"]=tr.ewm(alpha=1/14,adjust=False,min_periods=14).mean()
    delta=d.close.diff(); gain=delta.clip(lower=0).ewm(alpha=1/14,adjust=False,min_periods=14).mean(); loss=(-delta.clip(upper=0)).ewm(alpha=1/14,adjust=False,min_periods=14).mean()
    d["rsi"]=100-100/(1+gain/loss); d["ema20"]=d.close.ewm(span=20,adjust=False).mean()
    d["sma50"]=d.close.rolling(50).mean(); d["sma200"]=d.close.rolling(200).mean(); d["v20"]=d.volume.rolling(20).mean()
    return d

def evaluate(ticker: str, stock: pd.DataFrame, spy: pd.DataFrame, earnings_date=None) -> dict:
    d=indicators(stock); m=indicators(spy); x,y=d.iloc[-1],d.iloc[-2]; sx=m.iloc[-1]
    checks={
        "market regime": sx.close>sx.sma200 and sx.sma50>sx.sma200,
        "stock trend": x.close>x.sma200 and x.sma50>x.sma200,
        "EMA20 pullback": y.low<=1.01*y.ema20 and y.close>=y.ema20,
        "RSI 45–60": 45<=y.rsi<=60,
        "price confirmation": x.close>y.high,
        "volume confirmation": x.volume>=1.25*x.v20,
        "liquidity": x.close>=10 and x.close*x.v20>=20_000_000,
    }
    checks["gap safety"]=abs(x.open-y.close)<=x.atr
    checks["earnings safety"]=earnings_date is None or abs((earnings_date.date()-d.index[-1].date()).days)>7
    passed=sum(checks.values()); confidence=round(100*passed/len(checks))
    label="STRONG BUY" if passed==len(checks) else "WATCH" if passed>=6 else "AVOID"
    risk=2*x.atr; entry_low=x.close*.998; entry_high=x.close*1.002
    return {"ticker":ticker.upper(),"label":label,"confidence":confidence,"price":float(round(x.close,2)),"entry_low":float(round(entry_low,2)),"entry_high":float(round(entry_high,2)),"stop":float(round(x.close-risk,2)),"target":float(round(x.close+.75*risk,2)),"rationale":", ".join(k for k,v in checks.items() if v),"warnings":[k for k,v in checks.items() if not v]}
