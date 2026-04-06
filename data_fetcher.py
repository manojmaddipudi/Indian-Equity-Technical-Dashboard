"""
Data fetching module for weekly OHLC data using yfinance
"""

import yfinance as yf
import pandas as pd
import sys
from typing import Dict, Tuple
from config import WEEKLY_INTERVAL, LOOKBACK_PERIOD


def log_info(message: str):
    """Print info message to stdout"""
    print(f"[INFO] {message}")


def log_warning(message: str):
    """Print warning message to stderr"""
    print(f"[WARN] {message}", file=sys.stderr)


def log_error(message: str):
    """Print error message to stderr"""
    print(f"[ERROR] {message}", file=sys.stderr)


def validate_data(df: pd.DataFrame, ticker: str, min_rows: int = 40) -> Tuple[bool, str]:
    """
    Validate fetched data meets minimum requirements.

    Args:
        df: DataFrame with OHLC data
        ticker: Ticker symbol (for error messages)
        min_rows: Minimum number of rows required (default: 40 for 40W EMA)

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if df is None or df.empty:
        return False, "No data returned"

    if len(df) < min_rows:
        return False, f"Insufficient data: {len(df)} weeks (need at least {min_rows})"

    # Check for required columns
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return False, f"Missing columns: {missing_cols}"

    # Check for all-NaN Close column (critical for EMA calculation)
    if df['Close'].isna().all():
        return False, "Close prices are all NaN"

    # Check for negative prices (data quality issue)
    if (df['Close'] <= 0).any():
        return False, "Found non-positive close prices"

    return True, ""


def include_current_week_data(ticker_obj: yf.Ticker, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """
    Include current week's data even if the week hasn't closed yet.

    This fetches the latest available trading day's price and uses it for the current week.

    Args:
        ticker_obj: yfinance Ticker object
        df: DataFrame with weekly OHLC data
        ticker: Ticker symbol (for logging)

    Returns:
        DataFrame with current week's data included/updated
    """
    from datetime import datetime, timedelta

    try:
        # Get the latest available price using recent data
        latest_data = ticker_obj.history(period="1d", interval="1d")

        if latest_data.empty:
            log_warning(f"{ticker}: No recent daily data available, using last weekly close")
            return df

        # Remove any rows with NaN Close prices (weekends/holidays)
        latest_data = latest_data.dropna(subset=['Close'])

        if latest_data.empty:
            log_warning(f"{ticker}: No valid recent daily data, using last weekly close")
            return df

        # Get the most recent valid trading day's data
        latest_close = latest_data['Close'].iloc[-1]
        latest_date = latest_data.index[-1]
        latest_high = latest_data['High'].iloc[-1]
        latest_low = latest_data['Low'].iloc[-1]
        latest_open = latest_data['Open'].iloc[-1]
        latest_volume = latest_data['Volume'].iloc[-1]

        last_weekly_date = df.index[-1]
        last_weekly_close = df['Close'].iloc[-1]

        # Calculate days difference
        days_diff = (latest_date - last_weekly_date).days

        # If the latest daily price is different from weekly close, or more recent, update
        if abs(latest_close - last_weekly_close) > 0.01 or days_diff > 0:
            # Create a new row for current week with today's date
            current_date = pd.Timestamp.now(tz=latest_date.tz)

            new_row = pd.DataFrame({
                'Open': [latest_open],
                'High': [latest_high],
                'Low': [latest_low],
                'Close': [latest_close],
                'Volume': [latest_volume]
            }, index=[current_date])

            # Append the current week's data
            df = pd.concat([df, new_row])

            log_info(f"{ticker}: Included current week data (as of {latest_date.date()}, price: Rs {latest_close:.2f})")
        else:
            log_info(f"{ticker}: Weekly data already current (last: {last_weekly_date.date()}, close: Rs {last_weekly_close:.2f})")

        return df

    except Exception as e:
        log_warning(f"{ticker}: Could not fetch current week data: {str(e)}")
        return df


def fetch_weekly_data(ticker: str, period: str = LOOKBACK_PERIOD) -> pd.DataFrame:
    """
    Fetch weekly OHLC data for a single ticker using yfinance.
    Includes current week's data even if the week hasn't closed yet.

    Args:
        ticker: NSE ticker symbol (e.g., "CUMMINSIND.NS")
        period: Historical period to fetch (default: from config.LOOKBACK_PERIOD)

    Returns:
        DataFrame with columns: [Open, High, Low, Close, Volume]
        Indexed by date (weekly)
        Includes current week's latest price

    Raises:
        ValueError: If ticker data cannot be fetched or is invalid
    """
    try:
        log_info(f"Fetching weekly data for {ticker}...")

        # Fetch data from yfinance
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(period=period, interval=WEEKLY_INTERVAL)

        # Validate the fetched data
        is_valid, error_msg = validate_data(df, ticker)
        if not is_valid:
            raise ValueError(f"Data validation failed: {error_msg}")

        # Forward-fill small gaps (1-2 weeks) - common due to market holidays
        # Only fill Close prices; OHLC will be handled separately if needed
        df['Close'] = df['Close'].ffill(limit=2)

        # Drop rows where Close is still NaN after forward fill
        initial_rows = len(df)
        df = df.dropna(subset=['Close'])
        dropped_rows = initial_rows - len(df)

        if dropped_rows > 0:
            log_warning(f"{ticker}: Dropped {dropped_rows} rows with missing Close prices")

        # Include current week's data (even if week hasn't closed)
        df = include_current_week_data(ticker_obj, df, ticker)

        # Re-validate after all processing
        is_valid, error_msg = validate_data(df, ticker)
        if not is_valid:
            raise ValueError(f"Data validation failed after cleaning: {error_msg}")

        log_info(f"{ticker}: Fetched {len(df)} weeks of data")
        return df

    except Exception as e:
        log_error(f"Failed to fetch {ticker}: {str(e)}")
        raise ValueError(f"Failed to fetch {ticker}: {str(e)}")


def fetch_all_tickers(tickers: list) -> Dict[str, Dict]:
    """
    Fetch weekly data for all tickers with error isolation.

    One ticker failure doesn't crash the entire run.

    Args:
        tickers: List of ticker symbols

    Returns:
        Dictionary with keys:
            "success": {ticker: dataframe}
            "failed": {ticker: error_message}
    """
    results = {
        "success": {},
        "failed": {}
    }

    log_info(f"Fetching data for {len(tickers)} tickers...")

    for ticker in tickers:
        try:
            df = fetch_weekly_data(ticker)
            results["success"][ticker] = df
        except Exception as e:
            results["failed"][ticker] = str(e)

    # Summary
    success_count = len(results["success"])
    failed_count = len(results["failed"])

    log_info(f"Data fetch complete: {success_count} successful, {failed_count} failed")

    if failed_count > 0:
        log_warning(f"Failed tickers: {list(results['failed'].keys())}")

    return results
