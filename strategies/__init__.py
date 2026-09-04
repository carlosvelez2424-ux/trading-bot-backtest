# Inicializador del paquete de estrategias
from strategies.base_strategy import BaseStrategy
from strategies.moving_average_cross import MovingAverageCross
from strategies.mean_reversion import MeanReversion
from strategies.rsi_macd import RSI_MACD

__all__ = ['BaseStrategy', 'MovingAverageCross', 'MeanReversion', 'RSI_MACD']
