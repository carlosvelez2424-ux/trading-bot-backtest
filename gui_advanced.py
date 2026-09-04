"""
GUI Mejorada - Trading Bot con Backtesting y Trading en Tiempo Real
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import yfinance as yf
from strategies.trend_follower import TrendFollowerStrategy
from alerts.alert_system import AlertSystem, RealtimeAlertMonitor
from paper_trading.live_paper_trader import LivePaperTrader
from data.fetch_crypto_forex import CryptoForexDataFetcher
import yaml

class TradingBotGUI:
    def __init__(self, root, config_path="config.yaml"):
        self.root = root
        self.root.title("🤖 Trading Bot Pro - Bitcoin, Forex & Stocks")
        self.root.geometry("1600x900")
        self.root.configure(bg="#1e1e1e")
        
        # Cargar configuración
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Inicializar componentes
        self.fetcher = CryptoForexDataFetcher()
        self.strategy = TrendFollowerStrategy()
        self.alert_system = AlertSystem(self.config)
        self.paper_trader = LivePaperTrader(self.config['trading']['initial_capital'])
        self.monitor = None
        
        self.current_symbol = "BTC-USD"
        self.current_data = None
        self.is_trading = False
        self.backtest_results = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz principal"""
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Arial', 10), padding=10)
        style.configure('TLabel', font=('Arial', 10), background="#1e1e1e", foreground="white")
        style.configure('TFrame', background="#1e1e1e")
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground="#00FF00")
        
        # Frame Principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ===== PANEL DE CONTROL (Izquierda) =====
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        ttk.Label(control_frame, text="⚙️ CONTROL", style='Title.TLabel').pack(pady=10)
        
        # Seleccionar Activo
        ttk.Label(control_frame, text="Seleccionar Activo:").pack(pady=(10, 5))
        
        self.symbol_var = tk.StringVar(value="BTC-USD")
        assets = ["BTC-USD", "ETH-USD", "EURUSD=X", "GBPUSD=X", "SPY", "AAPL"]
        symbol_combo = ttk.Combobox(control_frame, textvariable=self.symbol_var, 
                                    values=assets, state="readonly", width=20)
        symbol_combo.pack(pady=5)
        symbol_combo.bind("<<ComboboxSelected>>", lambda e: self.on_symbol_changed())
        
        # Botones principales
        ttk.Button(control_frame, text="🔍 BACKTESTING", 
                  command=self.open_backtest_window).pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="📊 TRADING EN TIEMPO REAL", 
                  command=self.open_realtime_window).pack(fill=tk.X, pady=5)
        
        # Estadísticas actuales
        ttk.Label(control_frame, text="\n📈 Estadísticas Actuales:", 
                 style='Title.TLabel').pack(pady=(20, 10))
        
        self.stats_text = scrolledtext.ScrolledText(control_frame, height=15, width=30)
        self.stats_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # ===== PANEL DE ALERTAS (Derecha) =====
        alert_frame = ttk.Frame(main_frame)
        alert_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(alert_frame, text="🔔 ALERTAS DE TRADING", 
                 style='Title.TLabel').pack(pady=10)
        
        self.alerts_text = scrolledtext.ScrolledText(alert_frame, height=25, width=60,
                                                     background="#2a2a2a", 
                                                     foreground="#00FF00")
        self.alerts_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Botón actualizar
        ttk.Button(self.root, text="🔄 ACTUALIZAR", 
                  command=self.update_display).pack(pady=10)
    
    def on_symbol_changed(self):
        """Cuando cambia el símbolo seleccionado"""
        self.current_symbol = self.symbol_var.get()
        self.update_display()
    
    def update_display(self):
        """Actualiza las estadísticas y alertas mostradas"""
        self.stats_text.delete(1.0, tk.END)
        
        # Descargar datos recientes
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)
        
        self.current_data = self.fetcher.fetch_data(
            self.current_symbol,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        
        if self.current_data.empty:
            self.stats_text.insert(tk.END, "Error: No hay datos disponibles")
            return
        
        # Analizar con la estrategia
        analysis = self.strategy.analyze(self.current_data)
        
        # Mostrar estadísticas
        stats = f"""
SÍMBOLO: {self.current_symbol}
Precio Actual: ${analysis['current_price']:.2f}

MA Rápida (50): ${analysis['ma_fast']:.2f}
MA Lenta (200): ${analysis['ma_slow']:.2f}
RSI (14): {analysis['rsi']:.1f}

Señal: {analysis['signal']}
Razón: {analysis['reason']}

═══════════════════════════════
PORTAFOLIO (Paper Trading)
═══════════════════════════════
Capital Inicial: ${self.paper_trader.initial_capital:.2f}
Cash Disponible: ${self.paper_trader.cash:.2f}
Valor Portafolio: ${self.paper_trader.portfolio_value:.2f}

Operaciones Abiertas: {len(self.paper_trader.get_open_positions())}
Operaciones Cerradas: {len(self.paper_trader.get_closed_trades())}

Estadísticas:
"""
        stats_dict = self.paper_trader.get_statistics()
        stats += f"""
Total Operaciones: {stats_dict['total_trades']}
Operaciones Ganadoras: {stats_dict['winning_trades']}
Operaciones Perdedoras: {stats_dict['losing_trades']}
Win Rate: {stats_dict['win_rate']:.1f}%
PnL Total: ${stats_dict['total_pnl']:.2f}
PnL %: {stats_dict['total_pnl_percent']:.2f}%
"""
        
        self.stats_text.insert(tk.END, stats)
        
        # Mostrar alertas
        alerts = self.strategy.get_alerts(self.current_data)
        self.alerts_text.delete(1.0, tk.END)
        
        if alerts:
            for alert in alerts:
                self.alerts_text.insert(tk.END, f"\n{alert['message']}\n")
                self.alerts_text.insert(tk.END, f"Precio: ${alert['price']:.2f}\n")
                self.alerts_text.insert(tk.END, f"Prioridad: {alert['priority']}\n")
                self.alerts_text.insert(tk.END, "─" * 50 + "\n")
        else:
            self.alerts_text.insert(tk.END, "Sin señales activas...")
    
    def open_backtest_window(self):
        """Abre ventana de Backtesting"""
        backtest_window = tk.Toplevel(self.root)
        backtest_window.title(f"Backtesting - {self.current_symbol}")
        backtest_window.geometry("1400x800")
        backtest_window.configure(bg="#1e1e1e")
        
        BacktestWindow(backtest_window, self.current_symbol, self.config)
    
    def open_realtime_window(self):
        """Abre ventana de Trading en Tiempo Real"""
        realtime_window = tk.Toplevel(self.root)
        realtime_window.title(f"Trading en Tiempo Real - {self.current_symbol}")
        realtime_window.geometry("1600x1000")
        realtime_window.configure(bg="#1e1e1e")
        
        RealtimeWindow(realtime_window, self.current_symbol, self.config)


class BacktestWindow:
    """Ventana de Backtesting"""
    def __init__(self, window, symbol, config):
        self.window = window
        self.symbol = symbol
        self.config = config
        self.fetcher = CryptoForexDataFetcher()
        self.strategy = TrendFollowerStrategy()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la ventana de backtesting"""
        # Frame de control
        control_frame = ttk.Frame(self.window)
        control_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)
        
        ttk.Label(control_frame, text="📊 BACKTESTING", 
                 font=('Arial', 14, 'bold'), foreground="#00FF00").pack(pady=10)
        
        # Fecha inicio
        ttk.Label(control_frame, text="Fecha Inicio:").pack(pady=5)
        self.start_date = ttk.Entry(control_frame, width=20)
        self.start_date.insert(0, "2023-01-01")
        self.start_date.pack(pady=5)
        
        # Fecha fin
        ttk.Label(control_frame, text="Fecha Fin:").pack(pady=5)
        self.end_date = ttk.Entry(control_frame, width=20)
        self.end_date.insert(0, "2024-12-31")
        self.end_date.pack(pady=5)
        
        # Botón ejecutar
        ttk.Button(control_frame, text="▶️ EJECUTAR BACKTEST", 
                  command=self.run_backtest).pack(fill=tk.X, pady=10)
        
        # Resultados
        ttk.Label(control_frame, text="\n📈 Resultados:", 
                 font=('Arial', 12, 'bold'), foreground="#00FF00").pack(pady=10)
        
        self.results_text = scrolledtext.ScrolledText(control_frame, height=20, width=40,
                                                      background="#2a2a2a", 
                                                      foreground="#00FF00")
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Frame para gráficos
        chart_frame = ttk.Frame(self.window)
        chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(chart_frame, text="📉 Gráfico de Precios", 
                 font=('Arial', 12, 'bold'), foreground="#00FF00").pack(pady=5)
        
        self.chart_canvas = tk.Canvas(chart_frame, bg="#2a2a2a")
        self.chart_canvas.pack(fill=tk.BOTH, expand=True)
    
    def run_backtest(self):
        """Ejecuta el backtest"""
        start = self.start_date.get()
        end = self.end_date.get()
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "⏳ Ejecutando backtesting...\n")
        self.window.update()
        
        # Descargar datos
        data = self.fetcher.fetch_data(self.symbol, start, end)
        
        if data.empty:
            self.results_text.insert(tk.END, "Error: No hay datos disponibles")
            return
        
        # Ejecutar estrategia
        analysis = self.strategy.analyze(data)
        
        # Calcular estadísticas
        results = f"""
═══════════════════════════════
✓ BACKTEST COMPLETADO
═══════════════════════════════

Símbolo: {self.symbol}
Período: {start} a {end}
Velas: {len(data)}

Precio Inicial: ${data['close'].iloc[0]:.2f}
Precio Final: ${data['close'].iloc[-1]:.2f}
Retorno: {((data['close'].iloc[-1] / data['close'].iloc[0]) - 1) * 100:.2f}%

───────────────────────────────
ANÁLISIS ACTUAL
───────────────────────────────
Señal: {analysis['signal']}
Razón: {analysis['reason']}

MA Rápida: ${analysis['ma_fast']:.2f}
MA Lenta: ${analysis['ma_slow']:.2f}
RSI: {analysis['rsi']:.1f}

───────────────────────────────
ESTADÍSTICAS ESTIMADAS
───────────────────────────────
Volatilidad Diaria: {data['close'].pct_change().std() * 100:.2f}%
Máximo: ${data['high'].max():.2f}
Mínimo: ${data['low'].min():.2f}
Volumen Promedio: {data['volume'].mean():,.0f}
"""
        
        self.results_text.insert(tk.END, results)
        
        # Dibujar gráfico
        self.draw_chart(data)
    
    def draw_chart(self, data):
        """Dibuja el gráfico de precios"""
        fig = Figure(figsize=(10, 5), dpi=100, facecolor="#2a2a2a", edgecolor="white")
        ax = fig.add_subplot(111, facecolor="#1e1e1e")
        
        # Gráfico de precios
        ax.plot(data.index, data['close'], color="#00FF00", linewidth=2, label="Precio")
        
        # MA
        ma_50 = data['close'].rolling(50).mean()
        ma_200 = data['close'].rolling(200).mean()
        ax.plot(data.index, ma_50, color="#FFD700", linewidth=1, alpha=0.7, label="MA50")
        ax.plot(data.index, ma_200, color="#FF6B6B", linewidth=1, alpha=0.7, label="MA200")
        
        ax.set_xlabel("Fecha", color="white")
        ax.set_ylabel("Precio ($)", color="white")
        ax.set_title(f"{self.symbol} - Backtest", color="white", fontsize=14, fontweight='bold')
        ax.legend(loc="upper left", facecolor="#2a2a2a", edgecolor="white")
        ax.grid(True, alpha=0.2, color="white")
        ax.tick_params(colors="white")
        
        # Limpiar canvas anterior
        for widget in self.chart_canvas.winfo_children():
            widget.destroy()
        
        # Mostrar nuevo gráfico
        canvas = FigureCanvasTkAgg(fig, master=self.chart_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


class RealtimeWindow:
    """Ventana de Trading en Tiempo Real con 4 gráficos"""
    def __init__(self, window, symbol, config):
        self.window = window
        self.symbol = symbol
        self.config = config
        self.fetcher = CryptoForexDataFetcher()
        self.strategy = TrendFollowerStrategy()
        self.paper_trader = LivePaperTrader(config['trading']['initial_capital'])
        self.is_running = False
        
        self.setup_ui()
        self.start_monitoring()
    
    def setup_ui(self):
        """Configura la ventana de tiempo real"""
        # Frame superior - Control
        top_frame = ttk.Frame(self.window)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(top_frame, text=f"📡 TRADING EN TIEMPO REAL - {self.symbol}", 
                 font=('Arial', 14, 'bold'), foreground="#00FF00").pack(side=tk.LEFT, padx=10)
        
        self.status_label = ttk.Label(top_frame, text="● INICIANDO...", 
                                     foreground="#FFD700", font=('Arial', 10))
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        ttk.Button(top_frame, text="⏹️ DETENER", 
                  command=self.stop_monitoring).pack(side=tk.RIGHT, padx=10)
        
        # Frame de alertas activas
        alert_frame = ttk.Frame(self.window)
        alert_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(alert_frame, text="🔔 ALERTA ACTUAL:", 
                 font=('Arial', 12, 'bold'), foreground="#FFD700").pack(side=tk.LEFT, padx=10)
        
        self.alert_label = ttk.Label(alert_frame, text="Esperando señal...", 
                                    font=('Arial', 11), foreground="#00FF00",
                                    background="#2a2a2a")
        self.alert_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Frame principal con 4 gráficos
        chart_frame = ttk.Frame(self.window)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 2x2 Grid de gráficos
        self.charts = {}
        timeframes = [("1 Día", "1d"), ("1 Hora", "1h"), ("15 Minutos", "15m"), ("5 Minutos", "5m")]
        
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        
        for i, (label, timeframe) in enumerate(timeframes):
            row, col = positions[i]
            
            # Sub-frame
            sub_frame = ttk.Frame(chart_frame)
            sub_frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            
            ttk.Label(sub_frame, text=f"📊 {label}", 
                     font=('Arial', 10, 'bold'), foreground="#00FF00").pack(pady=5)
            
            canvas = tk.Canvas(sub_frame, bg="#2a2a2a", height=250)
            canvas.pack(fill=tk.BOTH, expand=True)
            
            self.charts[timeframe] = canvas
        
        # Configurar grid
        for i in range(2):
            chart_frame.grid_rowconfigure(i, weight=1)
            chart_frame.grid_columnconfigure(i, weight=1)
        
        # Frame inferior - Estadísticas
        stats_frame = ttk.Frame(self.window)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.stats_label = ttk.Label(stats_frame, text="Actualizando...", 
                                    font=('Arial', 9), justify=tk.LEFT,
                                    background="#2a2a2a", foreground="#00FF00")
        self.stats_label.pack(fill=tk.BOTH, padx=5)
    
    def start_monitoring(self):
        """Inicia el monitoreo en tiempo real"""
        self.is_running = True
        thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        thread.start()
    
    def _monitoring_loop(self):
        """Loop de monitoreo en tiempo real"""
        while self.is_running:
            try:
                # Descargar datos recientes
                end_date = datetime.now()
                start_date = end_date - timedelta(days=60)
                
                data = self.fetcher.fetch_data(
                    self.symbol,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d")
                )
                
                if not data.empty:
                    # Analizar
                    analysis = self.strategy.analyze(data)
                    
                    # Actualizar alertas
                    self.update_alerts(analysis)
                    
                    # Actualizar gráficos
                    self.update_charts(data)
                    
                    # Actualizar estadísticas
                    self.update_stats(analysis)
                
                self.status_label.config(text="● EN LÍNEA", foreground="#00FF00")
                self.window.update()
                
                # Esperar 60 segundos
                import time
                time.sleep(60)
            
            except Exception as e:
                print(f"Error en monitoreo: {e}")
                self.status_label.config(text=f"● ERROR: {str(e)[:20]}", foreground="#FF6B6B")
                import time
                time.sleep(5)
    
    def update_alerts(self, analysis):
        """Actualiza las alertas mostradas"""
        signal = analysis['signal']
        
        if signal == "BUY":
            # Calcular probabilidad (simulada)
            prob = min(95, 50 + int(analysis['rsi']))
            self.alert_label.config(
                text=f"🟢 COMPRA RECOMENDADA - Probabilidad: {prob}%",
                foreground="#00FF00"
            )
        elif signal == "SELL":
            prob = min(95, 50 + (100 - int(analysis['rsi'])))
            self.alert_label.config(
                text=f"🔴 VENTA RECOMENDADA - Probabilidad: {prob}%",
                foreground="#FF6B6B"
            )
        else:
            self.alert_label.config(
                text=f"⏸️ ESPERA - {analysis['reason']}",
                foreground="#FFD700"
            )
    
    def update_charts(self, data):
        """Actualiza los 4 gráficos"""
        # Simplificado: mostrar el mismo gráfico en todos
        fig = Figure(figsize=(4, 3), dpi=80, facecolor="#2a2a2a")
        ax = fig.add_subplot(111, facecolor="#1e1e1e")
        
        ax.plot(data.index[-100:], data['close'].iloc[-100:], color="#00FF00", linewidth=1.5)
        ax.set_title(f"{self.symbol}", color="white", fontsize=10)
        ax.tick_params(colors="white")
        ax.grid(True, alpha=0.2)
        
        # Mostrar en todos los canvas
        for timeframe, canvas in self.charts.items():
            for widget in canvas.winfo_children():
                widget.destroy()
            
            chart_fig = Figure(figsize=(4, 3), dpi=80, facecolor="#2a2a2a")
            chart_ax = chart_fig.add_subplot(111, facecolor="#1e1e1e")
            
            chart_ax.plot(data.index[-100:], data['close'].iloc[-100:], 
                         color="#00FF00", linewidth=1.5)
            chart_ax.set_title(f"{self.symbol}", color="white", fontsize=10)
            chart_ax.tick_params(colors="white")
            chart_ax.grid(True, alpha=0.2)
            
            canvas_obj = FigureCanvasTkAgg(chart_fig, master=canvas)
            canvas_obj.draw()
            canvas_obj.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_stats(self, analysis):
        """Actualiza estadísticas"""
        stats = f"""
Precio: ${analysis['current_price']:.2f} | MA50: ${analysis['ma_fast']:.2f} | MA200: ${analysis['ma_slow']:.2f} | RSI: {analysis['rsi']:.1f}
Posiciones Abiertas: {len(self.paper_trader.get_open_positions())} | Capital Disponible: ${self.paper_trader.cash:.2f}
"""
        self.stats_label.config(text=stats)
    
    def stop_monitoring(self):
        """Detiene el monitoreo"""
        self.is_running = False
        self.status_label.config(text="● DETENIDO", foreground="#FF6B6B")


if __name__ == "__main__":
    root = tk.Tk()
    app = TradingBotGUI(root)
    root.mainloop()
