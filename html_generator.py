"""
Indian Equity Technical Dashboard - HTML Generator
Converts summary data to HTML dashboard using Jinja2 templates
"""

import os
from datetime import datetime
from typing import Dict, List
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


def get_template_context(summaries: List[Dict]) -> Dict:
    """
    Prepare context dictionary for Jinja2 template.

    Args:
        summaries: List of summary dictionaries from signal_analyzer.generate_all_summaries()

    Returns:
        Dictionary containing:
            - summaries: Original summary list
            - timestamp: Current datetime formatted string
            - total_stocks: Number of analyzed stocks
            - breach_count: Number of stocks breaching 40W EMA
            - near_count: Number of stocks near 40W EMA
            - above_count: Number of stocks above 40W EMA
            - failed_tickers: List of failed ticker symbols (if any)
    """
    # Count status types
    breach_count = sum(1 for s in summaries if s['status']['signal'] == 'BREACH')
    near_count = sum(1 for s in summaries if s['status']['signal'] == 'NEAR')
    above_count = sum(1 for s in summaries if s['status']['signal'] == 'ABOVE')

    # Format timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Context dictionary for template
    context = {
        "summaries": summaries,
        "timestamp": timestamp,
        "total_stocks": len(summaries),
        "breach_count": breach_count,
        "near_count": near_count,
        "above_count": above_count,
        "failed_tickers": []  # Populated by caller if needed
    }

    return context


def generate_html_dashboard(summaries: List[Dict], failed_tickers: List[str] = None,
                            output_path: str = "dashboard.html") -> None:
    """
    Generate HTML dashboard from stock summaries.

    Args:
        summaries: List of summary dicts from signal_analyzer.generate_all_summaries()
        failed_tickers: List of ticker symbols that failed to fetch (optional)
        output_path: Where to write dashboard.html (default: project root)

    Process:
        1. Load Jinja2 template from templates/ directory
        2. Prepare template context (summaries + metadata)
        3. Render HTML
        4. Write to file

    Raises:
        TemplateNotFound: If dashboard_template.html is missing
        IOError: If cannot write to output_path
    """
    # Determine template directory (relative to this file)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(current_dir, 'templates')

    # Verify template directory exists
    if not os.path.exists(template_dir):
        raise FileNotFoundError(
            f"Templates directory not found: {template_dir}\n"
            f"Expected structure: {current_dir}/templates/dashboard_template.html"
        )

    # Load Jinja2 environment
    env = Environment(loader=FileSystemLoader(template_dir))

    try:
        template = env.get_template('dashboard_template.html')
    except TemplateNotFound:
        raise FileNotFoundError(
            f"Template file not found: {template_dir}/dashboard_template.html\n"
            "Please ensure dashboard_template.html exists in the templates/ directory"
        )

    # Prepare context
    context = get_template_context(summaries)

    # Add failed tickers to context
    if failed_tickers:
        context["failed_tickers"] = failed_tickers

    # Render HTML
    html_content = template.render(context)

    # Write to file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    except IOError as e:
        raise IOError(f"Failed to write HTML dashboard to {output_path}: {str(e)}")


def log_html_generation(output_path: str, success_count: int, total_count: int) -> None:
    """
    Log HTML dashboard generation summary.

    Args:
        output_path: Path where HTML was written
        success_count: Number of successfully analyzed stocks
        total_count: Total number of stocks in watchlist
    """
    abs_path = os.path.abspath(output_path)
    print(f"\n[INFO] HTML Dashboard generated successfully!")
    print(f"[INFO] Location: {abs_path}")
    print(f"[INFO] Stocks analyzed: {success_count}/{total_count}")
    print(f"[INFO] Open in browser: start {output_path}")
