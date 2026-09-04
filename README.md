# Trading Bot - Backtesting & Optimization System

Sistema riguroso de backtesting, optimización y paper trading para validar estrategias de trading de largo plazo.

## Objetivo

Determinar si es posible construir un sistema de trading con expectativa matemática positiva comenzando con capital pequeño ($50+), validando mediante:

1. **Backtesting** en datos históricos
2. **Validación out-of-sample** (evitar overfitting)
3. **Optimización de parámetros** de forma sistemática
4. **Paper trading** en tiempo real
5. **Análisis riguroso de métricas**

## Características

✅ Backtesting robusto con cálculo de comisiones y spreads  
✅ Validación en datos nunca vistos (out-of-sample)  
✅ Optimización bayesiana de parámetros  
✅ Cálculo de métricas: Sharpe ratio, drawdown, win rate, etc.  
✅ Generación de reportes detallados  
✅ Paper trading simulado  
✅ Múltiples estrategias disponibles  
✅ Visualización de resultados  

## Estructura del Proyecto

```
trading-bot-backtest/
├── data/
│   ├── __init__.py
│   └── fetch_data.py              # Descarga datos de Yahoo Finance
├── strategies/
│   ├── __init__.py
│   ├── base_strategy.py            # Clase base para estrategias
│   ├── moving_average_cross.py     # Estrategia: Cruce de medias móviles
│   ├── mean_reversion.py           # Estrategia: Mean reversion
│   └── rsi_macd.py                 # Estrategia: RSI + MACD
├── backtest/
│   ├── __init__.py
│   ├── engine.py                   # Motor de backtesting
│   ├── validator.py                # Validador out-of-sample
│   └── metrics.py                  # Cálculo de métricas
├── optimization/
│   ├── __init__.py
│   └── optimizer.py                # Optimización bayesiana
├── paper_trading/
│   ├── __init__.py
│   └── simulator.py                # Simulador de paper trading
├── reporting/
│   ├── __init__.py
│   ├── report_generator.py         # Generador de reportes
│   └── visualizer.py               # Visualizaciones
├── config.yaml                     # Configuración central
├── requirements.txt                # Dependencias
├── main.py                         # Punto de entrada principal
└── README.md
```

## Instalación

```bash
git clone https://github.com/carlosvelez2424-ux/trading-bot-backtest.git
cd trading-bot-backtest
pip install -r requirements.txt
```

## Configuración Inicial

Edita `config.yaml` para especificar:
- Capital inicial
- Activos a backtestear
- Rango de fechas
- Comisiones y spreads
- Estrategia a usar

## Uso

### 1. Backtesting
```bash
python main.py --mode backtest --strategy moving_average_cross --symbol SPY
```

### 2. Optimización
```bash
python main.py --mode optimize --strategy moving_average_cross --symbol SPY
```

### 3. Validación Out-of-Sample
```bash
python main.py --mode validate --strategy moving_average_cross --symbol SPY
```

### 4. Paper Trading
```bash
python main.py --mode paper_trading --strategy moving_average_cross --symbol SPY
```

## Metodología

### Fase 1: Backtesting
- Prueba la estrategia en datos históricos completos
- Calcula todas las métricas de rendimiento
- Identifica si hay ventaja estadística

### Fase 2: Validación Out-of-Sample
- Divide datos en: entrenamiento (70%), validación (15%), prueba (15%)
- Optimiza parámetros SOLO en período de entrenamiento
- Valida en período que nunca vio
- Evita overfitting

### Fase 3: Optimización
- Utiliza Bayesian Optimization
- Busca parámetros óptimos
- Valida robustez de los parámetros

### Fase 4: Paper Trading
- Simula operaciones en tiempo real
- Registra cada trade con contexto completo
- Permite evaluar performance fuera de muestra histórica

## Métricas Generadas

- **Rentabilidad total**: % de ganancia desde inicio
- **Rentabilidad anualizada**: % promedio anual
- **Sharpe Ratio**: Rendimiento ajustado por riesgo
- **Máximo Drawdown**: Caída máxima desde pico
- **Win Rate**: % de operaciones ganadoras
- **Ratio Riesgo/Beneficio**: Ganancia promedio / Pérdida promedio
- **Número de operaciones**: Total de trades ejecutados
- **Rachas**: Máximas rachas ganadoras/perdedoras
- **Factor de ganancia**: Ganancias totales / Pérdidas totales

## Supuestos y Consideraciones

⚠️ **Importante:**
- Los backtests incluyen comisiones y spreads realistas
- NO hay garantía de rendimiento futuro
- El mercado cambia; estrategias pasadas pueden no funcionar
- El deslizamiento (slippage) no se modela perfectamente
- El paper trading simula pero no es trading real

## Requisitos Mínimos

- Python 3.8+
- pandas, numpy
- yfinance (para datos)
- scikit-optimize (para optimización)
- plotly (para visualizaciones)

## Flujo de Trabajo Recomendado

1. Ejecuta backtest en periodo de 5-10 años
2. Si Sharpe > 0.5 y drawdown < 30%, continúa
3. Ejecuta optimización
4. Valida en datos out-of-sample
5. Ejecuta paper trading por 1-3 meses
6. Analiza resultados y decide si pasar a dinero real

## Licencia

MIT License

## Disclaimer

Este proyecto es educativo. Trading conlleva riesgo de pérdida total. No es asesoría financiera. Úsalo bajo tu propio riesgo.
