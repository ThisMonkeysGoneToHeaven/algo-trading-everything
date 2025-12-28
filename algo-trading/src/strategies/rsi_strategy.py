"""RSI (Relative Strength Index) Strategy"""

import logging

import backtrader as bt

from src.backtesting.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


class RSIStrategy(BaseStrategy):
    """
    RSI (Relative Strength Index) Strategy.

    Buy signal: RSI < 30 (oversold)
    Sell signal: RSI > 70 (overbought)
    """

    params = (
        ("rsi_period", 14),
        ("rsi_lower", 30),  # Oversold threshold
        ("rsi_upper", 70),  # Overbought threshold
    )

    def _init_indicators(self):
        """Initialize RSI indicator"""
        self.rsi = bt.indicators.RSI(
            self.data.close, period=self.params.rsi_period, plotname='RSI'
        )

    def next(self):
        """Generate trading signals based on RSI levels"""
        # Buy signal: RSI oversold
        if self.rsi[0] < self.params.rsi_lower and not self.position:
            self.buy_signal()
            self.log(f'BUY CREATE, Close: {self.data.close[0]:.2f}, RSI: {self.rsi[0]:.2f}')

        # Sell signal: RSI overbought
        elif self.rsi[0] > self.params.rsi_upper and self.position:
            self.sell_signal()
            self.log(f'SELL CREATE, Close: {self.data.close[0]:.2f}, RSI: {self.rsi[0]:.2f}')
