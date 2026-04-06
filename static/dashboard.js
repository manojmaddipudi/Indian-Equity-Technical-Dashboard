/**
 * Interactive dashboard JavaScript for watchlist management and data refresh.
 * Uses vanilla JavaScript with Fetch API (no frameworks per CLAUDE.md).
 */

// DOM elements
const refreshBtn = document.getElementById('refreshBtn');
const editWatchlistBtn = document.getElementById('editWatchlistBtn');
const watchlistModal = document.getElementById('watchlistModal');
const closeModal = document.querySelector('.close');
const addTickerBtn = document.getElementById('addTickerBtn');
const newTickerInput = document.getElementById('newTickerInput');
const watchlistItems = document.getElementById('watchlistItems');
const statusMessage = document.getElementById('statusMessage');
const loadingSpinner = document.getElementById('loadingSpinner');

/**
 * Show status message to user.
 * @param {string} message - Message to display
 * @param {string} type - 'success' or 'error'
 */
function showStatus(message, type = 'success') {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    statusMessage.style.display = 'block';

    // Auto-hide after 5 seconds
    setTimeout(() => {
        statusMessage.style.display = 'none';
    }, 5000);
}

/**
 * Show or hide loading spinner.
 * @param {boolean} show - True to show, false to hide
 */
function showLoading(show) {
    loadingSpinner.style.display = show ? 'flex' : 'none';
}

/**
 * Refresh data from server and update UI.
 */
refreshBtn.addEventListener('click', async () => {
    try {
        showLoading(true);
        refreshBtn.disabled = true;

        const response = await fetch('/api/refresh', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        // Update dashboard with new data
        updateDashboard(data);

        showStatus(
            `✅ Data refreshed! ${data.success_count}/${data.total_count} tickers successful`,
            'success'
        );
    } catch (error) {
        showStatus(`❌ Refresh failed: ${error.message}`, 'error');
    } finally {
        showLoading(false);
        refreshBtn.disabled = false;
    }
});

/**
 * Update dashboard tables and stats with new data.
 * @param {Object} data - Context data from /api/refresh
 */
function updateDashboard(data) {
    // Update summary stats
    const stats = document.querySelectorAll('.summary-stats .stat');
    if (stats.length >= 4) {
        stats[0].textContent = `${data.total_stocks} Stocks Analyzed`;
        stats[1].textContent = `${data.breach_count} BREACH 🔴`;
        stats[2].textContent = `${data.near_count} NEAR 🟡`;
        stats[3].textContent = `${data.above_count} ABOVE 🟢`;
    }

    // Update timestamp
    const timestampElement = document.querySelector('header p');
    if (timestampElement) {
        timestampElement.innerHTML = `<strong>Last Updated:</strong> ${data.timestamp}`;
    }

    // Update EMA table
    const emaTableBody = document.querySelector('.ema-table tbody');
    if (emaTableBody && data.summaries) {
        emaTableBody.innerHTML = data.summaries.map(s => `
            <tr class="status-${s.status.color}">
                <td class="ticker">${s.ticker}</td>
                <td>₹${s.current_price.toFixed(2)}</td>
                <td>₹${s.emas['10W'].toFixed(2)}</td>
                <td>₹${s.emas['20W'].toFixed(2)}</td>
                <td>₹${s.emas['40W'].toFixed(2)}</td>
                <td><span class="badge ${s.status.color}">${s.status.signal}</span></td>
                <td>${s.status.distance_pct > 0 ? '+' : ''}${s.status.distance_pct.toFixed(1)}%</td>
            </tr>
        `).join('');
    }

    // Update Support/Resistance table
    const srTableBody = document.querySelector('.sr-table tbody');
    if (srTableBody && data.summaries) {
        srTableBody.innerHTML = data.summaries.map(s => `
            <tr>
                <td class="ticker">${s.ticker}</td>
                <td>₹${s.support_resistance['52w_high'].toFixed(2)}</td>
                <td>₹${s.support_resistance['52w_low'].toFixed(2)}</td>
                <td>₹${s.support_resistance['pivot_high'].toFixed(2)}</td>
                <td>₹${s.support_resistance['pivot_low'].toFixed(2)}</td>
                <td>${s.vs_52w_high_pct.toFixed(1)}%</td>
            </tr>
        `).join('');
    }

    // Update failed tickers footer
    const failedTickers = document.querySelector('.failed-tickers');
    if (failedTickers && data.failed_tickers) {
        if (data.failed_tickers.length > 0) {
            failedTickers.innerHTML = `<strong>⚠️ Failed tickers:</strong> ${data.failed_tickers.join(', ')}`;
            failedTickers.style.display = 'block';
        } else {
            failedTickers.style.display = 'none';
        }
    }
}

/**
 * Open watchlist editor modal.
 */
editWatchlistBtn.addEventListener('click', () => {
    watchlistModal.style.display = 'block';
    loadWatchlist();
});

/**
 * Close watchlist editor modal.
 */
closeModal.addEventListener('click', () => {
    watchlistModal.style.display = 'none';
});

/**
 * Close modal when clicking outside of it.
 */
window.addEventListener('click', (event) => {
    if (event.target === watchlistModal) {
        watchlistModal.style.display = 'none';
    }
});

/**
 * Load current watchlist into modal.
 */
async function loadWatchlist() {
    try {
        const response = await fetch('/api/watchlist');
        const data = await response.json();

        watchlistItems.innerHTML = data.tickers.map(ticker => `
            <li data-ticker="${ticker}">
                <span class="ticker-name">${ticker}</span>
                <button class="btn-delete" data-ticker="${ticker}">❌ Remove</button>
            </li>
        `).join('');

        // Update count in modal header
        document.querySelector('.current-watchlist h3').textContent =
            `Current Watchlist (${data.tickers.length} tickers)`;

        // Attach delete listeners to each button
        document.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const ticker = e.target.dataset.ticker;
                deleteTicker(ticker);
            });
        });
    } catch (error) {
        showStatus(`❌ Error loading watchlist: ${error.message}`, 'error');
    }
}

/**
 * Add new ticker to watchlist.
 */
addTickerBtn.addEventListener('click', async () => {
    const ticker = newTickerInput.value.trim().toUpperCase();

    if (!ticker) {
        showStatus('Please enter a ticker symbol', 'error');
        return;
    }

    try {
        const response = await fetch('/api/watchlist', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ticker})
        });

        const data = await response.json();

        if (data.success) {
            showStatus(data.message, 'success');
            newTickerInput.value = '';  // Clear input
            loadWatchlist();  // Reload list
        } else {
            showStatus(data.message, 'error');
        }
    } catch (error) {
        showStatus(`❌ Error adding ticker: ${error.message}`, 'error');
    }
});

/**
 * Delete ticker from watchlist with confirmation.
 * @param {string} ticker - Ticker symbol to remove
 */
async function deleteTicker(ticker) {
    if (!confirm(`Remove ${ticker} from watchlist?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/watchlist/${ticker}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showStatus(data.message, 'success');
            loadWatchlist();  // Reload list
        } else {
            showStatus(data.message, 'error');
        }
    } catch (error) {
        showStatus(`❌ Error removing ticker: ${error.message}`, 'error');
    }
}

/**
 * Allow Enter key to submit new ticker.
 */
newTickerInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        addTickerBtn.click();
    }
});
