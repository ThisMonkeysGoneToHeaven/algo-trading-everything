"""Configuration and constants for the trading bot"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
LOG_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
for directory in [DATA_DIR, RESULTS_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# =====================================================
# INDIAN MARKET CONFIGURATION
# =====================================================

# Trading configuration (India-specific)
DEFAULT_CAPITAL = 100000  # Starting capital in INR
DEFAULT_COMMISSION = 0.0005  # 0.05% brokerage commission (NSE typical)
DEFAULT_SLIPPAGE = 0.0002  # 0.02% slippage

# Indian market hours: 09:15 to 15:30 IST
MARKET_OPEN = "09:15"
MARKET_CLOSE = "15:30"
MARKET_TIMEZONE = "Asia/Kolkata"

# Data configuration
YAHOO_FINANCE_RETRY_ATTEMPTS = 3
YAHOO_FINANCE_TIMEOUT = 10

# Analysis configuration (India-specific)
RISK_FREE_RATE = 0.065  # 6.5% annual risk-free rate (RBI repo rate approx)
DAYS_PER_YEAR = 252  # Trading days per year on NSE

# Timeframes
TIMEFRAMES = {
    '1m': '1min',
    '5m': '5min',
    '15m': '15min',
    '30m': '30min',
    '1h': '1H',
    '1d': '1D',  # Default
    '1wk': '1wk',
    '1mo': '1mo',
}

DEFAULT_TIMEFRAME = '1d'

# =====================================================
# POPULAR INDIAN MARKET SYMBOLS
# =====================================================
# NSE Index: ^NSEI (NIFTY 50)
# BSE Index: ^BSESN (SENSEX)

INDIAN_STOCKS = {
    # NIFTY 50 - Large Cap
    'RELIANCE': 'RELIANCE.NS',
    'TCS': 'TCS.NS',
    'INFY': 'INFY.NS',
    'HINDUNILVR': 'HINDUNILVR.NS',
    'ICICIBANK': 'ICICIBANK.NS',
    'SBIN': 'SBIN.NS',
    'HDFC': 'HDFC.NS',
    'LT': 'LT.NS',
    'MARUTI': 'MARUTI.NS',
    'BAJAJ-AUTO': 'BAJAJ-AUTO.NS',
    'WIPRO': 'WIPRO.NS',
    'ADANIPORTS': 'ADANIPORTS.NS',
    'ASIANPAINT': 'ASIANPAINT.NS',
    'NTPC': 'NTPC.NS',
    'POWERGRID': 'POWERGRID.NS',
    'ITC': 'ITC.NS',
    'COALINDIA': 'COALINDIA.NS',
    'SUNPHARMA': 'SUNPHARMA.NS',
    'DRREDDY': 'DRREDDY.NS',
    'HCLTECH': 'HCLTECH.NS',

    # Mid Cap
    'BAJAJFINSV': 'BAJAJFINSV.NS',
    'AXISBANK': 'AXISBANK.NS',
    'BHARTIARTL': 'BHARTIARTL.NS',
    'IOC': 'IOC.NS',
    'JSWSTEEL': 'JSWSTEEL.NS',
    'TATASTEEL': 'TATASTEEL.NS',

    # Indices
    'NIFTY50': '^NSEI',
    'SENSEX': '^BSESN',
    'NIFTYJR': '^NSMIDCP',
}

# Indian Rupee pairs (Forex)
FOREX_PAIRS = {
    'USDINR': 'USDINR=X',
    'EURINR': 'EURINR=X',
    'GBPINR': 'GBPINR=X',
}

# Cryptocurrencies (common in India)
CRYPTO_PAIRS = {
    'BTC-INR': 'BTC-INR',
    'ETH-INR': 'ETH-INR',
}
