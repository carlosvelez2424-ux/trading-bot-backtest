"""
Descarga datos de Bitcoin, Crypto y Forex
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

class CryptoForexDataFetcher:
    def __init__(self, cache_dir: str = "./data/cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def fetch_data(self, symbol: str, start_date: str, end_date: str, 
                   interval: str = "1d") -> pd.DataFrame:
        """
        Descarga datos de yfinance
        
        Args:
            symbol: "BTC-USD", "ETH-USD", "EURUSD=X", etc.
            start_date: "2022-01-01"
            end_date: "2024-12-31"
            interval: "1d", "1h", "15m", etc.
        
        Returns:
            DataFrame con OHLCV
        """
        try:
            print(f"Descargando {symbol} ({start_date} a {end_date})...")
            
            data = yf.download(symbol, start=start_date, end=end_date, 
                             interval=interval, progress=False)
            
            if data.empty:
                print(f"No hay datos para {symbol}")
                return pd.DataFrame()
            
            # Limpiar nombres de columnas
            data.columns = [col.lower() for col in data.columns]
            
            # Asegurar que tenemos las columnas necesarias
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            data = data[required_cols]
            
            print(f"✓ {len(data)} velas descargadas")
            return data
        
        except Exception as e:
            print(f"Error descargando {symbol}: {e}")
            return pd.DataFrame()
    
    def fetch_realtime(self, symbol: str) -> dict:
        """
        Obtiene datos en tiempo real
        
        Args:
            symbol: "BTC-USD", "EURUSD=X", etc.
        
        Returns:
            dict con precio actual y datos
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            
            if data.empty:
                return {"error": f"No data for {symbol}"}
            
            last_row = data.iloc[-1]
            
            return {
                "symbol": symbol,
                "price": float(last_row['Close']),
                "open": float(last_row['Open']),
                "high": float(last_row['High']),
                "low": float(last_row['Low']),
                "volume": float(last_row['Volume']),
                "timestamp": data.index[-1]
            }
        
        except Exception as e:
            print(f"Error en tiempo real para {symbol}: {e}")
            return {"error": str(e)}
    
    def get_multiple_prices(self, symbols: list) -> dict:
        """
        Obtiene precios de múltiples símbolos
        
        Args:
            symbols: ["BTC-USD", "ETH-USD", "EURUSD=X"]
        
        Returns:
            dict con precios de cada símbolo
        """
        prices = {}
        for symbol in symbols:
            data = self.fetch_realtime(symbol)
            prices[symbol] = data
        return prices


# Ejemplo de uso
if __name__ == "__main__":
    fetcher = CryptoForexDataFetcher()
    
    # Descargar Bitcoin
    btc_data = fetcher.fetch_data("BTC-USD", "2024-01-01", "2024-12-31")
    print(f"\nBTC data shape: {btc_data.shape}")
    print(btc_data.tail())
    
    # Descargar EUR/USD
    eurusd_data = fetcher.fetch_data("EURUSD=X", "2024-01-01", "2024-12-31")
    print(f"\nEUR/USD data shape: {eurusd_data.shape}")
    
    # Precios en tiempo real
    print("\n--- Precios en Tiempo Real ---")
    prices = fetcher.get_multiple_prices(["BTC-USD", "ETH-USD", "EURUSD=X"])
    for symbol, data in prices.items():
        if "error" not in data:
            print(f"{symbol}: ${data['price']:.2f}")
