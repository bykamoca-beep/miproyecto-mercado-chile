import os
from datetime import datetime
import numpy as np
import pandas as pd
import yfinance as yf

# 1. Definir rutas dinámicas
# Obtener la carpeta actual donde se encuentra este script (.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Crear la carpeta 'data' al mismo nivel de tu proyecto
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

print("Descargando datos financieros en tiempo real desde Yahoo Finance...")

# 2. Definir Tickers para el mercado chileno / Mesa de Dinero y Retail
tickers = {
    # Acciones IPSA / Retail & Banca Chile
    'FALABELLA.SN': 'Falabella',
    'CENCOSUD.SN': 'Cencosud',
    'CHILE.SN': 'Banco de Chile',
    'BSANTANDER.SN': 'Banco Santander Chile',
    'SQM-B.SN': 'SQM',
    # Monedas y Commodities
    'CLP=X': 'USD/CLP',
    'HG=F': 'Cobre (Futuros)',
    'CL=F': 'Petróleo WTI',
    # Índices Globales y Renta Variable US
    '^GSPC': 'S&P 500',
    'EWW': 'iShares MSCI Mexico',  # Benchmark LATAM
}

# 3. Descargar datos históricos (Últimos 2 años)
simbolos = list(tickers.keys())
datos_crudos = yf.download(simbolos, period='2y', interval='1d')['Close']

# Renombrar columnas
datos_crudos = datos_crudos.rename(columns=tickers)

# 4. Procesamiento de Métricas
df_precios = datos_crudos.dropna().copy()
df_retornos = df_precios.pct_change().dropna()

# 5. Resumen Financiero Ejecutivo
ultimos_precios = df_precios.iloc[-1]
precios_hace_1d = df_precios.iloc[-2]
precios_hace_1m = (
    df_precios.iloc[-22] if len(df_precios) >= 22 else df_precios.iloc[0]
)
precios_hace_1a = (
    df_precios.iloc[-252] if len(df_precios) >= 252 else df_precios.iloc[0]
)

resumen_mercado = pd.DataFrame({
    'Activo': ultimos_precios.index,
    'Precio_Actual': ultimos_precios.values,
    'Variacion_Diaria_%': (
        (ultimos_precios - precios_hace_1d) / precios_hace_1d * 100
    ).values,
    'Variacion_Mensual_%': (
        (ultimos_precios - precios_hace_1m) / precios_hace_1m * 100
    ).values,
    'Variacion_Anual_%': (
        (ultimos_precios - precios_hace_1a) / precios_hace_1a * 100
    ).values,
    'Volatilidad_Anualizada_%': (df_retornos.std() * np.sqrt(252) * 100).values,
})

resumen_mercado = resumen_mercado.round(2)

print('\n--- RESUMEN DE MERCADO EN TIEMPO REAL ---')
print(resumen_mercado.to_string(index=False))

# 6. Exportar Archivos usando las rutas dinámicas
path_precios = os.path.join(DATA_DIR, 'precios_historicos_mercado.csv')
path_retornos = os.path.join(DATA_DIR, 'retornos_diarios_mercado.csv')
path_excel = os.path.join(DATA_DIR, 'Dashboard_Mercado_Tiempo_Real.xlsx')

df_precios.reset_index().to_csv(path_precios, index=False)
df_retornos.reset_index().to_csv(path_retornos, index=False)

with pd.ExcelWriter(path_excel, engine='openpyxl') as writer:
  resumen_mercado.to_excel(writer, sheet_name='Resumen_Ejecutivo', index=False)
  df_precios.reset_index().to_excel(
      writer, sheet_name='Precios_Historicos', index=False
  )

  matriz_correlacion = df_retornos.corr().round(2)
  matriz_correlacion.to_excel(writer, sheet_name='Matriz_Correlacion')

print(f'\n¡Archivos generados exitosamente en la carpeta: {DATA_DIR}')
print('1. precios_historicos_mercado.csv')
print('2. retornos_diarios_mercado.csv')
print('3. Dashboard_Mercado_Tiempo_Real.xlsx')

