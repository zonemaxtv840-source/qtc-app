import streamlit as st
import pandas as pd
import re, io
from datetime import datetime
from PIL import Image
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# --- CONFIGURACIÓN DE PÁGINA CON LOGO ---
try:
    img_logo = Image.open("logo.png")
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon=img_logo, layout="wide")
except:
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon="💼", layout="wide")

# --- ESTILOS CSS - CLAROS, VERDE SUAVE, TEXTOS OSCUROS ---
st.markdown("""
    <style>
    /* FONDO GENERAL CLARO */
    .stApp {
        background-color: #F1F8E9 !important;
    }
    .main .block-container {
        background-color: #F1F8E9 !important;
    }
    
    /* TODOS LOS TEXTOS OSCUROS */
    h1, h2, h3, h4, h5, h6, p, div, span, label, .stMarkdown {
        color: #1B5E20 !important;
    }
    
    /* SIDEBAR - VERDE OSCURO CON TEXTO CLARO */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2E7D32 0%, #1B5E20 100%);
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* BOTONES VERDE SUAVE */
    .stButton > button {
        background: #66BB6A !important;
        color: white !important;
        border-radius: 12px;
        font-weight: 600;
        border: none;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background: #4CAF50 !important;
        transform: translateY(-2px);
    }
    
    /* SELECTBOX - FONDO BLANCO, TEXTO NEGRO */
    .stSelectbox > div > div {
        background-color: white !important;
        color: black !important;
        border: 1px solid #66BB6A !important;
        border-radius: 10px !important;
    }
    .stSelectbox > div > div > div {
        color: black !important;
    }
    .stSelectbox label {
        color: #1B5E20 !important;
    }
    
    /* DROPDOWN - OPCIONES BLANCAS CON TEXTO NEGRO */
    div[data-baseweb="select"] ul {
        background-color: white !important;
        border: 1px solid #ddd !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="select"] li {
        color: black !important;
        background-color: white !important;
        padding: 8px 12px !important;
    }
    div[data-baseweb="select"] li:hover {
        background-color: #E8F5E9 !important;
    }
    div[data-baseweb="select"] li[aria-selected="true"] {
        background-color: #66BB6A !important;
        color: white !important;
    }
    
    /* FILE UPLOADER - FONDO BLANCO */
    .stFileUploader > div > div {
        background-color: white !important;
        border: 1px dashed #66BB6A !important;
        border-radius: 12px !important;
    }
    .stFileUploader button {
        background-color: #66BB6A !important;
        color: white !important;
    }
    
    /* INPUTS - FONDO BLANCO, TEXTO NEGRO */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        color: black !important;
        background-color: white !important;
        border: 1px solid #ddd !important;
        border-radius: 10px !important;
        font-size: 14px !important;
    }
    
    /* TABS - CLARAS */
    .stTabs [data-baseweb="tab-list"] {
        background-color: white !important;
        border-radius: 12px !important;
        padding: 6px !important;
        gap: 8px !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #1B5E20 !important;
        background-color: #F5F5F5 !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-weight: 500 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #66BB6A !important;
        color: white !important;
    }
    
    /* TARJETAS DE PRODUCTO - BLANCAS CON BORDE VERDE SUAVE */
    .product-card {
        background: white;
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #C8E6C9;
        transition: all 0.2s;
    }
    .product-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        border-color: #66BB6A;
    }
    
    /* BADGES DE STOCK */
    .stock-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .stock-good { background-color: #C8E6C9; color: #1B5E20 !important; }
    .stock-low { background-color: #FFF3E0; color: #E65100 !important; }
    .stock-none { background-color: #FFCDD2; color: #C62828 !important; }
    .stock-selected { background-color: #66BB6A; color: white !important; }
    .no-price { background-color: #FFECB3; color: #FF8F00 !important; }
    
    /* REPORTE DE EXCLUIDOS */
    .excluded-report {
        background: #FFF8E1;
        border-left: 4px solid #FFC107;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    .excluded-sku {
        font-family: monospace;
        font-weight: bold;
        color: #E65100;
        font-size: 0.9rem;
    }
    .excluded-reason {
        color: #FF8F00;
        font-size: 0.85rem;
    }
    
    /* MÉTRICAS DASHBOARD */
    .metric-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        border: 1px solid #C8E6C9;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #66BB6A !important;
    }
    
    /* RESULTADOS DE BÚSQUEDA */
    .search-result-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #66BB6A;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .search-sku {
        font-size: 1rem;
        font-weight: bold;
        font-family: monospace;
        color: #2E7D32;
    }
    .search-desc {
        font-size: 0.85rem;
        color: #555;
        margin: 4px 0;
    }
    .search-price {
        font-size: 1rem;
        font-weight: bold;
        color: #66BB6A;
    }
    .search-stock {
        font-size: 0.8rem;
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px solid #eee;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR CON LOGO ---
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.markdown('<h2 style="color: #66BB6A;">💚 QTC Pro</h2>', unsafe_allow_html=True)
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
        try:
            logo = Image.open("logo.png")
            st.image(logo, width=120)
        except:
            pass
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05);">
            <h1 style="text-align: center; color: #66BB6A;">💚 QTC Smart Sales</h1>
            <p style="text-align: center; color: #1B5E20;">Sistema Profesional de Cotización</p>
        </div>
        """, unsafe_allow_html=True)
        user = st.text_input("👤 Usuario")
        pw = st.text_input("🔒 Contraseña", type="password")
        if st.button("🌿 Ingresar", use_container_width=True):
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
        if any(h in item for h in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO', 'COD SAP'] for item in fila):
            df.columns = [str(c).strip() for c in df.iloc[i]]
            return df.iloc[i+1:].reset_index(drop=True)
    return df

def cargar_excel(archivo):
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
            if any(p in c_str for p in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO', 'COD SAP']):
                if col_sku is None: col_sku = c
            if any(p in c_str for p in ['DESC', 'NOMBRE', 'PRODUCTO']):
                if col_desc is None: col_desc = c
            if any(p in c_str for p in ['PRECIO', 'CAJA', 'VIP', 'MAYOR', 'IR', 'BOX', 'SUGERIDO', 'P.']):
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
        
        for c in df.columns:
            c_str = str(c).upper()
            if any(p in c_str for p in ['SKU', 'COD', 'NUMERO', 'ARTICULO']):
                if col_sku is None: col_sku = c
            if any(p in c_str for p in ['STOCK', 'DISPONIBLE', 'CANT', 'SALDO', 'EN STOCK']):
                if col_stock is None: col_stock = c
        
        if col_sku is None and len(df.columns) > 0: col_sku = df.columns[0]
        if col_stock is None and len(df.columns) > 1: col_stock = df.columns[1]
        
        return {
            'nombre': f"{archivo.name} [{hoja_seleccionada}]",
            'df': df,
            'col_sku': col_sku,
            'col_stock': col_stock
        }
    except:
        return None

def buscar_producto(catalogos, sku_buscar):
    for catalogo in catalogos:
        df = catalogo['df']
        mask = df[catalogo['col_sku']].astype(str).str.contains(sku_buscar, case=False, na=False, regex=False)
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

def buscar_en_catalogos_detallado(catalogos, termino, stocks, col_precio_consulta=None):
    """Búsqueda detallada con información de stock"""
    resultados_dict = {}
    
    # Separar términos (soporta búsqueda múltiple por espacios o comas)
    if ',' in termino:
        terminos = [t.strip() for t in termino.split(',')]
    else:
        terminos = [t.strip() for t in termino.split() if len(t.strip()) >= 2]
    
    for cat in catalogos:
        df = cat['df']
        for term in terminos:
            mask_sku = df[cat['col_sku']].astype(str).str.contains(term, case=False, na=False, regex=False)
            mask_desc = df[cat['col_desc']].astype(str).str.contains(term, case=False, na=False, regex=False)
            for idx, row in df[mask_sku | mask_desc].iterrows():
                sku = str(row[cat['col_sku']])
                
                if sku not in resultados_dict:
                    # Obtener precio
                    precio = None
                    if col_precio_consulta and col_precio_consulta != "(No mostrar precio)":
                        precio = corregir_numero(row[col_precio_consulta]) if col_precio_consulta in df.columns else 0
                    
                    # Obtener stock de TODAS las hojas
                    stocks_info = []
                    stock_total = 0
                    if stocks:
                        for stock in stocks:
                            mask_stock = stock['df'][stock['col_sku']].astype(str).str.contains(sku, case=False, na=False, regex=False)
                            if not stock['df'][mask_stock].empty:
                                row_stock = stock['df'][mask_stock].iloc[0]
                                cantidad = int(corregir_numero(row_stock[stock['col_stock']])) if stock['col_stock'] else 0
                                stocks_info.append({
                                    'origen': stock['nombre'],
                                    'stock': cantidad
                                })
                                stock_total += cantidad
                    
                    resultados_dict[sku] = {
                        'SKU': sku,
                        'Descripción': str(row[cat['col_desc']])[:100],
                        'Catálogo': cat['nombre'],
                        'Precio': precio,
                        'Stock_Total': stock_total,
                        'Stocks_Detalle': stocks_info
                    }
    
    return list(resultados_dict.values())

def obtener_precio(row, columnas_precio, col_seleccionada):
    if col_seleccionada and col_seleccionada in columnas_precio and col_seleccionada in row.index:
        return corregir_numero(row[col_seleccionada])
    return 0.0

def obtener_stock_detallado(sku, stocks):
    """Obtiene stock de todas las hojas"""
    resultados = []
    stock_total = 0
    
    for stock in stocks:
        mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku, case=False, na=False, regex=False)
        if not stock['df'][mask].empty:
            row = stock['df'][mask].iloc[0]
            cantidad = int(corregir_numero(row[stock['col_stock']])) if stock['col_stock'] else 0
            resultados.append({
                'origen': stock['nombre'],
                'stock': cantidad
            })
            stock_total += cantidad
    
    return stock_total, resultados

def obtener_stock(sku, stocks):
    for stock in stocks:
        mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku, case=False, na=False, regex=False)
        if not stock['df'][mask].empty:
            row = stock['df'][mask].iloc[0]
            cantidad = int(corregir_numero(row[stock['col_stock']])) if stock['col_stock'] else 0
            return cantidad, stock['nombre']
    return 0, "Sin stock"

def generar_excel_cotizacion(items, cliente, ruc):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    pd.DataFrame(items).to_excel(writer, sheet_name='Cotizacion', index=False, startrow=5)
    
    workbook = writer.book
    ws = writer.sheets['Cotizacion']
    
    fmt_header = workbook.add_format({'bg_color': '#66BB6A', 'bold': True, 'border': 1, 'align': 'center', 'font_color': 'white'})
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
# Logo en el título
try:
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        st.image("logo.png", width=70)
    with col_title:
        st.title("QTC Smart Sales Pro")
except:
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
if 'productos_seleccionados' not in st.session_state:
    st.session_state.productos_seleccionados = {}

tab_cotizacion, tab_buscar, tab_dashboard = st.tabs([
    "📦 Cotización", "🔍 Buscar Productos", "📊 Dashboard"
])

# ============================================
# TAB COTIZACIÓN
# ============================================
with tab_cotizacion:
    with st.sidebar:
        st.markdown("### 📂 Archivos")
        
        st.markdown("**📚 Catálogos de Precios**")
        archivos_catalogos = st.file_uploader(
            "Sube catálogos (Excel)",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            key="cat_upload"
        )
        if archivos_catalogos:
            for archivo in archivos_catalogos:
                resultado = cargar_excel(archivo)
                if resultado:
                    st.session_state.catalogos.append(resultado)
                    st.success(f"✅ {resultado['nombre']}")
        
        st.markdown("**📦 Reportes de Stock**")
        archivos_stock = st.file_uploader(
            "Sube stocks (Excel)",
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
        st.warning("🌿 Carga catálogos en el panel izquierdo")
    else:
        with st.expander("📋 Catálogos cargados"):
            for cat in st.session_state.catalogos:
                st.caption(f"• {cat['nombre']}")
        
        st.markdown("### 💰 Configuración de Precios")
        todas_columnas_precio = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio']:
                todas_columnas_precio.add(col)
        
        if todas_columnas_precio:
            col_precio = st.selectbox("Selecciona la columna de precio:", sorted(list(todas_columnas_precio)))
        else:
            col_precio = None
            st.warning("No hay columnas de precio detectadas")
        
        st.markdown("---")
        st.markdown("### 📝 Ingresa los productos")
        st.caption("Formato: SKU:CANTIDAD (uno por línea)")
        
        if 'skus_transferidos' in st.session_state:
            texto_defecto = "\n".join([f"{sku}:{cant}" for sku, cant in st.session_state.skus_transferidos.items()])
            del st.session_state.skus_transferidos
        else:
            texto_defecto = ""
        
        texto_skus = st.text_area("SKU:CANTIDAD", height=150, value=texto_defecto,
                                   placeholder="Ejemplo:\nCN0900009WH8:5\nRN0200065BK8:2")
        
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
        
        if st.button("🚀 PROCESAR COTIZACIÓN", use_container_width=True, type="primary") and pedidos:
            with st.spinner("Procesando..."):
                resultados = []
                for pedido in pedidos:
                    sku = pedido['sku']
                    cant_solicitada = pedido['cantidad']
                    
                    producto = buscar_producto(st.session_state.catalogos, sku)
                    stock_disponible, origen_stock = obtener_stock(sku, st.session_state.stocks)
                    
                    if producto['encontrado'] and stock_disponible > 0:
                        precio = obtener_precio(producto['row'], producto['columnas_precio'], col_precio)
                        estado = "✅ OK"
                        color_estado = "green"
                        descripcion = producto['descripcion'][:80]
                        origen_precio = producto['catalogo']
                        precio_valido = precio
                        motivo_exclusion = None
                        
                    elif producto['encontrado'] and stock_disponible == 0:
                        precio = obtener_precio(producto['row'], producto['columnas_precio'], col_precio)
                        estado = "⚠️ Sin stock"
                        color_estado = "orange"
                        descripcion = producto['descripcion'][:80]
                        origen_precio = producto['catalogo']
                        precio_valido = precio
                        motivo_exclusion = "Sin stock disponible"
                        
                    elif not producto['encontrado'] and stock_disponible > 0:
                        estado = "⚠️ Sin precio"
                        color_estado = "orange"
                        descripcion = "Producto con stock pero sin precio en catálogo"
                        precio_valido = 0
                        origen_precio = "No encontrado"
                        motivo_exclusion = "No está en lista de precios"
                        
                    else:
                        estado = "❌ No encontrado"
                        color_estado = "red"
                        descripcion = "Producto no existe en catálogos ni stock"
                        precio_valido = 0
                        origen_precio = "No encontrado"
                        stock_disponible = 0
                        motivo_exclusion = "No encontrado en catálogo ni stock"
                    
                    resultados.append({
                        'id': sku,
                        'SKU': sku,
                        'Descripción': descripcion,
                        'Precio': precio_valido,
                        'Solicitado': cant_solicitada,
                        'Stock_Disponible': stock_disponible,
                        'A_Cotizar': min(cant_solicitada, stock_disponible) if stock_disponible > 0 and precio_valido > 0 else 0,
                        'Total': precio_valido * min(cant_solicitada, stock_disponible) if stock_disponible > 0 and precio_valido > 0 else 0,
                        'Estado': estado,
                        'Color_Estado': color_estado,
                        'Origen_Precio': origen_precio if producto['encontrado'] else "❌ Sin precio",
                        'Origen_Stock': origen_stock,
                        'Motivo_Exclusion': motivo_exclusion
                    })
                
                st.session_state.resultados = resultados
        
        if st.session_state.resultados:
            st.markdown("---")
            st.markdown("### 📊 Resultados de la cotización")
            
            resultados_editados = []
            
            cols = st.columns([2, 3, 1.2, 1, 1, 1.2, 1.5])
            cols[0].markdown("**SKU**")
            cols[1].markdown("**Descripción**")
            cols[2].markdown("**Precio**")
            cols[3].markdown("**Sol.**")
            cols[4].markdown("**Stock**")
            cols[5].markdown("**A Cotizar**")
            cols[6].markdown("**Estado**")
            st.divider()
            
            for i, item in enumerate(st.session_state.resultados):
                col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 3, 1.2, 1, 1, 1.2, 1.5])
                
                col1.markdown(f"`{item['SKU']}`")
                col2.markdown(item['Descripción'][:50])
                
                if item['Precio'] > 0:
                    col3.markdown(f"S/. {item['Precio']:,.2f}")
                else:
                    col3.markdown("❌ Sin precio")
                
                col4.markdown(str(item['Solicitado']))
                col5.markdown(str(item['Stock_Disponible']))
                
                if item['Precio'] > 0 and item['Stock_Disponible'] > 0:
                    nueva_cantidad = col6.number_input(
                        "Cant", min_value=0, max_value=item['Stock_Disponible'],
                        value=int(item['A_Cotizar']),
                        key=f"cant_{item['id']}_{i}",
                        label_visibility="collapsed"
                    )
                else:
                    nueva_cantidad = 0
                    col6.markdown("0")
                
                col7.markdown(f"<span style='color:{item['Color_Estado']}'>{item['Estado']}</span>", unsafe_allow_html=True)
                
                item_editado = item.copy()
                item_editado['A_Cotizar'] = nueva_cantidad
                item_editado['Total'] = item['Precio'] * nueva_cantidad
                resultados_editados.append(item_editado)
                
                st.divider()
            
            # Reporte de excluidos
            productos_excluidos = [r for r in resultados_editados if r['A_Cotizar'] == 0 and r['Motivo_Exclusion'] is not None]
            
            if productos_excluidos:
                st.markdown("### ⚠️ Productos no incluidos en la cotización")
                for excl in productos_excluidos:
                    st.markdown(f"""
                    <div class="excluded-report">
                        <span class="excluded-sku">📦 {excl['SKU']}</span><br>
                        <span style="font-size:0.85rem; color:#555;">{excl['Descripción'][:60]}</span><br>
                        <span class="excluded-reason">🚫 Motivo: {excl['Motivo_Exclusion']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Resumen
            items_validos = [r for r in resultados_editados if r['A_Cotizar'] > 0 and r['Precio'] > 0]
            total_cotizacion = sum(r['Total'] for r in items_validos)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("✅ A cotizar", len(items_validos))
            col2.metric("💰 Total", f"S/. {total_cotizacion:,.2f}")
            col3.metric("⚠️ Excluidos", len(resultados_editados) - len(items_validos))
            
            if items_validos:
                st.markdown("---")
                st.markdown("### 📥 Generar Cotización")
                col_cli1, col_cli2 = st.columns(2)
                with col_cli1:
                    cliente = st.text_input("🏢 Cliente", "CLIENTE NUEVO")
                with col_cli2:
                    ruc_cliente = st.text_input("📋 RUC/DNI", "-")
                
                if st.button("📥 GENERAR EXCEL", use_container_width=True, type="primary"):
                    items_excel = [{'sku': r['SKU'], 'desc': r['Descripción'], 'cant': r['A_Cotizar'], 'p_u': r['Precio'], 'total': r['Total']} for r in items_validos]
                    excel_data = generar_excel_cotizacion(items_excel, cliente, ruc_cliente)
                    st.download_button(label="💾 DESCARGAR", data=excel_data, file_name=f"Cotizacion_{cliente}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", use_container_width=True)
                    st.session_state.cotizaciones += 1
                    st.session_state.total_prods = len(items_validos)
                    st.balloons()
                    st.success("✅ Cotización generada!")

# ============================================
# TAB BUSCAR PRODUCTOS (UNIFICADO Y MEJORADO)
# ============================================
with tab_buscar:
    st.markdown("### 🔍 Buscar Productos")
    st.markdown("💡 **Busca por SKU o descripción** - Separa términos con comas o espacios para búsqueda múltiple")
    
    if not st.session_state.catalogos:
        st.warning("🌿 Primero carga catálogos en la pestaña 'Cotización'")
    else:
        # Selector de precio para mostrar
        todas_columnas = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio']:
                todas_columnas.add(col)
        
        col_precio_consulta = st.selectbox(
            "💰 Mostrar precios en columna:",
            options=["(No mostrar precio)"] + sorted(list(todas_columnas)),
            key="precio_busqueda"
        )
        
        # Campo de búsqueda unificado
        busqueda = st.text_input(
            "🔎 Buscar productos:", 
            placeholder="Escribe SKU o descripción... Ej: cable, cargador, CN0900009WH8"
        )
        
        if busqueda and len(busqueda) >= 2:
            with st.spinner("🔍 Buscando productos y consultando stock..."):
                precio_seleccionado = None if col_precio_consulta == "(No mostrar precio)" else col_precio_consulta
                resultados = buscar_en_catalogos_detallado(
                    st.session_state.catalogos, 
                    busqueda, 
                    st.session_state.stocks,
                    precio_seleccionado
                )
            
            if resultados:
                st.success(f"✅ {len(resultados)} resultados encontrados")
                
                for res in resultados:
                    # Determinar color del stock
                    if res['Stock_Total'] <= 0:
                        stock_color = "🔴 Sin stock"
                        stock_class = "stock-none"
                    elif res['Stock_Total'] < 10:
                        stock_color = f"🟠 Stock bajo: {res['Stock_Total']} unidades"
                        stock_class = "stock-low"
                    else:
                        stock_color = f"🟢 Stock disponible: {res['Stock_Total']} unidades"
                        stock_class = "stock-good"
                    
                    # Construir detalles de stock por hoja
                    stock_detalle = ""
                    for s in res['Stocks_Detalle']:
                        if s['stock'] > 0:
                            stock_detalle += f"<span class='stock-badge {stock_class}' style='background:#E8F5E9;'>{s['origen'][:30]}: {s['stock']} uds</span> "
                    
                    st.markdown(f"""
                    <div class="search-result-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <span class="search-sku">📦 {res['SKU']}</span><br>
                                <span class="search-desc">{res['Descripción']}</span>
                            </div>
                            <div>
                                <span class="search-price">{f'S/. {res["Precio"]:,.2f}' if res["Precio"] else "Sin precio"}</span>
                            </div>
                        </div>
                        <div class="search-stock">
                            {stock_detalle}
                            <br>
                            <span style="font-size:0.75rem; color:#888;">📁 Catálogo: {res['Catálogo'][:40]}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Botón para agregar
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Agregar a cotización**")
                    with col2:
                        cantidad = st.number_input(
                            "Cant",
                            min_value=0,
                            max_value=999,
                            value=0,
                            key=f"add_{res['SKU']}",
                            label_visibility="collapsed"
                        )
                        if cantidad > 0:
                            st.session_state.productos_seleccionados[res['SKU']] = st.session_state.productos_seleccionados.get(res['SKU'], 0) + cantidad
                    st.divider()
            else:
                st.warning("No se encontraron productos. Intenta con otros términos.")
        
        # Mostrar productos seleccionados
        if st.session_state.productos_seleccionados:
            st.markdown("---")
            st.markdown(f"### ✅ Productos seleccionados ({len(st.session_state.productos_seleccionados)})")
            
            # Mostrar tabla de seleccionados con resumen de stock
            seleccionados_lista = []
            for sku, cant in st.session_state.productos_seleccionados.items():
                stock_total, _ = obtener_stock(sku, st.session_state.stocks)
                seleccionados_lista.append({
                    'SKU': sku,
                    'Cantidad a cotizar': cant,
                    'Stock disponible': stock_total,
                    'Estado': '⚠️ Stock insuficiente' if cant > stock_total else '✅ OK'
                })
            
            st.dataframe(pd.DataFrame(seleccionados_lista), use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Limpiar todo", use_container_width=True):
                    st.session_state.productos_seleccionados = {}
                    st.rerun()
            with col2:
                if st.button("📋 TRANSFERIR A COTIZACIÓN", use_container_width=True, type="primary"):
                    st.session_state.skus_transferidos = st.session_state.productos_seleccionados.copy()
                    st.session_state.productos_seleccionados = {}
                    st.success(f"✅ {len(st.session_state.skus_transferidos)} productos transferidos!")
                    st.info("👉 Ve a la pestaña 'Cotización' y haz clic en PROCESAR")

# ============================================
# TAB DASHBOARD
# ============================================
with tab_dashboard:
    st.markdown("### 📊 Dashboard de Ventas")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.get('cotizaciones', 0)}</div>
            <div class="metric-label">📄 Cotizaciones</div>
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
            <div style="font-size:0.8rem;">📦 {total_stocks} stocks</div>
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
st.markdown("*💚 QTC Smart Sales Pro - Sistema Profesional de Cotización*")
