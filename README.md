# StockPilot AI

Personal, explainable trading dashboard using React + Vite and FastAPI. Version 1 is read-only and requires manual confirmation before any broker order.

## Quick start

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

Frontend (second terminal):

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. API docs are at http://localhost:8000/docs.

## Version 2 strategy

- Long-only swing pullback
- SPY and stock above 200-day SMA; 50-day SMA above 200-day SMA
- Prior-day low within 1% of EMA20, close above EMA20, RSI(14) 45–60
- Confirmation close above prior high with volume at least 125% of 20-day average
- Minimum price $10 and average daily dollar volume $20M
- Stop 2 ATR; target 0.75R; maximum hold 20 sessions
- Reject signals near earnings or when entry gaps more than 1 ATR

The preliminary validation produced a 60% win rate and 1.14 profit factor. Historical results are not guarantees.

