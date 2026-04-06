"""
Verification script to show detailed EMA calculations for one stock
"""

import yfinance as yf
import pandas as pd
import numpy as np
from config import WEEKLY_INTERVAL, LOOKBACK_PERIOD

def verify_single_stock(ticker: str = "CUMMINSIND.NS"):
    """Show detailed calculation breakdown for one stock"""

    print(f"\n{'='*80}")
    print(f"Verification Report for {ticker}")
    print(f"{'='*80}\n")

    # Fetch data
    print(f"Fetching weekly data...")
    data = yf.Ticker(ticker).history(period=LOOKBACK_PERIOD, interval=WEEKLY_INTERVAL)

    print(f"Total weeks of data: {len(data)}")
    print(f"Date range: {data.index[0].date()} to {data.index[-1].date()}\n")

    # Show last 10 weeks of raw data
    print("Last 10 weeks of Close prices:")
    print("-" * 80)
    last_10 = data[['Close']].tail(10)
    for date, row in last_10.iterrows():
        print(f"  {date.date()}: Rs {row['Close']:,.2f}")

    print(f"\n{'='*80}")
    print("EMA Calculations (Logarithmic Scale)")
    print(f"{'='*80}\n")

    # Calculate logarithmic EMAs
    close_prices = data['Close']

    # 10W EMA
    log_prices = np.log(close_prices)
    log_ema_10 = log_prices.ewm(span=10, adjust=False).mean()
    ema_10 = np.exp(log_ema_10)

    # 20W EMA
    log_ema_20 = log_prices.ewm(span=20, adjust=False).mean()
    ema_20 = np.exp(log_ema_20)

    # 40W EMA
    log_ema_40 = log_prices.ewm(span=40, adjust=False).mean()
    ema_40 = np.exp(log_ema_40)

    # Current values
    current_price = close_prices.iloc[-1]
    current_ema_10 = ema_10.iloc[-1]
    current_ema_20 = ema_20.iloc[-1]
    current_ema_40 = ema_40.iloc[-1]

    print(f"Current Price:  Rs {current_price:,.2f}")
    print(f"10W EMA:        Rs {current_ema_10:,.2f}")
    print(f"20W EMA:        Rs {current_ema_20:,.2f}")
    print(f"40W EMA:        Rs {current_ema_40:,.2f}")

    print(f"\n{'='*80}")
    print("40W EMA Analysis")
    print(f"{'='*80}\n")

    # Calculate position
    distance_pct = ((current_price - current_ema_40) / current_ema_40) * 100

    if current_price < current_ema_40:
        status = "BREACH (EXIT SIGNAL)"
        status_color = "RED"
    elif distance_pct <= 3.0:
        status = "NEAR (CAUTION ZONE)"
        status_color = "AMBER"
    else:
        status = "ABOVE (SAFE ZONE)"
        status_color = "GREEN"

    print(f"Distance from 40W EMA: {distance_pct:+.2f}%")
    print(f"Status: {status} [{status_color}]")

    # Show last 5 weeks of EMAs
    print(f"\n{'='*80}")
    print("Last 5 weeks - EMA progression")
    print(f"{'='*80}\n")

    comparison_df = pd.DataFrame({
        'Close': close_prices,
        '10W': ema_10,
        '20W': ema_20,
        '40W': ema_40
    }).tail(5)

    print(comparison_df.to_string(float_format=lambda x: f'{x:,.2f}'))

    # Support/Resistance
    print(f"\n{'='*80}")
    print("Support/Resistance Levels")
    print(f"{'='*80}\n")

    lookback_52w = min(52, len(data))
    last_52_weeks = data.tail(lookback_52w)
    last_4_weeks = data.tail(4)

    print(f"52-Week High:     Rs {last_52_weeks['High'].max():,.2f}")
    print(f"52-Week Low:      Rs {last_52_weeks['Low'].min():,.2f}")
    print(f"4-Week Pivot High: Rs {last_4_weeks['High'].max():,.2f}")
    print(f"4-Week Pivot Low:  Rs {last_4_weeks['Low'].min():,.2f}")

    vs_52w_high = ((current_price - last_52_weeks['High'].max()) / last_52_weeks['High'].max()) * 100
    print(f"\nCurrent vs 52W High: {vs_52w_high:+.2f}%")

    print(f"\n{'='*80}")
    print("Logarithmic vs Linear EMA Comparison")
    print(f"{'='*80}\n")

    # Calculate linear EMA for comparison
    linear_ema_40 = close_prices.ewm(span=40, adjust=False).mean().iloc[-1]

    print(f"40W EMA (Logarithmic): Rs {current_ema_40:,.2f}")
    print(f"40W EMA (Linear):      Rs {linear_ema_40:,.2f}")
    print(f"Difference:            Rs {abs(current_ema_40 - linear_ema_40):,.2f}")
    print(f"\nNote: Logarithmic EMA is preferred for Weinstein/Minervini methodology")
    print(f"as it weights percentage changes equally, not absolute price changes.")

    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    verify_single_stock()
