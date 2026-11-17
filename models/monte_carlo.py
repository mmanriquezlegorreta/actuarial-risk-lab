"""
ACTUARIAL RISK LAB
Motor Monte Carlo y analisis de escenarios.
"""

import numpy as np
from models.mortality import load_mortality_table


# ==========================================
# 1. CALCULO DE PRIMA PURA
# ==========================================

def calculate_net_premium(
    age, term, sum_insured, interest_rate
):

    table = load_mortality_table()

    v = 1 / (1 + interest_rate)

    survival = 1.0
    epv_benefit = 0.0
    epv_premiums = 0.0

    for year in range(term):

        current_age = age + year

        qx = float(table.loc[current_age, "qx"])

        epv_benefit += (
            sum_insured
            * (v ** (year + 1))
            * survival
            * qx
        )

        epv_premiums += (
            (v ** year) * survival
        )

        survival *= (1 - qx)

    if epv_premiums <= 0:
        raise ValueError("Factor de primas no valido.")

    return epv_benefit / epv_premiums


def simulate_portfolio(
    age=40,
    term=10,
    number_insured=1000,
    sum_insured=500000,
    interest_rate=0.05,
    simulations=10000,
    seed=42,
    mortality_multiplier=1.0
):

    # Validaciones
    if age < 0 or int(age) != age:
        raise ValueError("Edad invalida.")

    if term <= 0 or int(term) != term:
        raise ValueError("Plazo invalido.")

    if number_insured <= 0 or int(number_insured) != number_insured:
        raise ValueError("Cantidad de asegurados invalida.")

    if simulations <= 0 or int(simulations) != simulations:
        raise ValueError("Simulaciones invalidas.")

    if sum_insured <= 0:
        raise ValueError("Suma asegurada invalida.")

    if interest_rate <= -1:
        raise ValueError("Tasa de interes invalida.")

    if mortality_multiplier <= 0:
        raise ValueError("Multiplicador invalido.")

    table = load_mortality_table()

    required_ages = range(age, age + term)

    if not all(a in table.index for a in required_ages):
        raise ValueError("La tabla no cubre todo el plazo.")

    # Prima pura
    premium = calculate_net_premium(
        age,
        term,
        sum_insured,
        interest_rate
    )

    rng = np.random.default_rng(seed)

    losses = np.zeros(simulations)

    # Numero inicial de asegurados vivos
    alive_count = np.full(
        simulations,
        number_insured,
        dtype=np.int64
    )

    for year in range(term):

        current_age = age + year

        qx = float(table.loc[current_age, "qx"])

        qx = min(
            1.0,
            qx * mortality_multiplier
        )

        # Cobro de primas al inicio del año
        discount_premium = (
            1 / (1 + interest_rate) ** year
        )

        losses -= (
            alive_count
            * premium
            * discount_premium
        )

        # Simulacion binomial de fallecimientos
        deaths = rng.binomial(
            alive_count,
            qx
        )

        # Pago de indemnizaciones al final del año
        discount_claim = (
            1 / (1 + interest_rate) ** (year + 1)
        )

        losses += (
            deaths
            * sum_insured
            * discount_claim
        )

        # Actualizar supervivientes
        alive_count -= deaths

    return {
        "premium": premium,
        "losses": losses
    }

# ==========================================
# 3. INDICADORES DE RIESGO
# ==========================================

def calculate_risk_metrics(
    losses,
    initial_capital,
    confidence_level=0.95
):

    losses = np.asarray(losses, dtype=float)

    # Validaciones
    if losses.ndim != 1:
        raise ValueError(
            "Las perdidas deben ser un arreglo unidimensional."
        )

    if len(losses) < 2:
        raise ValueError(
            "Se requieren al menos dos simulaciones."
        )

    if not np.all(np.isfinite(losses)):
        raise ValueError(
            "Existen valores invalidos en las perdidas."
        )

    if not np.isfinite(initial_capital) or initial_capital < 0:
        raise ValueError("Capital inicial invalido.")

    if not 0 < confidence_level < 1:
        raise ValueError("Nivel de confianza invalido.")

    # 1. Perdida esperada
    expected_loss = np.mean(losses)

    # 2. Desviacion estandar muestral
    standard_deviation = np.std(
        losses,
        ddof=1
    )

    # 3. Valor en Riesgo
    var = np.quantile(
        losses,
        confidence_level,
        method="linear"
    )

    # 4. TVaR mediante promedio integral
    # de la cola superior de la distribucion

    sorted_losses = np.sort(losses)[::-1]

    tail_mass = (
        1 - confidence_level
    ) * len(losses)

    full_count = int(np.floor(tail_mass))

    fractional_part = (
        tail_mass - full_count
    )

    tail_sum = np.sum(
        sorted_losses[:full_count]
    )

    if fractional_part > 0:
        tail_sum += (
            fractional_part
            * sorted_losses[full_count]
        )

    tvar = tail_sum / tail_mass

    # 5. Probabilidad de insolvencia
    insolvency_probability = np.mean(
        losses > initial_capital
    )

    return {
        "expected_loss": expected_loss,
        "standard_deviation": standard_deviation,
        "var_95": var,
        "tvar_95": tvar,
        "insolvency_probability": insolvency_probability
    }
# ==========================================
# 4. MODELO DE SOLVENCIA
# ==========================================

def calculate_solvency_metrics(
    losses,
    initial_capital
):

    losses = np.asarray(losses, dtype=float)

    if losses.ndim != 1 or len(losses) < 2:
        raise ValueError("Muestra de perdidas invalida.")

    if not np.all(np.isfinite(losses)):
        raise ValueError("Existen perdidas invalidas.")

    if not np.isfinite(initial_capital) or initial_capital < 0:
        raise ValueError("Capital inicial invalido.")

    # Requerimientos de capital
    var_95 = max(
        0.0,
        float(np.quantile(losses, 0.95))
    )

    var_99 = max(
        0.0,
        float(np.quantile(losses, 0.99))
    )

    tvar_95 = max(
        0.0,
        float(
            calculate_risk_metrics(
                losses,
                initial_capital
            )["tvar_95"]
        )
    )

    # Margenes de solvencia
    margin_95 = initial_capital - var_95

    margin_99 = initial_capital - var_99

    # Probabilidad empirica de insolvencia
    insolvency = float(
        np.mean(losses > initial_capital)
    )

    # Clasificacion respecto al VaR
    if initial_capital >= var_95:

        status = "SOLVENCIA ADECUADA"

    else:

        status = "CAPITAL INSUFICIENTE AL 95%"

    return {
        "capital_available": initial_capital,
        "required_capital_95": var_95,
        "required_capital_99": var_99,
        "tvar_95": tvar_95,
        "solvency_margin_95": margin_95,
        "solvency_margin_99": margin_99,
        "insolvency_probability": insolvency,
        "status": status
    }