# ============================================================================
# MÓDULO DE MÉTRICAS - Cálculo de métricas de rendimiento
# ============================================================================

import pandas as pd
import numpy as np

class MetricsCalculator:
    """
    Calcula métricas adicionales de rendimiento
    """
    
    @staticmethod
    def calculate_all_metrics(equity_curve, trades, initial_capital, benchmark_returns=None):
        """
        Calcula todas las métricas disponibles
        
        Returns:
            Dict con todas las métricas calculadas
        """
        equity_df = pd.DataFrame(equity_curve)
        returns = equity_df['equity'].pct_change().dropna()
        
        metrics = {}
        
        # Rentabilidad
        final_equity = equity_df['equity'].iloc[-1]
        metrics['total_return'] = final_equity - initial_capital
        metrics['total_return_pct'] = (metrics['total_return'] / initial_capital) * 100
        metrics['annualized_return'] = MetricsCalculator._calculate_annualized_return(
            initial_capital, final_equity, len(equity_df)
        )
        
        # Riesgo
        metrics['volatility'] = returns.std() * np.sqrt(252)
        metrics['max_drawdown'] = MetricsCalculator._calculate_max_drawdown(equity_df)
        metrics['calmar_ratio'] = MetricsCalculator._calculate_calmar_ratio(
            metrics['annualized_return'], abs(metrics['max_drawdown'])
        )
        
        # Sharpe
        risk_free_rate = 0.02  # Suponer 2% de tasa libre de riesgo
        metrics['sharpe_ratio'] = MetricsCalculator._calculate_sharpe_ratio(
            returns, risk_free_rate
        )
        
        # Sortino
        metrics['sortino_ratio'] = MetricsCalculator._calculate_sortino_ratio(
            returns, risk_free_rate
        )
        
        # Estadísticas de trades
        closed_trades = [t for t in trades if t['exit_price'] is not None]
        if closed_trades:
            winning_trades = [t for t in closed_trades if t['profit'] > 0]
            losing_trades = [t for t in closed_trades if t['profit'] <= 0]
            
            metrics['num_trades'] = len(closed_trades)
            metrics['win_rate'] = (len(winning_trades) / len(closed_trades)) * 100
            metrics['avg_win'] = np.mean([t['profit'] for t in winning_trades]) if winning_trades else 0
            metrics['avg_loss'] = np.mean([t['profit'] for t in losing_trades]) if losing_trades else 0
            metrics['profit_factor'] = MetricsCalculator._calculate_profit_factor(closed_trades)
        
        return metrics
    
    @staticmethod
    def _calculate_annualized_return(initial, final, days):
        """Calcula rentabilidad anualizada"""
        years = days / 252.0
        if years > 0 and initial > 0:
            return ((final / initial) ** (1 / years) - 1) * 100
        return 0
    
    @staticmethod
    def _calculate_max_drawdown(equity_df):
        """Calcula máximo drawdown"""
        cummax = equity_df['equity'].cummax()
        drawdown = (equity_df['equity'] - cummax) / cummax
        return drawdown.min() * 100
    
    @staticmethod
    def _calculate_calmar_ratio(annualized_return, max_drawdown):
        """Calcula Calmar Ratio"""
        if max_drawdown != 0:
            return annualized_return / abs(max_drawdown)
        return 0
    
    @staticmethod
    def _calculate_sharpe_ratio(returns, risk_free_rate=0.02):
        """Calcula Sharpe Ratio"""
        excess_returns = returns.mean() * 252 - risk_free_rate
        volatility = returns.std() * np.sqrt(252)
        if volatility > 0:
            return excess_returns / volatility
        return 0
    
    @staticmethod
    def _calculate_sortino_ratio(returns, risk_free_rate=0.02):
        """Calcula Sortino Ratio (solo riesgo a la baja)"""
        excess_returns = returns.mean() * 252 - risk_free_rate
        downside_returns = returns[returns < 0]
        downside_volatility = downside_returns.std() * np.sqrt(252)
        if downside_volatility > 0:
            return excess_returns / downside_volatility
        return 0
    
    @staticmethod
    def _calculate_profit_factor(trades):
        """Calcula Profit Factor"""
        gross_profit = sum([t['profit'] for t in trades if t['profit'] > 0])
        gross_loss = abs(sum([t['profit'] for t in trades if t['profit'] <= 0]))
        if gross_loss > 0:
            return gross_profit / gross_loss
        return 0 if gross_profit == 0 else float('inf')
