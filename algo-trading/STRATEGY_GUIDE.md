# How to Write & Use Custom Trading Strategies

This guide teaches you how to create your own trading strategies for the Algo Trading Bot.

## Quick Start: Creating Your First Strategy

### Step 1: Create a New Strategy File

Create a new Python file in `src/strategies/` directory. For example, let's create a **Volume-Weighted Strategy**:

```bash
# Create the file
touch src/strategies/volume_strategy.py
```

### Step 2: Write Your Strategy Class

Here's a template to get started:

```python
"""Your Strategy Description"""

import logging
import backtrader as bt
from src.backtesting.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


class VolumeStrategy(BaseStrategy):
    """
    Your strategy documentation here.
    Explain:
    - What signals it uses
    - When to buy
    - When to sell
    - What market conditions it works best in
    """

    # Strategy parameters - users can customize these
    params = (
        ("volume_period", 20),  # Look back period for volume analysis
        ("volume_threshold", 1.5),  # Minimum volume ratio
    )

    def _init_indicators(self):
        """Initialize all technical indicators"""
        # Calculate indicators here
        # Calculate moving average of volume
        self.volume_sma = bt.indicators.SimpleMovingAverage(
            self.data.volume, period=self.params.volume_period
        )

    def next(self):
        """Generate buy/sell signals (called for each bar)"""
        current_volume = self.data.volume[0]
        avg_volume = self.volume_sma[0]
        current_price = self.data.close[0]

        # BUY: Volume surge detected
        if (current_volume > avg_volume * self.params.volume_threshold and
            not self.position):
            self.buy_signal()
            self.log(f"BUY - Volume: {current_volume:.0f}, Avg: {avg_volume:.0f}")

        # SELL: Volume dries up
        elif (current_volume < avg_volume and self.position):
            self.sell_signal()
            self.log(f"SELL - Volume returned to normal")
```

### Step 3: Register Your Strategy

Add your strategy to `src/strategies/__init__.py`:

```python
from .volume_strategy import VolumeStrategy

__all__ = [..., 'VolumeStrategy']
```

### Step 4: Run Your Strategy

```bash
# Test your strategy
python main.py backtest --symbol INFY.NS --strategy volume_strategy

# With custom parameters
python main.py backtest --symbol TCS.NS --strategy volume_strategy \
  --volume-period 25 --volume-threshold 2.0

# With visualization
python main.py backtest --symbol RELIANCE.NS --strategy volume_strategy --plot
```

---

## Understanding the BaseStrategy Class

Your strategy inherits from `BaseStrategy`, which provides:

### Key Methods to Override

#### 1. `_init_indicators()`
Initialize all technical indicators in this method:

```python
def _init_indicators(self):
    """Called once at strategy initialization"""
    # Example indicators
    self.sma_fast = bt.indicators.SimpleMovingAverage(
        self.data.close, period=10
    )
    self.sma_slow = bt.indicators.SimpleMovingAverage(
        self.data.close, period=30
    )
    self.rsi = bt.indicators.RSI(self.data.close, period=14)
    self.bb = bt.indicators.BollingerBands(self.data.close, period=20)
```

#### 2. `next()`
Generate signals for each bar (called for every candle):

```python
def next(self):
    """Called for each bar/candle"""
    # Access current values using [0]
    price = self.data.close[0]
    open_ = self.data.open[0]
    high = self.data.high[0]
    low = self.data.low[0]
    volume = self.data.volume[0]

    # Previous values using [-1], [-2], etc.
    prev_close = self.data.close[-1]
    price_2_bars_ago = self.data.close[-2]

    # Your signal logic
    if price > self.sma_fast[0] and self.sma_fast[0] > self.sma_slow[0]:
        self.buy_signal()
    elif price < self.sma_slow[0]:
        self.sell_signal()
```

### Useful Properties

```python
# Current position
if self.position:  # True if holding a position
    size = self.position.size  # Current position size
    price = self.position.price  # Entry price

# Portfolio info
portfolio_value = self.broker.getvalue()  # Current portfolio value
cash = self.broker.getcash()  # Available cash

# Bar information
current_date = self.datas[0].datetime.date(0)  # Current bar date
```

### Helper Methods

```python
# Place orders
self.buy_signal()   # Buy 1 unit
self.sell_signal()  # Sell position

# Logging
self.log(f"Price: {self.data.close[0]:.2f}")
```

---

## Real-World Examples

### Example 1: Simple Moving Average Crossover

```python
class SimpleMACrossover(BaseStrategy):
    """When fast MA crosses above slow MA, buy. When it crosses below, sell."""

    params = (
        ("ma_fast", 10),
        ("ma_slow", 30),
    )

    def _init_indicators(self):
        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.ma_fast
        )
        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.ma_slow
        )
        # Detects crossover automatically
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

    def next(self):
        # crossover > 0 means fast MA crossed above slow MA (bullish)
        # crossover < 0 means fast MA crossed below slow MA (bearish)
        if self.crossover > 0:
            self.buy_signal()
            self.log(f"GOLDEN CROSS - Fast MA above Slow MA")
        elif self.crossover < 0:
            self.sell_signal()
            self.log(f"DEATH CROSS - Fast MA below Slow MA")
```

### Example 2: Mean Reversion (Bollinger Bands)

```python
class MeanReversion(BaseStrategy):
    """Buy when price touches lower band, sell at upper band or middle."""

    params = (
        ("bb_period", 20),
        ("bb_std", 2),
    )

    def _init_indicators(self):
        self.bb = bt.indicators.BollingerBands(
            self.data.close,
            period=self.params.bb_period,
            devfactor=self.params.bb_std
        )

    def next(self):
        price = self.data.close[0]

        # Buy at lower band (oversold)
        if price <= self.bb.lines.bot[0] and not self.position:
            self.buy_signal()
            self.log(f"Price touching lower band: {price:.2f}")

        # Sell at middle band (mean reversion)
        elif price >= self.bb.lines.mid[0] and self.position:
            self.sell_signal()
            self.log(f"Price reaching middle band: {price:.2f}")
```

### Example 3: Trend Following with Momentum

```python
class TrendMomentum(BaseStrategy):
    """Buy on uptrend with increasing momentum. Sell on momentum loss."""

    params = (
        ("momentum_period", 10),
        ("trend_period", 50),
    )

    def _init_indicators(self):
        # Momentum indicator (ROC = Rate of Change)
        self.momentum = bt.indicators.Momentum(
            self.data.close, period=self.params.momentum_period
        )
        # Trend: Long MA
        self.trend = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.trend_period
        )

    def next(self):
        price = self.data.close[0]
        momentum = self.momentum[0]

        # Buy: Price above trend + positive momentum
        if price > self.trend[0] and momentum > 0 and not self.position:
            self.buy_signal()
            self.log(f"Uptrend with momentum: {momentum:.2f}")

        # Sell: Momentum becomes negative
        elif momentum < 0 and self.position:
            self.sell_signal()
            self.log(f"Momentum loss: {momentum:.2f}")
```

### Example 4: Multi-Signal Strategy

```python
class MultiSignal(BaseStrategy):
    """Combine multiple signals for more robust entries."""

    def _init_indicators(self):
        # Trend
        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=20
        )
        # Momentum
        self.rsi = bt.indicators.RSI(self.data.close, period=14)
        # Volatility
        self.bb = bt.indicators.BollingerBands(self.data.close, period=20)

    def next(self):
        price = self.data.close[0]

        # BUY conditions (must have ALL):
        # 1. Price above 20-day SMA
        # 2. RSI not overbought (< 70)
        # 3. Price above lower Bollinger Band
        buy_trend = price > self.sma[0]
        buy_momentum = self.rsi[0] < 70
        buy_volatility = price > self.bb.lines.bot[0]

        if buy_trend and buy_momentum and buy_volatility and not self.position:
            self.buy_signal()
            self.log("Multi-signal BUY")

        # SELL conditions:
        # 1. RSI overbought (> 70)
        # 2. Price below SMA
        sell_momentum = self.rsi[0] > 70
        sell_trend = price < self.sma[0]

        if (sell_momentum or sell_trend) and self.position:
            self.sell_signal()
            self.log("Multi-signal SELL")
```

---

## Common Backtrader Indicators

### Trend Indicators
```python
# Moving Averages
bt.indicators.SimpleMovingAverage(self.data, period=20)
bt.indicators.ExponentialMovingAverage(self.data, period=20)

# MACD
bt.indicators.MACD(self.data)

# ADX (Trend Strength)
bt.indicators.AverageDirectionalMovementIndex(self.data)
```

### Momentum Indicators
```python
# RSI
bt.indicators.RSI(self.data, period=14)

# Stochastic
bt.indicators.Stochastic(self.data)

# ROC (Rate of Change)
bt.indicators.RateOfChange(self.data, period=10)

# Momentum
bt.indicators.Momentum(self.data, period=10)
```

### Volatility Indicators
```python
# Bollinger Bands
bt.indicators.BollingerBands(self.data, period=20)

# ATR (Average True Range)
bt.indicators.AverageTrueRange(self.data, period=14)

# Standard Deviation
bt.indicators.StandardDeviation(self.data, period=20)
```

### Volume Indicators
```python
# On-Balance Volume
bt.indicators.OnBalanceVolume(self.data)

# Volume Rate of Change
bt.indicators.RateOfChange(self.data.volume, period=10)
```

---

## Testing Your Strategy

### 1. Backtest on Indian Stocks

```bash
# Test on NIFTY 50 stocks
python main.py backtest --symbol RELIANCE.NS --strategy my_strategy --plot
python main.py backtest --symbol INFY.NS --strategy my_strategy
python main.py backtest --symbol TCS.NS --strategy my_strategy
python main.py backtest --symbol HDFC.NS --strategy my_strategy
```

### 2. Optimize Parameters

```bash
# Try different parameters
python main.py backtest --symbol INFY.NS --strategy my_strategy --fast-ma 5
python main.py backtest --symbol INFY.NS --strategy my_strategy --fast-ma 10
python main.py backtest --symbol INFY.NS --strategy my_strategy --fast-ma 15
```

### 3. Test Different Timeframes

```bash
# 1-hour data
python main.py backtest --symbol INFY.NS --strategy my_strategy --interval 1h

# 30-minute data
python main.py backtest --symbol INFY.NS --strategy my_strategy --interval 30m

# Weekly data
python main.py backtest --symbol INFY.NS --strategy my_strategy --interval 1wk
```

### 4. Test on Different Periods

```bash
# Bull market
python main.py backtest --symbol INFY.NS --strategy my_strategy \
  --start-date 2023-03-01 --end-date 2024-09-01

# Bear market
python main.py backtest --symbol INFY.NS --strategy my_strategy \
  --start-date 2022-01-01 --end-date 2023-06-01

# Volatile period
python main.py backtest --symbol INFY.NS --strategy my_strategy \
  --start-date 2024-01-01 --end-date 2024-12-31
```

---

## Analyzing Results

The backtest generates comprehensive metrics:

### Key Metrics to Evaluate

| Metric | What it means | Good value |
|--------|--------------|-----------|
| **Total Return** | Profit/loss % | > 20% |
| **Sharpe Ratio** | Risk-adjusted return | > 1.0 |
| **Max Drawdown** | Worst loss from peak | < 20% |
| **Win Rate** | % profitable trades | > 50% |
| **Profit Factor** | Gross profit / Gross loss | > 1.5 |
| **Calmar Ratio** | Return / Max Drawdown | > 1.0 |

### What to Look For

```
✓ Good Strategy
- Total Return > 20%
- Sharpe > 1.0
- Win Rate > 50%
- Max Drawdown < 20%
- Profit Factor > 1.5

✗ Bad Strategy
- Negative returns
- Sharpe < 0.5
- Win Rate < 40%
- Max Drawdown > 50%
- Profit Factor < 1.0
```

---

## Advanced Tips

### 1. Account for Transaction Costs

Adjust commission based on your broker:
```bash
# Zero-fee broker (like some discount brokers)
python main.py backtest --symbol INFY.NS --strategy my_strategy --commission 0

# Zerodha-like (0.05% brokerage)
python main.py backtest --symbol INFY.NS --strategy my_strategy --commission 0.0005

# Traditional broker (0.1% brokerage)
python main.py backtest --symbol INFY.NS --strategy my_strategy --commission 0.001
```

### 2. Use Different Capital Amounts

Test with realistic capital:
```bash
# ₹1 Lakh
python main.py backtest --symbol INFY.NS --strategy my_strategy --capital 100000

# ₹10 Lakhs
python main.py backtest --symbol INFY.NS --strategy my_strategy --capital 1000000

# ₹25 Lakhs (enough for 4-5 stocks)
python main.py backtest --symbol INFY.NS --strategy my_strategy --capital 2500000
```

### 3. Avoid Overfitting

- Test on different symbols
- Test on different time periods
- Test on different market conditions (bull/bear/sideways)
- Don't over-optimize parameters

### 4. Walk-Forward Analysis

Test on different periods to see consistency:

```bash
# Period 1: 2022
python main.py backtest --symbol INFY.NS --strategy my_strategy \
  --start-date 2022-01-01 --end-date 2022-12-31

# Period 2: 2023
python main.py backtest --symbol INFY.NS --strategy my_strategy \
  --start-date 2023-01-01 --end-date 2023-12-31

# Period 3: 2024
python main.py backtest --symbol INFY.NS --strategy my_strategy \
  --start-date 2024-01-01 --end-date 2024-12-31
```

---

## Debugging Your Strategy

### Enable Detailed Logging

Your strategy automatically logs key signals. Check the logs:

```
2025-02-19 10:30:45 - BUY CREATE, 243.83, Fast MA: 233.96, Slow MA: 232.85
2025-03-11 14:22:10 - SELL CREATE, 223.05, Fast MA: 235.65, Slow MA: 235.94
```

### Print Debug Information

```python
def next(self):
    print(f"Date: {self.datas[0].datetime.date(0)}")
    print(f"Price: {self.data.close[0]:.2f}")
    print(f"Volume: {self.data.volume[0]:.0f}")
    print(f"Position: {self.position.size if self.position else 'No position'}")
```

---

## Next Steps

1. **Start simple**: Master MA Crossover before complex strategies
2. **Combine signals**: Use multiple indicators for confirmation
3. **Manage risk**: Always have stop-losses
4. **Test thoroughly**: On different symbols and time periods
5. **Keep records**: Document what works and what doesn't

Happy trading! 📈
