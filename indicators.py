"""
Technical indicators module - EMA calculations and support/resistance levels
"""

import pandas as pd
import numpy as np
from typing import Dict
from config import EMA_PERIODS


def calculate_log_ema(prices: pd.Series, period: int) -> pd.Series:
    """
    Calculate Exponential Moving Average on logarithmic scale.

    This is critical for Weinstein/Minervini methodology as it weights
    percentage changes equally rather than absolute price changes.

    Process:
    1. Convert prices to natural log
    2. Calculate EMA using pandas ewm()
    3. Convert back to price scale using exp()

    Args:
        prices: Series of closing prices
        period: EMA period (e.g., 10, 20, 40)

    Returns:
        Series of EMA values in original price scale

    Note:
        Using adjust=False for standard EMA calculation:
        EMA = price * multiplier + EMA_prev * (1 - multiplier)
        where multiplier = 2 / (period + 1)

    Example:
        For a stock moving from Rs 100 to Rs 110 (+10%) and another from
        Rs 1000 to Rs 1100 (+10%), logarithmic EMA treats both equally,
        whereas linear EMA would weight the second move 10x higher.
    """
    # Step 1: Convert to logarithmic scale
    log_prices = np.log(prices)

    # Step 2: Calculate EMA on log scale
    # adjust=False gives the standard EMA formula
    log_ema = log_prices.ewm(span=period, adjust=False).mean()

    # Step 3: Convert back to price scale
    price_ema = np.exp(log_ema)

    return price_ema


def calculate_all_emas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate 10W, 20W, and 40W EMAs for a dataset.

    Args:
        df: DataFrame with OHLC data (must have 'Close' column)

    Returns:
        DataFrame with original OHLC + EMA columns [EMA_10W, EMA_20W, EMA_40W]
    """
    df = df.copy()

    # Calculate each EMA period
    for label, period in EMA_PERIODS.items():
        col_name = f"EMA_{label}"
        df[col_name] = calculate_log_ema(df['Close'], period)

    return df


def calculate_support_resistance(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate support and resistance levels.

    Method:
    - 52W High: max(High) over last 52 weeks
    - 52W Low: min(Low) over last 52 weeks
    - Recent pivot high: max(High) from last 4 weeks
    - Recent pivot low: min(Low) from last 4 weeks

    Args:
        df: DataFrame with OHLC data

    Returns:
        Dictionary with keys: ["52w_high", "52w_low", "pivot_high", "pivot_low"]
    """
    # 52-week high/low (use all available data if < 52 weeks)
    lookback_52w = min(52, len(df))
    last_52_weeks = df.tail(lookback_52w)

    # 4-week pivots
    lookback_4w = min(4, len(df))
    last_4_weeks = df.tail(lookback_4w)

    return {
        "52w_high": last_52_weeks['High'].max(),
        "52w_low": last_52_weeks['Low'].min(),
        "pivot_high": last_4_weeks['High'].max(),
        "pivot_low": last_4_weeks['Low'].min()
    }
