"""
Indian Equity Technical Dashboard - Phase 2
Entry point and orchestration with HTML dashboard generation
"""

import sys
from config import WATCHLIST
from data_fetcher import fetch_all_tickers, log_info, log_error
from signal_analyzer import generate_all_summaries
from terminal_display import format_terminal_output
from html_generator import generate_html_dashboard, log_html_generation


def main():
    """
    Phase 2 entry point: Fetch data, calculate indicators, display outputs.

    Flow:
        1. Load watchlist configuration
        2. Fetch weekly data for all tickers
        3. Calculate EMAs and indicators for successful fetches
        4. Analyze 40W EMA position and generate summaries
        5. Display formatted, color-coded terminal output
        6. Generate HTML dashboard file
        7. Report any failed tickers
    """
    try:
        # Step 1: Load configuration
        log_info(f"Loading watchlist with {len(WATCHLIST)} tickers...")

        # Step 2: Fetch weekly data for all tickers
        fetch_results = fetch_all_tickers(WATCHLIST)

        # Check if we have any successful fetches
        if not fetch_results["success"]:
            log_error("No data available to display. All tickers failed to fetch.")
            log_error("Possible causes:")
            log_error("  - Network connection issues")
            log_error("  - Invalid ticker symbols")
            log_error("  - Yahoo Finance API unavailable")
            sys.exit(1)

        # Step 3 & 4: Calculate indicators and generate summaries
        log_info("Calculating EMAs and technical indicators...")
        summaries = generate_all_summaries(fetch_results)

        # Step 5: Display terminal output
        format_terminal_output(summaries)

        # Step 6: Generate HTML dashboard
        log_info("Generating HTML dashboard...")
        failed_tickers = list(fetch_results["failed"].keys())
        generate_html_dashboard(summaries, failed_tickers=failed_tickers)

        # Step 7: Report completion
        success_count = len(fetch_results["success"])
        total_count = len(WATCHLIST)
        log_html_generation("dashboard.html", success_count, total_count)

    except KeyboardInterrupt:
        print("\n[INFO] Analysis interrupted by user")
        sys.exit(0)

    except Exception as e:
        log_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
