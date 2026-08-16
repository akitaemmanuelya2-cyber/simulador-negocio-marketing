import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Simulador de Negocio y Marketing",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Simulador de Negocio y Marketing")
st.write(
    "Explora escenarios de precios, costos y presupuesto de marketing "
    "para estimar su impacto en ventas y ganancias."
)


# ============================================================
# FUNCIONES DEL MODELO
# ============================================================

def optimizar_marketing(presupuesto_total):
    """
    Distribuye el presupuesto entre Instagram, Facebook,
    TikTok y Google Ads.

    Los porcentajes y ROI corresponden a los supuestos
    del prototipo original.
    """

    if presupuesto_total <= 0:
        return 0, 0, 0, 0, 0

    inversion_instagram = presupuesto_total * 0.40
    inversion_facebook = presupuesto_total * 0.30
    inversion_tiktok = presupuesto_total * 0.20
    inversion_google = presupuesto_total * 0.10

    clientes_ig = (inversion_instagram * 3.5) / 4
    clientes_fb = (inversion_facebook * 3.0) / 4
    clientes_tk = (inversion_tiktok * 2.5) / 4
    clientes_gg = (inversion_google * 2.0) / 4

    total_clientes_nuevos = int(
        clientes_ig
        + clientes_fb
        + clientes_tk
        + clientes_gg
    )

    return (
        inversion_instagram,
        inversion_facebook,
        inversion_tiktok,
        inversion_google,
        total_clientes_nuevos
    )


def simular_escenario_negocio(
    df_original,
    cambio_precio_porcentaje,
    presupuesto_marketing,
    cantidad_promedio=None,
    costo_porcentaje=70
):
    """
    Calcula ventas y ganancias históricas y simuladas.

    Si el CSV contiene Quantity, utiliza sus datos.
    Si no contiene Quantity, utiliza el promedio
    introducido por el usuario.
    """

    df_simulado = df_original.copy()

    # 1. Calculamos el costo del proveedor
    df_simulado["Costo_Proveedor"] = (
        df_simulado["Sales"]
        * (costo_porcentaje / 100)
    )

    # 2. Calculamos la ganancia neta histórica
    df_simulado["Ganancia_Neta"] = (
        df_simulado["Sales"]
        - df_simulado["Costo_Proveedor"]
    )

    # 3. Aplicamos el cambio de precio
    factor_precio = 1 + (
        cambio_precio_porcentaje / 100
    )

    df_simulado["Nuevas_Ventas"] = (
        df_simulado["Sales"]
        * factor_precio
    )

    # 4. Aplicamos la elasticidad
    factor_cantidad = 1 - (
        cambio_precio_porcentaje / 100 * 0.5
    )

    # Si Quantity existe, usamos los datos reales.
    # Si no existe, usamos el promedio proporcionado.
    if "Quantity" in df_simulado.columns:
        df_simulado["Cantidad_Base"] = (
            df_simulado["Quantity"]
        )
    else:
        df_simulado["Cantidad_Base"] = (
            cantidad_promedio
        )

    df_simulado["Nueva_Cantidad"] = (
        df_simulado["Cantidad_Base"]
        * factor_cantidad
    )

    # 5. Calculamos el impacto del marketing
    (
        _,
        _,
        _,
        _,
        clientes_nuevos
    ) = optimizar_marketing(
        presupuesto_marketing
    )

    unidades_extra_marketing = (
        clientes_nuevos * 1.5
    )

    # 6. Métricas históricas
    ventas_totales_historicas = (
        df_simulado["Sales"].sum()
    )

    ganancia_total_historica = (
        df_simulado["Ganancia_Neta"].sum()
    )

    # 7. Métricas proyectadas
    promedio_cantidad = (
        df_simulado["Cantidad_Base"].mean()
    )

    if promedio_cantidad <= 0:
        raise ValueError(
            "La cantidad promedio debe ser mayor que cero."
        )

    precio_promedio_unidad = (
        df_simulado["Sales"].mean()
        / promedio_cantidad
    )

    ventas_totales_simuladas = (
        (
            df_simulado["Nuevas_Ventas"]
            * factor_cantidad
        ).sum()
        + (
            unidades_extra_marketing
            * precio_promedio_unidad
        )
    )

    nuevos_costos_proveedor = (
        df_simulado["Costo_Proveedor"]
        * factor_cantidad
    ).sum()

    # Ganancia =
    # Ventas - Costos - Publicidad
    ganancia_total_simulada = (
        ventas_totales_simuladas
        - nuevos_costos_proveedor
        - presupuesto_marketing
    )

    return (
        ventas_totales_historicas,
        ganancia_total_historica,
        ventas_totales_simuladas,
        ganancia_total_simulada
    )


# ============================================================
# GRÁFICO DE MARKETING
# ============================================================

def crear_grafico_marketing(
    ig,
    fb,
    tk,
    gg
):
    datos_mkt = {
        "Red Social": [
            "Instagram",
            "Facebook",
            "TikTok",
            "Google Ads"
        ],
        "Inversión Recomendada ($)": [
            ig,
            fb,
            tk,
            gg
        ]
    }

    fig = px.bar(
        datos_mkt,
        x="Red Social",
        y="Inversión Recomendada ($)",
        text="Inversión Recomendada ($)",
        title=(
            "Distribución sugerida de tu "
            "presupuesto de marketing"
        ),
        color="Red Social",
        color_discrete_map={
            "Instagram": "#E1306C",
            "Facebook": "#1877F2",
            "TikTok": "#000000",
            "Google Ads": "#4285F4"
        }
    )

    fig.update_traces(
        texttemplate="$%{text:.2f}",
        textposition="outside"
    )

    fig.update_layout(
        showlegend=False,
        yaxis_title="Dinero a invertir ($)",
        xaxis_title=""
    )

    return fig


# ============================================================
# GRÁFICO COMPARATIVO
# ============================================================

def crear_grafico_comparacion(
    v_hist,
    g_hist,
    v_sim,
    g_sim
):
    fig = go.Figure(
        data=[
            go.Bar(
                name="Histórico (Pasado)",
                x=[
                    "Ventas Totales",
                    "Ganancia Neta"
                ],
                y=[
                    v_hist,
                    g_hist
                ],
                marker_color="#636EFA"
            ),
            go.Bar(
                name="Simulado (Futuro)",
                x=[
                    "Ventas Totales",
                    "Ganancia Neta"
                ],
                y=[
                    v_sim,
                    g_sim
                ],
                marker_color="#00CC96"
            )
        ]
    )

    fig.update_layout(
        title="Comparativa de impacto financiero",
        barmode="group",
        yaxis_title="Monto en dinero ($)",
        legend_title="Escenarios"
    )

    fig.update_traces(
        texttemplate="$%{y:,.2f}",
        textposition="outside"
    )

    return fig


# ============================================================
# ENTRADA DE DATOS
# ============================================================

st.header("1. Ingresa los datos de tu negocio")

# ============================================================
# SELECCIÓN DE MONEDA
# ============================================================

monedas = {
    "🇨🇴 COP - Peso colombiano": {
        "codigo": "COP",
        "simbolo": "$",
        "decimales": 0
    },
    "🇺🇸 USD - Dólar estadounidense": {
        "codigo": "USD",
        "simbolo": "$",
        "decimales": 2
    },
    "🇪🇺 EUR - Euro": {
        "codigo": "EUR",
        "simbolo": "€",
        "decimales": 2
    }
}

moneda_seleccionada = st.selectbox(
    "¿En qué moneda quieres trabajar?",
    list(monedas.keys())
)

moneda = monedas[moneda_seleccionada]

codigo_moneda = moneda["codigo"]
simbolo_moneda = moneda["simbolo"]
decimales_moneda = moneda["decimales"]

def formatear_dinero(valor):
    if decimales_moneda == 0:
        return f"{simbolo_moneda} {valor:,.0f} {codigo_moneda}"
    else:
        return f"{simbolo_moneda} {valor:,.2f} {codigo_moneda}"

st.caption(
    f"Todos los valores de esta simulación "
    f"se mostrarán en {codigo_moneda}."
)

modo_datos = st.radio(
    "¿Cómo quieres trabajar?",
    [
        "Tengo un CSV",
        "No tengo un CSV, quiero introducir estimaciones"
    ],
    horizontal=True
)

df = None
cantidad_promedio = None


# ============================================================
# OPCIÓN A: USUARIO CON CSV
# ============================================================

if modo_datos == "Tengo un CSV":

    archivo = st.file_uploader(
        "Sube tu archivo CSV",
        type=["csv"],
        help=(
            "El archivo debe contener una columna "
            "de ventas. Quantity es opcional."
        )
    )

    if archivo is not None:

        try:

            df = pd.read_csv(archivo)

            st.success(
                f"Archivo cargado correctamente: "
                f"{len(df):,} registros."
            )

            st.subheader("Columnas encontradas")

            st.write(
                df.columns.tolist()
            )

            # Buscamos Sales de forma flexible
            columna_sales = next(
                (
                    col
                    for col in df.columns
                    if str(col).strip().lower()
                    == "sales"
                ),
                None
            )

            if columna_sales is None:

                st.error(
                    "No encontramos una columna llamada "
                    "'Sales'. Por ahora necesitamos una "
                    "columna de ventas."
                )

                df = None

            else:

                if columna_sales != "Sales":

                    df = df.rename(
                        columns={
                            columna_sales: "Sales"
                        }
                    )

                # Buscamos Quantity
                columna_quantity = next(
                    (
                        col
                        for col in df.columns
                        if str(col).strip().lower()
                        == "quantity"
                    ),
                    None
                )

                if columna_quantity is not None:

                    if columna_quantity != "Quantity":

                        df = df.rename(
                            columns={
                                columna_quantity: "Quantity"
                            }
                        )

                    st.success(
                        "✓ Quantity encontrada. "
                        "Utilizaremos los datos "
                        "proporcionados en el archivo."
                    )

                else:

                    st.warning(
                        "⚠ Quantity no fue proporcionada."
                    )

                    st.info(
                        "No pasa nada. Introduce una "
                        "cantidad promedio por registro "
                        "y nosotros hacemos el resto."
                    )

                    cantidad_promedio = (
                        st.number_input(
                            "Cantidad promedio por registro",
                            min_value=0.01,
                            value=3.0,
                            step=1.0
                        )
                    )

        except Exception as error:

            st.error(
                f"No pudimos leer el archivo. "
                f"Detalle: {error}"
            )

            df = None


# ============================================================
# OPCIÓN B: USUARIO SIN CSV
# ============================================================

else:

    st.info(
        "¿No tienes un CSV? No pasa nada. "
        "Introduce algunos valores estimados "
        "y nosotros hacemos el resto. 💡"
    )

    ventas_estimadas = st.number_input(
        "Ventas históricas totales",
        min_value=0.01,
        value=10000.0,
        step=100.0
    )

    cantidad_promedio = st.number_input(
        "Cantidad promedio por registro",
        min_value=0.01,
        value=3.0,
        step=1.0
    )

    df = pd.DataFrame(
        {
            "Sales": [
                ventas_estimadas
            ],
            "Quantity": [
                cantidad_promedio
            ]
        }
    )


# ============================================================
# LIMPIEZA Y VALIDACIÓN
# ============================================================

if df is not None:

    # Convertimos Sales a número
    if "Sales" in df.columns:

        df["Sales"] = pd.to_numeric(
            df["Sales"],
            errors="coerce"
        )

    # Convertimos Quantity a número
    if "Quantity" in df.columns:

        df["Quantity"] = pd.to_numeric(
            df["Quantity"],
            errors="coerce"
        )

    # Procesamos fecha solamente si existe
    if "Order Date" in df.columns:

        df["Order Date"] = pd.to_datetime(
            df["Order Date"],
            errors="coerce",
            dayfirst=True
        )

    filas_antes = len(df)

    # Eliminamos ventas inválidas
    df = df.dropna(
        subset=["Sales"]
    )

    df = df[
        df["Sales"] > 0
    ]

    filas_eliminadas = (
        filas_antes - len(df)
    )

    if filas_eliminadas > 0:

        st.info(
            f"Se eliminaron "
            f"{filas_eliminadas:,} registros "
            "sin ventas válidas o con ventas "
            "menores o iguales a cero."
        )

    if df.empty:

        st.error(
            "No quedaron registros válidos "
            "para realizar el análisis."
        )

        st.stop()

    # Validamos Quantity si existe
    if "Quantity" in df.columns:

        df = df.dropna(
            subset=["Quantity"]
        )

        df = df[
            df["Quantity"] > 0
        ]

    # Si no existe Quantity, usamos promedio
    if "Quantity" not in df.columns:

        if cantidad_promedio is None:

            cantidad_promedio = (
                st.number_input(
                    "Cantidad promedio por registro",
                    min_value=0.01,
                    value=3.0,
                    step=1.0
                )
            )

    else:

        cantidad_promedio = float(
            df["Quantity"].mean()
        )


    # ========================================================
    # PARÁMETROS DEL ESCENARIO
    # ========================================================

    st.header(
        "2. Diseña tu escenario"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        cambio_precio = st.number_input(
            "Cambio de precio (%)",
            min_value=-90.0,
            max_value=100.0,
            value=5.0,
            step=1.0,
            help=(
                "Ejemplo: 5 significa aumentar "
                "el precio un 5%. -10 significa "
                "reducirlo un 10%."
            )
        )

    with col2:

        presupuesto_marketing = st.number_input(
            "Presupuesto de marketing",
            min_value=0.0,
            value=50.0,
            step=10.0
        )

    with col3:

        costo_porcentaje = st.number_input(
            "Costo del proveedor (%)",
            min_value=0.0,
            max_value=100.0,
            value=70.0,
            step=1.0,
            help=(
                "Porcentaje de las ventas "
                "destinado al costo del proveedor."
            )
        )

    st.divider()


    # ========================================================
    # SIMULACIÓN
    # ========================================================

    try:

        (
            ventas_historicas,
            ganancia_historica,
            ventas_simuladas,
            ganancia_simulada
        ) = simular_escenario_negocio(
            df,
            cambio_precio,
            presupuesto_marketing,
            cantidad_promedio=cantidad_promedio,
            costo_porcentaje=costo_porcentaje
        )

    except ValueError as error:

        st.error(
            str(error)
        )

        st.stop()


    # ========================================================
    # RESULTADOS
    # ========================================================

    st.header(
        "3. Resultados"
    )

    diferencia_ventas = (
        ventas_simuladas
        - ventas_historicas
    )

    diferencia_ganancia = (
        ganancia_simulada
        - ganancia_historica
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    with col1:

        st.metric(
    "Ventas históricas",
    formatear_dinero(ventas_historicas)
       )

    with col2:

        st.metric(
    "Ventas simuladas",
    formatear_dinero(ventas_simuladas),
    formatear_dinero(diferencia_ventas)
)

    with col3:

        st.metric(
    "Ganancia histórica",
    formatear_dinero(ganancia_historica)
)

    with col4:

        st.metric(
    "Ganancia simulada",
    formatear_dinero(ganancia_simulada),
    f"${diferencia_ganancia:,.2f}"
)


    # ========================================================
    # RECOMENDACIÓN DE MARKETING
    # ========================================================

    st.header(
        "4. Recomendación de inversión en marketing"
    )

    (
        inversion_instagram,
        inversion_facebook,
        inversion_tiktok,
        inversion_google,
        clientes_nuevos
    ) = optimizar_marketing(
        presupuesto_marketing
    )

    col1, col2 = st.columns(
        [2, 1]
    )

    with col1:

        st.plotly_chart(
            crear_grafico_marketing(
                inversion_instagram,
                inversion_facebook,
                inversion_tiktok,
                inversion_google
            ),
            use_container_width=True
        )

    with col2:

        st.metric(
            "Clientes nuevos estimados",
            f"{clientes_nuevos:,}"
        )

        st.write(
            "### Distribución recomendada"
        )

        st.write(
            f"📸 Instagram: "
            f"**${inversion_instagram:,.2f}**"
        )

        st.write(
            f"📘 Facebook: "
            f"**${inversion_facebook:,.2f}**"
        )

        st.write(
            f"🎵 TikTok: "
            f"**${inversion_tiktok:,.2f}**"
        )

        st.write(
            f"🔎 Google Ads: "
            f"**${inversion_google:,.2f}**"
        )


    # ========================================================
    # COMPARACIÓN FINANCIERA
    # ========================================================

    st.header(
        "5. Impacto financiero"
    )

    st.plotly_chart(
        crear_grafico_comparacion(
            ventas_historicas,
            ganancia_historica,
            ventas_simuladas,
            ganancia_simulada
        ),
        use_container_width=True
    )


    # ========================================================
    # DATOS UTILIZADOS
    # ========================================================

    with st.expander(
        "Ver datos utilizados en el análisis"
    ):

        st.dataframe(
            df.head(100),
            use_container_width=True
        )

    st.caption(
        "Nota: las recomendaciones de marketing "
        "utilizan los supuestos de ROI, distribución "
        "del presupuesto y CAC definidos en el "
        "prototipo original. Son estimaciones, "
        "no resultados garantizados."
    )
