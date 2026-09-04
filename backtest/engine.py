# ============================================================================
# MOTOR DE BACKTESTING - Ejecuta la estrategia en datos históricos
# ============================================================================

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class BacktestEngine:
    """
    Motor de backtesting que ejecuta una estrategia en datos históricos
    y calcula todas las métricas de rendimiento.
    """
    
    def __init__(self, initial_capital=50, commission=0.0005, spread=0.0001, slippage=0.0002):
        """
        Inicializa el motor de backtesting
        
        Args:
            initial_capital: Capital inicial en USD
            commission: Comisión por operación (ej: 0.0005 = 0.05%)
            spread: Spread promedio (ej: 0.0001 = 0.01%)
            slippage: Deslizamiento (ej: 0.0002 = 0.02%)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.spread = spread
        self.slippage = slippage
        
        # Resultados
        self.trades = []
        self.equity_curve = []
        self.results = {}
    
    def run(self, data, strategy):
        """
        Ejecuta el backtesting
        
        Args:
            data: DataFrame con OHLCV
            strategy: Objeto de estrategia con método generate_signals()
        
        Returns:
            Dict con resultados y métricas
        """
        print(f"\nIniciando backtesting...")
        print(f"Capital inicial: ${self.initial_capital}")
        print(f"Período: {data.index[0].date()} a {data.index[-1].date()}")
        print(f"Comisión: {self.commission*100:.2f}%")
        print(f"Spread: {self.spread*100:.2f}%")
        print(f"Slippage: {self.slippage*100:.2f}%")
        
        # Generar señales
        signals = strategy.generate_signals(data)
        data['Signal'] = signals
        
        # Simular operaciones
        capital = self.initial_capital
        position = 0  # 0 = sin posición, > 0 = comprado, < 0 = vendido
        entry_price = 0
        entry_date = None
        
        for i in range(len(data)):
            date = data.index[i]
            close_price = data['Adj Close'].iloc[i]
            signal = data['Signal'].iloc[i]
            
            # SEÑAL DE COMPRA
            if signal == 1 and position == 0:
                entry_price = close_price * (1 + self.spread + self.slippage)
                position_size = capital / entry_price  # N° de acciones que podemos comprar
                cost = position_size * entry_price
                commission_cost = cost * self.commission
                
                capital -= cost + commission_cost
                position = position_size
                entry_date = date
                
                self.trades.append({
                    'entry_date': entry_date,
                    'exit_date': None,
                    'type': 'BUY',
                    'entry_price': entry_price,
                    'exit_price': None,
                    'quantity': position_size,
                    'profit': None,
                    'profit_pct': None,
                    'return': None
                })
            
            # SEÑAL DE VENTA
            elif signal == -1 and position > 0:
                exit_price = close_price * (1 - self.spread - self.slippage)
                revenue = position * exit_price
                commission_cost = revenue * self.commission
                
                capital += revenue - commission_cost
                profit = (exit_price - entry_price) * position
                profit_pct = ((exit_price - entry_price) / entry_price) * 100
                
                self.trades[-1]['exit_date'] = date
                self.trades[-1]['exit_price'] = exit_price
                self.trades[-1]['profit'] = profit
                self.trades[-1]['profit_pct'] = profit_pct
                self.trades[-1]['return'] = profit / (entry_price * position) * 100
                
                position = 0
            
            # Registrar equity curve
            if position > 0:
                position_value = position * close_price
                total_equity = capital + position_value
            else:
                total_equity = capital
            
            self.equity_curve.append({
                'date': date,
                'equity': total_equity,
                'capital': capital,
                'position': position
            })
        
        # Cerrar posición abierta al final
        if position > 0:
            exit_price = data['Adj Close'].iloc[-1]
            revenue = position * exit_price
            commission_cost = revenue * self.commission
            capital += revenue - commission_cost
            
            profit = (exit_price - entry_price) * position
            profit_pct = ((exit_price - entry_price) / entry_price) * 100
            
            self.trades[-1]['exit_date'] = data.index[-1]
            self.trades[-1]['exit_price'] = exit_price
            self.trades[-1]['profit'] = profit
            self.trades[-1]['profit_pct'] = profit_pct
        
        # Calcular métricas
        self.results = self._calculate_metrics(data)
        
        print(f"\n✅ Backtesting completado")
        self._print_results()
        
        return self.results
    
    def _calculate_metrics(self, data):
        """
        Calcula todas las métricas de rendimiento
        """
        equity_df = pd.DataFrame(self.equity_curve)
        
        # Rentabilidad
        final_equity = equity_df['equity'].iloc[-1]
        total_return = final_equity - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        # Rentabilidad anualizada
        days = len(data)
        years = days / 252.0
        annualized_return = ((final_equity / self.initial_capital) ** (1/years) - 1) * 100
        
        # Drawdown
        cummax = equity_df['equity'].cummax()
        drawdown = (equity_df['equity'] - cummax) / cummax
        max_drawdown = drawdown.min() * 100
        
        # Métricas de trades
        closed_trades = [t for t in self.trades if t['exit_price'] is not None]
        winning_trades = [t for t in closed_trades if t['profit'] > 0]
        losing_trades = [t for t in closed_trades if t['profit'] <= 0]
        
        num_trades = len(closed_trades)
        win_rate = (len(winning_trades) / num_trades * 100) if num_trades > 0 else 0
        
        avg_win = np.mean([t['profit'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['profit'] for t in losing_trades]) if losing_trades else 0
        
        profit_factor = sum([t['profit'] for t in winning_trades]) / abs(sum([t['profit'] for t in losing_trades])) if losing_trades else 0
        
        # Sharpe Ratio
        returns = equity_df['equity'].pct_change().dropna()
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        
        # Rachas
        winning_streak = 0
        losing_streak = 0
        max_winning_streak = 0
        max_losing_streak = 0
        
        for trade in closed_trades:
            if trade['profit'] > 0:
                winning_streak += 1
                losing_streak = 0
                max_winning_streak = max(max_winning_streak, winning_streak)
            else:
                losing_streak += 1
                winning_streak = 0
                max_losing_streak = max(max_losing_streak, losing_streak)
        
        return {
            'initial_capital': self.initial_capital,
            'final_capital': final_equity,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'annualized_return': annualized_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'num_trades': num_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_winning_streak': max_winning_streak,
            'max_losing_streak': max_losing_streak,
            'trades': closed_trades
        }
    
    def _print_results(self):
        """
        Imprime los resultados en la consola
        """
        r = self.results
        
        print("\n" + "="*70)
        print("RESULTADOS DEL BACKTESTING")
        print("="*70)
        
        print(f"\nCAPITAL:")
        print(f"  Inicial:        ${r['initial_capital']:.2f}")
        print(f"  Final:          ${r['final_capital']:.2f}")
        print(f"  Ganancia:       ${r['total_return']:.2f}")
        
        print(f"\nRENTABILIDAD:")
        print(f"  Total:          {r['total_return_pct']:.2f}%")
        print(f"  Anualizada:     {r['annualized_return']:.2f}%")
        print(f"  Sharpe Ratio:   {r['sharpe_ratio']:.2f}")
        print(f"  Máx Drawdown:   {r['max_drawdown']:.2f}%")
        
        print(f"\nOPERACIONES:")
        print(f"  Total Trades:   {r['num_trades']}")
        print(f"  Win Rate:       {r['win_rate']:.2f}%")
        print(f"  Ganancia Prom:  ${r['avg_win']:.2f}")
        print(f"  Pérdida Prom:   ${r['avg_loss']:.2f}")
        print(f"  Profit Factor:  {r['profit_factor']:.2f}")
        
        print(f"\nRACHAS:")
        print(f"  Máx Rachas +:   {r['max_winning_streak']}")
        print(f"  Máx Rachas -:   {r['max_losing_streak']}")
        
        print("\n" + "="*70)
