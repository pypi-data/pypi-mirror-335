# Coeficiente de Dispersión Relativa Fuentex (CDR-FX)

Librería Python para calcular claramente el **Coeficiente de Dispersión Relativa Fuentex (CDR-FX)**, una métrica útil para evaluar la dispersión relativa de variables en datasets.

##  Instalación

Puedes instalar la librería directamente desde PyPI con:

```bash
pip install cdr_fuentex
```

##  Uso rápido

```python
import pandas as pd
from cdr_fuentex import calcular_cdr_fx

# Crear un DataFrame de ejemplo
df = pd.DataFrame({
    'Edad': [25, 29, 32, 45],
    'Ingreso': [2500000, 3900000, 2850000, 5250000],
    'Peso': [60, 85, 68, 95]
})

# Calcular el CDR-FX
resultado = calcular_cdr_fx(df)
print(resultado)
```

## 📊 Interpretación de resultados

| Rango de CDR-FX | Interpretación |
|-----------------|----------------|
| **≈ 1** | Baja dispersión, normalización opcional. |
| **1.3 - 1.7** | Dispersión moderada, evaluar normalización. |
| **1.7 - 2.0** | Alta dispersión, normalización recomendada. |

## 🔖 Hash SHA-256 del archivo original

Este hash garantiza la integridad del archivo `cdr_fuentex.py` en su versión original.

```
2df7662c8cd1c501156aa7498a5229830e268fe65b95dc7433f64249b16842eb
```

## 📜 Licencia

Este proyecto está licenciado bajo la **MIT License**.

## 📩 Contacto

- **Autor**: Sergio Fuentes
- **Email**: Fuentex.datalab@gmail.com
- **Repositorio GitHub**: [https://github.com/FuentexDatalab/cdr_fuentex](https://github.com/FuentexDatalab/cdr_fuentex)

Si te resulta útil, ⭐ ¡dale una estrella en GitHub! 😊
 
