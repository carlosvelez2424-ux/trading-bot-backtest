# ============================================================================
# MÓDULO DE DATOS - Descarga y procesamiento de datos históricos
# ============================================================================

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class DataFetcher:
    """Descarga y procesa datos históricos de Yahoo Finance"""
    
    def __init__(self, cache_dir="./data/cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def fetch_data(self, symbol, start_date, end_date, interval="1d"):
        """
        Descarga datos históricos de Yahoo Finance
        
        Args:
            symbol: Símbolo del activo (ej: 'SPY')
            start_date: Fecha inicio (string: 'YYYY-MM-DD')
            end_date: Fecha fin (string: 'YYYY-MM-DD')
            interval: Intervalo ('1d' para diario)
        
        Returns:
            DataFrame con OHLCV (Open, High, Low, Close, Volume)
        """
        try:
            print(f"Descargando datos de {symbol} desde {start_date} hasta {end_date}...")
            
            # Descargar datos
            data = yf.download(
                symbol,
                start=start_date,
                end=end_date,
                interval=interval,
                progress=False
            )
            
            if data.empty:
                raise ValueError(f"No se encontraron datos para {symbol}")
            
            # Limpiar datos
            data = data.dropna()
            
            # Añadir columnas útiles
            data['Returns'] = data['Adj Close'].pct_change()
            data['Log_Returns'] = np.log(data['Adj Close'] / data['Adj Close'].shift(1))
            
            print(f"✅ Datos descargados: {len(data)} días")
            print(f"Rango: {data.index[0].date()} a {data.index[-1].date()}")
            
            return data
        
        except Exception as e:
            print(f"❌ Error al descargar datos: {str(e)}")
            raise
    
    def add_indicators(self, data, indicators_config):
        """
        Añade indicadores técnicos a los datos
        
        Args:
            data: DataFrame OHLCV
            indicators_config: Dict con indicadores a calcular
        
        Returns:
            DataFrame con indicadores añadidos
        """
        data = data.copy()
        
        # Media Móvil Simple (SMA)
        if 'sma' in indicators_config:
            for period in indicators_config['sma']:
                data[f'SMA_{period}'] = data['Adj Close'].rolling(window=period).mean()
        
        # Media Móvil Exponencial (EMA)
        if 'ema' in indicators_config:
            for period in indicators_config['ema']:
                data[f'EMA_{period}'] = data['Adj Close'].ewm(span=period).mean()
        
        # RSI (Relative Strength Index)
        if 'rsi' in indicators_config:
            for period in indicators_config['rsi']:
                data[f'RSI_{period}'] = self._calculate_rsi(data['Adj Close'], period)
        
        # MACD
        if 'macd' in indicators_config:
            macd_config = indicators_config['macd']
            data['MACD'], data['MACD_Signal'], data['MACD_Hist'] = self._calculate_macd(
                data['Adj Close'],
                fast=macd_config.get('fast', 12),
                slow=macd_config.get('slow', 26),
                signal=macd_config.get('signal', 9)
            )
        
        # Bandas de Bollinger
        if 'bollinger' in indicators_config:
            for period in indicators_config['bollinger']:
                bb_upper, bb_middle, bb_lower = self._calculate_bollinger(
                    data['Adj Close'], period
                )
                data[f'BB_Upper_{period}'] = bb_upper
                data[f'BB_Middle_{period}'] = bb_middle
                data[f'BB_Lower_{period}'] = bb_lower
        
        # ATR (Average True Range)
        if 'atr' in indicators_config:
            for period in indicators_config['atr']:
                data[f'ATR_{period}'] = self._calculate_atr(data, period)
        
        return data
    
    @staticmethod
    def _calculate_rsi(prices, period=14):
        """Calcula RSI (Relative Strength Index)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def _calculate_macd(prices, fast=12, slow=26, signal=9):
        """Calcula MACD (Moving Average Convergence Divergence)"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def _calculate_bollinger(prices, period=20, std_dev=2):
        """Calcula Bandas de Bollinger"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        
        return upper_band, sma, lower_band
    
    @staticmethod
    def _calculate_atr(data, period=14):
        """Calcula ATR (Average True Range)"""
        high_low = data['High'] - data['Low']
        high_close = abs(data['High'] - data['Adj Close'].shift())
        low_close = abs(data['Low'] - data['Adj Close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    def split_data(self, data, train_ratio=0.70, val_ratio=0.15):
        """
        Divide datos en train, validation, test
        
        Args:
            data: DataFrame completo
            train_ratio: Proporción entrenamiento (ej: 0.70 = 70%)
            val_ratio: Proporción validación (ej: 0.15 = 15%)
        
        Returns:
            Tupla (train_data, val_data, test_data)
        """
        n = len(data)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))
        
        train = data[:train_end]
        val = data[train_end:val_end]
        test = data[val_end:]
        
        print(f"\nDatos divididos:")
        print(f"  Entrenamiento: {len(train)} días ({train_ratio*100:.0f}%)")
        print(f"  Validación: {len(val)} días ({val_ratio*100:.0f}%)")
        print(f"  Prueba: {len(test)} días ({(1-train_ratio-val_ratio)*100:.0f}%)")
        
        return train, val, test
