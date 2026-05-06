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

# --- ESTILOS CSS CORREGIDOS (TEXTO BLANCO EN FONDO OSCURO DEL DROPDOWN) ---
st.markdown("""
    <style>
    /* Fondo general */
    .stApp {
        background-color: #F0F2F6;
    }
    
    /* SELECTBOX - FONDO BLANCO CON TEXTO NEGRO */
    .stSelectbox > div > div {
        background-color: white !important;
        color: black !important;
        border: 1px solid #27AE60 !important;
        border-radius: 8px !important;
    }
    
    .stSelectbox > div > div > div {
        color: black !important;
    }
    
    .stSelectbox label {
        color: #1a1a2e !important;
    }
    
    /* DROPDOWN MENU - FONDO BLANCO, TEXTO NEGRO */
    div[data-baseweb="select"] > div {
        background-color: white !important;
    }
    
    div[data-baseweb="select"] ul {
        background-color: white !important;
        border: 1px solid #ccc !important;
        border-radius: 8px !important;
    }
    
    div[data-baseweb="select"] li {
        color: black !important;
        background-color: white !important;
        padding: 8px 12px !important;
    }
    
    div[data-baseweb="select"] li:hover {
        background-color: #e8f5e9 !important;
        color: black !important;
    }
    
    div[data-baseweb="select"] li[aria-selected="true"] {
        background-color: #27AE60 !important;
        color: white !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a472a 0%, #0d2818 100%);
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Botones */
    .stButton > button {
        background: #27AE60;
        color: white !important;
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Inputs */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        color: black !important;
        background-color: white !important;
        border: 1px solid #ccc !important;
        border-radius: 8px !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: white !important;
        border-radius: 10px !important;
        padding: 4px !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #1a1a2e !important;
        background-color: #f0f0f0 !important;
        border-radius: 8px !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #27AE60 !important;
        color: white !important;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #ddd;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #27AE60 !important;
    }
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
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 20px;">
            <h1 style="text-align: center; color: #27AE60;">💚 QTC Smart Sales</h1>
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

def cargar_catalogo_con_hojas(archivo):
    """Carga todas las hojas de un Excel y permite seleccionar cuál usar"""
    try:
        xls = pd.ExcelFile(archivo)
        hojas = xls.sheet_names
        
        # Mostrar selector de hoja en sidebar
        hoja_seleccionada = st.sidebar.selectbox(
            f"Hoja de {archivo.name}:",
            hojas,
            key=f"hoja_{archivo.name}"
        )
        
        df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)
        df = limpiar_cabeceras(df)
        
        # Detectar columnas
        col_sku = None
        col_desc = None
        columnas_precio = []
        
        for c in df.columns:
            c_str = str(c).upper()
            if any(p in c_str for p in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO']):
                if col_sku is None:
                    col_sku = c
            if any(p in c_str for p in ['DESC', 'NOMBRE', 'PRODUCTO']):
                if col_desc is None:
                    col_desc = c
            if any(p in c_str for p in ['PRECIO', 'CAJA', 'VIP', 'MAYOR', 'IR', 'BOX', 'SUGERIDO']):
                columnas_precio.append(c)
        
        if col_sku is None and len(df.columns) > 0:
            col_sku = df.columns[0]
        if col_desc is None and len(df.columns) > 1:
            col_desc = df.columns[1]
        
        return {
            'nombre': f"{archivo.name} - {hoja_seleccionada}",
            'df': df,
            'col_sku': col_sku,
            'col_desc': col_desc,
            'columnas_precio': columnas_precio,
            'hoja_original': hoja_seleccionada
        }
    except Exception as e:
        st.error(f"Error en {archivo.name}: {str(e)}")
        return None

def cargar_stock_con_hojas(archivo):
    """Carga stock permitiendo elegir la hoja"""
    try:
        xls = pd.ExcelFile(archivo)
        hojas = xls.sheet_names
        
        hoja_seleccionada = st.sidebar.selectbox(
            f"Hoja de stock {archivo.name}:",
            hojas,
            key=f"stock_hoja_{archivo.name}"
        )
        
        df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)
        df = limpiar_cabeceras(df)
        
        # Detectar columnas
        col_sku = None
        col_stock = None
        col_comprometido = None
        col_solicitado = None
        
        for c in df.columns:
            c_str = str(c).upper()
            if any(p in c_str for p in ['SKU', 'COD', 'NUMERO', 'ARTICULO']):
                if col_sku is None:
                    col_sku = c
            if 'STOCK' in c_str or 'DISPONIBLE' in c_str or 'EN STOCK' in c_str:
                col_stock = c
            if 'COMPROMET' in c_str:
                col_comprometido = c
            if 'SOLICIT' in c_str:
                col_solicitado = c
        
        if col_sku is None and len(df.columns) > 0:
            col_sku = df.columns[0]
        if col_stock is None and len(df.columns) > 1:
            col_stock = df.columns[1]
        
        return {
            'nombre': f"{archivo.name} - {hoja_seleccionada}",
            'df': df,
            'col_sku': col_sku,
            'col_stock': col_stock,
            'col_comprometido': col_comprometido,
            'col_solicitado': col_solicitado
        }
    except Exception as e:
        st.error(f"Error en stock {archivo.name}: {str(e)}")
        return None

def buscar_producto(catalogos, sku_buscar):
    for catalogo in catalogos:
        df = catalogo['df']
        col_sku = catalogo['col_sku']
        mask = df[col_sku].astype(str).str.contains(sku_buscar, case=False, na=False)
        if not df[mask].empty:
            row = df[mask].iloc[0]
            return {
                'encontrado': True,
                'catalogo': catalogo['nombre'],
                'sku': str(row[col_sku]),
                'descripcion': str(row[catalogo['col_desc']]),
                'row': row,
                'columnas_precio': catalogo['columnas_precio']
            }
    return {'encontrado': False}

def obtener_precio(row, columnas_precio, col_seleccionada):
    if col_seleccionada in columnas_precio and col_seleccionada in row.index:
        return corregir_numero(row[col_seleccionada])
    return 0.0

def obtener_stock(sku, stocks):
    stock_total = 0
    comprometido = 0
    solicitado = 0
    origen = ""
    
    for stock in stocks:
        mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku, case=False, na=False)
        if not stock['df'][mask].empty:
            row = stock['df'][mask].iloc[0]
            stock_total += int(corregir_numero(row[stock['col_stock']])) if stock['col_stock'] else 0
            if stock['col_comprometido']:
                comprometido += int(corregir_numero(row[stock['col_comprometido']])) if stock['col_comprometido'] in row.index else 0
            if stock['col_solicitado']:
                solicitado += int(corregir_numero(row[stock['col_solicitado']])) if stock['col_solicitado'] in row.index else 0
            origen = stock['nombre']
            break
    
    return stock_total, comprometido, solicitado, origen

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
# INTERFAZ PRINCIPAL
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

tab_cotizacion, tab_config = st.tabs(["📦 Cotización", "⚙️ Configuración"])

# ============================================
# TAB CONFIGURACIÓN
# ============================================
with tab_config:
    st.markdown("### 📂 Carga de Archivos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📚 Catálogos de Precios")
        archivos_catalogos = st.file_uploader(
            "Sube catálogos (Excel)",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            key="catalogos_upload"
        )
        
        if archivos_catalogos:
            for archivo in archivos_catalogos:
                resultado = cargar_catalogo_con_hojas(archivo)
                if resultado:
                    st.session_state.catalogos.append(resultado)
                    st.success(f"✅ {resultado['nombre']}")
    
    with col2:
        st.markdown("#### 📦 Reportes de Stock")
        st.caption("Selecciona qué hoja usar para cada archivo")
        
        archivos_stock = st.file_uploader(
            "Sube stocks (Excel)",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            key="stocks_upload"
        )
        
        if archivos_stock:
            for archivo in archivos_stock:
                resultado = cargar_stock_con_hojas(archivo)
                if resultado:
                    st.session_state.stocks.append(resultado)
                    st.success(f"✅ {resultado['nombre']}")

# ============================================
# TAB COTIZACIÓN
# ============================================
with tab_cotizacion:
    if not st.session_state.catalogos:
        st.warning("⚠️ Primero carga los catálogos en 'Configuración'")
    else:
        # Selección de precio
        st.markdown("### 💰 Precio a usar")
        
        todas_columnas_precio = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio']:
                todas_columnas_precio.add(col)
        
        if todas_columnas_precio:
            col_precio = st.selectbox(
                "Selecciona la columna de precio:",
                options=sorted(list(todas_columnas_precio)),
                help="Todos los productos usarán esta columna"
            )
        else:
            col_precio = None
            st.warning("No se detectaron columnas de precio")
        
        st.markdown("---")
        st.markdown("### 📝 Ingresa los productos")
        st.caption("Formato: SKU : CANTIDAD (uno por línea)")
        
        # Text area para SKUs
        texto_skus = st.text_area(
            "SKU:CANTIDAD",
            height=150,
            placeholder="Ejemplo:\nCG0900004CLR8:5\nCN0900009WH8:2"
        )
        
        pedidos = []
        if texto_skus:
            for line in texto_skus.split('\n'):
                line = line.strip()
                if ':' in line:
                    sku, cant = line.split(':')
                    try:
                        pedidos.append({'sku': sku.strip().upper(), 'cantidad': int(cant.strip())})
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
                    
                    # Buscar en catálogos
                    producto = buscar_producto(st.session_state.catalogos, sku)
                    
                    if not producto['encontrado']:
                        resultados.append({
                            'SKU': sku,
                            'Descripción': 'NO ENCONTRADO',
                            'Precio': 0,
                            'Solicitado': cant_solicitada,
                            'Stock': 0,
                            'Comprometido': 0,
                            'Disponible': 0,
                            'Total': 0,
                            'Estado': '❌ No encontrado'
                        })
                        continue
                    
                    # Obtener precio
                    precio = obtener_precio(producto['row'], producto['columnas_precio'], col_precio) if col_precio else 0
                    
                    # Obtener stock
                    stock, comprometido, solicitado, origen_stock = obtener_stock(sku, st.session_state.stocks)
                    disponible = stock - comprometido - solicitado
                    
                    # Estado
                    if precio == 0:
                        estado = "⚠️ Sin precio"
                    elif disponible >= cant_solicitada:
                        estado = "✅ OK"
                    elif disponible > 0:
                        estado = f"⚠️ Stock insuficiente (disp: {disponible})"
                    else:
                        estado = "❌ Sin stock"
                    
                    resultados.append({
                        'SKU': sku,
                        'Descripción': producto['descripcion'][:80],
                        'Catálogo': producto['catalogo'],
                        'Precio': precio,
                        'Solicitado': cant_solicitada,
                        'Stock': stock,
                        'Comprometido': comprometido,
                        'Disponible': disponible,
                        'Total': precio * min(cant_solicitada, disponible) if disponible > 0 else 0,
                        'Estado': estado,
                        'Origen_Stock': origen_stock
                    })
                
                st.session_state.resultados = resultados
        
        # Mostrar resultados ed
