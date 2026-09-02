import asyncio
from datetime import date, datetime, timedelta, timezone
import httpx

async def upcoming_earnings(tickers:list[str],days:int=14)->dict[str,datetime]:
    wanted={t.upper() for t in tickers}; found={}
    headers={"User-Agent":"Mozilla/5.0","Accept":"application/json, text/plain, */*","Origin":"https://www.nasdaq.com","Referer":"https://www.nasdaq.com/"}
    async with httpx.AsyncClient(headers=headers,timeout=20) as client:
        async def one(day:date):
            r=await client.get("https://api.nasdaq.com/api/calendar/earnings",params={"date":day.isoformat()}); r.raise_for_status()
            rows=((r.json().get("data") or {}).get("rows") or [])
            return day,rows
        batches=await asyncio.gather(*(one(date.today()+timedelta(days=i)) for i in range(days+1)),return_exceptions=True)
    for item in batches:
        if isinstance(item,Exception): continue
        day,rows=item
        for row in rows:
            symbol=(row.get("symbol") or "").upper()
            if symbol in wanted: found[symbol]=datetime.combine(day,datetime.min.time(),tzinfo=timezone.utc)
    return found
