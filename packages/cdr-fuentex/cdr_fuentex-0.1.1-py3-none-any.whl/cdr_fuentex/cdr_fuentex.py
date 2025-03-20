import pandas as pd

# ======================================================
# Coeficiente de Dispersión Relativa Fuentex (CDR-FX)
# Autor: Sergio Fuentes
# Fecha de creación: 2025-03-19
# Licencia: MIT License
# Hash original SHA-256: Verificado en README.md
# ======================================================

def calcular_cdr_fx(df):
    """
    Calcula el Coeficiente de Dispersión Relativa Fuentex (CDR-FX) para un dataset.
    
    Parámetros:
    -----------
    df: pandas.DataFrame
        Dataset numérico a analizar.
        
    Retorna:
    --------
    pandas.DataFrame
        DataFrame con varianza, CDR-FX, nivel de dispersión y recomendaciones.
    """
    varianzas = df.var(numeric_only=True)
    varianza_max = varianzas.max()
    cdr_fx = 1 + (varianzas / varianza_max)

    resultados = pd.DataFrame({
        'Varianza': varianzas,
        'CDR-FX': cdr_fx,
        'Nivel dispersión': [
            "Alta (domina)" if x >= 1.7 else "Media" if x >= 1.3 else "Baja" 
            for x in cdr_fx
        ],
        'Recomendación': [
            f"Normalizar obligatoriamente '{var}'." if x >= 1.7 else
            f"Evaluar normalizar '{var}'." if x >= 1.3 else
            f"Normalización opcional para '{var}'."
            for var, x in zip(varianzas.index, cdr_fx)
        ]
    })

    return resultados.sort_values(by='CDR-FX', ascending=False)
 
