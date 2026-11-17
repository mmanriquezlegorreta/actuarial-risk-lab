import numpy as np

from models.monte_carlo import simulate_portfolio


print("\n======================================")
print(" ACTUARIAL RISK LAB")
print(" VALIDACION MATEMATICA")
print("======================================")

# Ejecutar simulacion
results = simulate_portfolio(
    age=40,
    term=10,
    number_insured=1000,
    sum_insured=500000,
    interest_rate=0.05,
    simulations=10000,
    seed=42
)

losses = results["losses"]

# 1. Media simulada
mean_loss = np.mean(losses)

# 2. Desviacion estandar
std_loss = np.std(losses, ddof=1)

# 3. Error estandar
standard_error = std_loss / np.sqrt(len(losses))

# 4. Intervalo de confianza
lower = mean_loss - 1.96 * standard_error
upper = mean_loss + 1.96 * standard_error

# 5. Resultados
print(f"\nPrima pura: ${results['premium']:,.2f}")

print(f"Perdida promedio: ${mean_loss:,.2f}")

print(f"Desviacion estandar: ${std_loss:,.2f}")

print(f"Error estandar: ${standard_error:,.2f}")

print("\nINTERVALO DE CONFIANZA DEL 95%")

print(f"Limite inferior: ${lower:,.2f}")

print(f"Limite superior: ${upper:,.2f}")

# 6. Comprobacion
if lower <= 0 <= upper:
    print("\nRESULTADO: VALIDACION SATISFACTORIA")
    print("El cero pertenece al intervalo de confianza.")
else:
    print("\nRESULTADO: REVISAR EL MODELO")

print("\n======================================")