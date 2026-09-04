# ============================================================================
# CLASE BASE PARA ESTRATEGIAS
# ============================================================================

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

class BaseStrategy(ABC):
    """
    Clase base para todas las estrategias de trading.
    Define la interfaz que todas las estrategias deben implementar.
    """
    
    def __init__(self, name, params=None):
        """
        Inicializa la estrategia
        
        Args:
            name: Nombre de la estrategia
            params: Dict con parámetros de la estrategia
        """
        self.name = name
        self.params = params or {}
        self.signals = None  # Será generado por next_signal()
    
    @abstractmethod
    def generate_signals(self, data):
        """
        Genera señales de compra/venta basadas en los datos históricos.
        
        Args:
            data: DataFrame con OHLCV e indicadores
        
        Returns:
            Series con valores: 1 (COMPRA), -1 (VENTA), 0 (NADA)
        """
        pass
    
    def calculate_position_size(self, account_value, risk_amount, stop_loss_percent):
        """
        Calcula el tamaño de la posición basado en el riesgo
        
        Args:
            account_value: Valor actual de la cuenta
            risk_amount: Cantidad máxima a arriesgar ($)
            stop_loss_percent: Stop loss en porcentaje
        
        Returns:
            Número de acciones a comprar
        """
        if stop_loss_percent <= 0:
            return 0
        
        position_size = risk_amount / stop_loss_percent
        return position_size
    
    def get_description(self):
        """Retorna descripción de la estrategia"""
        return f"{self.name} - Parámetros: {self.params}"
