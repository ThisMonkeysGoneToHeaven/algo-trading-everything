"""Visualization utilities for backtest results"""

import logging
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

from src.utils.config import RESULTS_DIR

logger = logging.getLogger(__name__)


class ResultsVisualizer:
    """Create visualizations for backtest results"""

    def __init__(self, figsize: tuple = (14, 10)):
        """Initialize the visualizer"""
        self.figsize = figsize
        self.results_dir = RESULTS_DIR

    def plot_equity_curve(
        self, equity_values: pd.Series, dates: pd.DatetimeIndex, symbol: str, filename: Optional[str] = None
    ):
        """Plot equity curve over time"""
        fig, ax = plt.subplots(figsize=self.figsize)

        ax.plot(dates, equity_values, linewidth=2, label='Portfolio Value', color='blue')
        ax.set_xlabel('Date')
        ax.set_ylabel('Portfolio Value ($)')
        ax.set_title(f'Equity Curve - {symbol}')
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=max(1, len(dates) // 12)))
        fig.autofmt_xdate(rotation=45)

        self._save_plot(filename or f'equity_curve_{symbol}.png')
        return fig

    def plot_drawdown(
        self, equity_values: pd.Series, dates: pd.DatetimeIndex, symbol: str, filename: Optional[str] = None
    ):
        """Plot drawdown over time"""
        # Calculate drawdown
        cumulative = equity_values
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max * 100

        fig, ax = plt.subplots(figsize=self.figsize)

        ax.fill_between(dates, drawdown, 0, color='red', alpha=0.3, label='Drawdown')
        ax.plot(dates, drawdown, linewidth=1, color='red')
        ax.set_xlabel('Date')
        ax.set_ylabel('Drawdown (%)')
        ax.set_title(f'Drawdown - {symbol}')
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=max(1, len(dates) // 12)))
        fig.autofmt_xdate(rotation=45)

        self._save_plot(filename or f'drawdown_{symbol}.png')
        return fig

    def plot_returns_distribution(
        self, returns: pd.Series, symbol: str, filename: Optional[str] = None, bins: int = 50
    ):
        """Plot distribution of returns"""
        fig, ax = plt.subplots(figsize=(10, 6))

        returns_pct = returns.pct_change().dropna() * 100
        ax.hist(returns_pct, bins=bins, color='blue', alpha=0.7, edgecolor='black')
        ax.set_xlabel('Daily Return (%)')
        ax.set_ylabel('Frequency')
        ax.set_title(f'Returns Distribution - {symbol}')
        ax.grid(True, alpha=0.3, axis='y')

        # Add statistics
        mean_return = returns_pct.mean()
        std_return = returns_pct.std()
        ax.axvline(mean_return, color='green', linestyle='--', linewidth=2, label=f'Mean: {mean_return:.2f}%')
        ax.axvline(0, color='black', linestyle='-', linewidth=0.5)
        ax.legend()

        self._save_plot(filename or f'returns_dist_{symbol}.png')
        return fig

    def plot_monthly_returns_heatmap(
        self, returns: pd.Series, symbol: str, filename: Optional[str] = None
    ):
        """Plot monthly returns as a heatmap"""
        # Calculate monthly returns
        monthly_returns = returns.resample('M').apply(lambda x: (x.iloc[-1] / x.iloc[0] - 1) * 100)

        # Pivot to year-month format
        monthly_returns.index = pd.to_datetime(monthly_returns.index)
        pivot_data = pd.DataFrame({
            'year': monthly_returns.index.year,
            'month': monthly_returns.index.month,
            'return': monthly_returns.values
        })
        pivot_table = pivot_data.pivot(index='month', columns='year', values='return')

        fig, ax = plt.subplots(figsize=(12, 6))

        im = ax.imshow(pivot_table.values, cmap='RdYlGn', aspect='auto', vmin=-10, vmax=10)
        ax.set_xticks(np.arange(len(pivot_table.columns)))
        ax.set_yticks(np.arange(len(pivot_table.index)))
        ax.set_xticklabels(pivot_table.columns)
        ax.set_yticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        ax.set_xlabel('Year')
        ax.set_ylabel('Month')
        ax.set_title(f'Monthly Returns Heatmap - {symbol}')

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Return (%)')

        # Add text annotations
        for i in range(len(pivot_table.index)):
            for j in range(len(pivot_table.columns)):
                if not pd.isna(pivot_table.iloc[i, j]):
                    text = ax.text(j, i, f'{pivot_table.iloc[i, j]:.1f}',
                                 ha="center", va="center", color="black", fontsize=8)

        fig.tight_layout()
        self._save_plot(filename or f'monthly_heatmap_{symbol}.png')
        return fig

    def plot_strategy_comparison(
        self,
        results: Dict[str, pd.Series],
        symbol: str,
        filename: Optional[str] = None,
    ):
        """Plot comparison of multiple strategies"""
        fig, ax = plt.subplots(figsize=self.figsize)

        for strategy_name, equity_values in results.items():
            # Normalize to 100 at start
            normalized = (equity_values / equity_values.iloc[0]) * 100
            ax.plot(normalized, label=strategy_name, linewidth=2)

        ax.set_xlabel('Date')
        ax.set_ylabel('Normalized Equity Value (Start = 100)')
        ax.set_title(f'Strategy Comparison - {symbol}')
        ax.grid(True, alpha=0.3)
        ax.legend()

        self._save_plot(filename or f'strategy_comparison_{symbol}.png')
        return fig

    def _save_plot(self, filename: str):
        """Save plot to results directory"""
        filepath = self.results_dir / filename
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        logger.info(f"Plot saved to {filepath}")
        plt.close()

    @staticmethod
    def show_plots():
        """Display all plots"""
        plt.show()
