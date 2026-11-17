import streamlit as st
import numpy as np
import plotly.express as px
from models.monte_carlo import (
    simulate_portfolio,
    calculate_risk_metrics,
    calculate_solvency_metrics
)

from models.mortality import load_mortality_table

# ==========================================
# CONFIGURACION
# ==========================================

st.set_page_config(
    page_title="ACTUARIAL RISK LAB",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>

/* Fondo principal */
.stApp {
    background-color: #0B1120;
    color: #F1F5F9;
}

/* Barra superior */
[data-testid="stHeader"] {
    background-color: #0B1120;
}

/* Panel lateral */
[data-testid="stSidebar"] {
    background-color: #111C30;
}

[data-testid="stSidebar"] * {
    color: #E2E8F0;
}

/* Titulos */
h1, h2, h3, h4 {
    color: #F8FAFC !important;
}

/* Texto general */
p, label, span {
    color: #CBD5E1;
}

/* Indicadores financieros */
[data-testid="stMetric"] {
    background-color: #16243A;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #29415F;
}

/* Etiquetas de indicadores */
[data-testid="stMetricLabel"] {
    color: #94A3B8 !important;
}

/* Valores financieros */
[data-testid="stMetricValue"] {
    color: #F8FAFC !important;
}

/* Inputs */
[data-testid="stNumberInput"] input {
    background-color: #F8FAFC;
    color: #0F172A;
}

/* Botones */
.stButton button {
    border-radius: 8px;
    font-weight: bold;
}

/* Separadores */
hr {
    border-color: #263852;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# ENCABEZADO
# ==========================================

st.title("ACTUARIAL RISK LAB")

st.caption(
    "SIMULADOR ESTOCASTICO DE RIESGO Y SOLVENCIA"
)

st.markdown("---")


# ==========================================
# PANEL DE CONTROL
# ==========================================

st.sidebar.title("CONFIGURACION")

st.sidebar.subheader("Cartera")

age = st.sidebar.slider(
    "Edad de los asegurados",
    18, 90, 40
)

term = st.sidebar.slider(
    "Duracion del seguro",
    1,
    min(30, 111 - age),
    min(10, 111 - age)
)

number_insured = st.sidebar.number_input(
    "Numero de asegurados",
    min_value=100,
    max_value=10000,
    value=1000,
    step=100
)

sum_insured = st.sidebar.number_input(
    "Suma asegurada ($)",
    min_value=10000,
    max_value=5000000,
    value=500000,
    step=50000
)

st.sidebar.subheader("Finanzas")

interest_rate = st.sidebar.slider(
    "Tasa de interes (%)",
    0.0, 15.0, 5.0
) / 100

initial_capital = st.sidebar.number_input(
    "Capital inicial ($)",
    min_value=100000,
    max_value=100000000,
    value=2000000,
    step=100000
)

simulations = st.sidebar.select_slider(
    "Numero de simulaciones",
    options=[1000, 5000, 10000, 25000, 50000],
    value=10000
)

run = st.sidebar.button(
    "EJECUTAR SIMULACION",
    type="primary",
    use_container_width=True
)


# ==========================================
# EJECUCION DEL MODELO
# ==========================================

if "results" not in st.session_state:
    st.session_state.results = None

if run:

    with st.spinner("Ejecutando simulacion actuarial..."):

        try:

            st.session_state.results = simulate_portfolio(
                age=age,
                term=term,
                number_insured=number_insured,
                sum_insured=sum_insured,
                interest_rate=interest_rate,
                simulations=simulations
            )

            st.session_state.parameters = {
                "age": age,
                "term": term,
                "number_insured": number_insured,
                "sum_insured": sum_insured,
                "interest_rate": interest_rate,
                "capital": initial_capital,
                "simulations": simulations
            }

        except Exception as error:

            st.error(f"Error en el modelo: {error}")


# ==========================================
# RESULTADOS
# ==========================================

if st.session_state.results is None:

    st.info(
        "Configura los parametros y ejecuta "
        "la simulacion para visualizar los resultados."
    )

else:

    results = st.session_state.results
    params = st.session_state.parameters

    losses = results["losses"]

    metrics = calculate_risk_metrics(
        losses,
        params["capital"]
    )
    solvency = calculate_solvency_metrics(
    losses,
    params["capital"]
    )
    st.subheader("Indicadores ejecutivos")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Prima pura anual",
        f"${results['premium']:,.2f}"
    )

    col2.metric(
        "Perdida esperada",
        f"${metrics['expected_loss']:,.2f}"
    )

    col3.metric(
    "VaR 95%",
    f"${metrics['var_95']:,.0f}"
    )

    col4.metric(
        "Riesgo de insolvencia",
        f"{metrics['insolvency_probability']:.2%}"
    )

    st.markdown("---")

    st.subheader("Distribucion de perdidas")

    fig = px.histogram(
        x=losses,
        nbins=70,
        title="Distribucion de resultados Monte Carlo",
        labels={"x": "Perdida neta ($)", "y": "Frecuencia"},
        template="plotly_dark"
    )

    fig.add_vline(
    x=metrics["var_95"],
    line_dash="dash",
    line_color="#F59E0B",
    annotation_text="VaR 95%",
    annotation_position="top left"
)

    fig.add_vline(
    x=params["capital"],
    line_dash="dot",
    line_color="#38BDF8",
    annotation_text="Capital disponible",
    annotation_position="bottom right"
)
    fig.update_layout(
        paper_bgcolor="#0B1120",
        plot_bgcolor="#111C30",
        font_color="#E2E8F0"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown("---")

    st.subheader("Analisis financiero")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Desviacion estandar",
        f"${metrics['standard_deviation']:,.2f}"
    )

    col2.metric(
        "TVaR 95%",
        f"${metrics['tvar_95']:,.2f}"
    )

    col3.metric(
        "Capital inicial",
        f"${params['capital']:,.2f}"
    )

    st.markdown("---")

    # ANALISIS DE SOLVENCIA
# ======================================

    st.subheader("Analisis de solvencia")

    col1, col2, col3 = st.columns(3)

    col1.metric(
    "Capital requerido (VaR 95%)",
    f"${solvency['required_capital_95']:,.2f}"
)

    col2.metric(
    "Capital requerido (VaR 99%)",
    f"${solvency['required_capital_99']:,.2f}"
)

    col3.metric(
    "Margen de solvencia (95%)",
    f"${solvency['solvency_margin_95']:,.2f}"
)

    st.write("**Estado:**", solvency["status"])

    st.write(
    "**Probabilidad de insolvencia:**",
    f"{solvency['insolvency_probability']:.2%}"
)

    st.markdown("---")
    # ======================================
    # COMPARADOR DE ESCENARIOS
    # ======================================

    st.markdown("---")

    st.header("Comparador de escenarios actuariales")

    st.write(
        "Analisis de sensibilidad ante cambios "
        "en la mortalidad de la cartera."
    )

    scenarios = {
    "Optimista": 0.80,
    "Base": 1.00,
    "Adverso": 1.20,
    "Severo": 1.50
    }

    scenario_data = []

    for scenario_name, multiplier in scenarios.items():

        scenario_results = simulate_portfolio(
            age=params["age"],
            term=params["term"],
            number_insured=params["number_insured"],
            sum_insured=params["sum_insured"],
            interest_rate=params["interest_rate"],
            simulations=params["simulations"],
            seed=42,
            mortality_multiplier=multiplier
        )

        scenario_metrics = calculate_risk_metrics(
            scenario_results["losses"],
            params["capital"]
        )

        scenario_data.append({
            "Escenario": scenario_name,
            "Multiplicador de mortalidad": multiplier,
            "Perdida esperada": scenario_metrics["expected_loss"],
            "VaR 95%": scenario_metrics["var_95"],
            "TVaR 95%": scenario_metrics["tvar_95"],
            "Insolvencia": scenario_metrics["insolvency_probability"]
        })

    import pandas as pd

    scenario_df = pd.DataFrame(scenario_data)

    st.dataframe(
    scenario_df.style.format({
        "Multiplicador de mortalidad": "{:.0%}",
        "Perdida esperada": "${:,.2f}",
        "VaR 95%": "${:,.2f}",
        "TVaR 95%": "${:,.2f}",
        "Insolvencia": "{:.2%}"
    }),
    use_container_width=True,
    hide_index=True
)

    st.subheader("Comparacion del riesgo")

    fig_scenarios = px.bar(
        scenario_df,
        x="Escenario",
        y="VaR 95%",
        color="Escenario",
        title="Comparacion del VaR entre escenarios",
        template="plotly_dark"
    )

    fig_scenarios.update_layout(
    paper_bgcolor="#0B1120",
    plot_bgcolor="#111C30",
    font_color="#E2E8F0",
    title_font_color="#F8FAFC",
    legend_title_font_color="#E2E8F0"
)

    st.plotly_chart(
        fig_scenarios,
        use_container_width=True
    )

    st.info(
        "La prima se mantiene calculada con la mortalidad "
        "original. Se analiza el impacto de desviaciones "
        "en la mortalidad experimentada."
    )
        # ==========================================
    # MATHEMATICAL LAB
    # CENTRO DE DEMOSTRACION ACTUARIAL
    # ==========================================

    st.markdown("---")

    st.header("MATHEMATICAL LAB")

    st.caption(
        "Centro de analisis, demostracion y validacion "
        "de los fundamentos actuariales."
    )

    # Datos del modelo
    table = load_mortality_table()

    age = params["age"]
    term = params["term"]
    n = params["number_insured"]
    insured = params["sum_insured"]
    interest = params["interest_rate"]

    v = 1 / (1 + interest)

    q_values = [
        float(table.loc[age + k, "qx"])
        for k in range(term)
    ]

    p_values = [1 - q for q in q_values]

    survival_prob = float(np.prod(p_values))
    death_prob = 1 - survival_prob

    # Componentes de prima
    survival = 1.0
    epv_benefit = 0.0
    epv_annuity = 0.0

    for k in range(term):

        qx = q_values[k]

        epv_benefit += (
            insured
            * (v ** (k + 1))
            * survival
            * qx
        )

        epv_annuity += (
            (v ** k) * survival
        )

        survival *= (1 - qx)

    premium_calculated = epv_benefit / epv_annuity

    # Error estandar Monte Carlo
    standard_error = (
        metrics["standard_deviation"]
        / np.sqrt(len(losses))
    )

    confidence_low = (
        metrics["expected_loss"]
        - 1.96 * standard_error
    )

    confidence_high = (
        metrics["expected_loss"]
        + 1.96 * standard_error
    )

    # ==========================================
    # MODULO 1: MORTALIDAD
    # ==========================================

    with st.expander(
        "01 | PROBABILIDAD DE MORTALIDAD Y SUPERVIVENCIA",
        expanded=True
    ):

        st.subheader("Fundamento matematico")

        st.latex(r"p_x = 1-q_x")

        st.write(
            "Donde qx representa la probabilidad de fallecimiento "
            "entre las edades x y x+1, mientras que px representa "
            "la probabilidad de sobrevivir ese periodo."
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "Probabilidad anual de fallecimiento",
            f"{q_values[0]:.4%}"
        )

        col2.metric(
            "Probabilidad anual de supervivencia",
            f"{p_values[0]:.4%}"
        )

        st.markdown("**Sustitucion numerica:**")

        st.latex(
            rf"p_{{{age}}}=1-({q_values[0]:.6f})"
        )

        st.latex(
            rf"p_{{{age}}}={p_values[0]:.6f}"
        )

        st.write(
            "La probabilidad de supervivencia se obtiene "
            "como complemento de la mortalidad."
        )

    # ==========================================
    # MODULO 2: SUPERVIVENCIA ACUMULADA
    # ==========================================

    with st.expander(
        "02 | PROBABILIDAD ACUMULADA DE SUPERVIVENCIA"
    ):

        st.subheader("Probabilidad de sobrevivir n años")

        st.latex(
            r"{}_np_x = \prod_{k=0}^{n-1}p_{x+k}"
        )

        st.write(
            "La supervivencia acumulada se obtiene multiplicando "
            "las probabilidades anuales de supervivencia."
        )

        st.latex(
            r"{}_{" + str(term) + r"}p_{" + str(age) + r"}"
            + r"=\prod_{k=0}^{" + str(term - 1)
            + r"}p_{" + str(age) + r"+k}"
        )

        st.metric(
            f"Supervivencia a {term} años",
            f"{survival_prob:.4%}"
        )

        st.metric(
            f"Fallecimiento acumulado a {term} años",
            f"{death_prob:.4%}"
        )

        st.write(
            "Interpretacion: bajo la tabla de mortalidad utilizada, "
            "esta es la probabilidad de que una persona de la edad "
            "analizada sobreviva todo el plazo."
        )

    # ==========================================
    # MODULO 3: PRIMA PURA
    # ==========================================

    with st.expander(
        "03 | CALCULO DE PRIMA PURA"
    ):

        st.subheader("Principio de equivalencia actuarial")

        st.latex(
            r"P=\frac{VP(\text{Beneficios})}"
            r"{VP(\text{Unidad de primas})}"
        )

        st.write(
            "La prima pura nivelada se determina igualando "
            "el valor presente esperado de las primas con "
            "el valor presente esperado de las indemnizaciones."
        )

        st.markdown("**Valor presente de beneficios:**")

        st.latex(
            r"EPV(B)=S\sum_{k=0}^{n-1}"
            r"v^{k+1}\,{}_kp_x\,q_{x+k}"
        )

        st.markdown("**Factor de primas:**")

        st.latex(
            r"\ddot a_{x:\overline n|}"
            r"=\sum_{k=0}^{n-1}v^k\,{}_kp_x"
        )

        st.markdown("**Datos utilizados:**")

        st.write(f"- Edad inicial: {age} años")
        st.write(f"- Duracion: {term} años")
        st.write(f"- Suma asegurada: ${insured:,.2f}")
        st.write(f"- Tasa de interes: {interest:.2%}")

        st.markdown("**Sustitucion de resultados:**")

        st.write(
            f"Valor presente esperado de beneficios: "
            f"${epv_benefit:,.2f}"
        )

        st.write(
            f"Factor de valor presente de primas: "
            f"{epv_annuity:.6f}"
        )

        st.latex(
            rf"P=\frac{{{epv_benefit:,.2f}}}"
            rf"{{{epv_annuity:.6f}}}"
        )

        st.metric(
            "PRIMA PURA ANUAL",
            f"${premium_calculated:,.2f}"
        )

        st.success(
            "La prima se calcula bajo el principio "
            "de equivalencia actuarial."
        )

    # ==========================================
    # MODULO 4: VALOR PRESENTE
    # ==========================================

    with st.expander(
        "04 | MATEMATICA FINANCIERA Y VALOR PRESENTE"
    ):

        st.subheader("Descuento de flujos futuros")

        st.latex(
            r"VP=\frac{C_t}{(1+i)^t}"
        )

        st.write(
            "El valor presente permite expresar una cantidad "
            "futura en unidades monetarias actuales."
        )

        discount_factor = v ** term

        st.write(f"- Capital futuro de referencia: ${insured:,.2f}")
        st.write(f"- Tasa de descuento: {interest:.2%}")
        st.write(f"- Periodo: {term} años")

        st.latex(
            rf"VP=\frac{{{insured:,.2f}}}"
            rf"{{(1+{interest:.4f})^{{{term}}}}}"
        )

        st.metric(
            "Factor de descuento",
            f"{discount_factor:.6f}"
        )

        st.metric(
            "Valor presente",
            f"${insured * discount_factor:,.2f}"
        )

    # ==========================================
    # MODULO 5: MONTE CARLO
    # ==========================================

    with st.expander(
        "05 | SIMULACION ESTOCASTICA MONTE CARLO"
    ):

        st.subheader("Fundamento probabilistico")

        st.latex(
            r"\widehat{E[S]}="
            r"\frac{1}{N}\sum_{j=1}^{N}S_j"
        )

        st.write(
            "El metodo Monte Carlo utiliza numeros aleatorios "
            "para generar multiples escenarios posibles y "
            "estimar el comportamiento de las perdidas."
        )

        st.markdown("**Parametros de simulacion:**")

        st.write(f"- Asegurados: {n:,}")
        st.write(f"- Simulaciones: {len(losses):,}")
        st.write(f"- Plazo: {term} años")
        st.write(f"- Suma asegurada: ${insured:,.2f}")

        st.markdown("**Resultados estadisticos:**")

        st.latex(
            r"SE(\bar S)=\frac{s}{\sqrt{N}}"
        )

        st.metric(
            "Perdida promedio simulada",
            f"${metrics['expected_loss']:,.2f}"
        )

        st.metric(
            "Error estandar",
            f"${standard_error:,.2f}"
        )

        st.markdown("**Intervalo de confianza del 95 %:**")

        st.latex(
            r"\bar S\pm1.96\frac{s}{\sqrt{N}}"
        )

        st.write(
            f"Limite inferior: ${confidence_low:,.2f}"
        )

        st.write(
            f"Limite superior: ${confidence_high:,.2f}"
        )

        if confidence_low <= 0 <= confidence_high:

            st.success(
                "El intervalo contiene cero. "
                "El resultado es consistente con el "
                "principio de equivalencia actuarial."
            )

        else:

            st.warning(
                "El intervalo no contiene cero. "
                "Se recomienda revisar la consistencia "
                "del modelo y sus supuestos."
            )

    # ==========================================
    # MODULO 6: RIESGO FINANCIERO
    # ==========================================

    with st.expander(
        "06 | MEDICION DE RIESGO Y SOLVENCIA"
    ):

        st.subheader("Valor en riesgo (VaR)")

        st.latex(
            r"VaR_{95\%}(S)=Q_{0.95}(S)"
        )
        st.write(
            "El VaR identifica el percentil 95 de la "
            "distribucion de perdidas."
        )

        st.metric(
            "VaR 95%",
            f"${metrics['var_95']:,.2f}"
        )

        st.markdown("**Perdida esperada en la cola (TVaR):**")

        st.latex(
            r"TVaR_{95\%}=E[S\mid S\geq VaR_{95\%}]"
        )

        st.metric(
            "TVaR 95%",
            f"${metrics['tvar_95']:,.2f}"
        )

        st.markdown("**Probabilidad de insolvencia:**")

        st.latex(
            r"P(S>K)"
        )

        st.write(
            f"Capital disponible: ${params['capital']:,.2f}"
        )

        st.metric(
            "Probabilidad de exceder el capital",
            f"{metrics['insolvency_probability']:.2%}"
        )

        st.write(
            "Esta medida representa la frecuencia de escenarios "
            "en los que las perdidas netas superan el capital "
            "inicial disponible."
        )

    # ==========================================
    # RESUMEN FINAL
    # ==========================================

    st.markdown("---")

    st.header("Resumen de resultados actuariales")

    summary = {
        "Edad": age,
        "Plazo": term,
        "Asegurados": n,
        "Suma asegurada": f"${insured:,.2f}",
        "Prima pura": f"${premium_calculated:,.2f}",
        "Supervivencia acumulada": f"{survival_prob:.4%}",
        "VaR 95%": f"${metrics['var_95']:,.2f}",
        "TVaR 95%": f"${metrics['tvar_95']:,.2f}",
        "Riesgo de insolvencia": f"{metrics['insolvency_probability']:.2%}"
    }

    st.json(summary)

    st.success(
        "ACTUARIAL RISK LAB: analisis matematico completado."
    )