"""Enhanced visualization with buy/sell points and detailed analysis"""

import logging
from typing import List, Tuple, Optional, Dict, Any

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

from src.utils.config import RESULTS_DIR

logger = logging.getLogger(__name__)


class EnhancedVisualizer:
    """Create detailed visualizations with buy/sell signals and analytics"""

    def __init__(self, figsize: Tuple[int, int] = (16, 12)):
        """Initialize the visualizer"""
        self.figsize = figsize
        self.results_dir = RESULTS_DIR

    def plot_strategy_analysis(
        self,
        data: pd.DataFrame,
        trades: List[Dict[str, Any]],
        symbol: str,
        strategy_name: str,
        filename: Optional[str] = None,
    ):
        """
        Create comprehensive strategy analysis plot with:
        - Price and indicators
        - Buy/Sell entry points
        - Profit/Loss regions
        - Returns below

        Args:
            data: OHLCV DataFrame
            trades: List of trade dicts with 'entry_date', 'exit_date', 'entry_price', 'exit_price', 'pnl'
            symbol: Stock symbol
            strategy_name: Name of the strategy
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figsize, gridspec_kw={'height_ratios': [3, 1]})

        # Plot price
        ax1.plot(data.index, data['Close'], linewidth=2, color='black', label='Close Price', zorder=2)

        # Add volume
        ax1_vol = ax1.twinx()
        ax1_vol.bar(data.index, data['Volume'], alpha=0.2, color='gray', label='Volume')
        ax1_vol.set_ylabel('Volume', fontsize=10)
        ax1_vol.tick_params(axis='y', labelsize=8)

        # Plot buy/sell signals
        if trades:
            for trade in trades:
                entry_date = trade.get('entry_date')
                exit_date = trade.get('exit_date')
                entry_price = trade.get('entry_price')
                exit_price = trade.get('exit_price')
                pnl = trade.get('pnl', 0)

                # Plot entry signal
                if entry_date and entry_price:
                    ax1.scatter(entry_date, entry_price, color='green', s=200, marker='^',
                              zorder=5, edgecolors='darkgreen', linewidths=2, label='Buy Signal' if trade == trades[0] else '')

                # Plot exit signal
                if exit_date and exit_price:
                    color = 'red' if pnl < 0 else 'orange'
                    ax1.scatter(exit_date, exit_price, color=color, s=200, marker='v',
                              zorder=5, edgecolors='darkred', linewidths=2, label='Sell Signal' if trade == trades[0] else '')

                # Draw profit/loss shaded region
                if entry_date and exit_date:
                    ax1.axvspan(entry_date, exit_date, alpha=0.1, color='green' if pnl >= 0 else 'red')

        ax1.set_ylabel('Price (INR)', fontsize=11)
        ax1.set_title(f'{symbol} - {strategy_name}\nBuy/Sell Signals & Price Action', fontsize=13, fontweight='bold')
        ax1.legend(loc='upper left', fontsize=9)
        ax1.grid(True, alpha=0.3)

        # Plot returns
        returns = data['Close'].pct_change() * 100
        colors = ['green' if r > 0 else 'red' for r in returns]
        ax2.bar(data.index, returns, color=colors, alpha=0.6, width=1)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax2.set_ylabel('Daily Return (%)', fontsize=11)
        ax2.set_xlabel('Date', fontsize=11)
        ax2.grid(True, alpha=0.3, axis='y')

        # Format dates
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=max(1, len(data) // 12)))
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=max(1, len(data) // 12)))
        fig.autofmt_xdate(rotation=45)

        fig.tight_layout()
        self._save_plot(filename or f'strategy_analysis_{symbol}_{strategy_name}.png')
        return fig

    def plot_drawdown_detailed(
        self,
        data: pd.DataFrame,
        symbol: str,
        strategy_name: str,
        filename: Optional[str] = None,
    ):
        """Plot detailed drawdown analysis"""
        # Calculate cumulative returns
        returns = data['Close'].pct_change().fillna(0)
        cumulative = (1 + returns).cumprod()

        # Calculate drawdown
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max * 100

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={'height_ratios': [2, 1]})

        # Plot cumulative returns
        ax1.plot(data.index, (cumulative - 1) * 100, linewidth=2, color='blue', label='Cumulative Return')
        ax1.fill_between(data.index, (cumulative - 1) * 100, 0, alpha=0.2, color='blue')
        ax1.set_ylabel('Cumulative Return (%)', fontsize=11)
        ax1.set_title(f'{symbol} - {strategy_name}\nCumulative Returns', fontsize=13, fontweight='bold')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)

        # Plot drawdown
        colors = ['red' if dd < 0 else 'green' for dd in drawdown]
        ax2.bar(data.index, drawdown, color=colors, alpha=0.6, width=1, label='Drawdown')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax2.set_ylabel('Drawdown (%)', fontsize=11)
        ax2.set_xlabel('Date', fontsize=11)
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')

        # Format dates
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=max(1, len(data) // 12)))
        ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=max(1, len(data) // 12)))
        fig.autofmt_xdate(rotation=45)

        fig.tight_layout()
        self._save_plot(filename or f'drawdown_analysis_{symbol}_{strategy_name}.png')
        return fig

    def plot_returns_distribution(
        self,
        data: pd.DataFrame,
        symbol: str,
        strategy_name: str,
        filename: Optional[str] = None,
        bins: int = 50,
    ):
        """Plot returns distribution with statistics"""
        returns_pct = data['Close'].pct_change().dropna() * 100

        fig, ax = plt.subplots(figsize=(12, 6))

        ax.hist(returns_pct, bins=bins, color='skyblue', alpha=0.7, edgecolor='black')
        ax.set_xlabel('Daily Return (%)', fontsize=11)
        ax.set_ylabel('Frequency', fontsize=11)
        ax.set_title(f'{symbol} - {strategy_name}\nReturns Distribution', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        # Add statistics
        mean_return = returns_pct.mean()
        std_return = returns_pct.std()
        ax.axvline(mean_return, color='green', linestyle='--', linewidth=2.5, label=f'Mean: {mean_return:.2f}%')
        ax.axvline(0, color='black', linestyle='-', linewidth=1)
        ax.axvline(mean_return + std_return, color='orange', linestyle=':', linewidth=2, label=f'Std: {std_return:.2f}%')
        ax.axvline(mean_return - std_return, color='orange', linestyle=':', linewidth=2)

        # Add text with statistics
        stats_text = f"Mean: {mean_return:.3f}%\nStd Dev: {std_return:.3f}%\nSkew: {returns_pct.skew():.3f}"
        ax.text(0.98, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        ax.legend(loc='upper left', fontsize=9)
        fig.tight_layout()
        self._save_plot(filename or f'returns_dist_{symbol}_{strategy_name}.png')
        return fig

    def plot_monthly_heatmap(
        self,
        data: pd.DataFrame,
        symbol: str,
        strategy_name: str,
        filename: Optional[str] = None,
    ):
        """Plot monthly returns heatmap"""
        # Calculate monthly returns
        monthly_data = data['Close'].resample('M').last()
        monthly_returns = monthly_data.pct_change() * 100

        # Create year-month pivot
        monthly_returns.index = pd.to_datetime(monthly_returns.index)
        pivot_data = pd.DataFrame({
            'year': monthly_returns.index.year,
            'month': monthly_returns.index.month,
            'return': monthly_returns.values
        })
        pivot_table = pivot_data.pivot(index='month', columns='year', values='return').fillna(0)

        fig, ax = plt.subplots(figsize=(12, 6))

        im = ax.imshow(pivot_table.values, cmap='RdYlGn', aspect='auto', vmin=-5, vmax=5)
        ax.set_xticks(np.arange(len(pivot_table.columns)))
        ax.set_yticks(np.arange(len(pivot_table.index)))
        ax.set_xticklabels(pivot_table.columns)
        ax.set_yticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        ax.set_xlabel('Year', fontsize=11)
        ax.set_ylabel('Month', fontsize=11)
        ax.set_title(f'{symbol} - {strategy_name}\nMonthly Returns Heatmap (%)', fontsize=13, fontweight='bold')

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Return (%)', fontsize=10)

        # Add text annotations
        for i in range(len(pivot_table.index)):
            for j in range(len(pivot_table.columns)):
                if pivot_table.iloc[i, j] != 0:
                    text = ax.text(j, i, f'{pivot_table.iloc[i, j]:.1f}',
                                 ha="center", va="center", color="black", fontsize=8, fontweight='bold')

        fig.tight_layout()
        self._save_plot(filename or f'monthly_heatmap_{symbol}_{strategy_name}.png')
        return fig

    def _save_plot(self, filename: str):
        """Save plot to results directory"""
        filepath = self.results_dir / filename
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        logger.info(f"Plot saved to {filepath}")
        plt.close()
