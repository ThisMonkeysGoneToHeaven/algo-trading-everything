"""Command-line interface for the trading bot"""

import logging
from datetime import datetime, timedelta

import click
import pandas as pd

from src.data.data_fetcher import DataFetcher
from src.backtesting.backtest_engine import BacktestEngine
from src.strategies import MAcrossoverStrategy, RSIStrategy, BollingerBandsStrategy, MomentumStrategy
from src.utils.visualization import ResultsVisualizer
from src.utils.config import DEFAULT_CAPITAL, DEFAULT_COMMISSION, TIMEFRAMES, INDIAN_STOCKS

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Strategy mapping
STRATEGIES = {
    'ma_crossover': MAcrossoverStrategy,
    'rsi': RSIStrategy,
    'bollinger_bands': BollingerBandsStrategy,
    'momentum': MomentumStrategy,
}


@click.group()
def cli():
    """Algorithmic Trading Bot - Backtest and analyze trading strategies"""
    pass


@cli.command()
@click.option('--symbol', default='INFY.NS', help='Stock symbol (e.g., INFY.NS, TCS.NS, RELIANCE.NS)')
@click.option('--start-date', default=None, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', default=None, help='End date (YYYY-MM-DD)')
@click.option('--interval', default='1d', type=click.Choice(list(TIMEFRAMES.keys())),
              help='Data interval/timeframe')
@click.option('--save', is_flag=True, help='Save data to CSV')
def fetch_data(symbol: str, start_date: str, end_date: str, interval: str, save: bool):
    """Fetch market data from Yahoo Finance

    Examples:
        # Fetch Indian stock data
        python main.py fetch-data --symbol INFY.NS
        python main.py fetch-data --symbol TCS.NS --interval 1h
        python main.py fetch-data --symbol RELIANCE.NS --start-date 2024-01-01 --save
    """
    try:
        # Default dates: last 1 year
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

        mapped_interval = TIMEFRAMES.get(interval, '1d')
        click.echo(f"Fetching {symbol} data from {start_date} to {end_date} (Interval: {interval})...")

        fetcher = DataFetcher()
        data = fetcher.fetch(symbol, start_date, end_date, interval=mapped_interval)

        click.echo(f"✓ Successfully fetched {len(data)} records")
        click.echo(f"\nFirst few rows:")
        click.echo(data.head().to_string())
        click.echo(f"\nLast few rows:")
        click.echo(data.tail().to_string())

        if save:
            filepath = fetcher.save_to_csv(data, symbol)
            click.echo(f"\n✓ Data saved to {filepath}")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option('--symbol', default='INFY.NS', help='Stock symbol (e.g., INFY.NS, TCS.NS)')
@click.option('--strategy', default='ma_crossover', type=click.Choice(list(STRATEGIES.keys())),
              help='Trading strategy')
@click.option('--start-date', default=None, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', default=None, help='End date (YYYY-MM-DD)')
@click.option('--interval', default='1d', type=click.Choice(list(TIMEFRAMES.keys())),
              help='Data interval/timeframe')
@click.option('--capital', default=DEFAULT_CAPITAL, type=float, help='Initial capital (INR)')
@click.option('--commission', default=DEFAULT_COMMISSION, type=float, help='Commission per trade')
@click.option('--plot', is_flag=True, help='Generate visualization plots')
@click.option('--fast-ma', default=10, type=int, help='Fast MA period (MA Crossover)')
@click.option('--slow-ma', default=30, type=int, help='Slow MA period (MA Crossover)')
@click.option('--rsi-period', default=14, type=int, help='RSI period (RSI Strategy)')
@click.option('--roc-period', default=10, type=int, help='ROC period (Momentum Strategy)')
def backtest(symbol: str, strategy: str, start_date: str, end_date: str, interval: str,
             capital: float, commission: float, plot: bool,
             fast_ma: int, slow_ma: int, rsi_period: int, roc_period: int):
    """Run backtest on a strategy

    Examples:
        # Backtest MA Crossover on Infosys
        python main.py backtest --symbol INFY.NS --strategy ma_crossover

        # Backtest Momentum strategy on TCS with 1h timeframe
        python main.py backtest --symbol TCS.NS --strategy momentum --interval 1h

        # Backtest RSI with custom parameters
        python main.py backtest --symbol RELIANCE.NS --strategy rsi --rsi-period 21 --plot
    """
    try:
        # Default dates: last 1 year
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

        mapped_interval = TIMEFRAMES.get(interval, '1d')

        click.echo(f"Starting backtest...")
        click.echo(f"  Symbol: {symbol}")
        click.echo(f"  Strategy: {strategy}")
        click.echo(f"  Period: {start_date} to {end_date}")
        click.echo(f"  Timeframe: {interval}")
        click.echo(f"  Capital: ₹{capital:,.2f}")
        click.echo(f"  Commission: {commission*100:.3f}%")

        # Fetch data
        click.echo(f"\n1. Fetching data...")
        fetcher = DataFetcher()
        data = fetcher.fetch(symbol, start_date, end_date, interval=mapped_interval)
        click.echo(f"   ✓ Fetched {len(data)} records")

        # Setup strategy parameters
        strategy_class = STRATEGIES[strategy]
        strategy_params = {}

        if strategy == 'ma_crossover':
            strategy_params = {'fast_ma': fast_ma, 'slow_ma': slow_ma}
        elif strategy == 'rsi':
            strategy_params = {'rsi_period': rsi_period}
        elif strategy == 'momentum':
            strategy_params = {'roc_period': roc_period}

        # Run backtest
        click.echo(f"\n2. Running backtest...")
        engine = BacktestEngine(initial_capital=capital, commission=commission)
        results = engine.run(strategy_class, data, strategy_params, symbol)

        # Print results
        click.echo(f"\n3. Results:")
        engine.print_results(results)

        # Generate plots
        if plot:
            click.echo(f"\n4. Generating visualizations...")
            try:
                visualizer = ResultsVisualizer()
                dates = data.index

                # Create equity curve: start at capital, grow by total return
                equity_values = pd.Series(
                    [capital * (1 + results['total_return']/100)] * len(dates),
                    index=dates
                )

                visualizer.plot_equity_curve(equity_values, dates, symbol)
                visualizer.plot_drawdown(equity_values, dates, symbol)
                click.echo(f"   ✓ Generated visualizations in results/ directory")
            except Exception as e:
                click.echo(f"   ! Could not generate visualizations: {e}")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
def list_strategies():
    """List available trading strategies"""
    click.echo("Available Strategies:")
    click.echo("=" * 50)
    for name, strategy_class in STRATEGIES.items():
        click.echo(f"\n{name}:")
        if strategy_class.__doc__:
            click.echo(f"  {strategy_class.__doc__.strip()}")
    click.echo("\n" + "=" * 50)


@cli.command()
@click.argument('symbol')
@click.argument('strategy', type=click.Choice(list(STRATEGIES.keys())))
@click.option('--start-date', default=None, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', default=None, help='End date (YYYY-MM-DD)')
def quick_test(symbol: str, strategy: str, start_date: str, end_date: str):
    """Quick backtest with default parameters"""
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

    click.invoke(backtest, {
        'symbol': symbol,
        'strategy': strategy,
        'start_date': start_date,
        'end_date': end_date,
        'capital': DEFAULT_CAPITAL,
        'commission': DEFAULT_COMMISSION,
        'plot': False,
        'fast_ma': 10,
        'slow_ma': 30,
        'rsi_period': 14,
    })


if __name__ == '__main__':
    cli()
