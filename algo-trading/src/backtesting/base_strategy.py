"""Base strategy class for all trading strategies"""

import logging

import backtrader as bt

logger = logging.getLogger(__name__)


class BaseStrategy(bt.Strategy):
    """
    Base class for all trading strategies.

    Provides common functionality for trading signals and order management.
    Subclasses should override _init_indicators() and next() methods.
    """

    params = (
        ("position_size", 0.95),  # Use 95% of available capital per trade
        ("risk_per_trade", 0.02),  # Risk 2% per trade
        ("stop_loss_pct", 0.05),  # 5% stop loss
    )

    def __init__(self):
        """Initialize strategy indicators and state tracking"""
        self.order = None
        self.buy_price = None
        self.buy_comm = None
        self.trade_count = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0

        # Strategy-specific initialization
        self._init_indicators()

    def _init_indicators(self):
        """Initialize technical indicators. Override in subclass."""
        pass

    def next(self):
        """
        Generate trading signals.
        Should be implemented by subclass.
        Called for each bar in the data feed.
        """
        pass

    def notify_order(self, order):
        """
        Handle order notifications (submitted, accepted, completed, cancelled, etc.).
        """
        if order.status in [order.Submitted, order.Accepted]:
            # Order submitted/accepted - do nothing yet
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
                self.buy_comm = order.executed.comm
                logger.debug(f"BUY executed at price: {order.executed.price:.2f}")

            elif order.issell():
                logger.debug(f"SELL executed at price: {order.executed.price:.2f}")
                # Calculate trade result
                profit = order.executed.price - self.buy_price if self.buy_price else 0
                if profit > 0:
                    self.winning_trades += 1
                else:
                    self.losing_trades += 1
                self.total_profit += profit

            self.trade_count += 1
            self.order = None

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            logger.warning(f"Order canceled/margin/rejected: {order.status}")
            self.order = None

    def notify_trade(self, trade):
        """
        Handle trade notifications (when a trade closes).
        """
        if trade.isclosed:
            pnl_pct = (trade.pnl / trade.value) * 100 if trade.value else 0
            logger.debug(f"Trade closed - PnL: {trade.pnl:.2f}, PnL%: {pnl_pct:.2f}%")

    def buy_signal(self):
        """Execute a buy order if not already in position"""
        if not self.position:
            self.order = self.buy()

    def sell_signal(self):
        """Execute a sell order if in position"""
        if self.position:
            self.order = self.sell()

    def get_portfolio_value(self):
        """Get current portfolio value"""
        return self.broker.getvalue()

    def get_position_size(self):
        """Get current position size"""
        if self.position:
            return self.position.size
        return 0

    def log(self, txt, dt=None):
        """Log a string with date information"""
        dt = dt or self.datas[0].datetime.date(0)
        logger.info(f"{dt.isoformat()} {txt}")
