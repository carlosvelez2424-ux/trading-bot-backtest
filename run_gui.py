#!/usr/bin/env python3
# ============================================================================
# SCRIPT PARA EJECUTAR LA INTERFAZ GRÁFICA
# ============================================================================

import tkinter as tk
import sys
import os

# Añadir el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import TradingBotGUI

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = TradingBotGUI(root)
        root.mainloop()
    except ImportError as e:
        print(f"\nError: Falta instalar dependencias")
        print(f"Ejecuta primero: pip install -r requirements.txt\n")
        print(f"Detalles del error: {e}")
        input("Presiona Enter para salir...")
    except Exception as e:
        print(f"\nError al iniciar la aplicación: {e}")
        input("Presiona Enter para salir...")
