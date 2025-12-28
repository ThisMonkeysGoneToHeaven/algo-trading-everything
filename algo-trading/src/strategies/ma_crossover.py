"""Moving Average Crossover Strategy"""

import logging

import backtrader as bt

from src.backtesting.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


class MAcrossoverStrategy(BaseStrategy):
    """
    Moving Average Crossover Strategy.

    Buy signal: When fast MA crosses above slow MA
    Sell signal: When fast MA crosses below slow MA
    """

    params = (
        ("fast_ma", 10),  # Fast moving average period
        ("slow_ma", 30),  # Slow moving average period
    )

    def _init_indicators(self):
        """Initialize moving average indicators"""
        # Calculate moving averages
        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.fast_ma, plotname='Fast MA'
        )
        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.slow_ma, plotname='Slow MA'
        )

        # Crossover indicator
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

    def next(self):
        """Generate trading signals based on MA crossover"""
        # Buy signal: fast MA crosses above slow MA
        if self.crossover > 0:
            self.buy_signal()
            self.log(
                f'BUY CREATE, {self.data.close[0]:.2f}, '
                f'Fast MA: {self.fast_ma[0]:.2f}, Slow MA: {self.slow_ma[0]:.2f}'
            )

        # Sell signal: fast MA crosses below slow MA
        elif self.crossover < 0:
            self.sell_signal()
            self.log(
                f'SELL CREATE, {self.data.close[0]:.2f}, '
                f'Fast MA: {self.fast_ma[0]:.2f}, Slow MA: {self.slow_ma[0]:.2f}'
            )
