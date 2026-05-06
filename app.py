import streamlit as st
import pandas as pd
import re, io, os
from datetime import datetime
from PIL import Image
import numpy as np

# --- CONFIGURACIÓN ---
try:
    img_logo = Image.open("logo.png")
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon=img_logo, layout="wide")
except:
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon="💼", layout="wide")

# ============================================
# 🎨 COLORES MEJORADOS - MÁXIMA LEGIBILIDAD
# ============================================
COLORES = {
    # Fondos
    "fondo_principal": "#F8F9FA",        # Gris muy claro
    "fondo_tarjetas": "#FFFFFF",         # Blanco puro
    "fondo_sidebar": "#1a472a",          # Verde oscuro elegante
    
    # Textos
    "texto_principal": "#2C3E50",        # Azul grisáceo oscuro (muy legible)
    "texto_secundario": "#6C757D",       # Gris medio
    "texto_blanco": "#FFFFFF",           # Blanco puro
    
    # Colores corporativos
    "primario": "#27AE60",               # Verde fresh
    "primario_oscuro": "#1E8449",        # Verde más oscuro
    "primario_claro": "#82E0AA",         # Verde claro
    "secundario": "#3498DB",             # Azul para acciones secundarias
    "exito": "#28A745",                  # Verde éxito
    "peligro": "#DC3545",                # Rojo
    "advertencia": "#FFC107",            # Amarillo
    "info": "#17A2B8",                   # Cyan
    
    # Bordes y sombras
    "borde": "#DEE2E6",
    "sombra": "rgba(0,0,0,0.1)",
}

# --- ESTILOS CSS MEJORADOS ---
st.markdown(f"""
    <style>
    /* Fondo general */
    .stApp {{
        background-color: {COLORES["fondo_principal"]};
    }}
    
    /* Texto general */
    .main .block-container {{
        color: {COLORES["texto_principal"]} !important;
    }}
    
    h1, h2, h3, h4, h5, h6, p, span, div, label {{
        color: {COLORES["texto_principal"]} !important;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: {COLORES["fondo_sidebar"]};
    }}
    
    [data-testid="stSidebar"] * {{
        color: {COLORES["texto_blanco"]} !important;
    }}
    
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {{
        color: {COLORES["texto_blanco"]} !important;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background: {COLORES["fondo_tarjetas"]};
        border-radius: 12px;
        padding: 0.5rem;
        gap: 0.5rem;
        box-shadow: 0 2px 4px {COLORES["sombra"]};
    }}
    
    .stTabs [data-baseweb="tab"] {{
        color: {COLORES["texto_principal"]} !important;
        background: #E9ECEF;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {COLORES["primario"]};
        color: {COLORES["texto_blanco"]} !important;
    }}
    
    /* Botones principales */
    .stButton > button {{
        background: {COLORES["primario"]};
        color: {COLORES["texto_blanco"]} !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s;
    }}
    
    .stButton > button:hover {{
        background: {COLORES["primario_oscuro"]};
        transform: translateY(-1px);
        box-shadow: 0 2px 8px {COLORES["sombra"]};
    }}
    
    /* Botón secundario */
    .stButton > button:has(.secondary) {{
        background: {COLORES["secundario"]};
    }}
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {{
        background: {COLORES["fondo_tarjetas"]};
        color: {COLORES["texto_principal"]} !important;
        border: 1px solid {COLORES["borde"]};
        border-radius: 8px;
    }}
    
    /* Dataframe */
    .stDataFrame {{
        background: {COLORES["fondo_tarjetas"]};
        border-radius: 10px;
        border: 1px solid {COLORES["borde"]};
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background: {COLORES["fondo_tarjetas"]};
        color: {COLORES["texto_principal"]} !important;
        border-radius: 8px;
        font-weight: 600;
    }}
    
    /* Cards de métricas */
    .metric-card {{
        background: {COLORES["fondo_tarjetas"]};
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 8px {COLORES["sombra"]};
        border: 1px solid {COLORES["borde"]};
    }}
    
    .metric-value {{
        font-size: 2rem;
        font-weight: bold;
        color: {COLORES["primario"]} !important;
    }}
    
    .metric-label {{
        font-size: 0.85rem;
        color: {COLORES["texto_secundario"]} !important;
        margin-top: 0.5rem;
    }}
    
    /* Alertas */
    .stAlert {{
        border-radius: 8px;
        border-left: 4px solid {COLORES["primario"]};
    }}
    
    /* Resultados de búsqueda */
    .search-result {{
        background: {COLORES["fondo_tarjetas"]};
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 3px solid {COLORES["primario"]};
        cursor: pointer;
        transition: all 0.2s;
    }}
    
    .search-result:hover {{
        background: {COLORES["primario_claro"]};
        transform: translateX(5px);
    }}
    
    .search-sku {{
        font-weight: bold;
        color: {COLORES["primario"]};
        font-size: 1rem;
    }}
    
    .search-desc {{
        color: {COLORES["texto_secundario"]};
        font-size: 0.9rem;
    }}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 💼 QTC Pro")
    st.markdown("---")
    
    if "cotizaciones" in st.session_state:
        st.metric("📄 Cotizaciones", st.session_state.get("cotizaciones", 0))
        st.metric("📦 Productos", st.session_state.get("total_prods", 0))

# --- LOGIN ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.container():
            st.markdown(f"""
            <div style="background: {COLORES['fondo_tarjetas']}; padding: 2rem; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
                <h1 style="text-align: center; color: {COLORES['primario']};">💚 QTC Smart Sales</h1>
                <p style="text-align: center;">Sistema Corporativo de Ventas</p>
            </div>
            """, unsafe_allow_html=True)
            
            user = st.text_input("👤 Usuario")
            pw = st.text_input("🔒 Contraseña", type="password")
            
            if st.button("🔐 Ingresar", use_container_width=True):
                if user == "admin" and pw == "qtc2026":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
    st.stop()

# --- FUNCIONES PRINCIPALES ---
def corregir_numero(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "0"]:
        return 0.0
    s = re.sub(r'[^\d.,]', '', str(valor).replace('S/', '').replace('$', ''))
    s = s.replace(',', '.') if '.' not in s else s.replace(',', '')
    try:
        return float(s)
    except:
        return 0.0

def generar_excel(items, cliente, ruc):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df = pd.DataFrame(items)
    df.to_excel(writer, sheet_name='Cotizacion', index=False)
    
    workbook = writer.book
    ws = writer.sheets['Cotizacion']
    
    # Formato de encabezado
    header_fmt = workbook.add_format({
        'bg_color': COLORES['primario'].replace('#', ''),
        'bold': True,
        'font_color': 'white',
        'align': 'center'
    })
    
    # Escribir encabezados
    for i, col in enumerate(['SKU', 'Descripción', 'Cantidad', 'Precio Unit.', 'Total']):
        ws.write(0, i, col, header_fmt)
    
    # Formato de moneda
    money_fmt = workbook.add_format({'num_format': 'S/. #,##0.00'})
    
    # Aplicar formato de moneda a las columnas de precio y total
    ws.set_column('D:D', 15, money_fmt)
    ws.set_column('E:E', 15, money_fmt)
    
    writer.close()
    return output.getvalue()

def extraer_skus_gemini(image):
    """Extrae SKU usando Gemini desde secrets"""
    try:
        import google.generativeai as genai
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        
        if not api_key:
            st.warning("⚠️ API Key no configurada")
            return []
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content([
            "Extrae todos los códigos SKU y sus cantidades de esta imagen de catálogo. "
            "Devuelve SOLO un array JSON en este formato: [{\"sku\": \"CODIGO\", \"cantidad\": NUMERO}]. "
            "Si no hay cantidad visible, asume cantidad = 1.",
            image
        ])
        
        texto = response.text
        import json
        match = re.search(r'\[.*\]', texto, re.DOTALL)
        if match:
            return json.loads(match.group())
        return []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

# --- INTERFAZ PRINCIPAL ---
st.title("💚 QTC Smart Sales Pro")
st.markdown("---")

# Crear tabs
tab_pedidos, tab_busqueda, tab_imagen, tab_dashboard = st.tabs([
    "📦 Gestión de Pedidos", 
    "🔍 Búsqueda por Descripción", 
    "🤖 SKU por Imagen", 
    "📊 Dashboard"
])

# ============================================
# TAB 1: GESTIÓN DE PEDIDOS
# ============================================
with tab_pedidos:
    st.sidebar.header("📂 Archivos")
    f_precios = st.sidebar.file_uploader("1. Catálogo de Precios", type=['xlsx'])
    f_stock = st.sidebar.file_uploader("2. Reporte de Stock", type=['xlsx'])
    
    if f_precios and f_stock:
        with st.spinner("Cargando datos..."):
            df_precios = pd.read_excel(f_precios)
            df_stock = pd.read_excel(f_stock)
            
            # Identificar columnas automáticamente
            col_sku = next((c for c in df_precios.columns if 'SKU' in str(c).upper() or 'COD' in str(c).upper()), df_precios.columns[0])
            col_desc = next((c for c in df_precios.columns if 'DESC' in str(c).upper() or 'NOMBRE' in str(c).upper()), df_precios.columns[1])
            col_stock = next((c for c in df_stock.columns if 'DISP' in str(c).upper() or 'STOCK' in str(c).upper()), df_stock.columns[-1])
            
            st.success("✅ Datos cargados correctamente")
            
            # Selector de precio
            palabras_precio = ['MAYOR', 'CAJA', 'VIP', 'PRECIO', 'UNIT']
            precios_opc = [c for c in df_precios.columns if any(p in str(c).upper() for p in palabras_precio)]
            if not precios_opc:
                precios_opc = df_precios.columns.tolist()
            
            col_precio = st.selectbox("🎯 Selecciona la columna de precio:", precios_opc)
            
            # Área para SKUs
            st.subheader("📝 Ingresa los SKU y cantidades")
            
            # Verificar si hay SKUs transferidos
            if 'skus_transferidos' in st.session_state:
                texto_defecto = "\n".join([f"{sku}:{cant}" for sku, cant in st.session_state.skus_transferidos.items()])
                del st.session_state.skus_transferidos
            else:
                texto_defecto = ""
            
            texto_skus = st.text_area(
                "Formato: SKU:CANTIDAD (uno por línea)", 
                height=150,
                value=texto_defecto,
                placeholder="Ejemplo:\nABC123:5\nXYZ789:2\nPROD456:10"
            )
            
            # Procesar SKUs
            pedidos = {}
            if texto_skus:
                for linea in texto_skus.split('\n'):
                    linea = linea.strip()
                    if ':' in linea:
                        sku, cant = linea.split(':')
                        pedidos[sku.strip().upper()] = int(cant.strip())
                    elif linea:
                        pedidos[linea.strip().upper()] = 1
            
            if st.button("🚀 PROCESAR DISPONIBILIDAD", use_container_width=True) and pedidos:
                with st.spinner("Procesando..."):
                    resultados = []
                    stock_col = df_stock.columns[0]  # Columna de SKU en stock
                    
                    for sku, cant_solicitada in pedidos.items():
                        # Buscar en precios
                        producto = df_precios[df_precios[col_sku].astype(str).str.contains(sku, case=False, na=False)]
                        
                        if not producto.empty:
                            precio = corregir_numero(producto.iloc[0][col_precio])
                            descripcion = producto.iloc[0][col_desc]
                            
                            # Buscar stock
                            stock_reg = df_stock[df_stock[stock_col].astype(str).str.contains(sku, case=False, na=False)]
                            stock_disponible = int(corregir_numero(stock_reg[col_stock].iloc[0])) if not stock_reg.empty else 0
                            
                            resultados.append({
                                'SKU': sku,
                                'Descripción': descripcion,
                                'Precio': precio,
                                'Solicitado': cant_solicitada,
                                'Stock': stock_disponible,
                                'Total': precio * cant_solicitada,
                                'Estado': '✅ OK' if stock_disponible >= cant_solicitada else '⚠️ Sin Stock'
                            })
                    
                    if resultados:
                        df_res = pd.DataFrame(resultados)
                        st.dataframe(df_res, use_container_width=True)
                        
                        total_cotizacion = df_res['Total'].sum()
                        productos_ok = len(df_res[df_res['Estado'] == '✅ OK'])
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("💰 Total Cotización", f"S/. {total_cotizacion:,.2f}")
                        col2.metric("✅ Productos OK", productos_ok)
                        col3.metric("⚠️ Sin Stock", len(resultados) - productos_ok)
                        
                        with st.expander("📥 Generar Cotización", expanded=True):
                            cliente = st.text_input("🏢 Nombre del Cliente", "CLIENTE NUEVO")
                            ruc = st.text_input("📋 RUC/DNI", "-")
                            
                            items_ok = [r for r in resultados if r['Estado'] == '✅ OK']
                            if items_ok and st.button("📥 Descargar Excel", use_container_width=True):
                                excel = generar_excel(items_ok, cliente, ruc)
                                st.download_button(
                                    label="💾 Guardar archivo",
                                    data=excel,
                                    file_name=f"Cotizacion_{cliente}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                                    use_container_width=True
                                )
                                st.session_state.cotizaciones = st.session_state.get("cotizaciones", 0) + 1
                                st.session_state.total_prods = len(items_ok)
                                st.balloons()

# ============================================
# TAB 2: BÚSQUEDA POR DESCRIPCIÓN
# ============================================
with tab_busqueda:
    st.markdown("### 🔍 Buscador de Productos por Descripción")
    st.info("💡 Busca productos por nombre o descripción y agrégalos a tu cotización")
    
    if 'df_precios_global' not in st.session_state and f_precios:
        df_precios_global = pd.read_excel(f_precios)
        # Identificar columnas
        col_sku_busq = next((c for c in df_precios_global.columns if 'SKU' in str(c).upper() or 'COD' in str(c).upper()), df_precios_global.columns[0])
        col_desc_busq = next((c for c in df_precios_global.columns if 'DESC' in str(c).upper() or 'NOMBRE' in str(c).upper()), df_precios_global.columns[1])
        col_precio_busq = next((c for c in df_precios_global.columns if 'PRECIO' in str(c).upper()), df_precios_global.columns[2] if len(df_precios_global.columns) > 2 else df_precios_global.columns[0])
        
        st.session_state.df_precios_global = df_precios_global
        st.session_state.col_sku_busq = col_sku_busq
        st.session_state.col_desc_busq = col_desc_busq
        st.session_state.col_precio_busq = col_precio_busq
    
    if 'df_precios_global' in st.session_state:
        df_busqueda = st.session_state.df_precios_global
        col_desc = st.session_state.col_desc_busq
        col_sku = st.session_state.col_sku_busq
        col_precio = st.session_state.col_precio_busq
        
        # Campo de búsqueda
        busqueda = st.text_input("🔎 Escribe el nombre o descripción del producto:", 
                                 placeholder="Ej: LAPTOP, MOUSE, CABLE HDMI...")
        
        if busqueda:
            # Buscar coincidencias (insensible a mayúsculas)
            mascara = df_busqueda[col_desc].astype(str).str.contains(busqueda, case=False, na=False)
            resultados_busqueda = df_busqueda[mascara]
            
            if not resultados_busqueda.empty:
                st.success(f"✅ Se encontraron {len(resultados_busqueda)} productos")
                
                # Mostrar resultados en cards
                st.markdown("### 📋 Resultados de búsqueda:")
                
                # Selector de cantidad por producto
                productos_seleccionados = {}
                
                for idx, row in resultados_busqueda.iterrows():
                    sku = str(row[col_sku]).strip()
                    desc = str(row[col_desc])[:80]  # Limitar longitud
                    precio = corregir_numero(row[col_precio])
                    
                    # Crear una card para cada resultado
                    with st.container():
                        col1, col2, col3, col4 = st.columns([2, 4, 1, 1])
                        with col1:
                            st.markdown(f"**📦 {sku}**")
                        with col2:
                            st.markdown(desc)
                        with col3:
                            st.markdown(f"💰 S/. {precio:,.2f}")
                        with col4:
                            cantidad = st.number_input("Cant", min_value=0, max_value=999, value=0, key=f"qty_{sku}")
                            if cantidad > 0:
                                productos_seleccionados[sku] = cantidad
                        st.divider()
                
                # Botón para agregar seleccionados
                if productos_seleccionados:
                    st.markdown("---")
                    st.markdown(f"### 📦 Productos seleccionados: {len(productos_seleccionados)}")
                    
                    # Mostrar resumen
                    resumen = []
                    for sku, cant in productos_seleccionados.items():
                        producto = df_busqueda[df_busqueda[col_sku].astype(str).str.contains(sku, case=False, na=False)]
                        if not producto.empty:
                            precio = corregir_numero(producto.iloc[0][col_precio])
                            resumen.append({
                                'SKU': sku,
                                'Descripción': producto.iloc[0][col_desc][:50],
                                'Cantidad': cant,
                                'Precio': precio,
                                'Total': precio * cant
                            })
                    
                    df_resumen = pd.DataFrame(resumen)
                    st.dataframe(df_resumen, use_container_width=True)
                    st.metric("Total seleccionado", f"S/. {df_resumen['Total'].sum():,.2f}")
                    
                    if st.button("📋 Transferir a Pedidos", use_container_width=True):
                        st.session_state.skus_transferidos = productos_seleccionados
                        st.success(f"✅ {len(productos_seleccionados)} productos transferidos")
                        st.info("👉 Ve a la pestaña 'Gestión de Pedidos' y haz clic en PROCESAR")
                else:
                    st.info("Selecciona cantidad (>0) para agregar productos")
            else:
                st.warning("⚠️ No se encontraron productos. Prueba con otra palabra")
        else:
            st.info("✏️ Escribe el nombre de un producto para buscar")
    else:
        st.warning("⚠️ Primero carga el Catálogo de Precios en la pestaña 'Gestión de Pedidos'")

# ============================================
# TAB 3: SKU POR IMAGEN
# ============================================
with tab_imagen:
    st.markdown("### 🤖 Captura Inteligente de SKU")
    st.info("💡 Sube una foto del catálogo y la IA extraerá los SKU automáticamente")
    
    imagen = st.file_uploader("📸 Subir imagen", type=['jpg', 'png', 'jpeg'])
    
    if imagen:
        img = Image.open(imagen)
        st.image(img, width=300)
        
        if st.button("🔍 Extraer SKU con Gemini", use_container_width=True):
            with st.spinner("🤖 Analizando imagen..."):
                datos = extraer_skus_gemini(img)
                
                if datos:
                    st.success(f"✅ Se encontraron {len(datos)} SKUs")
                    df_detectados = pd.DataFrame(datos)
                    st.dataframe(df_detectados, use_container_width=True)
                    
                    if st.button("📋 Transferir a Pedidos", use_container_width=True):
                        skus_dict = {item['sku']: item['cantidad'] for item in datos}
                        st.session_state.skus_transferidos = skus_dict
                        st.success("✅ Transferido! Ve a 'Gestión de Pedidos'")
                else:
                    st.warning("No se detectaron SKUs")
    
    st.markdown("---")
    st.markdown("### ✏️ Entrada Manual")
    num = st.number_input("Número de productos", min_value=1, max_value=10, value=3)
    
    skus_manual = {}
    for i in range(int(num)):
        col1, col2 = st.columns(2)
        with col1:
            sku = st.text_input(f"SKU {i+1}", key=f"manual_sku_{i}")
        with col2:
            cant = st.number_input(f"Cantidad", min_value=1, value=1, key=f"manual_cant_{i}", label_visibility="collapsed")
        if sku:
            skus_manual[sku.upper()] = cant
    
    if skus_manual and st.button("📋 Transferir Manual", use_container_width=True):
        st.session_state.skus_transferidos = skus_manual
        st.success(f"✅ {len(skus_manual)} SKUs transferidos")

# ============================================
# TAB 4: DASHBOARD
# ============================================
with tab_dashboard:
    st.markdown("### 📊 Panel de Control")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.get("cotizaciones", 0)}</div>
            <div class="metric-label">📄 Cotizaciones Generadas</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.get("total_prods", 0)}</div>
            <div class="metric-label">🌿 Productos Cotizados</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎯 Guía Rápida")
    st.markdown("""
    **1. Cargar archivos** → En la barra lateral izquierda
    
    **2. Buscar productos** → Usa la pestaña "Búsqueda por Descripción"
    
    **3. Capturar SKU** → Usa la pestaña "SKU por Imagen" con Gemini
    
    **4. Procesar pedido** → Ve a "Gestión de Pedidos" y haz clic en Procesar
    
    **5. Descargar cotización** → Genera el Excel listo para enviar
    """)

# --- FOOTER ---
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 1rem;">
    <p style="color: {COLORES['texto_secundario']};">💚 QTC Smart Sales Pro - Sistema Corporativo de Ventas con IA</p>
    <p style="color: {COLORES['texto_secundario']}; font-size: 0.8rem;">Versión 3.0 - Búsqueda por Descripción + Captura Inteligente</p>
</div>
""", unsafe_allow_html=True)
