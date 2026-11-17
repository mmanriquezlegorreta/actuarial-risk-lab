"""
ACTUARIAL RISK LAB
Motor de mortalidad y supervivencia.

Fuente: Tabla de mortalidad utilizada en clase.
"""

from pathlib import Path
import pandas as pd
import numpy as np


# ==========================================
# 1. CONFIGURACIÓN
# ==========================================

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "tabla_mortalidad.xlsx"


# ==========================================
# 2. CARGA Y VALIDACIÓN DE LA TABLA
# ==========================================

def load_mortality_table():

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {DATA_FILE}"
        )

    df = pd.read_excel(
        DATA_FILE,
        sheet_name="Mortalidad"
    )

    required_columns = ["x", "Q(x)"]

    if not all(col in df.columns for col in required_columns):
        raise ValueError(
            "La tabla debe contener las columnas x y Q(x)."
        )

    df = df[required_columns].copy()

    df.columns = ["edad", "qx"]

    df["edad"] = pd.to_numeric(
        df["edad"], errors="coerce"
    )

    df["qx"] = pd.to_numeric(
        df["qx"], errors="coerce"
    )

    # Detectar datos incompletos
    if df.isna().any().any():
        raise ValueError(
            "La tabla contiene edades o probabilidades vacías o inválidas."
        )

    # Validar edades
    if not np.all(df["edad"] % 1 == 0):
        raise ValueError(
            "Las edades deben ser números enteros."
        )

    df["edad"] = df["edad"].astype(int)

    if df["edad"].duplicated().any():
        raise ValueError(
            "Existen edades duplicadas."
        )

    df = df.sort_values("edad")

    # Validar rango de edades
    expected_ages = np.arange(0, 111)

    if not np.array_equal(
        df["edad"].to_numpy(),
        expected_ages
    ):
        raise ValueError(
            "La tabla debe contener todas las edades consecutivas de 0 a 110."
        )

    # Validar probabilidades
    if not df["qx"].between(0, 1).all():
        raise ValueError(
            "Las probabilidades deben estar entre 0 y 1."
        )

    # Calcular probabilidad de supervivencia
    df["px"] = 1 - df["qx"]

    return df.set_index("edad")


# ==========================================
# 3. PROBABILIDAD DE FALLECIMIENTO
# ==========================================

def get_qx(age):

    table = load_mortality_table()

    if age not in table.index:
        raise ValueError(
            f"No existe información para la edad {age}."
        )

    return float(table.loc[age, "qx"])


# ==========================================
# 4. PROBABILIDAD DE SUPERVIVENCIA
# ==========================================

def get_px(age):

    return 1 - get_qx(age)


# ==========================================
# 5. SUPERVIVENCIA ACUMULADA
# ==========================================

def survival_probability(age, years):

    if years < 0 or int(years) != years:
        raise ValueError(
            "Los años deben ser un entero no negativo."
        )

    if age < 0 or int(age) != age:
        raise ValueError(
            "La edad debe ser un entero no negativo."
        )

    table = load_mortality_table()

    ages = np.arange(age, age + years)

    if not all(a in table.index for a in ages):
        raise ValueError(
            "La tabla no contiene todas las edades solicitadas."
        )

    probabilities = table.loc[ages, "px"]

    return float(probabilities.prod())


# ==========================================
# 6. PROBABILIDAD DE FALLECIMIENTO
# ==========================================

def death_probability(age, years):

    return 1 - survival_probability(age, years)


# ==========================================
# 7. ESPERANZA DE VIDA CURTATA
# ==========================================

def life_expectancy(age):

    table = load_mortality_table()

    if age not in table.index:
        raise ValueError(
            f"No existe información para la edad {age}."
        )

    ages = table.index[table.index >= age]

    survival = 1.0
    expected_years = 0.0

    for current_age in ages:

        survival *= float(
            table.loc[current_age, "px"]
        )

        expected_years += survival

    return expected_years