"""
Signal analysis module - 40W EMA position and stock summaries
"""

import pandas as pd
from typing import Dict
from datetime import datetime
from config import NEAR_40W_THRESHOLD
from indicators import calculate_all_emas, calculate_support_resistance


def analyze_40w_ema_position(current_price: float, ema_40w: float,
                              threshold: float = NEAR_40W_THRESHOLD) -> Dict[str, any]:
    """
    Determine price position relative to 40W EMA.

    Args:
        current_price: Current closing price
        ema_40w: 40-week EMA value
        threshold: Proximity threshold (default: 3% from config)

    Returns:
        Dictionary with keys:
            "signal": "BREACH" | "NEAR" | "ABOVE"
            "distance_pct": Percentage distance from EMA (positive = above, negative = below)
            "color": "red" | "amber" | "green"

    Logic:
        - BREACH: current_price < ema_40w (EXIT SIGNAL - RED)
        - NEAR: current_price within threshold% above EMA (WARNING - AMBER)
        - ABOVE: current_price > threshold% above EMA (SAFE - GREEN)
    """
    # Calculate percentage distance from 40W EMA
    distance_pct = ((current_price - ema_40w) / ema_40w) * 100

    # Determine signal based on position
    if current_price < ema_40w:
        # Price below 40W EMA = exit signal
        signal = "BREACH"
        color = "red"
    elif distance_pct <= (threshold * 100):
        # Within threshold (default 3%) above EMA = caution zone
        signal = "NEAR"
        color = "amber"
    else:
        # More than threshold above EMA = safe zone
        signal = "ABOVE"
        color = "green"

    return {
        "signal": signal,
        "distance_pct": distance_pct,
        "color": color
    }


def generate_stock_summary(ticker: str, df: pd.DataFrame) -> Dict:
    """
    Generate complete analysis for a single stock.

    Args:
        ticker: Stock ticker symbol
        df: DataFrame with OHLC data and calculated EMAs

    Returns:
        Comprehensive dictionary with:
            - ticker: Stock symbol
            - current_price: Latest closing price
            - emas: Dict of EMA values (10W, 20W, 40W)
            - status: Dict with signal, color, distance_pct
            - support_resistance: Dict with 52W and pivot levels
            - vs_52w_high_pct: Percentage distance from 52W high
            - last_updated: Date of last data point
            - data_points: Number of weeks of data
    """
    # Get current (latest) price
    current_price = df['Close'].iloc[-1]

    # Extract EMA values (latest)
    emas = {
        "10W": df['EMA_10W'].iloc[-1],
        "20W": df['EMA_20W'].iloc[-1],
        "40W": df['EMA_40W'].iloc[-1]
    }

    # Analyze 40W EMA position
    status = analyze_40w_ema_position(current_price, emas["40W"])

    # Calculate support/resistance levels
    support_resistance = calculate_support_resistance(df)

    # Calculate distance from 52W high
    vs_52w_high_pct = ((current_price - support_resistance["52w_high"]) /
                       support_resistance["52w_high"]) * 100

    # Get metadata
    last_updated = df.index[-1]
    data_points = len(df)

    return {
        "ticker": ticker,
        "current_price": current_price,
        "emas": emas,
        "status": status,
        "support_resistance": support_resistance,
        "vs_52w_high_pct": vs_52w_high_pct,
        "last_updated": last_updated,
        "data_points": data_points
    }


def generate_all_summaries(fetch_results: Dict) -> list:
    """
    Generate summaries for all successfully fetched tickers.

    Args:
        fetch_results: Dictionary from data_fetcher.fetch_all_tickers()
                      with "success" and "failed" keys

    Returns:
        List of summary dictionaries (one per successful ticker)
    """
    summaries = []

    for ticker, df in fetch_results["success"].items():
        # Calculate EMAs first
        df_with_emas = calculate_all_emas(df)

        # Generate summary
        summary = generate_stock_summary(ticker, df_with_emas)
        summaries.append(summary)

    # Sort by ticker name for consistent display
    summaries.sort(key=lambda x: x["ticker"])

    return summaries
