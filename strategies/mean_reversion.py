# ============================================================================
# ESTRATEGIA 2: MEAN REVERSION (REVERSIÓN A LA MEDIA)
# ============================================================================

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy

class MeanReversion(BaseStrategy):
    """
    Estrategia de reversión a la media.
    
    LÓGICA:
    - COMPRA cuando el precio cae más de N desviaciones estándar por debajo de la media
    - VENTA cuando el precio sube más de N desviaciones estándar por encima de la media
    
    PARÁMETROS:
    - lookback: Período para calcular media y desv. est. (ej: 20)
    - std_dev: Número de desviaciones estándar (ej: 2.0)
    - stop_loss_percent: Stop loss relativo (ej: 0.03 = 3%)
    - take_profit_percent: Take profit relativo (ej: 0.04 = 4%)
    """
    
    def __init__(self, params=None):
        default_params = {
            'lookback': 20,
            'std_dev': 2.0,
            'stop_loss_percent': 0.03,
            'take_profit_percent': 0.04
        }
        if params:
            default_params.update(params)
        
        super().__init__("Mean Reversion", default_params)
    
    def generate_signals(self, data):
        """
        Genera señales basadas en reversión a la media
        
        Returns:
            Series con señales: 1 (COMPRA), -1 (VENTA), 0 (NADA)
        """
        data = data.copy()
        
        lookback = self.params['lookback']
        std_dev = self.params['std_dev']
        
        # Calcular media y desviación estándar
        data['Mean'] = data['Adj Close'].rolling(window=lookback).mean()
        data['Std'] = data['Adj Close'].rolling(window=lookback).std()
        
        data['Upper_Band'] = data['Mean'] + (std_dev * data['Std'])
        data['Lower_Band'] = data['Mean'] - (std_dev * data['Std'])
        
        # Crear señales
        signals = pd.Series(0, index=data.index)
        
        # COMPRA cuando precio está por debajo de la banda inferior
        signals[data['Adj Close'] < data['Lower_Band']] = 1
        
        # VENTA cuando precio está por encima de la banda superior
        signals[data['Adj Close'] > data['Upper_Band']] = -1
        
        self.signals = signals
        return signals
