# Indian Equity Technical Dashboard

Personal stock watchlist tool for NSE-listed equities with technical analysis based on Weinstein/Minervini methodology.

## Overview

This tool fetches weekly OHLC data for a customizable watchlist, computes logarithmic-scale EMAs, and identifies momentum signals. Outputs both a color-coded terminal summary and an HTML dashboard for browser viewing.

## Features

- **Weekly OHLC Data**: Fetches data from Yahoo Finance (yfinance) for NSE stocks
- **Logarithmic EMAs**: Calculates 10-week, 20-week, and 40-week EMAs on logarithmic scale
- **Signal Detection**: Identifies 40W EMA breaches (exit signals) and proximity warnings
- **Support/Resistance**: Computes 52-week high/low and 4-week pivot points
- **Dual Output**: Terminal display + HTML dashboard with color-coded status indicators
- **Browser-Friendly**: Clean, responsive HTML design for desktop and mobile viewing

## Methodology

### Weinstein/Minervini Approach

- **40-Week EMA**: Primary trend indicator. Price below 40W EMA = exit signal
- **Near 40W (within 3%)**: Caution zone - monitor for potential breakdown
- **Logarithmic Scale**: EMAs calculated on log prices for percentage-based perspective

### Why Logarithmic EMAs?

Standard EMAs weight absolute price changes equally. Logarithmic EMAs weight percentage changes equally, which is more appropriate for comparing stocks at different price levels (e.g., Rs 3000 vs Rs 100).

## Setup

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. Clone or download this project
2. Navigate to the project directory:
   ```bash
   cd "C:\Users\manoj\Documents\Projects\Indian Equity Technical Dashboard"
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Option 1: Interactive Web Dashboard (Recommended)

Start the Flask web server for an interactive dashboard:

```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

**Features:**
- 🔄 **Refresh Data**: Click "Refresh Data" button to fetch latest prices without restarting
- ✏️ **Edit Watchlist**: Add or remove tickers directly from the browser
  - Click "Edit Watchlist" to open the editor
  - Add ticker: Enter in `SYMBOL.NS` format (e.g., `RELIANCE.NS`)
  - Remove ticker: Click "❌ Remove" next to any ticker
  - Changes save automatically to `watchlist.json`
- 📊 **Real-Time Updates**: Dashboard updates without page reload
- 🎨 **Clean UI**: Color-coded status indicators with responsive design

**Runtime**: Initial load ~10-15 seconds, refresh ~10-15 seconds per request

**Stopping the Server**: Press `Ctrl+C` in the terminal

### Option 2: CLI Mode (Static HTML)

Run the command-line version for terminal output + static HTML:

```bash
python main.py
```

This will:
1. Fetch weekly data for all tickers in the watchlist
2. Calculate EMAs and technical indicators
3. Display color-coded summary tables in the terminal
4. Generate `dashboard.html` in the project root directory

**Runtime**: Approximately 10-15 seconds for 7 tickers

**Viewing the Static Dashboard:**

**Windows:**
```bash
start dashboard.html
```

**macOS:**
```bash
open dashboard.html
```

**Linux:**
```bash
xdg-open dashboard.html
```

Or simply double-click `dashboard.html` in File Explorer.

### Customizing the Watchlist

**Interactive Mode (app.py):**
- Click "Edit Watchlist" button in the dashboard
- Changes persist to `watchlist.json` automatically
- On first run, creates `watchlist.json` from `config.py`

**CLI Mode (main.py):**
Edit `config.py` and modify the `WATCHLIST` variable:

```python
WATCHLIST = [
    "CUMMINSIND.NS",
    "APARINDS.NS",
    # Add more NSE tickers here
]
```

Use Yahoo Finance ticker format: `SYMBOL.NS` for NSE stocks.

**Resetting Watchlist:**
Delete `watchlist.json` to recreate from `config.py` on next run.

## Output Explained

### EMA Summary Table

- **Price**: Current closing price (latest week)
- **10W/20W/40W EMA**: Exponential moving averages on logarithmic scale
- **Status**:
  - **BREACH** (Red): Price below 40W EMA - exit signal
  - **NEAR** (Amber): Price within 3% of 40W EMA - caution zone
  - **ABOVE** (Green): Price > 3% above 40W EMA - safe zone
- **Dist%**: Percentage distance from 40W EMA

### Support/Resistance Table

- **52W High/Low**: Highest high and lowest low over past 52 weeks
- **Pivot High/Low**: Local high/low from last 4 weeks
- **Current vs 52W**: How far current price is from 52-week high

## Troubleshooting

### "Failed to fetch ticker" errors

- **Check ticker symbol**: Ensure format is correct (e.g., `CUMMINSIND.NS`, not `CUMMINSIND`)
- **Network connection**: Verify internet connectivity
- **Market hours**: Data may be delayed; Yahoo Finance updates after market close

### "Insufficient data" warnings

- Ticker needs at least 40 weeks of historical data for 40W EMA
- Newly listed stocks may not have enough history

### Colors not displaying on Windows

The code uses `colorama` which auto-initializes on Windows. If colors don't appear:
- Run in Windows Terminal (recommended) instead of Command Prompt
- Update Windows to latest version

## Technical Details

### EMA Calculation

```python
# Logarithmic EMA formula
log_prices = np.log(prices)
log_ema = log_prices.ewm(span=period, adjust=False).mean()
price_ema = np.exp(log_ema)
```

### Data Source

- **Provider**: Yahoo Finance via yfinance library
- **Interval**: Weekly (`1wk`)
- **Lookback**: 2 years (ensures sufficient data for 40W EMA)

## Roadmap

### Phase 1 (Completed ✅)
- [x] Weekly data fetching
- [x] Logarithmic EMA calculation
- [x] Terminal output with color coding

### Phase 2 (Completed ✅)
- [x] HTML dashboard output (`dashboard.html`)
- [x] Responsive web design with color-coded status
- [x] Summary statistics and legend

### Phase 2.5 (Completed ✅)
- [x] Interactive web dashboard with Flask server
- [x] Real-time data refresh from browser
- [x] Watchlist editor (add/remove tickers via UI)
- [x] JSON-based watchlist persistence
- [x] Backward compatibility with CLI mode

### Phase 3 (Planned)
- [ ] Telegram bot for 40W EMA crossover alerts
- [ ] Cron job scheduling for automated runs

## License

Personal use tool. No license specified.

## Contact

For issues or questions, refer to project documentation in `CLAUDE.md`.
