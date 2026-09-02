# API

- `GET /health` — service health and version
- `GET /api/v1/strategy` — frozen strategy metadata
- `GET /api/v1/analyze/{ticker}` — latest explainable signal, entry, stop, target, confidence, and rationale
- `POST /api/v1/scan` — scan up to 25 tickers and persist results
- `GET /api/v1/signals` — signal journal
- `POST/GET /api/v1/positions` — open/list paper positions
- `POST /api/v1/positions/{id}/close` — close a paper position
- `GET /api/v1/performance` — realized paper statistics
- Interactive OpenAPI documentation: `/docs`
