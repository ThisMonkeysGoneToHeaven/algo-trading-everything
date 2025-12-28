"""Bollinger Bands Strategy"""

import logging

import backtrader as bt

from src.backtesting.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


class BollingerBandsStrategy(BaseStrategy):
    """
    Bollinger Bands Strategy.

    Buy signal: Price touches lower band (mean reversion)
    Sell signal: Price touches upper band
    """

    params = (
        ("bb_period", 20),
        ("bb_std", 2),  # Standard deviation multiplier
    )

    def _init_indicators(self):
        """Initialize Bollinger Bands indicator"""
        self.bb = bt.indicators.BollingerBands(
            self.data.close,
            period=self.params.bb_period,
            devfactor=self.params.bb_std,
            plotname='BB',
        )

    def next(self):
        """Generate trading signals based on Bollinger Bands"""
        # Buy signal: Price touches lower band
        if self.data.close[0] <= self.bb.lines.bot[0] and not self.position:
            self.buy_signal()
            self.log(
                f'BUY CREATE, Close: {self.data.close[0]:.2f}, '
                f'Lower Band: {self.bb.lines.bot[0]:.2f}'
            )

        # Sell signal: Price touches upper band
        elif self.data.close[0] >= self.bb.lines.top[0] and self.position:
            self.sell_signal()
            self.log(
                f'SELL CREATE, Close: {self.data.close[0]:.2f}, '
                f'Upper Band: {self.bb.lines.top[0]:.2f}'
            )
