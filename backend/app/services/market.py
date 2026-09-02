from datetime import datetime, timedelta, timezone
import httpx, pandas as pd

async def history(ticker: str, days: int=430) -> pd.DataFrame:
    now=datetime.now(timezone.utc); start=now-timedelta(days=days)
    url=f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    params={"period1":int(start.timestamp()),"period2":int(now.timestamp()),"interval":"1d","events":"div,splits"}
    async with httpx.AsyncClient(headers={"User-Agent":"Mozilla/5.0"},timeout=20) as client:
        r=await client.get(url,params=params); r.raise_for_status(); z=r.json()["chart"]["result"][0]
    q=z["indicators"]["quote"][0]
    return pd.DataFrame(q,index=pd.to_datetime(z["timestamp"],unit="s")).dropna().rename_axis("date")

