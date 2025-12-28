# Algorithmic Trading Bot - Indian Markets Edition

A Python-based backtesting framework optimized for Indian stock markets (NSE/BSE). Test trading strategies, analyze returns, and generate alpha with comprehensive metrics.

## Features

### Indian Market Optimization
- **NSE Stocks**: Trade NIFTY 50 and other NSE-listed stocks
- **Indian Indices**: NIFTY 50 (^NSEI), SENSEX (^BSESN)
- **India-specific Settings**:
  - Default capital in INR
  - NSE commission rates (0.05% typical)
  - RBI repo rate for risk-free calculations
  - IST timezone support

### Core Features
- **Data Fetching**: Retrieve market data from Yahoo Finance for any stock
- **Multiple Trading Strategies**:
  - Moving Average Crossover
  - RSI (Relative Strength Index)
  - Bollinger Bands
  - Momentum Strategy (ROC-based)
- **Flexible Timeframes**: 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo
- **Backtesting Engine**: Powered by Backtrader with realistic commission/slippage
- **Comprehensive Analytics**:
  - Sharpe Ratio & Sortino Ratio (risk-adjusted)
  - Maximum Drawdown & Drawdown Duration
  - Win Rate, Profit Factor, Recovery Factor
  - Calmar Ratio & Volatility Analysis
  - Daily/Monthly Returns Distribution
- **Advanced Visualization**:
  - Equity curve with price action
  - Buy/Sell entry points on chart
  - Drawdown analysis
  - Monthly returns heatmap
  - Returns distribution histogram
- **CLI Interface**: Easy command-line tools with examples

## Installation

1. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### 1. Fetch Indian Stock Data
```bash
# Fetch Infosys data
python main.py fetch-data --symbol INFY.NS --save

# Fetch TCS data with 1-hour candles
python main.py fetch-data --symbol TCS.NS --interval 1h

# Fetch Reliance with custom date range
python main.py fetch-data --symbol RELIANCE.NS --start-date 2024-01-01 --end-date 2024-12-31
```

### 2. Run a Backtest
```bash
# Simple MA Crossover on Infosys
python main.py backtest --symbol INFY.NS --strategy ma_crossover

# Momentum strategy on TCS with 1h timeframe
python main.py backtest --symbol TCS.NS --strategy momentum --interval 1h --plot

# RSI strategy on Reliance with visualization
python main.py backtest --symbol RELIANCE.NS --strategy rsi --plot
```

### 3. List Available Strategies
```bash
python main.py list-strategies
```

### 4. Popular Indian Stocks (NSE)
```bash
INFY.NS        # Infosys
TCS.NS         # Tata Consultancy Services
RELIANCE.NS    # Reliance Industries
HDFC.NS        # HDFC Bank
ICICIBANK.NS   # ICICI Bank
SBIN.NS        # State Bank of India
MARUTI.NS      # Maruti Suzuki
WIPRO.NS       # Wipro
ASIANPAINT.NS  # Asian Paints
LT.NS          # Larsen & Toubro

^NSEI          # NIFTY 50 Index
^BSESN         # SENSEX Index
```

## CLI Commands

### fetch-data
Fetch historical market data from Yahoo Finance

**Options**:
- `--symbol`: Stock ticker (default: AAPL)
- `--start-date`: Start date (YYYY-MM-DD)
- `--end-date`: End date (YYYY-MM-DD)
- `--save`: Save data to CSV file

**Example**:
```bash
python main.py fetch-data --symbol BTC-USD --save
```

### backtest
Run backtest with a specific strategy

**Options**:
- `--symbol`: Stock ticker (default: AAPL)
- `--strategy`: Strategy name (ma_crossover, rsi, bollinger_bands)
- `--start-date`: Start date (YYYY-MM-DD)
- `--end-date`: End date (YYYY-MM-DD)
- `--capital`: Initial capital (default: 100000)
- `--commission`: Commission per trade (default: 0.001)
- `--plot`: Generate visualization plots
- `--fast-ma`: Fast MA period for MA Crossover (default: 10)
- `--slow-ma`: Slow MA period for MA Crossover (default: 30)
- `--rsi-period`: RSI period for RSI Strategy (default: 14)

**Example**:
```bash
python main.py backtest --symbol AAPL --strategy ma_crossover --fast-ma 5 --slow-ma 20 --capital 50000
```

### list-strategies
List all available trading strategies

**Example**:
```bash
python main.py list-strategies
```

## Project Structure

```
algo-trading/
├── src/
│   ├── data/              # Data fetching modules
│   ├── backtesting/       # Backtesting engine and base strategy
│   ├── strategies/        # Trading strategy implementations
│   ├── analytics/         # Performance analysis
│   ├── utils/             # Utilities (config, visualization)
│   └── cli.py             # Command-line interface
├── data/                  # Downloaded market data
├── results/               # Backtest results and plots
├── logs/                  # Application logs
├── main.py                # Entry point
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Creating Custom Strategies

For detailed instructions on writing custom strategies, see **[STRATEGY_GUIDE.md](STRATEGY_GUIDE.md)**.

### Quick Template

```python
from src.backtesting.base_strategy import BaseStrategy
import backtrader as bt

class MyStrategy(BaseStrategy):
    """Your strategy description"""
    params = (
        ('param1', 10),
        ('param2', 20),
    )

    def _init_indicators(self):
        """Initialize indicators"""
        self.ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.param1
        )

    def next(self):
        """Generate buy/sell signals"""
        if self.data.close[0] > self.ma[0] and not self.position:
            self.buy_signal()
        elif self.data.close[0] < self.ma[0] and self.position:
            self.sell_signal()
```

### Steps to Add Your Strategy

1. Create file: `src/strategies/my_strategy.py`
2. Register in `src/strategies/__init__.py`
3. Run backtest:
```bash
python main.py backtest --symbol INFY.NS --strategy my_strategy --plot
```

### Strategy Examples Included
- **MA Crossover**: Simple moving average crossover
- **RSI**: Oversold/Overbought signals
- **Bollinger Bands**: Mean reversion
- **Momentum**: Trend following with ROC

## Key Metrics Explained

### Sharpe Ratio
Risk-adjusted return. Higher is better (typical range: 0-2+).
- Formula: (Return - Risk-free rate) / Volatility
- Good for comparing strategies with different volatilities

### Sortino Ratio
Similar to Sharpe but only penalizes downside volatility.
- More favorable for strategies with upside skew
- Typically higher than Sharpe Ratio

### Calmar Ratio
Return divided by maximum drawdown.
- Good for comparing risk-adjusted returns
- Formula: Annual Return / Max Drawdown

### Maximum Drawdown
Largest peak-to-trough decline in portfolio value.
- Expressed as percentage
- Lower is better (closer to 0)

### Win Rate
Percentage of profitable trades.
- Formula: Winning Trades / Total Trades × 100%

### Profit Factor
Gross profit divided by gross loss.
- Formula: Total Winning Trade Profit / Total Losing Trade Loss
- Above 1.0 indicates profitable strategy

## Performance Optimization Tips

1. **Adjust commission**: Set realistic commission rates for your broker
2. **Optimize parameters**: Use different parameter values to find optimal settings
3. **Longer periods**: Use more historical data for more reliable results
4. **Multiple symbols**: Test across different assets to validate generalization
5. **Risk management**: Implement stop-losses and position sizing

## Troubleshooting

### Yahoo Finance connection issues
- Check internet connection
- Try a different stock symbol
- Retry after a few minutes

### Memory issues with large datasets
- Use shorter date ranges
- Reduce update frequency (use weekly/monthly instead of daily)

### No results from backtest
- Check that data was successfully fetched
- Ensure strategy parameters are reasonable
- Check logs for error messages

## Future Enhancements

- Real-time trading integration with brokers (Alpaca, IB)
- Walk-forward analysis
- Monte Carlo simulations
- Machine learning-based strategies
- Web dashboard for visualization
- Multi-asset portfolio optimization
- Risk management modules (position sizing, stop-loss)

## Dependencies

- **backtrader**: Backtesting framework
- **pandas**: Data manipulation
- **numpy**: Numerical computing
- **yfinance**: Yahoo Finance data fetching
- **matplotlib**: Visualization
- **click**: CLI framework
- **scikit-learn**: Machine learning utilities

## License

MIT License

## Contributing

Contributions are welcome! Please submit pull requests or issues.

## Disclaimer

This is an educational tool for backtesting trading strategies. It is not investment advice. Always conduct your own research and risk management before trading real money.
