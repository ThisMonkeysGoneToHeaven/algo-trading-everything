"""Momentum Strategy - Example for learning"""

import logging

import backtrader as bt

from src.backtesting.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


class MomentumStrategy(BaseStrategy):
    """
    Momentum Strategy.

    Uses Rate of Change (ROC) indicator to identify trending markets.
    Buy signal: ROC is positive (uptrend)
    Sell signal: ROC is negative (downtrend)

    This strategy is good for trending markets and can generate
    significant alpha during strong market moves.
    """

    params = (
        ("roc_period", 10),  # Rate of Change period
        ("roc_threshold", 0.5),  # Minimum ROC (%) to trigger signals
    )

    def _init_indicators(self):
        """Initialize momentum indicators"""
        # Calculate Rate of Change (ROC)
        # ROC = ((Close - Close_N_periods_ago) / Close_N_periods_ago) * 100
        self.roc = bt.indicators.RateOfChange(
            self.data.close, period=self.params.roc_period, plotname='ROC'
        )

        # Simple Moving Average for trend confirmation
        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=20, plotname='SMA20'
        )

        # Track the momentum value for logging
        self.last_roc = 0

    def next(self):
        """Generate trading signals based on momentum"""
        current_roc = self.roc[0]
        current_price = self.data.close[0]
        current_sma = self.sma[0]

        # Buy signal: Positive momentum + price above SMA (uptrend confirmation)
        if (current_roc > self.params.roc_threshold and
            current_price > current_sma and
            not self.position):

            self.buy_signal()
            self.log(
                f'BUY SIGNAL - ROC: {current_roc:.2f}%, '
                f'Price: {current_price:.2f}, SMA: {current_sma:.2f}'
            )

        # Sell signal: Negative momentum or price below SMA
        elif ((current_roc < -self.params.roc_threshold or
               current_price < current_sma) and
              self.position):

            self.sell_signal()
            self.log(
                f'SELL SIGNAL - ROC: {current_roc:.2f}%, '
                f'Price: {current_price:.2f}, SMA: {current_sma:.2f}'
            )

        self.last_roc = current_roc
