# Quick Start Guide - Indian Equity Technical Dashboard

## Interactive Mode (Recommended)

### Start the Server

```bash
python app.py
```

### Open Dashboard

Navigate to: **http://localhost:5000**

### Features

1. **Refresh Data**
   - Click "🔄 Refresh Data" button
   - Wait 10-15 seconds for data fetch
   - Dashboard updates automatically (no page reload)

2. **Edit Watchlist**
   - Click "✏️ Edit Watchlist" button
   - **Add ticker**: Type `SYMBOL.NS` (e.g., `RELIANCE.NS`) and click "Add Ticker"
   - **Remove ticker**: Click "❌ Remove" next to any ticker
   - Changes save instantly to `watchlist.json`

3. **View Analysis**
   - **Summary Stats**: Stock counts by status (ABOVE/NEAR/BREACH)
   - **EMA Table**: Current prices, EMAs, distance from 40W EMA
   - **S/R Table**: Support/resistance levels, 52W high/low

### Stop the Server

Press `Ctrl+C` in the terminal

---

## CLI Mode (Alternative)

### Run Once

```bash
python main.py
```

### View Output

- **Terminal**: Color-coded tables
- **Browser**: Open `dashboard.html` (static file)

### Edit Watchlist

Edit `config.py` → modify `WATCHLIST` variable

---

## Ticker Format

**Required**: NSE symbols must end with `.NS`

✅ Valid:
- `RELIANCE.NS`
- `TCS.NS`
- `M&M.NS`

❌ Invalid:
- `RELIANCE` (missing `.NS`)
- `reliance.ns` (must be uppercase)
- `RELIANCE.BSE` (wrong exchange)

---

## Troubleshooting

### "Failed to fetch ticker"
- Check ticker format (must be `SYMBOL.NS`)
- Verify internet connection
- Stock may be delisted

### Port 5000 already in use
```bash
# Find and kill process on port 5000 (Windows)
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or use a different port in app.py
app.run(debug=True, port=5001)
```

### Colors not showing (Windows)
- Use Windows Terminal instead of Command Prompt
- Update Windows to latest version

### Reset watchlist
```bash
# Delete JSON to recreate from config.py
del watchlist.json
```

---

## Signal Meanings

| Status | Color | Meaning |
|--------|-------|---------|
| **ABOVE** 🟢 | Green | Price > 3% above 40W EMA (safe zone) |
| **NEAR** 🟡 | Amber | Price within 3% of 40W EMA (caution) |
| **BREACH** 🔴 | Red | Price below 40W EMA (**EXIT SIGNAL**) |

---

## Files Overview

| File | Purpose |
|------|---------|
| `app.py` | Flask web server (interactive mode) |
| `main.py` | CLI entry point (static mode) |
| `watchlist.json` | Persistent watchlist storage |
| `config.py` | Default watchlist (fallback) |
| `dashboard.html` | Static HTML output (CLI mode) |
| `templates/dashboard_interactive.html` | Interactive template |
| `static/dashboard.js` | Client-side JavaScript |

---

## Support

For detailed documentation, see:
- `README.md` - Full documentation
- `CLAUDE.md` - Project specification
