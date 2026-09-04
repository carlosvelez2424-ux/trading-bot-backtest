# Inicializador del paquete backtest
from backtest.engine import BacktestEngine
from backtest.validator import OutOfSampleValidator
from backtest.metrics import MetricsCalculator

__all__ = ['BacktestEngine', 'OutOfSampleValidator', 'MetricsCalculator']
