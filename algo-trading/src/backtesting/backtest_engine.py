"""Backtest engine for running trading strategies"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

import backtrader as bt
import pandas as pd

from src.data.data_fetcher import DataFetcher
from src.utils.config import DEFAULT_CAPITAL, DEFAULT_COMMISSION

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Run backtests with given strategies and data"""

    def __init__(
        self,
        initial_capital: float = DEFAULT_CAPITAL,
        commission: float = DEFAULT_COMMISSION,
    ):
        """
        Initialize the backtest engine.

        Args:
            initial_capital: Starting capital for the backtest
            commission: Commission per trade as decimal (0.001 = 0.1%)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.data_fetcher = DataFetcher()
        self.results: Dict[str, Any] = {}

    def run(
        self,
        strategy_class: Type[bt.Strategy],
        data: pd.DataFrame,
        strategy_params: Optional[Dict[str, Any]] = None,
        symbol: str = "SYMBOL",
    ) -> Dict[str, Any]:
        """
        Run a backtest with the given strategy.

        Args:
            strategy_class: Trading strategy class (must inherit from bt.Strategy)
            data: DataFrame with OHLCV data
            strategy_params: Optional parameters to pass to strategy
            symbol: Symbol being traded (for logging)

        Returns:
            Dictionary with backtest results
        """
        logger.info(f"Starting backtest for {symbol}...")

        # Create a cerebro engine
        cerebro = bt.Cerebro()

        # Set initial capital
        cerebro.broker.setcash(self.initial_capital)
        cerebro.broker.setcommission(commission=self.commission)

        # Create a data feed from the DataFrame
        data_feed = self._create_data_feed(data)
        cerebro.adddata(data_feed)

        # Add strategy
        if strategy_params is None:
            strategy_params = {}
        cerebro.addstrategy(strategy_class, **strategy_params)

        # Add analyzers for performance metrics
        self._add_analyzers(cerebro)

        # Run the backtest
        logger.info(f"Running strategy: {strategy_class.__name__}")
        results = cerebro.run()
        strat = results[0]

        # Extract results
        backtest_results = self._extract_results(strat, symbol)
        self.results = backtest_results

        logger.info(f"Backtest completed. Final portfolio value: ${backtest_results['final_value']:.2f}")
        return backtest_results

    def _create_data_feed(self, data: pd.DataFrame) -> bt.feeds.PandasData:
        """Create a Backtrader data feed from a DataFrame"""
        # Ensure the DataFrame has the required columns
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        if not all(col in data.columns for col in required_cols):
            raise ValueError(f"DataFrame must contain columns: {required_cols}")

        # Create PandasData feed
        data_feed = bt.feeds.PandasData(
            dataname=data,
            fromdate=data.index[0],
            todate=data.index[-1],
        )

        return data_feed

    def _add_analyzers(self, cerebro):
        """Add performance analyzers to the cerebro engine"""
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
        cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr')

    def _extract_results(self, strat, symbol: str) -> Dict[str, Any]:
        """Extract relevant metrics from backtest results"""
        analyzers = strat.analyzers

        # Get trade analysis
        trades = analyzers.trades.get_analysis()
        total_trades = trades.get('total', {}).get('total', 0)
        winning_trades = trades.get('won', {}).get('total', 0)
        losing_trades = trades.get('lost', {}).get('total', 0)

        # Get drawdown analysis
        try:
            drawdown = analyzers.drawdown.get_analysis()
            max_drawdown = (drawdown.get('max', {}).get('drawdown', 0) or 0) / 100  # Convert to decimal
        except Exception:
            max_drawdown = 0

        # Get returns analysis
        returns = analyzers.returns.get_analysis()
        total_return = returns.get('rtot', 0)
        annual_return = returns.get('rnorm', 0)

        # Get Sharpe ratio (annualized)
        try:
            sharpe = analyzers.sharpe_ratio.get_analysis()
            sharpe_ratio = sharpe.get('sharperatio', 0) or 0
        except Exception:
            sharpe_ratio = 0

        # Final portfolio value
        final_value = strat.broker.getvalue()
        total_profit = final_value - self.initial_capital

        # Win rate
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        # Profit factor
        profit_factor = 0.0
        if 'won' in trades and 'lost' in trades:
            won_sum = trades['won'].get('total', 0)
            lost_sum = abs(trades['lost'].get('total', 0))
            if lost_sum > 0:
                profit_factor = float(won_sum / lost_sum)
            elif won_sum > 0:
                profit_factor = float('inf')  # Will be handled in printing

        results = {
            'symbol': symbol,
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_profit': total_profit,
            'total_return': total_return * 100,  # Convert to percentage
            'annual_return': annual_return * 100,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown * 100,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'backtest_start': strat.datas[0].datetime.date(0),
            'backtest_end': strat.datas[0].datetime.date(-1),
            'strategy': strat.__class__.__name__,
        }

        return results

    def print_results(self, results: Optional[Dict[str, Any]] = None):
        """Pretty print backtest results"""
        if results is None:
            results = self.results

        if not results:
            logger.warning("No results to print")
            return

        print("\n" + "=" * 60)
        print(f"BACKTEST RESULTS FOR {results.get('symbol', 'UNKNOWN')}")
        print("=" * 60)
        print(f"Strategy: {results.get('strategy', 'N/A')}")
        print(f"Period: {results.get('backtest_start')} to {results.get('backtest_end')}")
        print(f"\nCapital:")
        print(f"  Initial Capital: ${results.get('initial_capital', 0):,.2f}")
        print(f"  Final Value: ${results.get('final_value', 0):,.2f}")
        print(f"  Total Profit: ${results.get('total_profit', 0):,.2f}")
        print(f"\nReturns:")
        print(f"  Total Return: {results.get('total_return', 0):.2f}%")
        print(f"  Annual Return: {results.get('annual_return', 0):.2f}%")
        print(f"  Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}")
        print(f"\nRisk Metrics:")
        print(f"  Max Drawdown: {results.get('max_drawdown', 0):.2f}%")
        print(f"\nTrade Statistics:")
        print(f"  Total Trades: {results.get('total_trades', 0)}")
        print(f"  Winning Trades: {results.get('winning_trades', 0)}")
        print(f"  Losing Trades: {results.get('losing_trades', 0)}")
        print(f"  Win Rate: {results.get('win_rate', 0):.2f}%")

        # Handle profit factor (can be infinity)
        pf = results.get('profit_factor', 0)
        if pf == float('inf'):
            print(f"  Profit Factor: ∞ (All winning trades)")
        else:
            print(f"  Profit Factor: {pf:.2f}")

        print("=" * 60 + "\n")
