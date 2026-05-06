import streamlit as st
import pandas as pd
import re, io
from datetime import datetime
from PIL import Image
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# --- CONFIGURACIÓN DE PÁGINA ---
try:
    img_logo = Image.open("logo.png")
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon=img_logo, layout="wide")
except:
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon="💼", layout="wide")

# ============================================
# ========== SECCIÓN DE COLORES =============
# ========== MODIFICA AQUÍ LOS HEX ==========
# ============================================

# COLORES PRINCIPALES
COLOR_FONDO_GENERAL = "#F0F2F6"        # Fondo gris muy claro
COLOR_TEXTO_PRINCIPAL = "#1a1a2e"      # Texto principal oscuro

# COLORES SIDEBAR
COLOR_SIDEBAR_FONDO1 = "#1a472a"       # Verde oscuro
COLOR_SIDEBAR_FONDO2 = "#0d2818"       # Verde muy oscuro
COLOR_SIDEBAR_TEXTO = "white"          # Texto blanco en sidebar
COLOR_SIDEBAR_SELECT_FONDO = "#2d5a3f"  # Fondo del select en sidebar (verde más claro)
COLOR_SIDEBAR_SELECT_TEXTO = "white"    # Texto del select en sidebar

# COLORES BOTONES
COLOR_BOTON_PRIMARIO = "#27AE60"       # Verde
COLOR_BOTON_HOVER = "#1E8449"          # Verde oscuro

# COLORES SELECTBOX (menú desplegable de precios)
COLOR_SELECTBOX_FONDO = "white"        # Fondo blanco
COLOR_SELECTBOX_TEXTO = "black"        # Texto negro
COLOR_SELECTBOX_BORDE = "#27AE60"      # Borde verde
COLOR_SELECTBOX_LABEL = "#1a1a2e"      # Label oscuro

# COLORES DROPDOWN
COLOR_DROPDOWN_FONDO = "white"         # Fondo blanco
COLOR_DROPDOWN_TEXTO = "black"         # Texto negro
COLOR_DROPDOWN_HOVER = "#e8f5e9"       # Verde claro
COLOR_DROPDOWN_SELECCIONADO = "#27AE60" # Verde
COLOR_DROPDOWN_SELECCIONADO_TEXTO = "white"

# COLORES TABS
COLOR_TABS_FONDO = "white"
COLOR_TAB_INACTIVA_FONDO = "#f0f0f0"
COLOR_TAB_INACTIVA_TEXTO = "#1a1a2e"
COLOR_TAB_ACTIVA_FONDO = "#27AE60"
COLOR_TAB_ACTIVA_TEXTO = "white"

# COLORES ESTADOS
COLOR_ESTADO_OK = "green"
COLOR_ESTADO_SIN_STOCK = "red"
COLOR_ESTADO_ADVERTENCIA = "orange"
COLOR_ESTADO_EXCLUIDO = "gray"

# ============================================
# ========== FIN COLORES ====================
# ============================================

# --- ESTILOS CSS ---
st.markdown(f"""
    <style>
    /* Fondo general */
    .stApp {{ background-color: {COLOR_FONDO_GENERAL}; }}
    
    /* Textos generales */
    h1, h2, h3, h4, p, div, span, label {{ color: {COLOR_TEXTO_PRINCIPAL} !important; }}
    
    /* SIDEBAR - fondo y texto */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLOR_SIDEBAR_FONDO1} 0%, {COLOR_SIDEBAR_FONDO2} 100%);
    }}
    [data-testid="stSidebar"] * {{ color: {COLOR_SIDEBAR_TEXTO} !important; }}
    
    /* SELECTBOX dentro del SIDEBAR (color corregido) */
    [data-testid="stSidebar"] .stSelectbox > div > div {{
        background-color: {COLOR_SIDEBAR_SELECT_FONDO} !important;
        color: {COLOR_SIDEBAR_SELECT_TEXTO} !important;
        border: 1px solid {COLOR_SELECTBOX_BORDE} !important;
    }}
    [data-testid="stSidebar"] .stSelectbox > div > div > div {{
        color: {COLOR_SIDEBAR_SELECT_TEXTO} !important;
    }}
    [data-testid="stSidebar"] .stSelectbox label {{
        color: {COLOR_SIDEBAR_TEXTO} !important;
    }}
    
    /* Botones */
    .stButton > button {{
        background: {COLOR_BOTON_PRIMARIO};
        color: white !important;
        border-radius: 10px;
        font-weight: 600;
    }}
    .stButton > button:hover {{ background: {COLOR_BOTON_HOVER}; }}
    
    /* SELECTBOX principal */
    .stSelectbox > div > div {{
        background-color: {COLOR_SELECTBOX_FONDO} !important;
        color: {COLOR_SELECTBOX_TEXTO} !important;
        border: 1px solid {COLOR_SELECTBOX_BORDE} !important;
        border-radius: 8px !important;
    }}
    .stSelectbox label {{ color: {COLOR_SELECTBOX_LABEL} !important; }}
    
    /* DROPDOWN */
    div[data-baseweb="select"] ul {{ background-color: {COLOR_DROPDOWN_FONDO} !important; }}
    div[data-baseweb="select"] li {{
        color: {COLOR_DROPDOWN_TEXTO} !important;
        background-color: {COLOR_DROPDOWN_FONDO} !important;
    }}
    div[data-baseweb="select"] li:hover {{ background-color: {COLOR_DROPDOWN_HOVER} !important; }}
    div[data-baseweb="select"] li[aria-selected="true"] {{
        background-color: {COLOR_DROPDOWN_SELECCIONADO} !important;
        color: {COLOR_DROPDOWN_SELECCIONADO_TEXTO} !important;
    }}
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] {{ background-color: {COLOR_TABS_FONDO} !important; }}
    .stTabs [data-baseweb="tab"] {{
        color: {COLOR_TAB_INACTIVA_TEXTO} !important;
        background-color: {COLOR_TAB_INACTIVA_FONDO} !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLOR_TAB_ACTIVA_FONDO} !important;
        color: {COLOR_TAB_ACTIVA_TEXTO} !important;
    }}
    
    /* Inputs */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {{
        color: black !important;
        background-color: white !important;
        border: 1px solid #ccc !important;
        border-radius: 8px !important;
    }}
    
    /* Metric cards */
    .metric-card {{
        background: white;
        border-radius: 15px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #ddd;
    }}
    .metric-value {{ font-size: 2rem; font-weight: bold; color: {COLOR_BOTON_PRIMARIO} !important; }}
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
        st.markdown(f"""
        <div style="background: white; padding: 2rem; border-radius: 20px;">
            <h1 style="text-align: center; color: {COLOR_BOTON_PRIMARIO};">💚 QTC Smart Sales</h1>
            <p style="text-align: center;">Sistema Profesional de Cotización</p>
        </div>
        """, unsafe_allow_html=True)
        user = st.text_input("👤 Usuario")
        pw = st.text_input("🔒 Contraseña", type="password")
        if st.button("Ingresar", use_container_width=True):
            if user == "admin" and pw == "qtc2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")
    st.stop()

# ============================================
# FUNCIONES PRINCIPALES
# ============================================

def corregir_numero(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "0", "0.0", "-"]:
        return 0.0
    s = str(valor).upper().replace('S/', '').replace('$', '').replace(' ', '').strip()
    if ',' in s and '.' in s:
        s = s.replace(',', '')
    elif ',' in s:
        partes = s.split(',')
        if len(partes[-1]) <= 2:
            s = s.replace(',', '.')
        else:
            s = s.replace(',', '')
    s = re.sub(r'[^\d.]', '', s)
    try:
        return float(s)
    except:
        return 0.0

def limpiar_cabeceras(df):
    for i in range(min(20, len(df))):
        fila = [str(x).upper() for x in df.iloc[i].values]
        if any(h in item for h in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO'] for item in fila):
            df.columns = [str(c).strip() for c in df.iloc[i]]
            return df.iloc[i+1:].reset_index(drop=True)
    return df

def cargar_catalogo(archivo):
    try:
        xls = pd.ExcelFile(archivo)
        hojas = xls.sheet_names
        hoja_seleccionada = st.sidebar.selectbox(
            f"📗 {archivo.name}:",
            hojas,
            key=f"cat_{archivo.name}"
        )
        df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)
        df = limpiar_cabeceras(df)
        
        col_sku = None
        col_desc = None
        columnas_precio = []
        
        for c in df.columns:
            c_str = str(c).upper()
            if any(p in c_str for p in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO']):
                if col_sku is None: col_sku = c
            if any(p in c_str for p in ['DESC', 'NOMBRE', 'PRODUCTO']):
                if col_desc is None: col_desc = c
            if any(p in c_str for p in ['PRECIO', 'CAJA', 'VIP', 'MAYOR', 'IR', 'BOX']):
                columnas_precio.append(c)
        
        if col_sku is None and len(df.columns) > 0: col_sku = df.columns[0]
        if col_desc is None and len(df.columns) > 1: col_desc = df.columns[1]
        
        return {
            'nombre': f"{archivo.name} [{hoja_seleccionada}]",
            'df': df,
            'col_sku': col_sku,
            'col_desc': col_desc,
            'columnas_precio': columnas_precio
        }
    except:
        return None

def cargar_stock(archivo):
    try:
        xls = pd.ExcelFile(archivo)
        hojas = xls.sheet_names
        hoja_seleccionada = st.sidebar.selectbox(
            f"📦 {archivo.name}:",
            hojas,
            key=f"stock_{archivo.name}"
        )
        df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)
        df = limpiar_cabeceras(df)
        
        col_sku = None
        col_stock = None
        col_comprometido = None
        
        for c in df.columns:
            c_str = str(c).upper()
            if any(p in c_str for p in ['SKU', 'COD', 'NUMERO', 'ARTICULO']):
                if col_sku is None: col_sku = c
            if 'STOCK' in c_str or 'DISPONIBLE' in c_str:
                col_stock = c
            if 'COMPROMET' in c_str:
                col_comprometido = c
        
        if col_sku is None and len(df.columns) > 0: col_sku = df.columns[0]
        if col_stock is None and len(df.columns) > 1: col_stock = df.columns[1]
        
        return {
            'nombre': f"{archivo.name} [{hoja_seleccionada}]",
            'df': df,
            'col_sku': col_sku,
            'col_stock': col_stock,
            'col_comprometido': col_comprometido
        }
    except:
        return None

def buscar_producto(catalogos, sku_buscar):
    for catalogo in catalogos:
        df = catalogo['df']
        mask = df[catalogo['col_sku']].astype(str).str.contains(sku_buscar, case=False, na=False)
        if not df[mask].empty:
            row = df[mask].iloc[0]
            return {
                'encontrado': True,
                'catalogo': catalogo['nombre'],
                'sku': str(row[catalogo['col_sku']]),
                'descripcion': str(row[catalogo['col_desc']]),
                'row': row,
                'columnas_precio': catalogo['columnas_precio']
            }
    return {'encontrado': False}

def obtener_precio(row, columnas_precio, col_seleccionada):
    if col_seleccionada and col_seleccionada in columnas_precio and col_seleccionada in row.index:
        return corregir_numero(row[col_seleccionada])
    return 0.0

def obtener_stock(sku, stocks):
    for stock in stocks:
        mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku, case=False, na=False)
        if not stock['df'][mask].empty:
            row = stock['df'][mask].iloc[0]
            stock_total = int(corregir_numero(row[stock['col_stock']])) if stock['col_stock'] else 0
            comprometido = int(corregir_numero(row[stock['col_comprometido']])) if stock['col_comprometido'] and stock['col_comprometido'] in row.index else 0
            disponible = stock_total - comprometido
            return stock_total, comprometido, disponible, stock['nombre']
    return 0, 0, 0, "Sin stock"

def buscar_en_catalogo(catalogos, termino):
    resultados = []
    for cat in catalogos:
        df = cat['df']
        mask_sku = df[cat['col_sku']].astype(str).str.contains(termino, case=False, na=False)
        mask_desc = df[cat['col_desc']].astype(str).str.contains(termino, case=False, na=False)
        for idx, row in df[mask_sku | mask_desc].iterrows():
            resultados.append({
                'SKU': str(row[cat['col_sku']]),
                'Descripción': str(row[cat['col_desc']])[:80],
                'Catálogo': cat['nombre']
            })
    return resultados

def generar_excel_cotizacion(items, cliente, ruc):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    pd.DataFrame(items).to_excel(writer, sheet_name='Cotizacion', index=False, startrow=5)
    
    workbook = writer.book
    ws = writer.sheets['Cotizacion']
    
    fmt_header = workbook.add_format({'bg_color': '#F79646', 'bold': True, 'border': 1, 'align': 'center', 'font_color': 'white'})
    fmt_money = workbook.add_format({'num_format': '"S/." #,##0.00', 'border': 1, 'align': 'right'})
    fmt_border = workbook.add_format({'border': 1})
    fmt_bold = workbook.add_format({'bold': True})
    
    ws.set_column('A:A', 20)
    ws.set_column('B:B', 75)
    ws.set_column('C:C', 12)
    ws.set_column('D:D', 18)
    ws.set_column('E:E', 18)
    
    ws.write('A1', 'FECHA:', fmt_bold)
    ws.write('B1', datetime.now().strftime("%d/%m/%Y"))
    ws.write('A2', 'CLIENTE:', fmt_bold)
    ws.write('B2', cliente.upper())
    ws.write('A3', 'RUC:', fmt_bold)
    ws.write('B3', ruc)
    
    ws.merge_range('F1:H1', 'DATOS BANCARIOS', fmt_header)
    ws.write('F2', 'BBVA SOLES:', workbook.add_format({'font_color': 'red', 'bold': True, 'border': 1}))
    ws.write('G2', '0011-0616-0100012617', fmt_border)
    
    headers = ['Código SAP', 'Descripción', 'Cantidad', 'Precio Unit.', 'Total']
    for i, header in enumerate(headers):
        ws.write(5, i, header, fmt_header)
    
    for row_idx, item in enumerate(items):
        ws.write_row(row_idx + 6, 0, [item['sku'], item['desc'], item['cant'], item['p_u'], item['total']], fmt_border)
        ws.write(row_idx + 6, 3, item['p_u'], fmt_money)
        ws.write(row_idx + 6, 4, item['total'], fmt_money)
    
    total_row = len(items) + 6
    ws.write(total_row, 3, 'TOTAL S/.', fmt_header)
    ws.write(total_row, 4, sum(item['total'] for item in items), fmt_money)
    
    writer.close()
    return output.getvalue()

# ============================================
# INTERFAZ PRINCIPAL - 3 TABS
# ============================================
st.title("💚 QTC Smart Sales Pro")
st.markdown("---")

# Inicializar session state
if 'catalogos' not in st.session_state:
    st.session_state.catalogos = []
if 'stocks' not in st.session_state:
    st.session_state.stocks = []
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 'cotizaciones' not in st.session_state:
    st.session_state.cotizaciones = 0
if 'total_prods' not in st.session_state:
    st.session_state.total_prods = 0

# Crear 3 tabs: Cotización, Buscar Productos, Dashboard
tab_cotizacion, tab_buscar, tab_dashboard = st.tabs([
    "📦 Cotización", "🔍 Buscar Productos", "📊 Dashboard"
])

# ============================================
# TAB 1: COTIZACIÓN
# ============================================
with tab_cotizacion:
    # Configuración en sidebar
    with st.sidebar:
        st.markdown("### 📂 Archivos")
        
        # Catálogos
        st.markdown("**📚 Catálogos**")
        archivos_catalogos = st.file_uploader(
            "Sube catálogos",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            key="cat_upload"
        )
        if archivos_catalogos:
            for archivo in archivos_catalogos:
                resultado = cargar_catalogo(archivo)
                if resultado:
                    st.session_state.catalogos.append(resultado)
                    st.success(f"✅ {resultado['nombre']}")
        
        # Stocks
        st.markdown("**📦 Stocks**")
        archivos_stock = st.file_uploader(
            "Sube stocks",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            key="stock_upload"
        )
        if archivos_stock:
            for archivo in archivos_stock:
                resultado = cargar_stock(archivo)
                if resultado:
                    st.session_state.stocks.append(resultado)
                    st.success(f"✅ {resultado['nombre']}")
    
    if not st.session_state.catalogos:
        st.warning("⚠️ Carga catálogos en el panel izquierdo")
    else:
        with st.expander("📋 Catálogos cargados"):
            for cat in st.session_state.catalogos:
                st.caption(f"• {cat['nombre']}")
        
        # Precio
        st.markdown("### 💰 Precio")
        todas_columnas_precio = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio']:
                todas_columnas_precio.add(col)
        
        if todas_columnas_precio:
            col_precio = st.selectbox("Columna de precio:", sorted(list(todas_columnas_precio)))
        else:
            col_precio = None
            st.warning("No hay columnas de precio")
        
        st.markdown("---")
        st.markdown("### 📝 Productos")
        st.caption("Formato: SKU:CANTIDAD (uno por línea)")
        
        texto_skus = st.text_area("SKU:CANTIDAD", height=150, 
                                   placeholder="Ejemplo:\nCG0900004CLR8:5\nCN0900009WH8:2")
        
        pedidos = []
        if texto_skus:
            for line in texto_skus.split('\n'):
                line = line.strip()
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) == 2:
                        try:
                            pedidos.append({'sku': parts[0].strip().upper(), 'cantidad': int(parts[1].strip())})
                        except:
                            pass
                elif line:
                    pedidos.append({'sku': line.strip().upper(), 'cantidad': 1})
        
        if st.button("🚀 PROCESAR", use_container_width=True, type="primary") and pedidos:
            with st.spinner("Procesando..."):
                resultados = []
                for pedido in pedidos:
                    sku = pedido['sku']
                    cant_solicitada = pedido['cantidad']
                    
                    producto = buscar_producto(st.session_state.catalogos, sku)
                    
                    if not producto['encontrado']:
                        resultados.append({
                            'id': sku, 'SKU': sku, 'Descripción': '❌ NO ENCONTRADO',
                            'Precio': 0, 'Solicitado': cant_solicitada,
                            'Stock_Total': 0, 'Comprometido': 0, 'Disponible': 0,
                            'A_Cotizar': 0, 'Total': 0,
                            'Estado': '❌ No encontrado', 'Color_Estado': 'red'
                        })
                        continue
                    
                    precio = obtener_precio(producto['row'], producto['columnas_precio'], col_precio)
                    stock, comprometido, disponible, origen = obtener_stock(sku, st.session_state.stocks)
                    
                    resultados.append({
                        'id': sku,
                        'SKU': sku,
                        'Descripción': producto['descripcion'][:80],
                        'Precio': precio,
                        'Solicitado': cant_solicitada,
                        'Stock_Total': stock,
                        'Comprometido': comprometido,
                        'Disponible': disponible,
                        'A_Cotizar': min(cant_solicitada, disponible) if disponible > 0 else 0,
                        'Total': precio * min(cant_solicitada, disponible) if disponible > 0 else 0,
                        'Estado': '✅ OK' if disponible >= cant_solicitada and precio > 0 else ('⚠️ Stock bajo' if disponible > 0 else '❌ Sin stock'),
                        'Color_Estado': COLOR_ESTADO_OK if disponible >= cant_solicitada and precio > 0 else (COLOR_ESTADO_ADVERTENCIA if disponible > 0 else COLOR_ESTADO_SIN_STOCK),
                        'Origen_Stock': origen
                    })
                
                st.session_state.resultados = resultados
        
        # Mostrar resultados editables
        if st.session_state.resultados:
            st.markdown("---")
            st.markdown("### 📊 Resultados (edita cantidades)")
            st.caption("💡 Puedes escribir cualquier cantidad, incluso si supera el stock disponible")
            
            resultados_editados = []
            
            # Encabezados
            cols = st.columns([2, 3, 1, 1, 1, 1, 1.2, 1.2, 1.5])
            cols[0].markdown("**SKU**")
            cols[1].markdown("**Descripción**")
            cols[2].markdown("**Precio**")
            cols[3].markdown("**Solicitado**")
            cols[4].markdown("**Stock**")
            cols[5].markdown("**Comprom.**")
            cols[6].markdown("**Disponible**")
            cols[7].markdown("**A Cotizar**")
            cols[8].markdown("**Estado**")
            st.divider()
            
            for i, item in enumerate(st.session_state.resultados):
                col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([2, 3, 1, 1, 1, 1, 1.2, 1.2, 1.5])
                
                col1.markdown(f"`{item['SKU']}`")
                col2.markdown(item['Descripción'][:50])
                col3.markdown(f"S/. {item['Precio']:,.2f}" if item['Precio'] > 0 else "-")
                col4.markdown(str(item['Solicitado']))
                col5.markdown(str(item['Stock_Total']))
                col6.markdown(str(item['Comprometido']))
                col7.markdown(str(item['Disponible']))
                
                # Input EDITABLE - permite poner cualquier cantidad manualmente
                nueva_cantidad = col8.number_input(
                    "Cant",
                    min_value=0,
                    max_value=9999,  # Límite alto para permitir cualquier valor manual
                    value=int(item['A_Cotizar']),
                    key=f"cant_{item['id']}_{i}",
                    label_visibility="collapsed"
                )
                
                # Recalcular total
                nuevo_total = item['Precio'] * nueva_cantidad
                
                # Determinar estado (ahora más flexible)
                if nueva_cantidad == 0:
                    estado_texto = "⏸️ Excluido"
                    color_estado = COLOR_ESTADO_EXCLUIDO
                elif item['Precio'] == 0:
                    estado_texto = "⚠️ Sin precio"
                    color_estado = COLOR_ESTADO_ADVERTENCIA
                elif nueva_cantidad <= item['Disponible']:
                    estado_texto = "✅ OK"
                    color_estado = COLOR_ESTADO_OK
                else:
                    estado_texto = f"⚠️ Excede stock ({item['Disponible']} disp.)"
                    color_estado = COLOR_ESTADO_ADVERTENCIA
                
                col9.markdown(f"<span style='color:{color_estado}'>{estado_texto}</span>", unsafe_allow_html=True)
                
                # Guardar
                item_editado = item.copy()
                item_editado['A_Cotizar'] = nueva_cantidad
                item_editado['Total'] = nuevo_total
                item_editado['Estado'] = estado_texto
                resultados_editados.append(item_editado)
                
                st.divider()
            
            # Resumen
            items_validos = [r for r in resultados_editados if r['A_Cotizar'] > 0 and r['Precio'] > 0]
            items_con_advertencia = [r for r in resultados_editados if r['A_Cotizar'] > 0 and r['A_Cotizar'] > r['Disponible'] and r['Disponible'] > 0]
            total_cotizacion = sum(r['Total'] for r in items_validos)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📦 A cotizar", len(items_validos))
            col2.metric("💰 Total", f"S/. {total_cotizacion:,.2f}")
            col3.metric("⚠️ Exceden stock", len(items_con_advertencia))
            col4.metric("⏸️ Excluidos", len(resultados_editados) - len(items_validos))
            
            # Generar cotización
            if items_validos:
                st.markdown("---")
                st.markdown("### 📥 Cotización")
                
                col_cli1, col_cli2 = st.columns(2)
                with col_cli1:
                    cliente = st.text_input("🏢 Cliente", "CLIENTE NUEVO")
                with col_cli2:
                    ruc_cliente = st.text_input("📋 RUC/DNI", "-")
                
                if st.button("📥 GENERAR EXCEL", use_container_width=True, type="primary"):
                    items_excel = [{
                        'sku': r['SKU'],
                        'desc': r['Descripción'],
                        'cant': r['A_Cotizar'],
                        'p_u': r['Precio'],
                        'total': r['Total']
                    } for r in items_validos]
                    
                    excel_data = generar_excel_cotizacion(items_excel, cliente, ruc_cliente)
                    
                    st.download_button(
                        label="💾 DESCARGAR",
                        data=excel_data,
                        file_name=f"Cotizacion_{cliente}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        use_container_width=True
                    )
                    
                    st.session_state.cotizaciones += 1
                    st.session_state.total_prods = len(items_validos)
                    st.balloons()
                    st.success("✅ Cotización generada!")

# ============================================
# TAB 2: BUSCAR PRODUCTOS
# ============================================
with tab_buscar:
    st.markdown("### 🔍 Buscar productos en catálogos")
    
    if not st.session_state.catalogos:
        st.warning("⚠️ Primero carga catálogos en la pestaña 'Cotización'")
    else:
        busqueda = st.text_input("Escribe SKU o descripción:", placeholder="Ej: cable, cargador, CN0900009WH8...")
        
        if busqueda and len(busqueda) > 2:
            with st.spinner("Buscando..."):
                resultados = buscar_en_catalogo(st.session_state.catalogos, busqueda)
            
            if resultados:
                st.success(f"✅ {len(resultados)} resultados encontrados")
                df_resultados = pd.DataFrame(resultados)
                st.dataframe(df_resultados, use_container_width=True)
                
                # Botón para transferir los primeros 10 SKU a cotización
                if st.button("📋 Transferir primeros 10 SKU a Cotización"):
                    skus_dict = {r['SKU']: 1 for r in resultados[:10]}
                    st.session_state.skus_transferidos = skus_dict
                    st.success("✅ Transferido! Ve a la pestaña Cotización")
                    st.info("Los SKU aparecerán en el área de texto con cantidad 1")
            else:
                st.warning("No se encontraron productos con ese término")

# ============================================
# TAB 3: DASHBOARD
# ============================================
with tab_dashboard:
    st.markdown("### 📊 Dashboard de Ventas")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.get('cotizaciones', 0)}</div>
            <div class="metric-label">📄 Cotizaciones Generadas</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.get('total_prods', 0)}</div>
            <div class="metric-label">🌿 Productos Cotizados</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        total_catalogos = len(st.session_state.get('catalogos', []))
        total_stocks = len(st.session_state.get('stocks', []))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_catalogos}</div>
            <div class="metric-label">📚 Catálogos</div>
            <div style="font-size:0.8rem;">+ {total_stocks} stocks</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📋 Resumen de Catálogos Cargados")
    
    if st.session_state.catalogos:
        for cat in st.session_state.catalogos:
            st.markdown(f"- **{cat['nombre']}**")
    else:
        st.info("No hay catálogos cargados")
    
    st.markdown("---")
    st.markdown("### 📋 Resumen de Stocks Cargados")
    
    if st.session_state.stocks:
        for stock in st.session_state.stocks:
            st.markdown(f"- **{stock['nombre']}**")
    else:
        st.info("No hay stocks cargados")
    
    st.markdown("---")
    st.markdown("### 🎯 Manual del Sistema")
    st.markdown("""
    **1. Cargar archivos:**
    - Sube tus catálogos de precios (Excel)
    - Sube tus reportes de stock (Excel)
    - Cada archivo permite elegir qué hoja usar
    
    **2. Configurar cotización:**
    - Selecciona la columna de precio (Caja, VIP, Mayor, etc.)
    - Ingresa los SKU en formato
