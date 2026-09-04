# ============================================================================
# VALIDADOR OUT-OF-SAMPLE
# ============================================================================

import pandas as pd
import numpy as np
from backtest.engine import BacktestEngine

class OutOfSampleValidator:
    """
    Valida que la estrategia sea robusta y no tenga overfitting.
    Divide datos en train, validation, test y compara resultados.
    """
    
    def __init__(self, initial_capital=50, commission=0.0005, spread=0.0001, slippage=0.0002):
        self.initial_capital = initial_capital
        self.commission = commission
        self.spread = spread
        self.slippage = slippage
        self.results = {}
    
    def validate(self, data, strategy, train_ratio=0.70, val_ratio=0.15):
        """
        Valida la estrategia en tres períodos separados
        
        Args:
            data: DataFrame completo con OHLCV
            strategy: Objeto de estrategia
            train_ratio: Proporción de entrenamiento
            val_ratio: Proporción de validación
        
        Returns:
            Dict con resultados de train, val, test
        """
        print(f"\n{'='*70}")
        print("VALIDACIÓN OUT-OF-SAMPLE")
        print(f"{'='*70}")
        
        # Dividir datos
        n = len(data)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))
        
        train_data = data[:train_end]
        val_data = data[train_end:val_end]
        test_data = data[val_end:]
        
        print(f"\nDatos divididos:")
        print(f"  Entrenamiento: {len(train_data)} días ({train_ratio*100:.0f}%)")
        print(f"  Validación:   {len(val_data)} días ({val_ratio*100:.0f}%)")
        print(f"  Prueba:        {len(test_data)} días ({(1-train_ratio-val_ratio)*100:.0f}%)")
        
        # Ejecutar backtests
        print(f"\n{'─'*70}")
        print("FASE 1: ENTRENAMIENTO (In-Sample)")
        print(f"{'─'*70}")
        engine_train = BacktestEngine(self.initial_capital, self.commission, self.spread, self.slippage)
        train_results = engine_train.run(train_data, strategy)
        
        print(f"\n{'─'*70}")
        print("FASE 2: VALIDACIÓN (Out-of-Sample)")
        print(f"{'─'*70}")
        engine_val = BacktestEngine(self.initial_capital, self.commission, self.spread, self.slippage)
        val_results = engine_val.run(val_data, strategy)
        
        print(f"\n{'─'*70}")
        print("FASE 3: PRUEBA (Out-of-Sample Futuro)")
        print(f"{'─'*70}")
        engine_test = BacktestEngine(self.initial_capital, self.commission, self.spread, self.slippage)
        test_results = engine_test.run(test_data, strategy)
        
        # Comparar resultados
        self.results = {
            'train': train_results,
            'validation': val_results,
            'test': test_results
        }
        
        self._print_comparison()
        
        return self.results
    
    def _print_comparison(self):
        """
        Imprime comparación entre períodos
        """
        train = self.results['train']
        val = self.results['validation']
        test = self.results['test']
        
        print(f"\n{'='*70}")
        print("COMPARACIÓN DE RESULTADOS")
        print(f"{'='*70}")
        
        print(f"\nRentabilidad Total (%):")
        print(f"  Entrenamiento: {train['total_return_pct']:>10.2f}%")
        print(f"  Validación:   {val['total_return_pct']:>10.2f}%")
        print(f"  Prueba:        {test['total_return_pct']:>10.2f}%")
        
        print(f"\nSharpe Ratio:")
        print(f"  Entrenamiento: {train['sharpe_ratio']:>10.2f}")
        print(f"  Validación:   {val['sharpe_ratio']:>10.2f}")
        print(f"  Prueba:        {test['sharpe_ratio']:>10.2f}")
        
        print(f"\nMáximo Drawdown (%):")
        print(f"  Entrenamiento: {train['max_drawdown']:>10.2f}%")
        print(f"  Validación:   {val['max_drawdown']:>10.2f}%")
        print(f"  Prueba:        {test['max_drawdown']:>10.2f}%")
        
        print(f"\nWin Rate (%):")
        print(f"  Entrenamiento: {train['win_rate']:>10.2f}%")
        print(f"  Validación:   {val['win_rate']:>10.2f}%")
        print(f"  Prueba:        {test['win_rate']:>10.2f}%")
        
        # Análisis de robustez
        print(f"\n{'─'*70}")
        print("ANÁLISIS DE ROBUSTEZ")
        print(f"{'─'*70}")
        
        # Degradación de Sharpe
        sharpe_degradation = ((val['sharpe_ratio'] - train['sharpe_ratio']) / train['sharpe_ratio'] * 100) if train['sharpe_ratio'] != 0 else 0
        print(f"\nDegradación Sharpe (Entrenamiento → Validación): {sharpe_degradation:.2f}%")
        
        if sharpe_degradation < -30:
            print("  ⚠️  ADVERTENCIA: Posible overfitting detectado")
        elif sharpe_degradation < -10:
            print("  ⚠️  Cierta degradación normal - Continuar validando")
        else:
            print("  ✅ Robusta - Comportamiento consistente")
        
        # Comparación train vs test
        sharpe_test_degradation = ((test['sharpe_ratio'] - train['sharpe_ratio']) / train['sharpe_ratio'] * 100) if train['sharpe_ratio'] != 0 else 0
        print(f"\nDegradación Sharpe (Entrenamiento → Prueba): {sharpe_test_degradation:.2f}%")
        
        if abs(sharpe_test_degradation) < 40:
            print("  ✅ Estrategia parece robusta")
        else:
            print("  ❌ Estrategia NO es suficientemente robusta")
        
        print(f"\n{'='*70}")
