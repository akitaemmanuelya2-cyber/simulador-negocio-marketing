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
# FUNCIONES DEL MODELO (CORREGIDAS Y SIMPLIFICADAS)
# ============================================================

def optimizar_marketing(presupuesto_total, precio_producto):
    """
    Distribuye el presupuesto en redes y calcula cuántos 
    clientes nuevos trae según el valor del producto.
    """
    if presupuesto_total <= 0 or precio_producto <= 0:
        return 0, 0, 0, 0, 0

    # 1. Repartimos el dinero en canales
    inversion_ig = presupuesto_total * 0.40  # 40% Instagram
    inversion_fb = presupuesto_total * 0.30  # 30% Facebook
    inversion_tk = presupuesto_total * 0.20  # 20% TikTok
    inversion_gg = presupuesto_total * 0.10  # 10% Google

    # 2. Estimamos cuánto cuesta conseguir 1 cliente (CAC)
    # Asumimos que traer 1 cliente cuesta el 20% del valor de tu producto (mínimo 1,000)
    costo_por_cliente = max(precio_producto * 0.20, 1000.0)

    # 3. Clientes nuevos totales que trae la publicidad
    total_clientes_nuevos = int(presupuesto_total / costo_por_cliente)

    return (
        inversion_ig,
        inversion_fb,
        inversion_tk,
        inversion_gg,
        total_clientes_nuevos
    )


def simular_escenario_negocio(
    df_original,
    cambio_precio_porcentaje,
    presupuesto_marketing,
    nuevo_precio_unitario,
    costo_unitario
):
    """
    Calcula las ventas y ganancias reales basándose en el costo unitario en moneda real.
    """
    df_simulado = df_original.copy()

    # 1. Ventas e Ingresos Históricos
    ventas_totales_historicas = df_simulado["Sales"].sum()
    unidades_historicas_totales = df_simulado["Quantity"].sum()

    # Costo total histórico del proveedor
    costos_historicos = unidades_historicas_totales * costo_unitario
    ganancia_total_historica = ventas_totales_historicas - costos_historicos

    # 2. Impacto del Cambio de Precio
    cambio_demanda_porcentaje = (cambio_precio_porcentaje * -0.5) / 100
    factor_demanda = max(0.0, 1 + cambio_demanda_porcentaje)
    unidades_base_simuladas = unidades_historicas_totales * factor_demanda

    # 3. Clientes extra por Marketing
    _, _, _, _, clientes_nuevos_mkt = optimizar_marketing(
        presupuesto_marketing, 
        nuevo_precio_unitario
    )

    # 4. Total de unidades simuladas
    unidades_totales_simuladas = unidades_base_simuladas + clientes_nuevos_mkt

    # 5. Métricas proyectadas
    ventas_totales_simuladas = unidades_totales_simuladas * nuevo_precio_unitario
    costo_proveedor_simulado = unidades_totales_simuladas * costo_unitario

    # Ganancia = Ventas - Costo de Fabricación/Proveedor - Publicidad
    ganancia_total_simulada = (
        ventas_totales_simuladas 
        - costo_proveedor_simulado 
        - presupuesto_marketing
    )

    return (
        ventas_totales_historicas,
        ganancia_total_historica,
        ventas_totales_simuladas,
        ganancia_total_simulada,
        costos_historicos,
        costo_proveedor_simulado
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
        "Tengo una base de datos (CSV)",
        "No tengo una base de datos (CSV), quiero introducir estimaciones"
    ],
    horizontal=True
)

df = None
cantidad_promedio = None


# ============================================================
# OPCIÓN A: USUARIO CON CSV
# ============================================================

if modo_datos == "Tengo una base de datos (CSV)":

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
        "¿No tienes una base de datos? No pasa nada. "
        "Ingresa los datos generales de tu negocio y calculamos el resto. 💡"
    )

    col_man1, col_man2 = st.columns(2)

    with col_man1:
        unidades_vendidas = st.number_input(
            "Cantidad de productos o unidades vendidas.",
            min_value=1,
            value=80,
            step=1,
            help="Ejemplo: Si vendiste 80 camisetas en el mes, ingresa 80."
        )

    with col_man2:
        precio_actual_manual = st.number_input(
            f"Precio de venta actual por unidad ({codigo_moneda})",
            min_value=0.0,
            value=50000.0,
            step=1000.0,
            format="%.0f"
        )

    # Calculamos las ventas históricas reales (Unidades x Precio)
    ventas_estimadas = unidades_vendidas * precio_actual_manual
    cantidad_promedio = 1.0  # Cada fila representa 1 unidad o la transacción total unificada

    st.success(
        f"💡 **Ventas históricas estimadas:** {formatear_dinero(ventas_estimadas)} "
        f"({unidades_vendidas:,} unidades a {formatear_dinero(precio_actual_manual)} c/u)"
    )

    df = pd.DataFrame(
        {
            "Sales": [ventas_estimadas],
            "Quantity": [unidades_vendidas]
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
    # 2. PARÁMETROS DEL ESCENARIO
    # ========================================================

    st.header("2. Diseña tu escenario")

    unidades_totales = df["Quantity"].sum()
    if unidades_totales > 0:
        precio_actual_calculado = float(df["Sales"].sum() / unidades_totales)
    else:
        precio_actual_calculado = 50000.0

    col1, col2, col3 = st.columns(3)

    with col1:
        nuevo_precio = st.number_input(
            f"Nuevo precio propuesto ({codigo_moneda})",
            min_value=0.0,
            value=float(precio_actual_calculado * 1.05),
            step=1000.0,
            format="%.0f",
            help=f"Precio actual registrado: {formatear_dinero(precio_actual_calculado)}"
        )

        if precio_actual_calculado > 0:
            cambio_precio = ((nuevo_precio - precio_actual_calculado) / precio_actual_calculado) * 100
        else:
            cambio_precio = 0.0

        st.caption(f"Precio actual: **{formatear_dinero(precio_actual_calculado)}** ({cambio_precio:+.1f}%)")

    with col2:
        presupuesto_marketing = st.number_input(
            f"Presupuesto para publicidad o marketing ({codigo_moneda})",
            min_value=0.0,
            value=50000.0,
            step=10000.0,
            format="%.0f",
            help="¿Cuánto quiero invertir en publicidad?"
        )

    with col3:
        costo_unitario = st.number_input(
            f"Costo por unidad / proveedor ({codigo_moneda})",
            min_value=0.0,
            value=float(precio_actual_calculado * 0.40),
            step=1000.0,
            format="%.0f",
            help="¿Cuánto te cuesta comprar o fabricar cada producto?"
        )

        porcentaje_equiv = (costo_unitario / nuevo_precio * 100) if nuevo_precio > 0 else 0
        st.caption(f"Equivale al **{porcentaje_equiv:.1f}%** del nuevo precio")

    st.divider()

    # ========================================================
    # SIMULACIÓN Y RESULTADOS
    # ========================================================

    try:
        (
            ventas_historicas,
            ganancia_historica,
            ventas_simuladas,
            ganancia_simulada,
            costos_historicos,
            costos_simulados
        ) = simular_escenario_negocio(
            df,
            cambio_precio,
            presupuesto_marketing,
            nuevo_precio_unitario=nuevo_precio,
            costo_unitario=costo_unitario
        )

        # Limpiamos espacios para que el Markdown de Streamlit aplique la negrita correctamente
        texto_antes = formatear_dinero(costos_historicos).strip()
        texto_despues = formatear_dinero(costos_simulados).strip()

        st.info(
            f"📦 **Inversión en Proveedores o Elaboración:** "
            f"**Antes: {texto_antes} ➔ Después: {texto_despues}**"
        )
        # Calculamos diferencias
        diferencia_ventas = ventas_simuladas - ventas_historicas
        diferencia_ganancia = ganancia_simulada - ganancia_historica

        st.header("3. Resultados")

        col_res1, col_res2, col_res3, col_res4 = st.columns(4)

        with col_res1:
            st.metric("Ventas históricas", formatear_dinero(ventas_historicas))

        with col_res2:
            st.metric("Ventas simuladas", formatear_dinero(ventas_simuladas), formatear_dinero(diferencia_ventas))

        with col_res3:
            st.metric("Ganancia histórica", formatear_dinero(ganancia_historica))

        with col_res4:
            st.metric("Ganancia simulada", formatear_dinero(ganancia_simulada), formatear_dinero(diferencia_ganancia))

    except Exception as error:
        st.error(f"Ocurrió un inconveniente al simular los datos: {error}")

    # ========================================================
    # 4. RECOMENDACIÓN DE INVERSIÓN EN MARKETING
    # ========================================================

    st.header("4. Recomendación de inversión en publicidad o marketing")

    # 1. Calculamos la distribución sugerida
    (
        inversion_ig,
        inversion_fb,
        inversion_tk,
        inversion_gg,
        clientes_nuevos
    ) = optimizar_marketing(presupuesto_marketing, nuevo_precio)

    if presupuesto_marketing > 0:
        st.write(
            f"Basado en un presupuesto de **{formatear_dinero(presupuesto_marketing)}**, "
            f"esta es la distribución estratégica sugerida para tus campañas:"
        )

        # Columna 1: Gráfico visual | Columna 2: Tabla de datos | Columna 3: Resultado de Clientes
        col_grafico, col_tabla, col_metrica = st.columns([1.2, 1.2, 1])

        with col_grafico:
            import plotly.graph_objects as go

            canales = ["Instagram Ads", "Facebook Ads", "TikTok Ads", "Google Search"]
            valores = [inversion_ig, inversion_fb, inversion_tk, inversion_gg]
            colores = ["#E1306C", "#1877F2", "#00F2FE", "#EA4335"]  # Colores representativos de las marcas

            fig = go.Figure(data=[go.Pie(
                labels=canales,
                values=valores,
                hole=0.5, # Hace que sea un gráfico de dona elegante
                marker_colors=colores,
                textinfo="percent",
                hoverinfo="label+value",
            )])

            fig.update_layout(
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                margin=dict(l=10, r=10, t=10, b=10),
                height=240,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white")
            )

            st.plotly_chart(fig, use_container_width=True)

        with col_tabla:
            datos_canales = {
                "Canal": ["Instagram Ads", "Facebook Ads", "TikTok Ads", "Google Search"],
                "Inversión": [
                    formatear_dinero(inversion_ig),
                    formatear_dinero(inversion_fb),
                    formatear_dinero(inversion_tk),
                    formatear_dinero(inversion_gg)
                ]
            }
            st.table(datos_canales)

        with col_metrica:
            st.metric(
                label="🎯 Clientes nuevos",
                value=f"+{clientes_nuevos}",
                help="Proyección de compradores adicionales estimando un costo por cliente dinámico."
            )

            costo_por_cliente = presupuesto_marketing / clientes_nuevos if clientes_nuevos > 0 else 0
            
            st.success(
                f"💡 **Costo estimado:** Traer 1 cliente te cuesta **{formatear_dinero(costo_por_cliente)}** en publicidad."
            )

    else:
        st.warning("⚠️ Ingresa un presupuesto de marketing mayor a $0 en la Sección 2 para ver la recomendación de inversión.")

    # ========================================================
    # 5. IMPACTO FINANCIERO
    # ========================================================

    st.header("5. Impacto financiero")
    st.write("Comparativa visual entre tu situación actual y el escenario simulado:")

    col_fig1, col_fig2 = st.columns(2)

    with col_fig1:
        # Gráfico 1: Comparativa de Ventas
        fig_ventas = go.Figure(data=[
            go.Bar(
                x=["Ventas Históricas", "Ventas Simuladas"],
                y=[ventas_historicas, ventas_simuladas],
                text=[formatear_dinero(ventas_historicas), formatear_dinero(ventas_simuladas)],
                textposition="auto",
                marker_color=["#4A5568", "#00C853"] # Gris actual vs Verde proyección
            )
        ])

        fig_ventas.update_layout(
            title="📈 Comparativa de Ventas Totales",
            yaxis_title=codigo_moneda,
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )

        st.plotly_chart(fig_ventas, use_container_width=True)

    with col_fig2:
        # Gráfico 2: Comparativa de Ganancia Neta
        fig_ganancia = go.Figure(data=[
            go.Bar(
                x=["Ganancia Histórica", "Ganancia Simulada"],
                y=[ganancia_historica, ganancia_simulada],
                text=[formatear_dinero(ganancia_historica), formatear_dinero(ganancia_simulada)],
                textposition="auto",
                marker_color=["#4A5568", "#29B6F6"] # Gris actual vs Azul proyección
            )
        ])

        fig_ganancia.update_layout(
            title="💰 Comparativa de Ganancia Neta",
            yaxis_title=codigo_moneda,
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )

        st.plotly_chart(fig_ganancia, use_container_width=True)

    # Mensaje de conclusión o veredicto del negocio
    roi_publicidad = ((ganancia_simulada - ganancia_historica) / presupuesto_marketing * 100) if presupuesto_marketing > 0 else 0

    if ganancia_simulada > ganancia_historica:
        st.success(
            f"🚀 **¡Escenario Positivo!** Con esta estrategia estás ganando "
            f"**{formatear_dinero(ganancia_simulada - ganancia_historica)} adicionales**. "
            f"Por cada $100 que inviertes en publicidad, recuperas tu inversión y te quedan **{roi_publicidad:.0f}% de retorno extra**."
        )
    else:
        st.warning(
            "⚠️ **Ojo con los números:** El aumento en costos o publicidad supera el margen generado. "
            "Ajusta el precio o reduce el presupuesto de marketing para asegurar ganancias."
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
