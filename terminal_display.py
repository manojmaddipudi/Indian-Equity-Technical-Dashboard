"""
Terminal output formatting with color-coded tables
"""

from tabulate import tabulate
from colorama import Fore, Style, init
from datetime import datetime
from typing import List, Dict

# Initialize colorama for cross-platform color support (especially Windows)
init(autoreset=True)


def format_number(value: float, decimals: int = 2) -> str:
    """
    Format number with comma separators.

    Args:
        value: Number to format
        decimals: Number of decimal places (default: 2)

    Returns:
        Formatted string (e.g., "2,450.50")
    """
    return f"{value:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format percentage with sign.

    Args:
        value: Percentage value (e.g., 7.5 for 7.5%)
        decimals: Number of decimal places (default: 1)

    Returns:
        Formatted string with sign (e.g., "+7.5%", "-2.3%")
    """
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.{decimals}f}%"


def get_color_for_status(status: str) -> str:
    """
    Get colorama color code for status.

    Args:
        status: "BREACH" | "NEAR" | "ABOVE"

    Returns:
        Colorama Fore color constant
    """
    color_map = {
        "BREACH": Fore.RED,
        "NEAR": Fore.YELLOW,
        "ABOVE": Fore.GREEN
    }
    return color_map.get(status, Fore.WHITE)


def create_ema_summary_table(summaries: List[Dict]) -> List[List]:
    """
    Create data rows for EMA summary table.

    Args:
        summaries: List of stock summary dictionaries

    Returns:
        List of table rows (each row is a list)
    """
    rows = []

    for summary in summaries:
        ticker = summary["ticker"]
        price = format_number(summary["current_price"])
        ema_10w = format_number(summary["emas"]["10W"])
        ema_20w = format_number(summary["emas"]["20W"])
        ema_40w = format_number(summary["emas"]["40W"])
        status = summary["status"]["signal"]
        dist_pct = format_percentage(summary["status"]["distance_pct"])

        # Get color for this row
        color = get_color_for_status(status)

        # Create colored row
        row = [
            color + ticker,
            color + price,
            color + ema_10w,
            color + ema_20w,
            color + ema_40w,
            color + status,
            color + dist_pct + Style.RESET_ALL
        ]

        rows.append(row)

    return rows


def create_support_resistance_table(summaries: List[Dict]) -> List[List]:
    """
    Create data rows for support/resistance table.

    Args:
        summaries: List of stock summary dictionaries

    Returns:
        List of table rows (each row is a list)
    """
    rows = []

    for summary in summaries:
        ticker = summary["ticker"]
        sr = summary["support_resistance"]

        row = [
            ticker,
            format_number(sr["52w_high"]),
            format_number(sr["52w_low"]),
            format_number(sr["pivot_high"]),
            format_number(sr["pivot_low"]),
            format_percentage(summary["vs_52w_high_pct"])
        ]

        rows.append(row)

    return rows


def print_header():
    """Print dashboard header with timestamp."""
    print()
    print("=" * 80)
    print(Fore.CYAN + Style.BRIGHT + "Indian Equity Technical Dashboard - Phase 1")
    print(Fore.CYAN + f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(Fore.CYAN + "Data: Weekly OHLC (Logarithmic EMAs)" + Style.RESET_ALL)
    print("=" * 80)
    print()


def print_legend():
    """Print color-coded legend explaining status signals."""
    print()
    print("Legend:")
    print(Fore.GREEN + "  ABOVE: " + Style.RESET_ALL +
          "Price > 3% above 40W EMA (safe zone)")
    print(Fore.YELLOW + "  NEAR:  " + Style.RESET_ALL +
          "Price within 3% of 40W EMA (caution zone)")
    print(Fore.RED + "  BREACH:" + Style.RESET_ALL +
          " Price below 40W EMA (EXIT SIGNAL)")
    print()
    print("  Dist%: Percentage distance from 40W EMA")
    print()


def format_terminal_output(summaries: List[Dict]) -> None:
    """
    Display formatted summary tables with color coding.

    Args:
        summaries: List of stock summary dictionaries

    Uses:
        - tabulate for table formatting
        - colorama for cross-platform color support
    """
    if not summaries:
        print(Fore.RED + "No data to display." + Style.RESET_ALL)
        return

    # Print header
    print_header()

    # Table 1: EMA Summary
    ema_headers = ["Ticker", "Price", "10W EMA", "20W EMA", "40W EMA", "Status", "Dist%"]
    ema_rows = create_ema_summary_table(summaries)

    print(Fore.CYAN + Style.BRIGHT + "EMA Summary" + Style.RESET_ALL)
    print(tabulate(ema_rows, headers=ema_headers, tablefmt="simple"))

    print()
    print("-" * 80)
    print()

    # Table 2: Support/Resistance
    sr_headers = ["Ticker", "52W High", "52W Low", "Pivot High", "Pivot Low", "vs 52W High"]
    sr_rows = create_support_resistance_table(summaries)

    print(Fore.CYAN + Style.BRIGHT + "Support/Resistance Levels" + Style.RESET_ALL)
    print(tabulate(sr_rows, headers=sr_headers, tablefmt="simple"))

    # Print legend
    print_legend()

    # Print data quality info
    total_stocks = len(summaries)
    breach_count = sum(1 for s in summaries if s["status"]["signal"] == "BREACH")
    near_count = sum(1 for s in summaries if s["status"]["signal"] == "NEAR")
    above_count = sum(1 for s in summaries if s["status"]["signal"] == "ABOVE")

    print(Fore.CYAN + f"Summary: {total_stocks} stocks analyzed" + Style.RESET_ALL)
    print(f"  {Fore.GREEN}{above_count} ABOVE{Style.RESET_ALL} | " +
          f"{Fore.YELLOW}{near_count} NEAR{Style.RESET_ALL} | " +
          f"{Fore.RED}{breach_count} BREACH{Style.RESET_ALL}")
    print()
