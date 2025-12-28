"""Performance analysis and metrics calculation"""

import logging
from typing import Dict, Any, List

import numpy as np
import pandas as pd

from src.utils.config import RISK_FREE_RATE, DAYS_PER_YEAR

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Analyze trading performance and calculate key metrics"""

    def __init__(self, returns: pd.Series, trades: List[Dict[str, Any]], risk_free_rate: float = RISK_FREE_RATE):
        """
        Initialize the analyzer.

        Args:
            returns: Series of portfolio returns
            trades: List of trade dictionaries with entry/exit prices and dates
            risk_free_rate: Annual risk-free rate for Sharpe/Sortino calculations
        """
        self.returns = returns
        self.trades = trades
        self.risk_free_rate = risk_free_rate
        self.daily_returns = returns
        self.annual_returns = None
        self.monthly_returns = None

    def calculate_all_metrics(self) -> Dict[str, Any]:
        """Calculate all performance metrics"""
        metrics = {
            'total_return': self.calculate_total_return(),
            'annual_return': self.calculate_annual_return(),
            'sharpe_ratio': self.calculate_sharpe_ratio(),
            'sortino_ratio': self.calculate_sortino_ratio(),
            'calmar_ratio': self.calculate_calmar_ratio(),
            'max_drawdown': self.calculate_max_drawdown(),
            'drawdown_duration': self.calculate_max_drawdown_duration(),
            'win_rate': self.calculate_win_rate(),
            'profit_factor': self.calculate_profit_factor(),
            'recovery_factor': self.calculate_recovery_factor(),
            'volatility': self.calculate_volatility(),
            'best_day': self.calculate_best_day(),
            'worst_day': self.calculate_worst_day(),
        }
        return metrics

    def calculate_total_return(self) -> float:
        """Calculate total return as percentage"""
        if len(self.returns) == 0:
            return 0.0
        return (self.returns.iloc[-1] - 1) * 100

    def calculate_annual_return(self) -> float:
        """Calculate annualized return"""
        if len(self.returns) == 0:
            return 0.0

        total_return = self.returns.iloc[-1] - 1
        n_years = len(self.returns) / DAYS_PER_YEAR

        if n_years <= 0:
            return 0.0

        annual_return = (1 + total_return) ** (1 / n_years) - 1
        return annual_return * 100

    def calculate_sharpe_ratio(self) -> float:
        """
        Calculate Sharpe Ratio (risk-adjusted return).
        Higher is better. Typical range: 0-2+
        """
        if len(self.daily_returns) < 2:
            return 0.0

        daily_returns = self.daily_returns.pct_change().dropna()

        if len(daily_returns) == 0 or daily_returns.std() == 0:
            return 0.0

        excess_return = daily_returns.mean() - (self.risk_free_rate / DAYS_PER_YEAR)
        sharpe = (excess_return / daily_returns.std()) * np.sqrt(DAYS_PER_YEAR)

        return float(sharpe)

    def calculate_sortino_ratio(self) -> float:
        """
        Calculate Sortino Ratio (only penalizes downside volatility).
        Higher is better. More favorable than Sharpe for upside-skewed strategies.
        """
        if len(self.daily_returns) < 2:
            return 0.0

        daily_returns = self.daily_returns.pct_change().dropna()

        if len(daily_returns) == 0:
            return 0.0

        # Only consider downside (negative) returns
        downside_returns = daily_returns[daily_returns < 0]

        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0

        excess_return = daily_returns.mean() - (self.risk_free_rate / DAYS_PER_YEAR)
        sortino = (excess_return / downside_returns.std()) * np.sqrt(DAYS_PER_YEAR)

        return float(sortino)

    def calculate_calmar_ratio(self) -> float:
        """
        Calculate Calmar Ratio (return divided by max drawdown).
        Higher is better. Good metric for comparing risk-adjusted returns.
        """
        annual_return = self.calculate_annual_return() / 100
        max_dd = self.calculate_max_drawdown() / 100

        if max_dd == 0 or max_dd is None:
            return 0.0

        calmar = annual_return / abs(max_dd)
        return float(calmar)

    def calculate_max_drawdown(self) -> float:
        """
        Calculate maximum drawdown (peak-to-trough decline).
        Expressed as percentage. Lower is better (closer to 0).
        """
        if len(self.returns) < 2:
            return 0.0

        cumulative = self.returns.cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max

        return float(drawdown.min() * 100)

    def calculate_max_drawdown_duration(self) -> int:
        """Calculate maximum number of days in a drawdown"""
        if len(self.returns) < 2:
            return 0

        cumulative = self.returns.cumprod()
        running_max = cumulative.expanding().max()
        in_drawdown = cumulative < running_max

        # Find consecutive True values
        drawdown_duration = 0
        current_duration = 0

        for is_dd in in_drawdown:
            if is_dd:
                current_duration += 1
                drawdown_duration = max(drawdown_duration, current_duration)
            else:
                current_duration = 0

        return int(drawdown_duration)

    def calculate_win_rate(self) -> float:
        """Calculate percentage of winning trades"""
        if len(self.trades) == 0:
            return 0.0

        winning = sum(1 for trade in self.trades if trade.get('pnl', 0) > 0)
        return (winning / len(self.trades)) * 100

    def calculate_profit_factor(self) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        if len(self.trades) == 0:
            return 0.0

        gross_profit = sum(trade.get('pnl', 0) for trade in self.trades if trade.get('pnl', 0) > 0)
        gross_loss = abs(sum(trade.get('pnl', 0) for trade in self.trades if trade.get('pnl', 0) < 0))

        if gross_loss == 0:
            return 0.0 if gross_profit == 0 else float('inf')

        return gross_profit / gross_loss

    def calculate_recovery_factor(self) -> float:
        """Calculate recovery factor (total return / max drawdown)"""
        total_return = self.calculate_total_return() / 100
        max_dd = self.calculate_max_drawdown() / 100

        if max_dd == 0:
            return 0.0

        return total_return / abs(max_dd)

    def calculate_volatility(self) -> float:
        """Calculate annualized volatility"""
        if len(self.daily_returns) < 2:
            return 0.0

        daily_returns = self.daily_returns.pct_change().dropna()

        if len(daily_returns) == 0:
            return 0.0

        return float(daily_returns.std() * np.sqrt(DAYS_PER_YEAR) * 100)

    def calculate_best_day(self) -> float:
        """Calculate best single day return"""
        if len(self.daily_returns) < 2:
            return 0.0

        daily_pct = self.daily_returns.pct_change().dropna()
        return float(daily_pct.max() * 100) if len(daily_pct) > 0 else 0.0

    def calculate_worst_day(self) -> float:
        """Calculate worst single day return"""
        if len(self.daily_returns) < 2:
            return 0.0

        daily_pct = self.daily_returns.pct_change().dropna()
        return float(daily_pct.min() * 100) if len(daily_pct) > 0 else 0.0

    def get_summary(self) -> str:
        """Get a formatted summary of all metrics"""
        metrics = self.calculate_all_metrics()

        summary = "\n" + "=" * 60 + "\n"
        summary += "PERFORMANCE ANALYSIS SUMMARY\n"
        summary += "=" * 60 + "\n"
        summary += f"Total Return:              {metrics['total_return']:.2f}%\n"
        summary += f"Annual Return:             {metrics['annual_return']:.2f}%\n"
        summary += f"Volatility (Annual):       {metrics['volatility']:.2f}%\n"
        summary += "\nRisk-Adjusted Metrics:\n"
        summary += f"  Sharpe Ratio:            {metrics['sharpe_ratio']:.2f}\n"
        summary += f"  Sortino Ratio:           {metrics['sortino_ratio']:.2f}\n"
        summary += f"  Calmar Ratio:            {metrics['calmar_ratio']:.2f}\n"
        summary += f"\nDrawdown Metrics:\n"
        summary += f"  Max Drawdown:            {metrics['max_drawdown']:.2f}%\n"
        summary += f"  Max DD Duration (days):  {metrics['drawdown_duration']}\n"
        summary += f"\nTrade Metrics:\n"
        summary += f"  Win Rate:                {metrics['win_rate']:.2f}%\n"
        summary += f"  Profit Factor:           {metrics['profit_factor']:.2f}\n"
        summary += f"  Recovery Factor:         {metrics['recovery_factor']:.2f}\n"
        summary += f"\nDaily Range:\n"
        summary += f"  Best Day:                {metrics['best_day']:.2f}%\n"
        summary += f"  Worst Day:               {metrics['worst_day']:.2f}%\n"
        summary += "=" * 60 + "\n"

        return summary
