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
# 🎨 INYECCIÓN DE CSS (DISEÑO PREMIUM Y LIMPIEZA)
# ============================================================
estilos_css = """
<style>
    /* 1. Ocultar los elementos predeterminados de Streamlit para que parezca app propia */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 2. Personalizar los botones principales con esquinas redondeadas */
    div.stButton > button {
        border-radius: 8px;
        font-weight: bold;
        border: 1px solid #CF9D7B;
        transition: all 0.3s ease;
    }
    
    /* 3. Efecto de luz (hover) al pasar el cursor sobre los botones */
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0px 6px 15px rgba(207, 157, 123, 0.3);
        border-color: #FAFAFA;
    }
    
    /* 4. Estilizar las tarjetas o contenedores para que combinen con la paleta */
    div.stMarkdown {
        letter-spacing: 0.2px;
    }
</style>
"""

st.markdown(estilos_css, unsafe_allow_html=True)

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
if 'seccion_activa' not in st.session_state:
    st.session_state['seccion_activa'] = "🤝 Modo Asistido"

def ir_a_seccion(seccion):
    st.session_state['en_simulador'] = True
    st.session_state['seccion_activa'] = seccion

def volver_portada():
    st.session_state['en_simulador'] = False

# ============================================================
# 🏠 PANTALLA 1: LA PORTADA (LOBBY - TRUCO 3)
# ============================================================
if not st.session_state['en_simulador']:
    # Contenedor central con estilo de bienvenida ejecutivo
    st.markdown("<h1 style='text-align: center; color: #FAFAFA;'>📊 Simulador de Negocio y Marketing</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #CF9D7B; font-size: 1.2rem; font-weight: bold;'>CENTRO DE MANDO Y DECISIONES ESTRATÉGICAS</p>", unsafe_allow_html=True)
    
    st.write("") # Espaciado elegante
    
    col_desc1, col_desc2, col_desc3 = st.columns([1, 3, 1])
    with col_desc2:
        st.write(
            "Bienvenido, Emmanuel. Antes de arriesgar tu capital en el mundo real, simula tus decisiones aquí. "
            "Audita tu inventario, ajusta tus precios, controla tus costos y planifica tu inversión publicitaria "
            "con precisión de analista de datos."
        )

    st.markdown("<hr style='border: 1px solid #162127;'>", unsafe_allow_html=True)

    st.markdown("#### 🚀 Selecciona tu módulo de trabajo:")

    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        st.success("🤝 **Modo Asistido**\n\nUsa nuestra tabla inteligente para ingresar tus costos o descarga una plantilla para rellenar.")
        st.button("Entrar al Asistido", on_click=ir_a_seccion, args=("🤝 Modo Asistido",), use_container_width=True)
    with col_p2:
        st.warning("🚀 **Modo Pro Ultra**\n\nConecta tu inventario histórico completo y obtén una radiografía profunda automatizada.")
        st.button("Entrar al Pro", on_click=ir_a_seccion, args=("🚀 Modo Pro Ultra",), use_container_width=True)
    with col_p3:
        st.error("🎯 **Estrategia MKT**\n\nSimula inversiones en redes sociales y calcula clientes nuevos al instante.")
        st.button("Entrar a Marketing", on_click=ir_a_seccion, args=("🎯 Estrategia Marketing",), use_container_width=True)

    st.divider()
    
    st.markdown("<h3 style='text-align: center; color: #CF9D7B;'>¿Listo para tomar el control?</h3>", unsafe_allow_html=True)
    st.write("") 
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        st.button("🚀 INGRESAR AL SIMULADOR", on_click=ir_a_seccion, args=("🤝 Modo Asistido",), use_container_width=True, type="primary")

# ============================================================
# ⚙️ PANTALLA 2: LA MAQUINARIA (APP PRINCIPAL)
# ============================================================
else:
    st.markdown("### Menú de Navegación")
    col_home, col_menu = st.columns([1.5, 8.5])
    
    with col_home:
        st.button("🏠 Volver al Home", on_click=volver_portada, use_container_width=True, type="secondary")
        
    with col_menu:
        opciones_menu = ["🤝 Modo Asistido", "🚀 Modo Pro Ultra", "🎯 Estrategia Marketing"]
        idx = opciones_menu.index(st.session_state['seccion_activa']) if st.session_state['seccion_activa'] in opciones_menu else 0
        menu_seleccionado = st.radio("Secciones", opciones_menu, index=idx, horizontal=True, label_visibility="collapsed")
        st.session_state['seccion_activa'] = menu_seleccionado

    st.divider()

    # VARIABLES GLOBALES
    df = None
    nuevo_precio = 0.0
    presupuesto_marketing = 0.0
    costo_unitario = 0.0
    codigo_moneda = "COP" 

    # ========================================================
    # SECCIÓN 1: MODO ASISTIDO (EL MINI-EXCEL)
    # ========================================================
    if menu_seleccionado == "🤝 Modo Asistido":
        st.subheader("🤝 Modo Asistido: Tu lienzo en blanco")
        st.write("Completa los datos de tus productos directamente aquí o descarga la plantilla para llenarla en tu computador y subirla después.")

        columnas_base = {
            "Producto": ["Ejemplo: Camiseta Negra", "", ""],
            "Cantidad Vendida": [100, 0, 0],
            "Precio de Venta": [50000.0, 0.0, 0.0],
            "Costo Proveedor": [20000.0, 0.0, 0.0]
        }
        df_plantilla = pd.DataFrame(columnas_base)

        col_descarga, col_subida = st.columns(2)
        
        with col_descarga:
            csv_plantilla = df_plantilla.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Plantilla CSV",
                data=csv_plantilla,
                file_name="plantilla_simulador.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        with col_subida:
            archivo_subido = st.file_uploader("📂 O sube tu archivo ya lleno", type=["csv"], label_visibility="collapsed")

        st.divider()

        st.markdown("### 📝 Llena tus datos en línea")
        st.caption("Haz doble clic en cualquier celda para editar. Puedes agregar nuevas filas en la parte inferior.")
        
        if archivo_subido is not None:
            df_base = pd.read_csv(archivo_subido)
        else:
            df_base = df_plantilla

        df_usuario = st.data_editor(
            df_base,
            num_rows="dynamic", 
            use_container_width=True,
            key="editor_datos"
        )
        
        primer_producto = str(df_usuario["Producto"].iloc[0])
        datos_listos = primer_producto != "" and primer_producto != "Ejemplo: Camiseta Negra"

        if datos_listos:
            st.success("✅ ¡Datos detectados! El motor de simulación está listo.")
            # Aquí inyectaremos el simulador más adelante
        else:
            st.info("👆 Empieza a escribir tus productos reales en la tabla para activar el análisis.")

    # ========================================================
    # SECCIÓN 2: MODO PRO ULTRA (EL DETECTIVE Y CSV COMPLETO)
    # ========================================================
    elif menu_seleccionado == "🚀 Modo Pro Ultra":
        st.subheader("🚀 Modo Pro Ultra: El Detective de Negocios")
        st.write("Sube tu base de datos histórica completa. Nuestro motor auditará tu catálogo, detectará fugas de capital y te permitirá simular escenarios complejos.")
        
        archivo_pro = st.file_uploader("📂 Sube tu archivo CSV histórico aquí", type=["csv"], key="uploader_pro")
        
        if archivo_pro is not None:
            try:
                df_pro = pd.read_csv(archivo_pro)
                
                mapeo_columnas = {
                    "ventas": "Sales", "Ventas": "Sales", "monto": "Sales", "Monto": "Sales", 
                    "cantidad": "Quantity", "Cantidad": "Quantity", "unidades": "Quantity", "Units": "Quantity",
                    "costo": "Cost", "Costo": "Cost"
                }
                df_pro = df_pro.rename(columns=mapeo_columnas)
                
                tasa_cambio = 1.0 
                if "Sales" in df_pro.columns:
                    df_pro["Sales"] = pd.to_numeric(df_pro["Sales"], errors='coerce').fillna(0) * tasa_cambio
                if "Quantity" not in df_pro.columns:
                    df_pro["Quantity"] = 1.0
                else:
                    df_pro["Quantity"] = pd.to_numeric(df_pro["Quantity"], errors='coerce').fillna(1)
                    
                st.success(f"✅ ¡Base de datos Pro cargada! Analizando {len(df_pro):,} registros...")
                
                def formatear_dinero_pro(valor):
                    return f"$ {valor:,.0f} COP" 
                
                st.markdown("### 🕵️‍♂️ Radiografía de tu Negocio")
                col_prod = "Product Name" if "Product Name" in df_pro.columns else ("Producto" if "Producto" in df_pro.columns else None)
                
                if col_prod:
                    df_agrupado = df_pro.groupby(col_prod).agg(
                        Total_Ventas=("Sales", "sum"), Total_Unidades=("Quantity", "sum")
                    ).reset_index()
                    
                    df_agrupado["Precio_Unitario"] = df_agrupado["Total_Ventas"] / df_agrupado["Total_Unidades"]
                    
                    rey = df_agrupado.loc[df_agrupado["Total_Ventas"].idxmax()]
                    hueso = df_agrupado.loc[df_agrupado["Total_Ventas"].idxmin()]
                    mas_caro = df_agrupado.loc[df_agrupado["Precio_Unitario"].idxmax()]
                    
                    col_det1, col_det2 = st.columns(2)
                    with col_det1:
                        st.info(f"🏆 **El Rey (Más ingresos):**\n\n*{rey[col_prod]}*\n\nGeneró: **{formatear_dinero_pro(rey['Total_Ventas'])}**")
                        st.success(f"💎 **El producto más costoso:**\n\n*{mas_caro[col_prod]}*\n\nPrecio aprox: **{formatear_dinero_pro(mas_caro['Precio_Unitario'])}**")
                    with col_det2:
                        if hueso['Total_Ventas'] == 0:
                            st.warning(f"💀 **El Hueso (Cero ventas):**\n\n*{hueso[col_prod]}*\n\nGeneró: **$ 0 COP**")
                        else:
                            st.warning(f"💀 **El Hueso (Menos ingresos):**\n\n*{hueso[col_prod]}*\n\nGeneró: **{formatear_dinero_pro(hueso['Total_Ventas'])}**")
                        
                        df_baratos = df_agrupado[df_agrupado["Precio_Unitario"] > 0]
                        if not df_baratos.empty:
                            mas_barato = df_baratos.loc[df_baratos["Precio_Unitario"].idxmin()]
                            st.error(f"🏷️ **El más económico:**\n\n*{mas_barato[col_prod]}*\n\nPrecio aprox: **{formatear_dinero_pro(mas_barato['Precio_Unitario'])}**")
                    
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
                        f"👋 **¡Hola, mi amigo emprendedor!** Aquí tu plan táctico basado en tu data histórica:\n\n"
                        f"🚀 Tu producto rey (*{rey[col_prod]}*) es tu motor principal. ¡Asegura inventario siempre!\n\n"
                        f"💀 Ese *{hueso[col_prod]}* es tu hueso. Considera armar un combo para rotarlo rápido.\n\n"
                        f"🏷️ Tu producto más económico (*{mas_barato[col_prod]}*) úsalo en pautas publicitarias para atraer tráfico."
                    )
                
                st.divider()

                st.header("🕹️ Simulador en Tiempo Real")
                st.write("Ajusta tus precios y costos globales, y observa el impacto financiero al instante.")
                
                df = df_pro 
                unidades_totales = df["Quantity"].sum()
                precio_actual_calculado = float(df["Sales"].sum() / unidades_totales) if unidades_totales > 0 else 50000.0
                tope_precio = float(precio_actual_calculado * 5) if precio_actual_calculado > 0 else 1000000.0
                paso_slider = 1000.0

                col_op1, col_op2 = st.columns(2)
                with col_op1:
                    nuevo_precio = st.slider("Nuevo precio propuesto (COP)", min_value=0.0, max_value=tope_precio, value=float(precio_actual_calculado * 1.05), step=paso_slider)
                    cambio_precio = ((nuevo_precio - precio_actual_calculado) / precio_actual_calculado) * 100 if precio_actual_calculado > 0 else 0.0
                    st.caption(f"Precio actual promediado: **{formatear_dinero_pro(precio_actual_calculado)}** ({cambio_precio:+.1f}%)")

                with col_op2:
                    costo_unitario = st.slider("Costo base por unidad (COP)", min_value=0.0, max_value=tope_precio, value=float(precio_actual_calculado * 0.40), step=paso_slider)
                    st.caption(f"Equivale al **{(costo_unitario / nuevo_precio * 100) if nuevo_precio > 0 else 0:.1f}%** del nuevo precio")

                st.divider()

                st.subheader("📊 Impacto Financiero Directo")
                try:
                    (v_hist, g_hist, v_sim, g_sim, c_hist, c_sim) = simular_escenario_negocio(df, cambio_precio, 0.0, nuevo_precio, costo_unitario)
                    dif_ganancia = g_sim - g_hist

                    col_res1, col_res2 = st.columns(2)
                    with col_res1:
                        st.metric("Ganancia Neta Histórica", formatear_dinero_pro(g_hist))
                    with col_res2:
                        st.metric("Ganancia Neta Simulada", formatear_dinero_pro(g_sim), formatear_dinero_pro(dif_ganancia))
                        
                    if g_sim > g_hist:
                        st.success(f"🚀 **¡Escenario Positivo!** Con esta proyección generas **{formatear_dinero_pro(dif_ganancia)}** extra.")
                    else:
                        st.error("⚠️ **Cuidado:** Tu margen de rentabilidad bajó. Estás perdiendo dinero frente al escenario histórico.")

                    fig_ganancia = go.Figure(data=[
                        go.Bar(name="Histórico", x=["Ganancias"], y=[g_hist], marker_color="#4A5568"),
                        go.Bar(name="Simulado", x=["Ganancias"], y=[g_sim], marker_color="#00C853" if g_sim > g_hist else "#D32F2F")
                    ])
                    fig_ganancia.update_layout(barmode='group', height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
                    st.plotly_chart(fig_ganancia, use_container_width=True)

                except Exception as error:
                    st.error(f"Error al simular: {error}")

            except Exception as e:
                st.error(f"❌ Error al procesar el archivo. Asegúrate de que sea un CSV válido. Detalle: {e}")
        else:
            st.info("👆 El motor está apagado. Sube tu CSV histórico para iniciar la auditoría.")

    # ========================================================
    # SECCIÓN 3: ESTRATEGIA MARKETING
    # ========================================================
    elif menu_seleccionado == "🎯 Estrategia Marketing":
        st.subheader("🎯 Inyección de Capital para Anuncios")
        st.write("Decide cuánto quieres invertir en publicidad para atraer nuevos clientes.")
        
        tope_mkt = 5000000.0 
        paso_mkt = 10000.0 
        
        def formatear_mkt(valor):
            return f"$ {valor:,.0f} COP"
            
        presupuesto_marketing = st.slider("Presupuesto para publicidad (COP)", min_value=0.0, max_value=tope_mkt, value=0.0, step=paso_mkt)
        
        precio_simulado_mkt = 50000.0
        (inversion_ig, inversion_fb, inversion_tk, inversion_gg, clientes_nuevos) = optimizar_marketing(presupuesto_marketing, precio_simulado_mkt)
        
        if presupuesto_marketing > 0:
            col_grafico, col_metrica = st.columns([1.5, 1])
            with col_grafico:
                fig_mkt = go.Figure(data=[go.Pie(labels=["Instagram", "Facebook", "TikTok", "Google"], values=[inversion_ig, inversion_fb, inversion_tk, inversion_gg], hole=0.5, marker_colors=["#E1306C", "#1877F2", "#00F2FE", "#EA4335"])])
                fig_mkt.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
                st.plotly_chart(fig_mkt, use_container_width=True)
            with col_metrica:
                st.metric("🎯 Clientes nuevos estimados", f"+{clientes_nuevos}")
                costo_c = presupuesto_marketing / clientes_nuevos if clientes_nuevos > 0 else 0
                st.success(f"Traer 1 cliente te cuesta aprox. **{formatear_mkt(costo_c)}**")
        else:
            st.warning("⚠️ Mueve la barra de presupuesto para arrancar.")
