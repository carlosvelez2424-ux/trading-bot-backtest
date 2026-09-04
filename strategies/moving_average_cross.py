# ============================================================================
# ESTRATEGIA 1: CRUCE DE MEDIAS MÓVILES
# ============================================================================

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy

class MovingAverageCross(BaseStrategy):
    """
    Estrategia de cruce de medias móviles simples.
    
    LÓGICA:
    - COMPRA cuando la media rápida cruza por encima de la media lenta
    - VENTA cuando la media rápida cruza por debajo de la media lenta
    
    PARÁMETROS:
    - fast_ma: Período de media móvil rápida (ej: 20)
    - slow_ma: Período de media móvil lenta (ej: 50)
    - stop_loss_percent: Stop loss relativo (ej: 0.02 = 2%)
    - take_profit_percent: Take profit relativo (ej: 0.05 = 5%)
    """
    
    def __init__(self, params=None):
        default_params = {
            'fast_ma': 20,
            'slow_ma': 50,
            'stop_loss_percent': 0.02,
            'take_profit_percent': 0.05
        }
        if params:
            default_params.update(params)
        
        super().__init__("Moving Average Crossover", default_params)
    
    def generate_signals(self, data):
        """
        Genera señales basadas en cruce de medias móviles
        
        Returns:
            Series con señales: 1 (COMPRA), -1 (VENTA), 0 (NADA)
        """
        data = data.copy()
        
        fast_ma = self.params['fast_ma']
        slow_ma = self.params['slow_ma']
        
        # Calcular medias móviles
        data['SMA_Fast'] = data['Adj Close'].rolling(window=fast_ma).mean()
        data['SMA_Slow'] = data['Adj Close'].rolling(window=slow_ma).mean()
        
        # Crear señales
        signals = pd.Series(0, index=data.index)
        
        # Identificar cruces
        fast_above_slow = data['SMA_Fast'] > data['SMA_Slow']
        cross_up = fast_above_slow & ~fast_above_slow.shift(1).fillna(False)
        cross_down = ~fast_above_slow & fast_above_slow.shift(1).fillna(False)
        
        signals[cross_up] = 1    # Señal de COMPRA
        signals[cross_down] = -1  # Señal de VENTA
        
        self.signals = signals
        return signals
