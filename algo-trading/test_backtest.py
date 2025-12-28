#!/usr/bin/env python3
"""Quick test to validate the complete system"""

import sys
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run a quick backtest to test the system"""
    try:
        logger.info("=" * 60)
        logger.info("ALGO TRADING BOT - SYSTEM TEST")
        logger.info("=" * 60)

        # Test 1: Import modules
        logger.info("\n[TEST 1] Importing modules...")
        try:
            from src.data.data_fetcher import DataFetcher
            from src.backtesting.backtest_engine import BacktestEngine
            from src.strategies import MAcrossoverStrategy, RSIStrategy
            logger.info("✓ All modules imported successfully")
        except ImportError as e:
            logger.error(f"✗ Import error: {e}")
            return False

        # Test 2: Fetch data
        logger.info("\n[TEST 2] Fetching market data...")
        try:
            fetcher = DataFetcher()
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

            logger.info(f"Fetching AAPL from {start_date} to {end_date}...")
            data = fetcher.fetch('AAPL', start_date, end_date)
            logger.info(f"✓ Fetched {len(data)} records")
            logger.info(f"  Price range: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")
        except Exception as e:
            logger.error(f"✗ Data fetching error: {e}")
            return False

        # Test 3: Run MA Crossover backtest
        logger.info("\n[TEST 3] Running MA Crossover backtest...")
        try:
            engine = BacktestEngine(initial_capital=100000, commission=0.001)
            results = engine.run(
                MAcrossoverStrategy,
                data,
                {'fast_ma': 10, 'slow_ma': 30},
                'AAPL'
            )
            logger.info("✓ MA Crossover backtest completed")
            logger.info(f"  Initial Capital: ${results['initial_capital']:,.2f}")
            logger.info(f"  Final Value: ${results['final_value']:,.2f}")
            logger.info(f"  Total Return: {results['total_return']:.2f}%")
            logger.info(f"  Sharpe Ratio: {results['sharpe_ratio']:.2f}")
            logger.info(f"  Max Drawdown: {results['max_drawdown']:.2f}%")
            logger.info(f"  Win Rate: {results['win_rate']:.2f}%")
        except Exception as e:
            logger.error(f"✗ MA Crossover backtest error: {e}")
            import traceback
            traceback.print_exc()
            return False

        # Test 4: Run RSI backtest
        logger.info("\n[TEST 4] Running RSI strategy backtest...")
        try:
            engine = BacktestEngine(initial_capital=100000, commission=0.001)
            results = engine.run(
                RSIStrategy,
                data,
                {'rsi_period': 14},
                'AAPL'
            )
            logger.info("✓ RSI backtest completed")
            logger.info(f"  Final Value: ${results['final_value']:,.2f}")
            logger.info(f"  Total Return: {results['total_return']:.2f}%")
            logger.info(f"  Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        except Exception as e:
            logger.error(f"✗ RSI backtest error: {e}")
            import traceback
            traceback.print_exc()
            return False

        # Test 5: Print detailed results
        logger.info("\n[TEST 5] Detailed Results")
        engine.print_results(results)

        logger.info("\n" + "=" * 60)
        logger.info("✓ ALL TESTS PASSED")
        logger.info("=" * 60)
        logger.info("\nYou can now use the trading bot!")
        logger.info("Try: python main.py --help")
        logger.info("Or: python main.py backtest --symbol AAPL --strategy ma_crossover\n")

        return True

    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
