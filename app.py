import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Simulador de Negocio y Marketing",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# FUNCIONES DEL MODELO
# ============================================================

def optimizar_marketing(presupuesto_total, precio_producto):
    if presupuesto_total <= 0 or precio_producto <= 0:
        return 0, 0, 0, 0, 0

    inversion_ig = presupuesto_total * 0.40  
    inversion_fb = presupuesto_total * 0.30  
    inversion_tk = presupuesto_total * 0.20  
    inversion_gg = presupuesto_total * 0.10  

    costo_por_cliente = max(precio_producto * 0.20, 1000.0)
    total_clientes_nuevos = int(presupuesto_total / costo_por_cliente)

    return (inversion_ig, inversion_fb, inversion_tk, inversion_gg, total_clientes_nuevos)

def simular_escenario_negocio(df_original, cambio_precio_porcentaje, presupuesto_marketing, nuevo_precio_unitario, costo_unitario):
    df_simulado = df_original.copy()

    ventas_totales_historicas = df_simulado["Sales"].sum()
    unidades_historicas_totales = df_simulado["Quantity"].sum()
    costos_historicos = unidades_historicas_totales * costo_unitario
    ganancia_total_historica = ventas_totales_historicas - costos_historicos

    cambio_demanda_porcentaje = (cambio_precio_porcentaje * -0.5) / 100
    factor_demanda = max(0.0, 1 + cambio_demanda_porcentaje)
    unidades_base_simuladas = unidades_historicas_totales * factor_demanda

    _, _, _, _, clientes_nuevos_mkt = optimizar_marketing(presupuesto_marketing, nuevo_precio_unitario)
    unidades_totales_simuladas = unidades_base_simuladas + clientes_nuevos_mkt

    ventas_totales_simuladas = unidades_totales_simuladas * nuevo_precio_unitario
    costo_proveedor_simulado = unidades_totales_simuladas * costo_unitario

    ganancia_total_simulada = (ventas_totales_simuladas - costo_proveedor_simulado - presupuesto_marketing)

    return (ventas_totales_historicas, ganancia_total_historica, ventas_totales_simuladas, 
            ganancia_total_simulada, costos_historicos, costo_proveedor_simulado)

# ============================================================
# CONTROL DE NAVEGACIÓN (MEMORIA DE TARS)
# ============================================================
if 'en_simulador' not in st.session_state:
    st.session_state['en_simulador'] = False

def iniciar_simulador():
    st.session_state['en_simulador'] = True

def volver_portada():
    st.session_state['en_simulador'] = False

# ============================================================
# 🏠 PANTALLA 1: LA PORTADA (LOBBY)
# ============================================================
if not st.session_state['en_simulador']:
    st.title("📊 Simulador de Negocio y Marketing")
    st.markdown("### Bienvenido a tu Centro de Mando Estratégico")
    st.write(
        "Antes de arriesgar tu capital en el mundo real, simula tus decisiones aquí. "
        "Audita tu inventario, ajusta tus precios, controla tus costos y planifica "
        "tu inversión publicitaria como un verdadero analista de datos."
    )

    st.divider()

    st.markdown("#### 🚀 ¿Qué puedes hacer en esta plataforma?")

    col_p1, col_p2, col_p3, col_p4 = st.columns(4)

    with col_p1:
        st.info("🎮 **Modo Demo**\n\nJuega con una base de datos precargada y descubre el potencial en segundos.")
    with col_p2:
        st.success("🤝 **Modo Asistido**\n\nSube un archivo básico y usa nuestra tabla inteligente para rellenar costos.")
    with col_p3:
        st.warning("🚀 **Modo Pro Ultra**\n\nConecta tu inventario completo y obtén una radiografía profunda.")
    with col_p4:
        st.error("🎯 **Estrategia MKT**\n\nSimula inversiones en redes sociales y calcula clientes nuevos.")

    st.divider()
    
    st.markdown("<h3 style='text-align: center;'>¿Listo para tomar el control?</h3>", unsafe_allow_html=True)
    st.write("") 
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        st.button("🚀 INGRESAR AL SIMULADOR", on_click=iniciar_simulador, use_container_width=True, type="primary")

# ============================================================
# ⚙️ PANTALLA 2: LA MAQUINARIA (APP PRINCIPAL)
# ============================================================
else:
    st.button("⬅️ Volver a la Portada", on_click=volver_portada)
    st.divider()

    st.header("1. Configuración Inicial de tu Negocio")

    monedas = {
        "🇨🇴 COP - Peso colombiano": {"codigo": "COP", "simbolo": "$", "decimales": 0},
        "🇺🇸 USD - Dólar estadounidense": {"codigo": "USD", "simbolo": "$", "decimales": 2},
        "🇪🇺 EUR - Euro": {"codigo": "EUR", "simbolo": "€", "decimales": 2}
    }

    col_moneda, col_modo = st.columns([1, 2])
    
    with col_moneda:
        moneda_seleccionada = st.selectbox("Selecciona tu moneda", list(monedas.keys()))
        moneda = monedas[moneda_seleccionada]
        codigo_moneda = moneda["codigo"]
        simbolo_moneda = moneda["simbolo"]
        decimales_moneda = moneda["decimales"]

    def formatear_dinero(valor):
        if decimales_moneda == 0:
            return f"{simbolo_moneda} {valor:,.0f} {codigo_moneda}"
        else:
            return f"{simbolo_moneda} {valor:,.2f} {codigo_moneda}"

    with col_modo:
        modo_trabajo = st.radio(
            "¿Cómo quieres empezar hoy?",
            ["Tengo una base de datos (CSV)", "No tengo base de datos (Ingresar manual)"],
            horizontal=True
        )

    st.divider()

    df = None
    cantidad_promedio = None
    nuevo_precio = 0.0
    presupuesto_marketing = 0.0
    costo_unitario = 0.0

    # --------------------------------------------------------
    # OPCIÓN A: CON CSV
    # --------------------------------------------------------
    if modo_trabajo == "Tengo una base de datos (CSV)":
        
        st.markdown("### 💱 Ajuste de Divisa")
        if codigo_moneda != "USD":
            tasa_cambio = st.number_input(
                f"Tasa de cambio actual (¿A cuánto equivale 1 USD en {codigo_moneda}?):",
                min_value=1.0, value=4000.0 if codigo_moneda == "COP" else 1.0, step=50.0
            )
        else:
            tasa_cambio = 1.0

        st.divider()

        tab_demo, tab_asistido, tab_pro, tab_marketing = st.tabs([
            "🎮 Modo Demo", "🤝 Modo Asistido", "🚀 Modo Pro Ultra", "🎯 Estrategia Marketing"
        ])

        with tab_demo:
            st.subheader("🎮 Explora la magia sin subir archivos")
            st.write("Hemos cargado una base de datos de ejemplo (Train CSV) para que veas el potencial al instante.")
            
            try:
                df_demo = pd.read_csv("train.csv") 
                
                mapeo_columnas_demo = {
                    "ventas": "Sales", "Ventas": "Sales", "monto": "Sales", "Monto": "Sales", 
                    "cantidad": "Quantity", "Cantidad": "Quantity", "unidades": "Quantity", "Units": "Quantity",
                    "costo": "Cost", "Costo": "Cost"
                }
                df_demo = df_demo.rename(columns=mapeo_columnas_demo)
                
                if "Sales" in df_demo.columns:
                    df_demo["Sales"] = df_demo["Sales"] * tasa_cambio
                if "Cost" in df_demo.columns:
                    df_demo["Cost"] = df_demo["Cost"] * tasa_cambio
                if "Quantity" not in df_demo.columns:
                    df_demo["Quantity"] = 1.0
                    
                st.success(f"✅ ¡Base Demo cargada! ({len(df_demo):,} registros listos para simular).")
                
                st.markdown("### 🕵️‍♂️ Radiografía de tu Negocio")
                col_prod = "Product Name" if "Product Name" in df_demo.columns else ("Producto" if "Producto" in df_demo.columns else None)
                
                if col_prod:
                    df_agrupado = df_demo.groupby(col_prod).agg(
                        Total_Ventas=("Sales", "sum"), Total_Unidades=("Quantity", "sum")
                    ).reset_index()
                    
                    df_agrupado["Precio_Unitario"] = df_agrupado["Total_Ventas"] / df_agrupado["Total_Unidades"]
                    
                    rey = df_agrupado.loc[df_agrupado["Total_Ventas"].idxmax()]
                    hueso = df_agrupado.loc[df_agrupado["Total_Ventas"].idxmin()]
                    mas_caro = df_agrupado.loc[df_agrupado["Precio_Unitario"].idxmax()]
                    
                    col_det1, col_det2 = st.columns(2)
                    with col_det1:
                        st.info(f"🏆 **El Rey (Más ingresos):**\n\n*{rey[col_prod]}*\n\nGeneró: **{formatear_dinero(rey['Total_Ventas'])}**")
                        st.success(f"💎 **El producto más costoso:**\n\n*{mas_caro[col_prod]}*\n\nPrecio aprox: **{formatear_dinero(mas_caro['Precio_Unitario'])}**")
                    with col_det2:
                        if hueso['Total_Ventas'] == 0:
                            st.warning(f"💀 **El Hueso (Cero ventas):**\n\n*{hueso[col_prod]}*\n\nGeneró: **$ 0 {codigo_moneda}**")
                        else:
                            st.warning(f"💀 **El Hueso (Menos ingresos):**\n\n*{hueso[col_prod]}*\n\nGeneró: **{formatear_dinero(hueso['Total_Ventas'])}**")
                        
                        df_baratos = df_agrupado[df_agrupado["Precio_Unitario"] > 0]
                        if not df_baratos.empty:
                            mas_barato = df_baratos.loc[df_baratos["Precio_Unitario"].idxmin()]
                            st.error(f"🏷️ **El más económico:**\n\n*{mas_barato[col_prod]}*\n\nPrecio aprox: **{formatear_dinero(mas_barato['Precio_Unitario'])}**")
                    
                    st.markdown("### 📊 Tablero de Rendimiento (Volumen)")
                    col_g1, col_g2 = st.columns(2)
                    with col_g1:
                        df_top5 = df_agrupado.sort_values(by="Total_Unidades", ascending=False).head(5)
                        fig_top = px.bar(df_top5, x="Total_Unidades", y=col_prod, orientation='h', title="🏆 Top 5", color_discrete_sequence=["#00C853"])
                        fig_top.update_layout(yaxis={'categoryorder':'total ascending'}, height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
                        st.plotly_chart(fig_top, use_container_width=True)
                        
                    with col_g2:
                        df_bottom5 = df_agrupado.sort_values(by="Total_Unidades", ascending=True).head(5)
                        fig_bottom = px.bar(df_bottom5, x="Total_Unidades", y=col_prod, orientation='h', title="💀 Bottom 5", color_discrete_sequence=["#D32F2F"])
                        fig_bottom.update_layout(yaxis={'categoryorder':'total descending'}, height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
                        if df_bottom5["Total_Unidades"].max() <= 10:
                            fig_bottom.update_xaxes(dtick=1)
                        st.plotly_chart(fig_bottom, use_container_width=True)
                
                st.markdown("### 💡 El Veredicto Estratégico")
                if col_prod and not df_agrupado.empty:
                    st.info(
                        f"👋 **¡Hola, mi amigo emprendedor!** Aquí tu plan táctico:\n\n"
                        f"🚀 Tu producto rey (*{rey[col_prod]}*) es una máquina. Prohibido quedarse sin stock.\n\n"
                        f"💀 Ese *{hueso[col_prod]}* es tu hueso. Liquídalo urgente.\n\n"
                        f"🏷️ Tienes el *{mas_barato[col_prod]}* como producto gancho. Úsalo en publicidad."
                    )
                
                st.divider()
                df = df_demo 

                st.header("🕹️ Simulador en Tiempo Real")
                
                unidades_totales = df["Quantity"].sum()
                precio_actual_calculado = float(df["Sales"].sum() / unidades_totales) if unidades_totales > 0 else 50000.0
                tope_precio = float(precio_actual_calculado * 5) if precio_actual_calculado > 0 else 1000000.0
                paso_slider = 1000.0 if codigo_moneda == "COP" else 1.0

                col_op1, col_op2 = st.columns(2)
                with col_op1:
                    nuevo_precio = st.slider(f"Nuevo precio propuesto ({codigo_moneda})", min_value=0.0, max_value=tope_precio, value=float(precio_actual_calculado * 1.05), step=paso_slider)
                    cambio_precio = ((nuevo_precio - precio_actual_calculado) / precio_actual_calculado) * 100 if precio_actual_calculado > 0 else 0.0
                    st.caption(f"Precio actual: **{formatear_dinero(precio_actual_calculado)}** ({cambio_precio:+.1f}%)")

                with col_op2:
                    costo_unitario = st.slider(f"Costo por unidad / proveedor ({codigo_moneda})", min_value=0.0, max_value=tope_precio, value=float(precio_actual_calculado * 0.40), step=paso_slider)
                    st.caption(f"Equivale al **{(costo_unitario / nuevo_precio * 100) if nuevo_precio > 0 else 0:.1f}%** del nuevo precio")

                st.divider()

                st.subheader("📊 Impacto Financiero Directo")
                try:
                    (v_hist, g_hist, v_sim, g_sim, c_hist, c_sim) = simular_escenario_negocio(df, cambio_precio, 0.0, nuevo_precio, costo_unitario)
                    dif_ganancia = g_sim - g_hist

                    col_res1, col_res2 = st.columns(2)
                    with col_res1:
                        st.metric("Ganancia Neta Histórica", formatear_dinero(g_hist))
                    with col_res2:
                        st.metric("Ganancia Neta Simulada", formatear_dinero(g_sim), formatear_dinero(dif_ganancia))
                        
                    if g_sim > g_hist:
                        st.success(f"🚀 **¡Escenario Positivo!** Generas **{formatear_dinero(dif_ganancia)}** extra.")
                    else:
                        st.error("⚠️ **Cuidado:** Tu margen bajó. Estás perdiendo dinero.")

                    fig_ganancia = go.Figure(data=[
                        go.Bar(name="Histórico", x=["Ganancias"], y=[g_hist], marker_color="#4A5568"),
                        go.Bar(name="Simulado", x=["Ganancias"], y=[g_sim], marker_color="#00C853" if g_sim > g_hist else "#D32F2F")
                    ])
                    fig_ganancia.update_layout(barmode='group', height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
                    st.plotly_chart(fig_ganancia, use_container_width=True)

                except Exception as error:
                    st.error(f"Error al simular: {error}")

            except FileNotFoundError:
                st.error("⚠️ Sube 'train.csv' a GitHub para usar la demo.")

        with tab_asistido:
            st.write("🤝 Próximamente: Tabla interactiva.")
        with tab_pro:
            st.write("🚀 Próximamente: Auditoría profunda.")
        with tab_marketing:
            st.subheader("🎯 Estrategia de Inversión")
            tope_mkt = 5000000.0 if codigo_moneda == "COP" else 2000.0
            paso_mkt = 10000.0 if codigo_moneda == "COP" else 10.0
            
            presupuesto_marketing = st.slider(f"Presupuesto para publicidad ({codigo_moneda})", min_value=0.0, max_value=tope_mkt, value=0.0, step=paso_mkt)
            (inversion_ig, inversion_fb, inversion_tk, inversion_gg, clientes_nuevos) = optimizar_marketing(presupuesto_marketing, nuevo_precio if nuevo_precio > 0 else 50000.0)
            
            if presupuesto_marketing > 0:
                col_grafico, col_metrica = st.columns([1.5, 1])
                with col_grafico:
                    fig_mkt = go.Figure(data=[go.Pie(labels=["Instagram", "Facebook", "TikTok", "Google"], values=[inversion_ig, inversion_fb, inversion_tk, inversion_gg], hole=0.5, marker_colors=["#E1306C", "#1877F2", "#00F2FE", "#EA4335"])])
                    fig_mkt.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
                    st.plotly_chart(fig_mkt, use_container_width=True)
                with col_metrica:
                    st.metric("🎯 Clientes nuevos estimados", f"+{clientes_nuevos}")
            else:
                st.warning("⚠️ Mueve la barra de presupuesto.")

    # --------------------------------------------------------
    # OPCIÓN B: SIN CSV (MANUAL)
    # --------------------------------------------------------
    else:
        st.info("💡 Ingresa los datos generales de tu negocio.")
        col_man1, col_man2 = st.columns(2)
        with col_man1:
            unidades_vendidas = st.number_input("Cantidad de productos vendidos.", min_value=1, value=80, step=1)
        with col_man2:
            precio_actual_manual = st.number_input(f"Precio de venta actual ({codigo_moneda})", min_value=0.0, value=50000.0, step=1000.0)

        ventas_estimadas = unidades_vendidas * precio_actual_manual
        st.success(f"💡 **Ventas históricas estimadas:** {formatear_dinero(ventas_estimadas)}")
        df = pd.DataFrame({"Sales": [ventas_estimadas], "Quantity": [unidades_vendidas]})
