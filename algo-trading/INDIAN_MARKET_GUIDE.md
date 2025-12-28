# Algo Trading Bot - Indian Market Guide

This guide shows you how to use the algo trading bot optimized for Indian stock markets.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Indian Market Features](#indian-market-features)
3. [Examples](#examples)
4. [Popular Indian Stocks](#popular-indian-stocks)
5. [Advanced Features](#advanced-features)

---

## Getting Started

### Installation

```bash
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### First Backtest

```bash
# Test MA Crossover on Infosys
python main.py backtest --symbol INFY.NS --strategy ma_crossover

# With visualization
python main.py backtest --symbol INFY.NS --strategy ma_crossover --plot
```

---

## Indian Market Features

### NSE Symbols Format

NSE stocks use the format `SYMBOL.NS`:

```
INFY.NS         # Infosys
TCS.NS          # Tata Consultancy Services
RELIANCE.NS     # Reliance Industries
HDFC.NS         # HDFC Bank
```

### India-Specific Configuration

The bot is pre-configured for Indian markets:

**In `src/utils/config.py`:**
```python
# Indian market commission (NSE typical: 0.05%)
DEFAULT_COMMISSION = 0.0005

# Capital in Indian Rupees
DEFAULT_CAPITAL = 100000  # ₹100,000

# Risk-free rate (RBI Repo Rate ~6.5%)
RISK_FREE_RATE = 0.065

# IST Timezone
MARKET_TIMEZONE = "Asia/Kolkata"
```

### Currency

All values are in **Indian Rupees (₹)**:

```
Initial Capital: ₹100,000
Final Value: ₹100,417.71
Total Profit: ₹417.71
```

---

## Examples

### Example 1: Simple MA Crossover on INFY

```bash
python main.py backtest \
  --symbol INFY.NS \
  --strategy ma_crossover \
  --fast-ma 10 \
  --slow-ma 30
```

**Result:**
```
Capital:
  Initial Capital: ₹100,000.00
  Final Value: ₹100,417.71
  Total Profit: ₹417.71

Trade Statistics:
  Total Trades: 8
  Winning Trades: 3
  Losing Trades: 4
  Win Rate: 37.50%
```

### Example 2: RSI Strategy on TCS with Different Timeframe

```bash
python main.py backtest \
  --symbol TCS.NS \
  --strategy rsi \
  --interval 1h \
  --rsi-period 14
```

### Example 3: Bollinger Bands on RELIANCE with Visualization

```bash
python main.py backtest \
  --symbol RELIANCE.NS \
  --strategy bollinger_bands \
  --plot
```

Generated files in `results/`:
- `equity_curve_RELIANCE.NS.png` - Price and equity curve
- `drawdown_analysis_RELIANCE.NS.png` - Drawdown over time
- `returns_dist_RELIANCE.NS.png` - Returns distribution

### Example 4: Momentum Strategy on Multiple Stocks

```bash
# Test on different NIFTY 50 stocks
python main.py backtest --symbol HDFC.NS --strategy momentum
python main.py backtest --symbol ICICIBANK.NS --strategy momentum
python main.py backtest --symbol SBIN.NS --strategy momentum
python main.py backtest --symbol MARUTI.NS --strategy momentum
```

### Example 5: Different Date Ranges

```bash
# Bull market period (2023-2024)
python main.py backtest --symbol INFY.NS --strategy ma_crossover \
  --start-date 2023-01-01 --end-date 2024-12-31

# Recent period
python main.py backtest --symbol INFY.NS --strategy ma_crossover \
  --start-date 2024-09-01 --end-date 2025-12-08

# Specific year
python main.py backtest --symbol INFY.NS --strategy ma_crossover \
  --start-date 2024-01-01 --end-date 2024-12-31
```

---

## Popular Indian Stocks

### NIFTY 50 - Large Cap

| Symbol | Company | Sector |
|--------|---------|--------|
| RELIANCE.NS | Reliance Industries | Energy |
| TCS.NS | Tata Consultancy Services | IT |
| INFY.NS | Infosys | IT |
| HINDUNILVR.NS | Hindustan Unilever | Consumer Goods |
| ICICIBANK.NS | ICICI Bank | Banking |
| SBIN.NS | State Bank of India | Banking |
| HDFC.NS | HDFC Bank | Banking |
| LT.NS | Larsen & Toubro | Engineering |
| MARUTI.NS | Maruti Suzuki | Auto |
| WIPRO.NS | Wipro | IT |

### Mid Cap

| Symbol | Company | Sector |
|--------|---------|--------|
| AXISBANK.NS | Axis Bank | Banking |
| BHARTIARTL.NS | Bharti Airtel | Telecom |
| JSWSTEEL.NS | JSW Steel | Steel |
| TATASTEEL.NS | Tata Steel | Steel |
| IOC.NS | Indian Oil Corp | Energy |

### Indices

| Symbol | Name |
|--------|------|
| ^NSEI | NIFTY 50 |
| ^BSESN | SENSEX (BSE 30) |
| ^NSMIDCP | NIFTY Midcap 50 |

---

## Advanced Features

### 1. Timeframe Support

Trade on different timeframes:

```bash
# 1-minute candles (day trading)
python main.py backtest --symbol INFY.NS --strategy ma_crossover --interval 1m

# 15-minute candles (intraday)
python main.py backtest --symbol INFY.NS --strategy ma_crossover --interval 15m

# 1-hour candles (swing trading)
python main.py backtest --symbol INFY.NS --strategy ma_crossover --interval 1h

# Daily candles (position trading) - DEFAULT
python main.py backtest --symbol INFY.NS --strategy ma_crossover --interval 1d

# Weekly candles (longer-term)
python main.py backtest --symbol INFY.NS --strategy ma_crossover --interval 1wk
```

### 2. Fetch Data

Download and analyze market data:

```bash
# Fetch and display data
python main.py fetch-data --symbol INFY.NS

# Save to CSV for external analysis
python main.py fetch-data --symbol INFY.NS --save

# Custom date range and timeframe
python main.py fetch-data \
  --symbol INFY.NS \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --interval 1h \
  --save
```

Saved files go to `data/INFY.NS_*.csv`

### 3. Parameter Optimization

Test different parameters to find optimal settings:

```bash
# MA Crossover - different parameter combinations
for fast in 5 10 15 20; do
  for slow in 30 50 100; do
    echo "Testing fast=$fast, slow=$slow"
    python main.py backtest --symbol INFY.NS --strategy ma_crossover \
      --fast-ma $fast --slow-ma $slow
  done
done
```

### 4. Risk Management

Adjust commission based on your broker:

```bash
# Zerodha-like (0.05% typical for NSE)
python main.py backtest --symbol INFY.NS --strategy ma_crossover \
  --commission 0.0005

# Interactive Brokers style (0.1%)
python main.py backtest --symbol INFY.NS --strategy ma_crossover \
  --commission 0.001

# No commission (some discount brokers)
python main.py backtest --symbol INFY.NS --strategy ma_crossover \
  --commission 0
```

### 5. Capital Simulation

Test with different capital amounts:

```bash
# Small capital (₹50,000)
python main.py backtest --symbol INFY.NS --strategy ma_crossover \
  --capital 50000

# Medium capital (₹5,00,000)
python main.py backtest --symbol INFY.NS --strategy ma_crossover \
  --capital 500000

# Large capital (₹25,00,000)
python main.py backtest --symbol INFY.NS --strategy ma_crossover \
  --capital 2500000
```

---

## Understanding Metrics

### Key Performance Indicators

#### Returns
```
Total Return: 0.42%
Annual Return: 0.22%
```
How much profit/loss your strategy made.

#### Risk-Adjusted Returns
```
Sharpe Ratio: -5.31
Sortino Ratio: (Downside risk only)
Calmar Ratio: (Return / Max Drawdown)
```
Measures return per unit of risk.

#### Drawdown
```
Max Drawdown: 0.26%
```
Worst peak-to-trough decline. Lower is better.

#### Trade Statistics
```
Total Trades: 8
Winning Trades: 3
Losing Trades: 4
Win Rate: 37.50%
Profit Factor: 0.75
```
Track trading behavior.

### Good vs Bad Results

| Metric | Good | Bad |
|--------|------|-----|
| Annual Return | > 20% | < 5% |
| Sharpe Ratio | > 1.0 | < 0.5 |
| Win Rate | > 50% | < 30% |
| Max Drawdown | < 20% | > 50% |
| Profit Factor | > 1.5 | < 1.0 |

---

## Writing Custom Strategies

### Quick Template

Create `src/strategies/my_strategy.py`:

```python
import backtrader as bt
from src.backtesting.base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    """Your strategy description"""

    params = (
        ("param1", 10),
        ("param2", 20),
    )

    def _init_indicators(self):
        """Initialize indicators"""
        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.param1
        )

    def next(self):
        """Generate signals"""
        if self.data.close[0] > self.sma[0] and not self.position:
            self.buy_signal()
        elif self.data.close[0] < self.sma[0] and self.position:
            self.sell_signal()
```

Register in `src/strategies/__init__.py`:
```python
from .my_strategy import MyStrategy

__all__ = [..., 'MyStrategy']
```

Test it:
```bash
python main.py backtest --symbol INFY.NS --strategy my_strategy
```

See [STRATEGY_GUIDE.md](STRATEGY_GUIDE.md) for detailed examples.

---

## Common Issues & Solutions

### Issue: No trades generated
**Cause:** Signal conditions too strict or incorrect indicators
**Solution:**
- Lower thresholds
- Check indicator calculations
- Print debug info in `next()`

### Issue: High commission affecting results
**Cause:** Commission not matching your broker
**Solution:**
- Check your broker's actual commission
- Adjust with `--commission` flag

### Issue: Data not downloading
**Cause:** Symbol format incorrect or no connection
**Solution:**
- Verify symbol format (e.g., `INFY.NS`)
- Check internet connection
- Try again in a few minutes

### Issue: Strategy generates losses
**Cause:** Bad signal logic or market conditions
**Solution:**
- Test on different time periods
- Add confirmation indicators
- Optimize parameters
- Use different stocks

---

## Next Steps

1. **Learn Strategies:** Read [STRATEGY_GUIDE.md](STRATEGY_GUIDE.md)
2. **Experiment:** Test on different Indian stocks
3. **Optimize:** Find best parameters for your capital
4. **Validate:** Test on multiple time periods
5. **Refine:** Combine multiple indicators for robust signals

---

## Resources

- **Backtrader Docs:** https://www.backtrader.com/
- **Yahoo Finance API:** https://finance.yahoo.com/
- **NSE Holidays:** Check NSE calendar for trading days
- **Technical Analysis:** Learn moving averages, RSI, Bollinger Bands

---

## Support

For issues or questions:
1. Check error messages in logs
2. Review example strategies
3. Test on different symbols/periods
4. Simplify strategy logic

Happy trading! 📈
