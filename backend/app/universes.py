UNIVERSES: dict[str, dict[str, object]] = {
    "sp100": {
        "name": "Top 100 US Large Caps",
        "description": "A liquid large-cap universe based on S&P 100-style constituents.",
        "tickers": [
            "AAPL","ABBV","ABT","ACN","ADBE","AIG","AMD","AMGN","AMT","AMZN",
            "AVGO","AXP","BA","BAC","BK","BKNG","BLK","BMY","BRK-B","C",
            "CAT","CHTR","CL","CMCSA","COF","COP","COST","CRM","CSCO","CVS",
            "CVX","DE","DHR","DIS","DUK","EMR","EXC","F","FDX","GD",
            "GE","GILD","GM","GOOG","GOOGL","GS","HD","HON","IBM","INTC",
            "INTU","JNJ","JPM","KO","LIN","LLY","LMT","LOW","MA","MCD",
            "MDLZ","MDT","MET","META","MMM","MO","MRK","MS","MSFT","NEE",
            "NFLX","NKE","NOW","NVDA","ORCL","PEP","PFE","PG","PLTR","PM",
            "PYPL","QCOM","RTX","SBUX","SCHW","SO","SPG","T","TGT","TMO",
            "TMUS","TSLA","TXN","UNH","UNP","UPS","USB","V","VZ","WMT",
        ],
    },
    "mega_cap": {
        "name": "Mega Cap Leaders",
        "description": "Highly liquid US market leaders for faster scans.",
        "tickers": ["AAPL","MSFT","NVDA","AMZN","GOOGL","META","AVGO","TSLA","BRK-B","LLY","JPM","V","WMT","MA","ORCL","NFLX","COST","XOM","JNJ","HD","PG","ABBV","BAC","KO","CRM"],
    },
    "ai_semis": {
        "name": "AI & Semiconductors",
        "description": "AI infrastructure, chips, networking, and data-center leaders.",
        "tickers": ["NVDA","AMD","AVGO","TSM","ASML","MU","ARM","QCOM","MRVL","AMAT","LRCX","KLAC","SMCI","ANET","CRDO","ALAB","DELL","HPE","ORCL","MSFT","GOOGL","AMZN","META","PLTR","SNOW"],
    },
    "growth": {
        "name": "High Growth",
        "description": "Liquid growth companies with higher volatility and opportunity.",
        "tickers": ["PLTR","RKLB","RDDT","HOOD","COIN","SHOP","SOFI","HIMS","CRWD","NET","DDOG","SNOW","MDB","APP","DUOL","CAVA","CELH","NU","MELI","SE","UBER","ABNB","DASH","TTD","TOST"],
    },
}
