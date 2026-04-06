"""
Watchlist persistence layer using JSON file storage.
Provides functions to load, save, add, and remove tickers from the watchlist.
"""

import json
import os
from typing import List, Dict

WATCHLIST_FILE = "watchlist.json"


def load_watchlist() -> List[str]:
    """
    Load watchlist from JSON file. Falls back to config.py if file doesn't exist.

    Returns:
        List of ticker symbols (e.g., ['CUMMINSIND.NS', 'RELIANCE.NS'])
    """
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, 'r') as f:
            data = json.load(f)
            return data.get("tickers", [])
    else:
        # Fallback to hardcoded config on first run
        from config import WATCHLIST
        save_watchlist(WATCHLIST)  # Create JSON file
        return WATCHLIST


def save_watchlist(tickers: List[str]) -> None:
    """
    Save watchlist to JSON file.

    Args:
        tickers: List of ticker symbols to save
    """
    with open(WATCHLIST_FILE, 'w') as f:
        json.dump({"tickers": tickers}, f, indent=2)


def add_ticker(ticker: str) -> Dict[str, any]:
    """
    Add ticker to watchlist with validation.

    Args:
        ticker: Ticker symbol to add (e.g., 'RELIANCE.NS')

    Returns:
        Dictionary with 'success' (bool) and 'message' (str) keys
    """
    ticker = ticker.strip().upper()

    # Validate format
    if not validate_ticker_format(ticker):
        return {
            "success": False,
            "message": "Invalid format. Use SYMBOL.NS (e.g., RELIANCE.NS)"
        }

    watchlist = load_watchlist()

    # Check for duplicates
    if ticker in watchlist:
        return {
            "success": False,
            "message": f"{ticker} already in watchlist"
        }

    watchlist.append(ticker)
    save_watchlist(watchlist)

    return {
        "success": True,
        "message": f"{ticker} added successfully"
    }


def remove_ticker(ticker: str) -> Dict[str, any]:
    """
    Remove ticker from watchlist.

    Args:
        ticker: Ticker symbol to remove

    Returns:
        Dictionary with 'success' (bool) and 'message' (str) keys
    """
    ticker = ticker.strip().upper()
    watchlist = load_watchlist()

    if ticker not in watchlist:
        return {
            "success": False,
            "message": f"{ticker} not found in watchlist"
        }

    watchlist.remove(ticker)
    save_watchlist(watchlist)

    return {
        "success": True,
        "message": f"{ticker} removed successfully"
    }


def validate_ticker_format(ticker: str) -> bool:
    """
    Check if ticker follows NSE format: SYMBOL.NS

    Args:
        ticker: Ticker symbol to validate

    Returns:
        True if valid format, False otherwise
    """
    ticker = ticker.strip().upper()
    return ticker.endswith('.NS') and len(ticker) > 3
