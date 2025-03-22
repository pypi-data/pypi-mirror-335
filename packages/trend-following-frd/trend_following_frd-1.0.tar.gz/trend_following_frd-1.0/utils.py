import pandas as pd

def get_monthly_series(daily_dict):
    # Convertir diccionario a Series con el índice de fechas
    daily_series = pd.Series(daily_dict)
    # Re-muestrear: tomar el último valor de cada mes
    monthly = daily_series.resample('ME').last()
    return monthly