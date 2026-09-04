# ============================================================================
# ESTRATEGIA 3: RSI + MACD
# ============================================================================

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy

class RSI_MACD(BaseStrategy):
    """
    Estrategia combinada de RSI y MACD.
    
    LÓGICA:
    - COMPRA cuando RSI < 30 (sobreventa) Y MACD cruza por encima de signal line
    - VENTA cuando RSI > 70 (sobrecompra) Y MACD cruza por debajo de signal line
    
    PARÁMETROS:
    - rsi_period: Período RSI (ej: 14)
    - rsi_oversold: Nivel de sobreventa (ej: 30)
    - rsi_overbought: Nivel de sobrecompra (ej: 70)
    - macd_fast, macd_slow, macd_signal: Parámetros MACD
    - stop_loss_percent: Stop loss (ej: 0.025 = 2.5%)
    - take_profit_percent: Take profit (ej: 0.045 = 4.5%)
    """
    
    def __init__(self, params=None):
        default_params = {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'stop_loss_percent': 0.025,
            'take_profit_percent': 0.045
        }
        if params:
            default_params.update(params)
        
        super().__init__("RSI + MACD", default_params)
    
    def generate_signals(self, data):
        """
        Genera señales basadas en RSI + MACD
        
        Returns:
            Series con señales: 1 (COMPRA), -1 (VENTA), 0 (NADA)
        """
        data = data.copy()
        
        # Calcular RSI
        rsi = self._calculate_rsi(data['Adj Close'], self.params['rsi_period'])
        data['RSI'] = rsi
        
        # Calcular MACD
        macd_line, signal_line, macd_hist = self._calculate_macd(
            data['Adj Close'],
            fast=self.params['macd_fast'],
            slow=self.params['macd_slow'],
            signal=self.params['macd_signal']
        )
        data['MACD'] = macd_line
        data['MACD_Signal'] = signal_line
        data['MACD_Hist'] = macd_hist
        
        # Crear señales
        signals = pd.Series(0, index=data.index)
        
        # MACD cruces
        macd_cross_up = (data['MACD'] > data['MACD_Signal']) & \
                        (data['MACD'].shift(1) <= data['MACD_Signal'].shift(1))
        macd_cross_down = (data['MACD'] < data['MACD_Signal']) & \
                          (data['MACD'].shift(1) >= data['MACD_Signal'].shift(1))
        
        # COMPRA: RSI en sobreventa + MACD cruce alcista
        buy_signal = (data['RSI'] < self.params['rsi_oversold']) & macd_cross_up
        signals[buy_signal] = 1
        
        # VENTA: RSI en sobrecompra + MACD cruce bajista
        sell_signal = (data['RSI'] > self.params['rsi_overbought']) & macd_cross_down
        signals[sell_signal] = -1
        
        self.signals = signals
        return signals
    
    @staticmethod
    def _calculate_rsi(prices, period=14):
        """Calcula RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def _calculate_macd(prices, fast=12, slow=26, signal=9):
        """Calcula MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
