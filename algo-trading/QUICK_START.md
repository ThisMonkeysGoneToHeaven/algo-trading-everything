# Quick Start Guide - 5 Minutes to First Backtest

## Installation (1 minute)

```bash
# Activate virtual environment
source venv/bin/activate

# If not yet created:
# python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

## Your First Backtest (2 minutes)

```bash
# Test MA Crossover on Infosys (INFY.NS)
python main.py backtest --symbol INFY.NS --strategy ma_crossover
```

**Result shows:**
- Total Profit/Loss
- Total Return %
- Sharpe Ratio (risk-adjusted)
- Max Drawdown (worst loss)
- Win Rate & Number of Trades

## Common Commands (Cheat Sheet)

### Backtest Different Strategies
```bash
# MA Crossover
python main.py backtest --symbol INFY.NS --strategy ma_crossover

# RSI (Overbought/Oversold)
python main.py backtest --symbol TCS.NS --strategy rsi

# Bollinger Bands (Mean Reversion)
python main.py backtest --symbol RELIANCE.NS --strategy bollinger_bands

# Momentum (Trend Following)
python main.py backtest --symbol HDFC.NS --strategy momentum
```

### Different Stocks
```bash
# Top IT stocks
python main.py backtest --symbol INFY.NS --strategy ma_crossover
python main.py backtest --symbol TCS.NS --strategy ma_crossover
python main.py backtest --symbol WIPRO.NS --strategy ma_crossover

# Banks
python main.py backtest --symbol ICICIBANK.NS --strategy ma_crossover
python main.py backtest --symbol SBIN.NS --strategy ma_crossover
python main.py backtest --symbol HDFC.NS --strategy ma_crossover

# Indices
python main.py backtest --symbol ^NSEI --strategy ma_crossover  # NIFTY 50
python main.py backtest --symbol ^BSESN --strategy ma_crossover  # SENSEX
```

### Different Timeframes
```bash
# 1-hour candles (intraday)
python main.py backtest --symbol INFY.NS --strategy ma_crossover --interval 1h

# 15-minute candles (day trading)
python main.py backtest --symbol INFY.NS --strategy ma_crossover --interval 15m

# Weekly (longer-term)
python main.py backtest --symbol INFY.NS --strategy ma_crossover --interval 1wk

# Daily (default - position trading)
python main.py backtest --symbol INFY.NS --strategy ma_crossover --interval 1d
```

### Different Date Ranges
```bash
# Last 1 year (default)
python main.py backtest --symbol INFY.NS --strategy ma_crossover

# Bull market period
python main.py backtest --symbol INFY.NS --strategy ma_crossover \
  --start-date 2023-01-01 --end-date 2024-12-31

# Recent 6 months
python main.py backtest --symbol INFY.NS --strategy ma_crossover \
  --start-date 2025-06-08 --end-date 2025-12-08

# Specific year
python main.py backtest --symbol INFY.NS --strategy ma_crossover \
  --start-date 2024-01-01 --end-date 2024-12-31
```

### With Visualization
```bash
# Generate charts (saved to results/)
python main.py backtest --symbol INFY.NS --strategy ma_crossover --plot
```

Creates:
- `equity_curve_INFY.NS.png` - Price action with buy/sell points
- `drawdown_analysis_INFY.NS.png` - Drawdown over time

### Custom Parameters
```bash
# MA Crossover with custom periods
python main.py backtest --symbol INFY.NS --strategy ma_crossover \
  --fast-ma 5 --slow-ma 20

# RSI with custom period
python main.py backtest --symbol INFY.NS --strategy rsi --rsi-period 21

# Momentum with custom ROC period
python main.py backtest --symbol INFY.NS --strategy momentum --roc-period 20
```

### Different Capital & Commission
```bash
# With ₹5,00,000 capital and Zerodha commission (0.05%)
python main.py backtest --symbol INFY.NS --strategy ma_crossover \
  --capital 500000 --commission 0.0005

# No commission (some brokers)
python main.py backtest --symbol INFY.NS --strategy ma_crossover \
  --commission 0

# High capital
python main.py backtest --symbol INFY.NS --strategy ma_crossover \
  --capital 2500000
```

## Fetch Data

```bash
# Download data and save to CSV
python main.py fetch-data --symbol INFY.NS --save

# Custom date range
python main.py fetch-data --symbol INFY.NS \
  --start-date 2024-01-01 --end-date 2024-12-31 --save

# 1-hour candles
python main.py fetch-data --symbol INFY.NS --interval 1h --save
```

## List Strategies

```bash
python main.py list-strategies
```

Shows all available strategies with descriptions.

## Interpreting Results

```
Strategy: MAcrossoverStrategy
Period: 2024-01-01 to 2024-12-31

Capital:
  Initial Capital: ₹100,000.00      ← Starting money
  Final Value: ₹100,417.71          ← Ending portfolio value
  Total Profit: ₹417.71             ← Net profit/loss

Returns:
  Total Return: 0.42%               ← Overall profit %
  Annual Return: 0.22%              ← Annualized return
  Sharpe Ratio: -5.31               ← Risk-adjusted return (>1 is good)

Risk Metrics:
  Max Drawdown: 0.26%               ← Worst loss from peak (<20% is good)

Trade Statistics:
  Total Trades: 8                   ← How many trades
  Winning Trades: 3                 ← Profitable trades
  Losing Trades: 4                  ← Losing trades
  Win Rate: 37.50%                  ← % of winning trades
  Profit Factor: 0.75               ← Profit/Loss ratio (>1.5 is good)
```

## What's Good?

| Metric | Target |
|--------|--------|
| Total Return | > 15-20% |
| Sharpe Ratio | > 1.0 |
| Win Rate | > 50% |
| Max Drawdown | < 20% |
| Profit Factor | > 1.5 |

## Next: Write Your Own Strategy

See [STRATEGY_GUIDE.md](STRATEGY_GUIDE.md) for:
- Template to copy
- Real-world examples
- All available indicators
- How to test it

## Quick Example: Custom Strategy

Create `src/strategies/simple_ma.py`:
```python
import backtrader as bt
from src.backtesting.base_strategy import BaseStrategy

class SimpleMa(BaseStrategy):
    def _init_indicators(self):
        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=20
        )

    def next(self):
        if self.data.close[0] > self.sma[0] and not self.position:
            self.buy_signal()
        elif self.data.close[0] < self.sma[0] and self.position:
            self.sell_signal()
```

Register in `src/strategies/__init__.py` and test:
```bash
python main.py backtest --symbol INFY.NS --strategy simple_ma
```

---

## Troubleshooting

### No trades generated
```bash
# Use simpler strategy first
python main.py backtest --symbol INFY.NS --strategy ma_crossover
```

### Wrong symbol format
```bash
# Correct (NSE stocks need .NS suffix)
python main.py backtest --symbol INFY.NS  # ✓
python main.py backtest --symbol INFY     # ✗ Won't work
```

### Can't download data
```bash
# Check internet, try again
python main.py fetch-data --symbol INFY.NS
```

---

## Popular Indian Stocks to Test

```
INFY.NS         Infosys (IT)
TCS.NS          Tata Consultancy Services (IT)
RELIANCE.NS     Reliance Industries (Energy)
HDFC.NS         HDFC Bank (Banking)
ICICIBANK.NS    ICICI Bank (Banking)
SBIN.NS         State Bank of India (Banking)
MARUTI.NS       Maruti Suzuki (Auto)
WIPRO.NS        Wipro (IT)
```

---

## Files Generated

```
results/
  ├── equity_curve_INFY.NS.png       # Price chart with buy/sell
  ├── drawdown_analysis_INFY.NS.png  # Drawdown chart
  ├── returns_dist_INFY.NS.png       # Returns histogram
  └── monthly_heatmap_INFY.NS.png    # Monthly returns heatmap

data/
  └── INFY.NS_*.csv                  # Downloaded market data
```

---

## Learning Path

1. **Run examples** (5 min) ← You are here
2. **Try different stocks** (10 min)
3. **Read [STRATEGY_GUIDE.md](STRATEGY_GUIDE.md)** (30 min)
4. **Write custom strategy** (20 min)
5. **Optimize parameters** (ongoing)
6. **Test on multiple periods** (ongoing)

---

Good luck with backtesting! 🚀
