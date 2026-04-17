"""
Flask web server for the Indian Equity Technical Dashboard.
Provides interactive UI with API endpoints for watchlist management and data refresh.
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime

from watchlist_manager import load_watchlist, add_ticker, remove_ticker
from data_fetcher import fetch_all_tickers, log_info
from signal_analyzer import generate_all_summaries
from html_generator import get_template_context

app = Flask(__name__)


@app.route('/')
def index():
    """
    Serve interactive dashboard with current data.
    """
    try:
        watchlist = load_watchlist()
        log_info(f"Loading dashboard for {len(watchlist)} tickers...")

        # Fetch and analyze data (same as main.py)
        fetch_results = fetch_all_tickers(watchlist)
        summaries = generate_all_summaries(fetch_results)

        # Prepare context for template
        context = get_template_context(summaries)
        context['watchlist'] = watchlist
        context['failed_tickers'] = list(fetch_results['failed'].keys())

        return render_template('dashboard_interactive.html', **context)

    except Exception as e:
        log_info(f"Error loading dashboard: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    """
    Get current watchlist as JSON.

    Returns:
        JSON: {"tickers": ["SYMBOL.NS", ...]}
    """
    watchlist = load_watchlist()
    return jsonify({"tickers": watchlist})


@app.route('/api/watchlist', methods=['POST'])
def add_to_watchlist():
    """
    Add ticker to watchlist.

    Request body:
        {"ticker": "SYMBOL.NS"}

    Returns:
        JSON: {"success": bool, "message": str}
    """
    data = request.get_json()
    ticker = data.get('ticker', '').strip().upper()

    if not ticker:
        return jsonify({
            "success": False,
            "message": "Ticker is required"
        }), 400

    result = add_ticker(ticker)
    status_code = 200 if result['success'] else 400

    return jsonify(result), status_code


@app.route('/api/watchlist/<ticker>', methods=['DELETE'])
def delete_from_watchlist(ticker):
    """
    Remove ticker from watchlist.

    Args:
        ticker: Ticker symbol to remove (URL parameter)

    Returns:
        JSON: {"success": bool, "message": str}
    """
    result = remove_ticker(ticker)
    status_code = 200 if result['success'] else 404

    return jsonify(result), status_code


@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """
    Fetch latest data and return updated summaries as JSON.

    Returns:
        JSON: Complete dashboard context (summaries, stats, etc.)
    """
    try:
        watchlist = load_watchlist()
        log_info(f"Refreshing data for {len(watchlist)} tickers...")

        # Fetch and analyze data
        fetch_results = fetch_all_tickers(watchlist)
        summaries = generate_all_summaries(fetch_results)

        # Prepare response context
        context = get_template_context(summaries)
        context['failed_tickers'] = list(fetch_results['failed'].keys())
        context['success_count'] = len(fetch_results['success'])
        context['total_count'] = len(watchlist)

        log_info(f"Refresh complete: {context['success_count']}/{context['total_count']} tickers successful")

        return jsonify(context)

    except Exception as e:
        log_info(f"Refresh error: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*80)
    print("Indian Equity Technical Dashboard - Interactive Mode")
    print("="*80)
    print("\nServer starting at: http://localhost:5000")
    print("Features: Real-time refresh, Watchlist editor")
    print("Press Ctrl+C to stop the server\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
