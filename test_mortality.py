from models.mortality import (
    load_mortality_table,
    get_qx,
    get_px,
    survival_probability,
    death_probability,
    life_expectancy
)

print("\n====================================")
print("       ACTUARIAL RISK LAB")
print("       MOTOR DE MORTALIDAD")
print("====================================\n")

table = load_mortality_table()

print("REGISTROS DE LA TABLA:")
print(table.head())

age = 40
years = 10

print("\nRESULTADOS ACTUARIALES")

print(f"Edad analizada: {age}")

print(f"Probabilidad de fallecimiento: {get_qx(age):.6f}")

print(f"Probabilidad de supervivencia: {get_px(age):.6f}")

print(
    f"Supervivencia a {years} años: "
    f"{survival_probability(age, years):.6f}"
)

print(
    f"Fallecimiento en {years} años: "
    f"{death_probability(age, years):.6f}"
)

print(
    f"Esperanza de vida curtata: "
    f"{life_expectancy(age):.4f} años"
)

print("\n====================================")
print("       VALIDACIÓN COMPLETADA")
print("====================================")