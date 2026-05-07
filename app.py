import streamlit as st
import pandas as pd
import re, io
from datetime import datetime
from PIL import Image
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================
try:
    img_logo = Image.open("logo.png")
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon=img_logo, layout="wide")
except:
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon="💼", layout="wide")

# ============================================
# ESTILOS CSS - VERDE SUAVE CORPORATIVO
# ============================================
st.markdown("""
    <style>
    /* FONDO GENERAL */
    .stApp { background-color: #F1F8E9 !important; }
    .main .block-container { background-color: #F1F8E9 !important; }
    
    /* TEXTOS OSCUROS */
    h1, h2, h3, h4, h5, h6, p, div, span, label, .stMarkdown {
        color: #1B5E20 !important;
    }
    
    /* SIDEBAR - VERDE CORPORATIVO */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2E7D32 0%, #1B5E20 100%);
    }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* BOTONES */
    .stButton > button {
        background: #66BB6A !important;
        color: white !important;
        border-radius: 12px;
        font-weight: 600;
        border: none;
        transition: all 0.3s;
    }
    .stButton > button:hover { background: #4CAF50 !important; transform: translateY(-2px); }
    
    /* SELECTBOX */
    .stSelectbox > div > div {
        background-color: white !important;
        color: black !important;
        border: 1px solid #66BB6A !important;
        border-radius: 10px !important;
    }
    .stSelectbox > div > div > div { color: black !important; }
    .stSelectbox label { color: #1B5E20 !important; }
    
    /* DROPDOWN */
    div[data-baseweb="select"] ul { background-color: white !important; border: 1px solid #ddd !important; border-radius: 10px !important; }
    div[data-baseweb="select"] li { color: black !important; background-color: white !important; }
    div[data-baseweb="select"] li:hover { background-color: #E8F5E9 !important; }
    div[data-baseweb="select"] li[aria-selected="true"] { background-color: #66BB6A !important; color: white !important; }
    
    /* FILE UPLOADER */
    .stFileUploader > div > div {
        background-color: white !important;
        border: 1px dashed #66BB6A !important;
        border-radius: 12px !important;
    }
    .stFileUploader button { background-color: #66BB6A !important; color: white !important; }
    
    /* INPUTS */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        color: black !important;
        background-color: white !important;
        border: 1px solid #ddd !important;
        border-radius: 10px !important;
    }
    
    /* TABS */
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
    
    /* TARJETAS */
    .product-card {
        background: white;
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #C8E6C9;
        transition: all 0.2s;
    }
    .product-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); border-color: #66BB6A; }
    
    /* REPORTE DE EXCLUIDOS */
    .excluded-report {
        background: #FFF8E1;
        border-left: 4px solid #FFC107;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    .excluded-sku { font-family: monospace; font-weight: bold; color: #E65100; font-size: 0.9rem; }
    .excluded-reason { color: #FF8F00; font-size: 0.85rem; }
    
    /* SUGERENCIAS */
    .suggestion-card {
        background: #E3F2FD;
        border-left: 4px solid #2196F3;
        padding: 0.6rem;
        margin: 0.3rem 0;
        border-radius: 8px;
        font-size: 0.85rem;
    }
    
    /* MÉTRICAS */
    .metric-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        border: 1px solid #C8E6C9;
    }
    .metric-value { font-size: 2.2rem; font-weight: bold; color: #66BB6A !important; }
    
    /* BADGES */
    .badge-ok { background-color: #C8E6C9; color: #1B5E20; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
    .badge-warning { background-color: #FFF3E0; color: #E65100; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
    .badge-danger { background-color: #FFCDD2; color: #C62828; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR CON LOGO
# ============================================
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.markdown("<h2 style='color: #66BB6A; text-align: center;'>💚 QTC Pro</h2>", unsafe_allow_html=True)
    st.markdown("---")
    if "cotizaciones" in st.session_state:
        st.metric("📄 Cotizaciones", st.session_state.get("cotizaciones", 0))
        st.metric("📦 Productos", st.session_state.get("total_prods", 0))

# ============================================
# LOGIN
# ============================================
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
    """Convierte texto con formato de moneda a número float"""
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
    """Detecta y limpia las cabeceras de un DataFrame"""
    for i in range(min(20, len(df))):
        fila = [str(x).upper() for x in df.iloc[i].values]
        if any(h in item for h in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO', 'COD SAP'] for item in fila):
            df.columns = [str(c).strip() for c in df.iloc[i]]
            return df.iloc[i+1:].reset_index(drop=True)
    return df

def cargar_catalogo(archivo):
    """Carga catálogo de precios con detección inteligente de columnas"""
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
        
        # Palabras clave para detectar columnas
        posibles_skus = ['SKU', 'COD', 'CODIGO', 'SAP', 'NUMERO', 'ARTICULO', 'COD SAP', 'NUMERO DE ARTICULO']
        posibles_desc = ['DESC', 'DESCRIPCION', 'NOMBRE', 'PRODUCTO', 'DESCRIPCIÓN', 'NOMBRE PRODUCTO']
        posibles_precios = ['PRECIO', 'CAJA', 'VIP', 'MAYOR', 'IR', 'BOX', 'SUGERIDO', 'P. IR', 'P. BOX', 'P. VIP']
        
        # Detectar columnas
        col_sku = next((c for c in df.columns if any(p in str(c).upper().replace('_', ' ').replace('-', ' ') for p in posibles_skus)), df.columns[0])
        col_desc = next((c for c in df.columns if any(p in str(c).upper().replace('_', ' ').replace('-', ' ') for p in posibles_desc)), df.columns[1] if len(df.columns) > 1 else df.columns[0])
        columnas_precio = [c for c in df.columns if any(p in str(c).upper().replace('_', ' ').replace('-', ' ') for p in posibles_precios)]
        
        with st.sidebar.expander(f"🔍 {archivo.name[:25]}..."):
            st.caption(f"📌 SKU: **{col_sku}**")
            st.caption(f"📌 Descripción: **{col_desc}**")
            if columnas_precio:
                st.caption(f"💰 Precios: **{', '.join(columnas_precio[:3])}**")
        
        return {
            'nombre': f"{archivo.name} [{hoja_seleccionada}]",
            'df': df,
            'col_sku': col_sku,
            'col_desc': col_desc,
            'columnas_precio': columnas_precio
        }
    except Exception as e:
        st.error(f"Error en {archivo.name}: {str(e)}")
        return None

def cargar_stock(archivo):
    """Carga archivo de stock con detección inteligente de columnas"""
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
        
        posibles_skus = ['SKU', 'COD', 'CODIGO', 'NUMERO', 'ARTICULO', 'NUMERO DE ARTICULO']
        posibles_stock = ['STOCK', 'DISPONIBLE', 'CANT', 'CANTIDAD', 'SALDO', 'EN STOCK', 'AVAILABLE']
        
        col_sku = next((c for c in df.columns if any(p in str(c).upper().replace('_', ' ').replace('-', ' ') for p in posibles_skus)), df.columns[0])
        col_stock = next((c for c in df.columns if any(p in str(c).upper().replace('_', ' ').replace('-', ' ') for p in posibles_stock)), df.columns[1] if len(df.columns) > 1 else df.columns[0])
        
        with st.sidebar.expander(f"🔍 Stock: {archivo.name[:25]}..."):
            st.caption(f"📌 SKU: **{col_sku}**")
            st.caption(f"📌 Stock: **{col_stock}**")
        
        return {
            'nombre': f"{archivo.name} [{hoja_seleccionada}]",
            'df': df,
            'col_sku': col_sku,
            'col_stock': col_stock
        }
    except Exception as e:
        st.error(f"Error en stock {archivo.name}: {str(e)}")
        return None

def buscar_precio(catalogos, sku):
    """Busca SKU en catálogos de precios con múltiples estrategias"""
    sku_limpio = sku.strip().upper()
    
    for cat in catalogos:
        df = cat['df']
        col_sku = cat['col_sku']
        
        # Estrategia 1: Coincidencia exacta
        mask = df[col_sku].astype(str).str.strip().str.upper() == sku_limpio
        if not df[mask].empty:
            row = df[mask].iloc[0]
            return {'encontrado': True, 'catalogo': cat['nombre'], 'row': row, 'columnas_precio': cat['columnas_precio'], 'descripcion': str(row[cat['col_desc']])}
        
        # Estrategia 2: Contiene
        mask = df[col_sku].astype(str).str.contains(sku_limpio, case=False, na=False, regex=False)
        if not df[mask].empty:
            row = df[mask].iloc[0]
            return {'encontrado': True, 'catalogo': cat['nombre'], 'row': row, 'columnas_precio': cat['columnas_precio'], 'descripcion': str(row[cat['col_desc']])}
    
    return {'encontrado': False}

def buscar_stock(stocks, sku):
    """Busca stock del SKU en archivos de stock"""
    sku_limpio = sku.strip().upper()
    for stock in stocks:
        mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False, regex=False)
        if not stock['df'][mask].empty:
            row = stock['df'][mask].iloc[0]
            cantidad = int(corregir_numero(row[stock['col_stock']])) if stock['col_stock'] else 0
            return cantidad, stock['nombre']
    return 0, "Sin stock"

def buscar_sugerencias(stocks, catalogos, sku_sin_precio):
    """Busca posibles coincidencias por descripción cuando el SKU no tiene precio"""
    # Obtener descripción del stock
    descripcion_stock = ""
    for stock in stocks:
        mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku_sin_precio, case=False, na=False, regex=False)
        if not stock['df'][mask].empty:
            for col in stock['df'].columns:
                if any(p in str(col).upper() for p in ['DESC', 'NOMBRE', 'PRODUCTO']):
                    descripcion_stock = str(stock['df'][mask].iloc[0][col])
                    break
            break
    
    if not descripcion_stock:
        return []
    
    # Buscar por palabras clave
    palabras = descripcion_stock.upper().split()[:4]
    sugerencias = []
    
    for cat in catalogos:
        df = cat['df']
        col_desc = cat['col_desc']
        
        for idx, row in df.iterrows():
            desc_cat = str(row[col_desc]).upper()
            coincidencias = sum(1 for p in palabras if p in desc_cat)
            if coincidencias >= 2:
                col_sku_cat = cat['col_sku']
                sugerencias.append({
                    'sku': str(row[col_sku_cat]),
                    'descripcion': str(row[col_desc])[:70],
                    'coincidencia': f"{coincidencias}/{len(palabras)} palabras",
                    'catalogo': cat['nombre'][:30]
                })
    
    return sugerencias[:3]

def obtener_precio(row, columnas_precio, col_seleccionada):
    """Obtiene el precio de la columna seleccionada"""
    if col_seleccionada and col_seleccionada in columnas_precio and col_seleccionada in row.index:
        return corregir_numero(row[col_seleccionada])
    return 0.0

def generar_excel(items, cliente, ruc):
    """Genera Excel con formato profesional de cotización"""
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
try:
    col_logo, col_title = st.columns([1, 6])
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

tab_cotizacion, tab_dashboard = st.tabs(["📦 Cotización", "📊 Dashboard"])

# ============================================
# TAB 1: COTIZACIÓN
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
                resultado = cargar_catalogo(archivo)
                if resultado:
                    st.session_state.catalogos.append(resultado)
                    st.success(f"✅ {resultado['nombre'][:50]}")
        
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
                    st.success(f"✅ {resultado['nombre'][:50]}")
    
    if not st.session_state.catalogos:
        st.warning("🌿 Carga catálogos en el panel izquierdo")
    else:
        with st.expander("📋 Catálogos cargados"):
            for cat in st.session_state.catalogos:
                st.caption(f"• {cat['nombre'][:60]}")
        
        if st.session_state.stocks:
            with st.expander("📋 Stocks cargados"):
                for stock in st.session_state.stocks:
                    st.caption(f"• {stock['nombre'][:60]}")
        
        # Configuración de precios
        st.markdown("### 💰 Configuración de Precios")
        todas_columnas_precio = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio']:
                todas_columnas_precio.add(col)
        
        if todas_columnas_precio:
            col_precio = st.selectbox("🎯 Selecciona la columna de precio:", sorted(list(todas_columnas_precio)))
        else:
            col_precio = None
            st.warning("⚠️ No se detectaron columnas de precio")
        
        st.markdown("---")
        st.markdown("### 📝 Ingresa los productos")
        st.caption("💡 Formato: SKU:CANTIDAD (uno por línea)")
        
        texto_skus = st.text_area("", height=150, placeholder="Ejemplo:\nRN0200046BK8:5\nCN0900009WH8:2")
        
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
            with st.spinner("🔍 Procesando..."):
                resultados = []
                for pedido in pedidos:
                    sku = pedido['sku']
                    cant = pedido['cantidad']
                    
                    # Buscar precio y stock
                    precio_info = buscar_precio(st.session_state.catalogos, sku)
                    stock, origen_stock = buscar_stock(st.session_state.stocks, sku)
                    
                    if precio_info['encontrado'] and stock > 0:
                        precio = obtener_precio(precio_info['row'], precio_info['columnas_precio'], col_precio)
                        resultados.append({
                            'id': sku, 'SKU': sku, 'Descripción': precio_info['descripcion'][:80],
                            'Precio': precio, 'Solicitado': cant, 'Stock': stock,
                            'A_Cotizar': min(cant, stock), 'Total': precio * min(cant, stock),
                            'Estado': '✅ OK', 'Color': 'green', 'Motivo': None
                        })
                    elif precio_info['encontrado'] and stock == 0:
                        precio = obtener_precio(precio_info['row'], precio_info['columnas_precio'], col_precio)
                        resultados.append({
                            'id': sku, 'SKU': sku, 'Descripción': precio_info['descripcion'][:80],
                            'Precio': precio, 'Solicitado': cant, 'Stock': 0,
                            'A_Cotizar': 0, 'Total': 0, 'Estado': '⚠️ Sin stock', 'Color': 'orange',
                            'Motivo': 'Sin stock disponible'
                        })
                    elif not precio_info['encontrado'] and stock > 0:
                        sugerencias = buscar_sugerencias(st.session_state.stocks, st.session_state.catalogos, sku)
                        resultados.append({
                            'id': sku, 'SKU': sku,
                            'Descripción': f"Producto con stock ({stock} uds) pero sin precio",
                            'Precio': 0, 'Solicitado': cant, 'Stock': stock,
                            'A_Cotizar': 0, 'Total': 0, 'Estado': '⚠️ Sin precio', 'Color': 'orange',
                            'Motivo': 'No está en lista de precios', 'Sugerencias': sugerencias
                        })
                    else:
                        resultados.append({
                            'id': sku, 'SKU': sku, 'Descripción': 'Producto no encontrado',
                            'Precio': 0, 'Solicitado': cant, 'Stock': 0,
                            'A_Cotizar': 0, 'Total': 0, 'Estado': '❌ No encontrado', 'Color': 'red',
                            'Motivo': 'No existe en catálogos ni stock'
                        })
                
                st.session_state.resultados = resultados
        
        # Mostrar resultados
        if st.session_state.resultados:
            st.markdown("---")
            st.markdown("### 📊 Resultados")
            
            resultados_editados = []
            
            # Encabezados
            c1, c2, c3, c4, c5, c6, c7 = st.columns([2, 3, 1.2, 1, 1, 1.2, 1.5])
            c1.markdown("**SKU**"); c2.markdown("**Descripción**"); c3.markdown("**Precio**")
            c4.markdown("**Sol.**"); c5.markdown("**Stock**"); c6.markdown("**A Cotizar**"); c7.markdown("**Estado**")
            st.divider()
            
            for i, item in enumerate(st.session_state.resultados):
                col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 3, 1.2, 1, 1, 1.2, 1.5])
                
                col1.markdown(f"`{item['SKU']}`")
                col2.markdown(item['Descripción'][:50])
                col3.markdown(f"S/. {item['Precio']:,.2f}" if item['Precio'] > 0 else "❌")
                col4.markdown(str(item['Solicitado']))
                col5.markdown(str(item['Stock']))
                
                if item['Precio'] > 0 and item['Stock'] > 0:
                    nueva_cant = col6.number_input("Cant", min_value=0, max_value=item['Stock'], value=int(item['A_Cotizar']), key=f"qty_{item['id']}_{i}", label_visibility="collapsed")
                else:
                    nueva_cant = 0
                    col6.markdown("0")
                
                col7.markdown(f"<span style='color:{item['Color']}'>{item['Estado']}</span>", unsafe_allow_html=True)
                
                # Mostrar sugerencias si existen
                if item.get('Sugerencias'):
                    with st.expander("🔍 Ver posibles coincidencias"):
                        for sug in item['Sugerencias']:
                            st.markdown(f"""
                            <div class="suggestion-card">
                                <b>📦 {sug['sku']}</b><br>
                                {sug['descripcion']}<br>
                                <span style="font-size:0.7rem;">🎯 {sug['coincidencia']} | 📁 {sug['catalogo']}</span>
                            </div>
                            """, unsafe_allow_html=True)
                
                item['A_Cotizar'] = nueva_cant
                item['Total'] = item['Precio'] * nueva_cant
                resultados_editados.append(item)
                st.divider()
            
            # Excluidos
            excluidos = [r for r in resultados_editados if r['A_Cotizar'] == 0 and r['Motivo']]
            if excluidos:
                st.markdown("### ⚠️ Productos no incluidos")
                for exc in excluidos:
                    st.markdown(f"""
                    <div class="excluded-report">
                        <span class="excluded-sku">📦 {exc['SKU']}</span><br>
                        <span style="font-size:0.85rem;">{exc['Descripción'][:60]}</span><br>
                        <span class="excluded-reason">🚫 {exc['Motivo']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Resumen
            items_validos = [r for r in resultados_editados if r['A_Cotizar'] > 0 and r['Precio'] > 0]
            total = sum(r['Total'] for r in items_validos)
            
            m1, m2, m3 = st.columns(3)
            m1.metric("✅ A cotizar", len(items_validos))
            m2.metric("💰 Total", f"S/. {total:,.2f}")
            m3.metric("⚠️ Excluidos", len(resultados_editados) - len(items_validos))
            
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
                    excel = generar_excel(items_excel, cliente, ruc_cliente)
                    st.download_button("💾 DESCARGAR", data=excel, file_name=f"Cotizacion_{cliente}.xlsx", use_container_width=True)
                    st.session_state.cotizaciones += 1
                    st.session_state.total_prods = len(items_validos)
                    st.balloons()
                    st.success("✅ Cotización generada!")

# ============================================
# TAB 2: DASHBOARD
# ============================================
with tab_dashboard:
    st.markdown("### 📊 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📄 Cotizaciones", st.session_state.get('cotizaciones', 0))
    col2.metric("🌿 Productos", st.session_state.get('total_prods', 0))
    col3.metric("📚 Catálogos", len(st.session_state.get('catalogos', [])))
    
    st.markdown("---")
    st.markdown("### 📋 Catálogos Cargados")
    for cat in st.session_state.get('catalogos', []):
        st.markdown(f"- **{cat['nombre'][:60]}**")
    
    st.markdown("---")
    st.markdown("### 📋 Stocks Cargados")
    for stock in st.session_state.get('stocks', []):
        st.markdown(f"- **{stock['nombre'][:60]}**")
    
    st.markdown("---")
    st.markdown("### 🎯 Ayuda Rápida")
    st.markdown("""
    **Formato de entrada:** `SKU:CANTIDAD` (uno por línea)
    
    **Ejemplo:**
