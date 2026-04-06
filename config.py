"""
Configuration for Indian Equity Technical Dashboard
"""

# Watchlist - NSE tickers (Yahoo Finance format: SYMBOL.NS)
WATCHLIST = [
    "CUMMINSIND.NS",
    "APARINDS.NS",
    "LUMAXTECH.NS",
    "MTARTECH.NS",
    "EICHERMOT.NS",
    "M&M.NS",
    "TDPOWERSYS.NS"
]

# EMA periods (in weeks)
EMA_PERIODS = {
    "10W": 10,
    "20W": 20,
    "40W": 40
}

# Signal thresholds
NEAR_40W_THRESHOLD = 0.03  # 3% proximity to 40W EMA triggers amber flag

# Data fetch parameters
WEEKLY_INTERVAL = "1wk"
LOOKBACK_PERIOD = "2y"  # 2 years ensures sufficient data for 40W EMA (40 weeks ≈ 10 months)
