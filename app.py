# app.py - QTC Smart Sales Pro v4.1
import streamlit as st
import pandas as pd
import re
import io
from datetime import datetime
from PIL import Image
import warnings
from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher

warnings.filterwarnings('ignore')

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================

st.set_page_config(
    page_title="QTC Smart Sales Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS COMPLETO
# ============================================

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
        border-right: 1px solid #e94560;
    }
    
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #e94560 !important;
    }
    
    .result-card {
        background: white;
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 5px solid #e94560;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .result-card, .result-card * {
        color: #1a1a2e !important;
    }
    
    .badge-yessica {
        background: #4CAF50;
        color: white !important;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: bold;
        display: inline-block;
        margin: 2px;
    }
    
    .badge-apri004 {
        background: #FF9800;
        color: #1a1a2e !important;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: bold;
        display: inline-block;
        margin: 2px;
    }
    
    .badge-apri001 {
        background: #f44336;
        color: white !important;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: bold;
        display: inline-block;
        margin: 2px;
    }
    
    .badge-warning {
        background: #ff9800;
        color: #1a1a2e !important;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: bold;
        display: inline-block;
    }
    
    .counter-summary {
        background: #f0f2f6;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        display: flex;
        gap: 1.5rem;
        flex-wrap: wrap;
        border: 1px solid #e0e0e0;
    }
    
    .counter-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        background: white;
    }
    
    .counter-number {
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .counter-label {
        color: #666;
    }
    
    .login-card {
        background: rgba(255,255,255,0.95);
        border-radius: 28px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        animation: fadeInUp 0.5s ease-out;
        max-width: 450px;
        margin: 0 auto;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(40px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .footer {
        text-align: center;
        padding: 1rem;
        color: #888;
        font-size: 0.7rem;
        border-top: 1px solid #333;
        margin-top: 2rem;
    }
    
    .alternativa-item {
        background: white;
        border-radius: 10px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border: 1px solid #FFE0B2;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

def corregir_numero(valor) -> float:
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

def limpiar_cabeceras(df: pd.DataFrame) -> pd.DataFrame:
    for i in range(min(20, len(df))):
        fila = [str(x).upper() for x in df.iloc[i].values]
        if any(h in item for h in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO'] for item in fila):
            df.columns = [str(c).strip() for c in df.iloc[i]]
            return df.iloc[i+1:].reset_index(drop=True)
    return df

def cargar_archivo(uploaded_file) -> Optional[pd.DataFrame]:
    nombre = uploaded_file.name.lower()
    try:
        if nombre.endswith('.csv'):
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except:
                df = pd.read_csv(uploaded_file, encoding='latin-1')
        else:
            df = pd.read_excel(uploaded_file)
        return limpiar_cabeceras(df)
    except Exception as e:
        st.error(f"Error: {str(e)[:80]}")
        return None

def detectar_columna_sku(df: pd.DataFrame) -> str:
    posibles = ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO', 'CODIGO']
    for col in df.columns:
        col_upper = str(col).upper()
        for posible in posibles:
            if posible.upper() in col_upper:
                return col
    return df.columns[0]

def detectar_columna_descripcion(df: pd.DataFrame) -> str:
    posibles = ['DESC', 'DESCRIPCION', 'NOMBRE', 'PRODUCTO', 'GOODS']
    for col in df.columns:
        col_upper = str(col).upper()
        for posible in posibles:
            if posible.upper() in col_upper:
                return col
    return None

def detectar_columnas_precio(df: pd.DataFrame) -> Dict:
    precios = {}
    mapeo = {'P. IR': ['IR', 'MAYORISTA', 'MAYOR'], 
             'P. BOX': ['BOX', 'CAJA'], 
             'P. VIP': ['VIP']}
    
    for key, patrones in mapeo.items():
        for col in df.columns:
            col_upper = str(col).upper()
            for patron in patrones:
                if patron in col_upper:
                    precios[key] = col
                    break
            if key in precios:
                break
    
    if not precios and 'PRECIO' in [str(c).upper() for c in df.columns]:
        precios['P. VIP'] = 'PRECIO'
    
    return precios

def cargar_catalogo(archivo) -> Optional[Dict]:
    df = cargar_archivo(archivo)
    if df is None:
        return None
    
    return {
        'nombre': archivo.name,
        'df': df,
        'col_sku': detectar_columna_sku(df),
        'col_desc': detectar_columna_descripcion(df),
        'precios': detectar_columnas_precio(df)
    }

def cargar_stock(archivos, modo: str) -> List[Dict]:
    stocks = []
    
    for archivo in archivos:
        try:
            xls = pd.ExcelFile(archivo)
            for hoja in xls.sheet_names:
                hoja_upper = hoja.upper()
                if modo == "XIAOMI":
                    if not any(h in hoja_upper for h in ['APRI', 'YESSICA']):
                        continue
                else:
                    if 'APRI.001' not in hoja_upper:
                        continue
                
                df = pd.read_excel(archivo, sheet_name=hoja)
                df = limpiar_cabeceras(df)
                
                stocks.append({
                    'nombre': f"{archivo.name} [{hoja}]",
                    'df': df,
                    'col_sku': detectar_columna_sku(df),
                    'hoja': hoja
                })
                st.success(f"✅ {archivo.name} → {hoja}")
        except Exception as e:
            st.error(f"Error: {str(e)[:80]}")
    
    return stocks

# ============================================
# FUNCIONES DE SIMILITUD Y BÚSQUEDA
# ============================================

def calcular_similitud(texto1: str, texto2: str) -> float:
    if not texto1 or not texto2:
        return 0.0
    
    texto1 = texto1.lower().strip()
    texto2 = texto2.lower().strip()
    
    if texto1 == texto2:
        return 100.0
    
    palabras1 = set(texto1.split())
    palabras2 = set(texto2.split())
    
    interseccion = len(palabras1.intersection(palabras2))
    union = len(palabras1.union(palabras2))
    
    if union == 0:
        return 0.0
    
    jaccard = interseccion / union
    sequence_match = SequenceMatcher(None, texto1, texto2).ratio()
    
    similitud = (jaccard * 0.7 + sequence_match * 0.3) * 100
    return round(similitud, 1)

def buscar_stock_para_sku(sku: str, stocks: List[Dict]) -> Dict:
    sku_limpio = sku.strip().upper()
    stock_yessica = 0
    stock_apri004 = 0
    stock_apri001 = 0
    
    for stock in stocks:
        df = stock['df']
        df_sku = df[stock['col_sku']].astype(str).str.strip().str.upper()
        mask = df_sku == sku_limpio
        if mask.any():
            for _, row in df[mask].iterrows():
                col_cant = None
                for col in df.columns:
                    col_upper = str(col).upper()
                    if any(p in col_upper for p in ['CANT', 'STOCK', 'DISPONIBLE', 'UNIDADES']):
                        col_cant = col
                        break
                
                if col_cant:
                    cantidad = int(corregir_numero(row[col_cant]))
                    hoja = stock['hoja'].upper()
                    if 'YESSICA' in hoja:
                        stock_yessica += cantidad
                    elif 'APRI.004' in hoja:
                        stock_apri004 += cantidad
                    elif 'APRI.001' in hoja:
                        stock_apri001 += cantidad
    
    return {
        'yessica': stock_yessica,
        'apri004': stock_apri004,
        'apri001': stock_apri001,
        'total': stock_yessica + stock_apri004 + stock_apri001
    }

def encontrar_alternativas_mismo_producto(sku_buscado: str, descripcion_buscada: str, 
                                           catalogos: List[Dict], stocks: List[Dict], 
                                           precio_key: str, umbral: float = 70.0) -> List[Dict]:
    alternativas = []
    sku_buscado_limpio = sku_buscado.strip().upper()
    
    if not descripcion_buscada or descripcion_buscada == f"SKU: {sku_buscado}":
        return alternativas
    
    for cat in catalogos:
        df = cat['df']
        if not cat['col_desc']:
            continue
            
        for _, row in df.iterrows():
            sku_alternativo = str(row[cat['col_sku']]).strip().upper()
            
            if sku_alternativo == sku_buscado_limpio:
                continue
            
            desc_alternativa = str(row[cat['col_desc']])[:200]
            similitud = calcular_similitud(descripcion_buscada, desc_alternativa)
            
            if similitud >= umbral:
                stock_info = buscar_stock_para_sku(sku_alternativo, stocks)
                
                precio = 0.0
                if precio_key in cat['precios']:
                    col_precio = cat['precios'][precio_key]
                    precio = corregir_numero(row[col_precio])
                
                alternativas.append({
                    'sku': sku_alternativo,
                    'descripcion': desc_alternativa,
                    'precio': precio,
                    'stock_yessica': stock_info['yessica'],
                    'stock_apri004': stock_info['apri004'],
                    'stock_apri001': stock_info['apri001'],
                    'stock_total': stock_info['total'],
                    'tiene_stock': stock_info['total'] > 0,
                    'tiene_precio': precio > 0,
                    'similitud': similitud
                })
    
    vistos = set()
    alternativas_unicas = []
    for alt in alternativas:
        if alt['sku'] not in vistos:
            vistos.add(alt['sku'])
            alternativas_unicas.append(alt)
    
    alternativas_unicas.sort(key=lambda x: (-x['similitud'], -x['stock_total']))
    return alternativas_unicas[:5]

# ============================================
# FUNCIÓN PRINCIPAL MODIFICADA
# ============================================

def buscar_producto(sku: str, catalogos: List[Dict], stocks: List[Dict], precio_key: str) -> Dict:
    """Busca producto por SKU. Si tiene stock pero no precio, busca SKU equivalente por descripción."""
    sku_limpio = sku.strip().upper()
    
    # PASO 1: BUSCAR STOCK
    stock_info = buscar_stock_para_sku(sku_limpio, stocks)
    
    # PASO 2: BUSCAR DESCRIPCIÓN
    descripcion = f"SKU: {sku}"
    precio = 0.0
    sku_equivalente = None
    similitud_equivalente = 0
    
    # 2a. Buscar en catálogos por SKU exacto
    for cat in catalogos:
        df = cat['df']
        df_sku = df[cat['col_sku']].astype(str).str.strip().str.upper()
        mask = df_sku == sku_limpio
        if mask.any():
            row = df[mask].iloc[0]
            if precio_key in cat['precios']:
                col_precio = cat['precios'][precio_key]
                precio = corregir_numero(row[col_precio])
            if cat['col_desc']:
                descripcion = str(row[cat['col_desc']])[:200]
            break
    
    # 2b. Si no encontró descripción en catálogos pero tiene stock, buscarla en STOCK
    if descripcion == f"SKU: {sku}" and stock_info['total'] > 0:
        for stock in stocks:
            df = stock['df']
            df_sku = df[stock['col_sku']].astype(str).str.strip().str.upper()
            mask = df_sku == sku_limpio
            if mask.any():
                row = df[mask].iloc[0]
                for col in df.columns:
                    col_upper = str(col).upper()
                    if any(p in col_upper for p in ['DESC', 'DESCRIPCION', 'PRODUCTO', 'NOMBRE', 'ARTICULO', 'GOODS']):
                        desc_stock = str(row[col])[:200]
                        if desc_stock and desc_stock != 'nan':
                            descripcion = desc_stock
                            break
                break
    
    # PASO 3: SI TIENE STOCK PERO NO PRECIO → BUSCAR SKU EQUIVALENTE POR DESCRIPCIÓN
    if precio == 0 and stock_info['total'] > 0 and descripcion and descripcion != f"SKU: {sku}":
        mejor_match = None
        mejor_similitud = 70.0
        
        for cat in catalogos:
            df = cat['df']
            if not cat['col_desc']:
                continue
            
            for _, row in df.iterrows():
                desc_catalogo = str(row[cat['col_desc']])[:200]
                similitud = calcular_similitud(descripcion, desc_catalogo)
                
                if similitud >= mejor_similitud:
                    mejor_similitud = similitud
                    sku_match = str(row[cat['col_sku']]).strip().upper()
                    
                    if sku_match == sku_limpio:
                        continue
                    
                    precio_match = 0.0
                    if precio_key in cat['precios']:
                        col_precio = cat['precios'][precio_key]
                        precio_match = corregir_numero(row[col_precio])
                    
                    mejor_match = {
                        'sku': sku_match,
                        'descripcion': desc_catalogo,
                        'precio': precio_match,
                        'similitud': similitud
                    }
        
        if mejor_match and mejor_match['precio'] > 0:
            sku_equivalente = mejor_match['sku']
            similitud_equivalente = mejor_match['similitud']
    
    # PASO 4: BUSCAR ALTERNATIVAS ADICIONALES
    alternativas = []
    if precio == 0 and stock_info['total'] > 0 and descripcion and descripcion != f"SKU: {sku}":
        alternativas = encontrar_alternativas_mismo_producto(
            sku, descripcion, catalogos, stocks, precio_key, umbral=70.0
        )
    
    return {
        'sku': sku,
        'descripcion': descripcion,
        'precio': precio,
        'stock_yessica': stock_info['yessica'],
        'stock_apri004': stock_info['apri004'],
        'stock_apri001': stock_info['apri001'],
        'stock_total': stock_info['total'],
        'tiene_stock': stock_info['total'] > 0,
        'tiene_precio': precio > 0,
        'usa_apri001': stock_info['apri001'] > 0 and stock_info['yessica'] == 0 and stock_info['apri004'] == 0,
        'sku_equivalente': sku_equivalente,
        'similitud_equivalente': similitud_equivalente,
        'alternativas': alternativas
    }

def construir_badge_stock(stock_yessica, stock_apri004, stock_apri001):
    badges = []
    if stock_yessica > 0:
        badges.append(f'<span class="badge-yessica">🟢 YESSICA: {stock_yessica}</span>')
    if stock_apri004 > 0:
        badges.append(f'<span class="badge-apri004">🟡 APRI.004: {stock_apri004}</span>')
    if stock_apri001 > 0:
        badges.append(f'<span class="badge-apri001">🔴 APRI.001: {stock_apri001} ⚠️</span>')
    if not badges:
        return '<span class="badge-warning">❌ Sin stock</span>'
    return ' '.join(badges)

def generar_excel(items: List[Dict], cliente: str, ruc: str) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame(items)
        df.to_excel(writer, sheet_name='Cotizacion', index=False, startrow=5)
        
        workbook = writer.book
        ws = writer.sheets['Cotizacion']
        
        fmt_header = workbook.add_format({'bg_color': '#e94560', 'bold': True, 'border': 1, 'align': 'center', 'font_color': 'white'})
        fmt_money = workbook.add_format({'num_format': '"S/." #,##0.00', 'border': 1, 'align': 'right'})
        fmt_border = workbook.add_format({'border': 1})
        fmt_bold = workbook.add_format({'bold': True})
        
        ws.write('A1', 'FECHA:', fmt_bold)
        ws.write('B1', datetime.now().strftime("%d/%m/%Y"))
        ws.write('A2', 'CLIENTE:', fmt_bold)
        ws.write('B2', cliente.upper())
        ws.write('A3', 'RUC:', fmt_bold)
        ws.write('B3', ruc)
        
        headers = ['SKU', 'Descripción', 'Cantidad', 'Precio Unit.', 'Total']
        for i, header in enumerate(headers):
            ws.write(5, i, header, fmt_header)
        
        for row_idx, item in enumerate(items):
            ws.write(row_idx + 6, 0, item['sku'], fmt_border)
            ws.write(row_idx + 6, 1, item['descripcion'], fmt_border)
            ws.write(row_idx + 6, 2, item['cantidad'], fmt_border)
            ws.write(row_idx + 6, 3, item['precio'], fmt_money)
            ws.write(row_idx + 6, 4, item['total'], fmt_money)
        
        total_row = len(items) + 6
        ws.write(total_row, 3, 'TOTAL S/.', fmt_header)
        ws.write(total_row, 4, sum(item['total'] for item in items), fmt_money)
    
    return output.getvalue()

# ============================================
# INICIALIZACIÓN DE SESIÓN
# ============================================

if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'modo' not in st.session_state:
    st.session_state.modo = "XIAOMI"
if 'precio_key' not in st.session_state:
    st.session_state.precio_key = "P. VIP"
if 'catalogos' not in st.session_state:
    st.session_state.catalogos = []
if 'stocks' not in st.session_state:
    st.session_state.stocks = []
if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# ============================================
# LOGIN
# ============================================

if not st.session_state.auth:
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        try:
            st.image("logo.png", width=100)
        except:
            st.markdown("<h1 style='color:#e94560;'>QTC</h1>", unsafe_allow_html=True)
        
        st.markdown("<h2 style='color:#1a1a2e;'>QTC Smart Sales Pro</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#666;'>Sistema Profesional de Cotización</p>", unsafe_allow_html=True)
        
        user = st.text_input("👤 Usuario", placeholder="Ingresa tu usuario")
        pw = st.text_input("🔒 Contraseña", type="password", placeholder="Ingresa tu contraseña")
        
        if st.button("🚀 Ingresar", use_container_width=True):
            if user == "admin" and pw == "qtc2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")
                st.info("💡 Usuario: admin | Contraseña: qtc2026")
        
        st.markdown("<div class='footer'>⚡ QTC Smart Sales Pro</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.stop()

# ============================================
# HEADER
# ============================================

col1, col2, col3 = st.columns([1, 5, 2])
with col1:
    try:
        st.image("logo.png", width=60)
    except:
        st.markdown("**QTC**", unsafe_allow_html=True)
with col2:
    st.markdown("# QTC Smart Sales Pro")
    st.caption("Sistema Profesional de Cotización")
with col3:
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 12px; text-align: right;">
        <span>👤 admin</span><br>
        <span style="font-size: 0.7rem;">Administrador</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 Cerrar Sesión", key="logout"):
        st.session_state.auth = False
        st.session_state.carrito = []
        st.rerun()

st.markdown("---")

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("### 🎯 Configuración")
    
    modo = st.radio(
        "Modo de cotización",
        ["XIAOMI", "GENERAL"],
        index=0 if st.session_state.modo == "XIAOMI" else 1
    )
    if modo != st.session_state.modo:
        st.session_state.modo = modo
        st.session_state.stocks = []
        st.session_state.carrito = []
        st.rerun()
    
    st.markdown("---")
    
    precio_opcion = st.radio(
        "💰 Nivel de precio",
        ["P. VIP", "P. BOX", "P. IR"],
        index=0
    )
    st.session_state.precio_key = precio_opcion
    
    st.markdown("---")
    
    st.markdown("### 📂 Archivos")
    
    st.markdown("**📚 Catálogos de precios**")
    archivos_cat = st.file_uploader(
        "Excel o CSV",
        type=['xlsx', 'xls', 'csv'],
        accept_multiple_files=True,
        key="cat_upload"
    )
    if archivos_cat:
        st.session_state.catalogos = []
        for archivo in archivos_cat:
            cat = cargar_catalogo(archivo)
            if cat:
                st.session_state.catalogos.append(cat)
                st.success(f"✅ {archivo.name[:30]}")
    
    st.markdown("**📦 Reportes de stock**")
    st.caption("Prioridad: YESSICA → APRI.004 → APRI.001")
    archivos_stock = st.file_uploader(
        "Excel",
        type=['xlsx', 'xls'],
        accept_multiple_files=True,
        key="stock_upload"
    )
    if archivos_stock:
        st.session_state.stocks = cargar_stock(archivos_stock, st.session_state.modo)
    
    st.markdown("---")
    
    if st.session_state.carrito:
        st.markdown(f"### 🛒 Carrito")
        st.metric("Productos", len(st.session_state.carrito))
        total = sum(item['total'] for item in st.session_state.carrito)
        st.metric("Total", f"S/ {total:,.2f}")
        
        if st.button("🧹 Limpiar carrito", use_container_width=True):
            st.session_state.carrito = []
            st.rerun()

# ============================================
# TABS PRINCIPALES
# ============================================

tab1, tab2, tab3 = st.tabs(["📦 MODO MASIVO (Bulk)", "🔍 BÚSQUEDA INTELIGENTE", "🛒 CARRITO DE COTIZACIÓN"])

# ========== TAB 1: MODO MASIVO ==========
with tab1:
    st.markdown("### 📦 Ingresa productos en formato masivo")
    st.caption("Formato: `SKU:CANTIDAD` (uno por línea)")
    
    texto_bulk = st.text_area(
        "",
        height=200,
        placeholder="Ejemplo:\nRN9401276NA8:100\nCN0200047BK8:100\nCN0200053NA8:10\nRN0200065BK8:50"
    )
    
    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        if st.button("🚀 Procesar lista", type="primary", use_container_width=True):
            if texto_bulk and st.session_state.catalogos and st.session_state.stocks:
                pedidos = []
                for line in texto_bulk.strip().split('\n'):
                    line = line.strip()
                    if ':' in line:
                        parts = line.split(':')
                        if len(parts) == 2:
                            try:
                                sku = parts[0].strip().upper()
                                cant = int(parts[1].strip())
                                if cant > 0:
                                    pedidos.append({'sku': sku, 'cantidad': cant})
                            except:
                                pass
                
                if pedidos:
                    with st.spinner("Procesando..."):
                        resultados_procesados = []
                        encontrados = 0
                        con_precio = 0
                        con_stock = 0
                        
                        for pedido in pedidos:
                            prod = buscar_producto(pedido['sku'], st.session_state.catalogos, st.session_state.stocks, st.session_state.precio_key)
                            
                            if prod['tiene_precio']:
                                encontrados += 1
                                con_precio += 1
                            
                            if prod['tiene_stock']:
                                con_stock += 1
                            
                            if prod['tiene_precio'] and prod['tiene_stock']:
                                cantidad_cotizar = min(pedido['cantidad'], prod['stock_total'])
                                estado = "✅ OK"
                                if cantidad_cotizar < pedido['cantidad']:
                                    estado = f"⚠️ Stock insuficiente ({cantidad_cotizar}/{pedido['cantidad']})"
                            elif not prod['tiene_precio']:
                                cantidad_cotizar = 0
                                estado = "❌ Sin precio"
                            else:
                                cantidad_cotizar = 0
                                estado = "❌ Sin stock"
                            
                            resultados_procesados.append({
                                **prod,
                                'cantidad_solicitada': pedido['cantidad'],
                                'cantidad_cotizar': cantidad_cotizar,
                                'estado': estado
                            })
                        
                        st.session_state.resultados_bulk = resultados_procesados
                        
                        total_ingresados = len(pedidos)
                        total_encontrados = encontrados
                        total_con_stock = con_stock
                        total_sin_precio = total_ingresados - total_encontrados
                        total_sin_stock = total_ingresados - total_con_stock
                        
                        st.markdown(f"""
                        <div class="counter-summary">
                            <div class="counter-item">
                                <span>📋</span>
                                <span class="counter-label">Ingresados:</span>
                                <span class="counter-number">{total_ingresados}</span>
                            </div>
                            <div class="counter-item" style="background: #4CAF50; color: white;">
                                <span>✅</span>
                                <span class="counter-label" style="color: white;">Encontrados:</span>
                                <span class="counter-number" style="color: white;">{total_encontrados}</span>
                            </div>
                            <div class="counter-item">
                                <span>📦</span>
                                <span class="counter-label">Con stock:</span>
                                <span class="counter-number">{total_con_stock}</span>
                            </div>
                            <div class="counter-item" style="background: #ffebee;">
                                <span>❌</span>
                                <span class="counter-label">Sin precio:</span>
                                <span class="counter-number" style="color: #f44336;">{total_sin_precio}</span>
                            </div>
                            <div class="counter-item" style="background: #ffebee;">
                                <span>🚫</span>
                                <span class="counter-label">Sin stock:</span>
                                <span class="counter-number" style="color: #f44336;">{total_sin_stock}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Reporte de productos no cotizables
                        sin_precio = [p for p in resultados_procesados if not p['tiene_precio'] and p['tiene_stock']]
                        sin_stock = [p for p in resultados_procesados if p['tiene_precio'] and not p['tiene_stock']]
                        sin_ambos = [p for p in resultados_procesados if not p['tiene_precio'] and not p['tiene_stock']]
                        
                        if sin_precio or sin_stock or sin_ambos:
                            st.markdown("""
                            <div style="background: #fff3e0; border-radius: 12px; padding: 1rem; margin: 1rem 0; border-left: 4px solid #ff9800;">
                                <strong style="color: #e65100;">⚠️ REPORTE DE PRODUCTOS NO COTIZABLES</strong>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if sin_precio:
                                st.markdown("<strong style='color:#f57c00;'>💰 Sin precio (existen en stock):</strong>", unsafe_allow_html=True)
                                df_sp = pd.DataFrame([{'SKU': p['sku'], 'Descripción': p['descripcion'][:50], 'Stock': p['stock_total']} for p in sin_precio])
                                st.dataframe(df_sp, use_container_width=True, hide_index=True)
                            
                            if sin_stock:
                                st.markdown("<strong style='color:#c62828;'>📦 Sin stock (existen en catálogo):</strong>", unsafe_allow_html=True)
                                df_ss = pd.DataFrame([{'SKU': p['sku'], 'Descripción': p['descripcion'][:50], 'Precio': f"S/ {p['precio']:.2f}"} for p in sin_stock])
                                st.dataframe(df_ss, use_container_width=True, hide_index=True)
                            
                            if sin_ambos:
                                st.markdown("<strong style='color:#b71c1c;'>❌ No encontrado (sin precio Y sin stock):</strong>", unsafe_allow_html=True)
                                df_sa = pd.DataFrame([{'SKU': p['sku'], 'Descripción': p['descripcion'][:50]} for p in sin_ambos])
                                st.dataframe(df_sa, use_container_width=True, hide_index=True)
                        
                        st.success(f"✅ Procesados {len(pedidos)} productos")
                        st.rerun()
                else:
                    st.warning("No se encontraron productos válidos")
            else:
                st.warning("Carga catálogos y stock primero")
    
    with col_b2:
        if st.button("📋 Agregar válidos al carrito", use_container_width=True):
            if hasattr(st.session_state, 'resultados_bulk'):
                agregados = 0
                for prod in st.session_state.resultados_bulk:
                    if prod['cantidad_cotizar'] > 0 and prod['tiene_precio']:
                        item_carrito = {
                            'sku': prod['sku'],
                            'descripcion': prod['descripcion'],
                            'cantidad': prod['cantidad_cotizar'],
                            'precio': prod['precio'],
                            'total': prod['precio'] * prod['cantidad_cotizar'],
                            'stock_yessica': prod['stock_yessica'],
                            'stock_apri004': prod['stock_apri004'],
                            'stock_apri001': prod['stock_apri001']
                        }
                        st.session_state.carrito.append(item_carrito)
                        agregados += 1
                st.success(f"✅ Agregados {agregados} productos al carrito")
                st.rerun()
    
    if hasattr(st.session_state, 'resultados_bulk') and st.session_state.resultados_bulk:
        st.markdown("### 📊 Resultados del procesamiento")
        
        for prod in st.session_state.resultados_bulk:
            badge_stock = construir_badge_stock(prod['stock_yessica'], prod['stock_apri004'], prod['stock_apri001'])
            
            estado_color = "🟢" if "OK" in prod['estado'] else "🟡" if "⚠️" in prod['estado'] else "🔴"
            
            st.markdown(f"""
            <div class="result-card">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <strong>📦 {prod['sku']}</strong><br>
                        <span style="font-size: 0.85rem;">{prod['descripcion']}</span>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 1.2rem;">{estado_color}</span>
                    </div>
                </div>
                <div style="margin-top: 8px;">
                    💰 Precio {st.session_state.precio_key}: <strong>S/ {prod['precio']:,.2f}</strong> | 
                    📦 Stock total: <strong>{prod['stock_total']}</strong>
                </div>
                <div style="margin-top: 8px;">
                    {badge_stock}
                </div>
                <div style="margin-top: 8px;">
                    📋 Solicitado: {prod['cantidad_solicitada']} | ✅ A cotizar: <strong>{prod['cantidad_cotizar']}</strong>
                </div>
                <div style="margin-top: 8px;">
                    <span class="badge-warning">{prod['estado']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)




# ========== TAB 2: BÚSQUEDA INTELIGENTE (VERSIÓN MEJORADA - BUSCA EN STOCK) ==========
with tab2:
    st.markdown("### 🔍 Buscar productos")
    st.caption("Escribe SKU o descripción - Busca en precios y en stock")
    
    busqueda = st.text_input("", placeholder="Ej: 'cargador', 'Type-C earphones', 'RN9401276NA8'")
    
    if busqueda and len(busqueda) >= 2 and st.session_state.catalogos and st.session_state.stocks:
        with st.spinner("🔍 Buscando en catálogos y stock..."):
            resultados_busqueda = []
            skus_vistos = set()
            
            # 1. BUSCAR EN CATÁLOGOS DE PRECIOS
            for cat in st.session_state.catalogos:
                df = cat['df']
                mask_sku = df[cat['col_sku']].astype(str).str.contains(busqueda, case=False, na=False)
                mask_desc = pd.Series([False] * len(df))
                if cat['col_desc']:
                    mask_desc = df[cat['col_desc']].astype(str).str.contains(busqueda, case=False, na=False)
                mask = mask_sku | mask_desc
                
                for _, row in df[mask].iterrows():
                    sku = str(row[cat['col_sku']]).strip().upper()
                    if sku in skus_vistos:
                        continue
                    skus_vistos.add(sku)
                    prod = buscar_producto(sku, st.session_state.catalogos, st.session_state.stocks, st.session_state.precio_key)
                    resultados_busqueda.append(prod)
            
            # 2. BUSCAR EN ARCHIVOS DE STOCK (para SKU que tienen stock pero no precio)
            for stock in st.session_state.stocks:
                df = stock['df']
                col_sku = stock['col_sku']
                col_desc = None
                for col in df.columns:
                    if any(p in str(col).upper() for p in ['DESC', 'NOMBRE', 'PRODUCTO', 'Descripción del artículo']):
                        col_desc = col
                        break
                
                if col_desc:
                    mask_desc = df[col_desc].astype(str).str.contains(busqueda, case=False, na=False)
                    for _, row in df[mask_desc].iterrows():
                        sku = str(row[col_sku]).strip().upper()
                        if sku in skus_vistos:
                            continue
                        # Verificar si este SKU tiene precio (buscando en catálogos)
                        tiene_precio = False
                        for cat in st.session_state.catalogos:
                            df_cat = cat['df']
                            df_sku_limpio = df_cat[cat['col_sku']].astype(str).str.strip().str.upper()
                            if (df_sku_limpio == sku).any():
                                tiene_precio = True
                                break
                        
                        # Si no tiene precio, crear un producto básico
                        if not tiene_precio:
                            # Buscar descripción
                            descripcion_stock = str(row[col_desc])[:200] if col_desc else f"SKU: {sku}"
                            
                            # Buscar stock
                            stock_yessica = 0
                            stock_apri004 = 0
                            stock_apri001 = 0
                            
                            # Buscar columna de cantidad
                            col_cant = None
                            for col in df.columns:
                                col_upper = str(col).upper()
                                if any(p in col_upper for p in ['CANT', 'STOCK', 'DISPONIBLE', 'UNIDADES']):
                                    col_cant = col
                                    break
                            
                            cantidad = int(corregir_numero(row[col_cant])) if col_cant else 0
                            hoja = stock['hoja'].upper()
                            if 'YESSICA' in hoja:
                                stock_yessica = cantidad
                            elif 'APRI.004' in hoja:
                                stock_apri004 = cantidad
                            elif 'APRI.001' in hoja:
                                stock_apri001 = cantidad
                            
                            stock_total = stock_yessica + stock_apri004 + stock_apri001
                            
                            prod = {
                                'sku': sku,
                                'descripcion': descripcion_stock,
                                'precio': 0.0,
                                'stock_yessica': stock_yessica,
                                'stock_apri004': stock_apri004,
                                'stock_apri001': stock_apri001,
                                'stock_total': stock_total,
                                'tiene_stock': stock_total > 0,
                                'tiene_precio': False,
                                'usa_apri001': stock_apri001 > 0 and stock_yessica == 0 and stock_apri004 == 0,
                                'alternativas': []
                            }
                            skus_vistos.add(sku)
                            resultados_busqueda.append(prod)
            
            if resultados_busqueda:
                st.markdown(f"✅ **{len(resultados_busqueda)}** productos encontrados")
                
                for prod in resultados_busqueda:
                    badge = construir_badge_stock_compacto(prod['stock_yessica'], prod['stock_apri004'], prod['stock_apri001'])
                    
                    if prod['tiene_stock'] and prod['tiene_precio']:
                        estado_icono = "🟢"
                        estado_texto = "Disponible"
                        bg_color = "#e8f5e9"
                        border_color = "#10b981"
                    elif prod['tiene_stock'] and not prod['tiene_precio']:
                        estado_icono = "🟡"
                        estado_texto = "Sin precio (con stock)"
                        bg_color = "#fff4e6"
                        border_color = "#f59e0b"
                    elif not prod['tiene_stock'] and prod['tiene_precio']:
                        estado_icono = "🔴"
                        estado_texto = "Sin stock"
                        bg_color = "#fce7f3"
                        border_color = "#ef4444"
                    else:
                        estado_icono = "⚪"
                        estado_texto = "No disponible"
                        bg_color = "#f1f5f9"
                        border_color = "#64748b"
                    
                    st.markdown(f"""
                    <div class="compact-row" style="background:{bg_color}; border-left-color:{border_color};">
                        <div style="display:flex; align-items:flex-start; justify-content:space-between; flex-wrap:wrap; gap:0.75rem;">
                            <div style="flex:2;">
                                <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;">
                                    <span style="font-size:1.1rem;">{estado_icono}</span>
                                    <strong style="font-size:0.95rem; font-family:monospace;">{prod['sku']}</strong>
                                    <span style="background:{border_color}; color:white; padding:0.15rem 0.5rem; border-radius:12px; font-size:0.65rem;">{estado_texto}</span>
                                </div>
                                <div style="font-size:0.8rem; color:#4b5563; margin-top:0.2rem;">{prod['descripcion'][:75]}</div>
                            </div>
                            <div style="display:flex; align-items:center; gap:0.75rem; flex-wrap:wrap;">
                                {'<span style="font-size:0.8rem; background:#e2e8f0; padding:0.2rem 0.6rem; border-radius:16px;">💰 S/ ' + f'{prod["precio"]:,.2f}' + '</span>' if prod['tiene_precio'] else '<span style="font-size:0.8rem; background:#fef3c7; padding:0.2rem 0.6rem; border-radius:16px;">💰 Sin precio</span>'}
                                <span style="font-size:0.8rem; font-weight:500;">
                                    📦 {prod['stock_total']}
                                </span>
                                <div style="display:flex; gap:0.25rem;">
                                    {badge}
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Si tiene stock y precio -> botón agregar
                    if prod['tiene_stock'] and prod['tiene_precio']:
                        col_cant, col_btn = st.columns([1, 2])
                        with col_cant:
                            cantidad = st.number_input(
                                "Cantidad", 
                                min_value=1, 
                                max_value=prod['stock_total'], 
                                value=1, 
                                step=1, 
                                key=f"compact_{prod['sku']}", 
                                label_visibility="collapsed"
                            )
                        with col_btn:
                            if st.button(f"➕ Agregar a cotización", key=f"add_compact_{prod['sku']}", use_container_width=True):
                                item_carrito = {
                                    'sku': prod['sku'],
                                    'descripcion': prod['descripcion'],
                                    'cantidad': cantidad,
                                    'precio': prod['precio'],
                                    'total': prod['precio'] * cantidad,
                                    'stock_yessica': prod['stock_yessica'],
                                    'stock_apri004': prod['stock_apri004'],
                                    'stock_apri001': prod['stock_apri001']
                                }
                                st.session_state.carrito.append(item_carrito)
                                st.success(f"✅ Agregado {cantidad}x {prod['sku']}")
                                st.rerun()
                    
                    # Si tiene stock pero no precio -> sugerir reemplazo
                    elif prod['tiene_stock'] and not prod['tiene_precio']:
                        reemplazo = buscar_reemplazo_directo(prod['sku'], prod['descripcion'], st.session_state.catalogos, st.session_state.stocks, st.session_state.precio_key)
                        if reemplazo:
                            st.markdown(f"""
                            <div class="sugerencia-badge">
                                💡 <strong>Sugerencia:</strong> "{prod['sku']}" no tiene precio, pero <strong>{reemplazo['sku']}</strong> tiene descripción similar ({reemplazo['similitud']:.0f}%) y SÍ tiene precio.
                            </div>
                            """, unsafe_allow_html=True)
                            col_cant_rep, col_btn_rep = st.columns([1, 2])
                            with col_cant_rep:
                                cant_rep = st.number_input("", min_value=1, max_value=reemplazo['stock_total'], value=1, step=1, key=f"reemp_{reemplazo['sku']}_{prod['sku']}", label_visibility="collapsed")
                            with col_btn_rep:
                                if st.button(f"➕ Usar {reemplazo['sku']}", key=f"use_reemp_{reemplazo['sku']}_{prod['sku']}", use_container_width=True):
                                    item_carrito = {
                                        'sku': reemplazo['sku'],
                                        'descripcion': reemplazo['descripcion'],
                                        'cantidad': cant_rep,
                                        'precio': reemplazo['precio'],
                                        'total': reemplazo['precio'] * cant_rep,
                                        'stock_yessica': reemplazo['stock_yessica'],
                                        'stock_apri004': reemplazo['stock_apri004'],
                                        'stock_apri001': reemplazo['stock_apri001']
                                    }
                                    st.session_state.carrito.append(item_carrito)
                                    st.success(f"✅ Agregado {cant_rep}x {reemplazo['sku']}")
                                    st.rerun()
                        else:
                            st.info(f"ℹ️ Este producto tiene {prod['stock_total']} unidades en stock pero no tiene precio en los catálogos. Contacta al administrador para agregar el precio.")
                    
                    # Si no tiene stock -> mostrar alternativas
                    elif not prod['tiene_stock'] and prod.get('alternativas') and len(prod['alternativas']) > 0:
                        st.markdown(f"""
                        <div class="sugerencia-badge" style="background:#fef3c7; color:#b45309;">
                            💡 <strong>Alternativas disponibles:</strong> {len(prod['alternativas'])} productos similares con stock.
                        </div>
                        """, unsafe_allow_html=True)
                        for alt in prod['alternativas'][:3]:
                            alt_badge = construir_badge_stock_compacto(alt['stock_yessica'], alt['stock_apri004'], alt['stock_apri001'])
                            st.markdown(f"""
                            <div style="background:white; border-radius:10px; padding:0.5rem 0.75rem; margin:0.3rem 0; border:1px solid #fed7aa;">
                                <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:0.5rem;">
                                    <div style="flex:2;">
                                        <strong style="font-size:0.85rem;">📦 {alt['sku']}</strong>
                                        <div style="font-size:0.7rem; color:#666;">{alt['descripcion'][:50]}</div>
                                    </div>
                                    <div><span style="font-size:0.75rem;">💰 S/ {alt['precio']:.2f}</span></div>
                                    <div>{alt_badge}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            col_cant_alt, col_btn_alt = st.columns([1, 2])
                            with col_cant_alt:
                                cant_alt = st.number_input("", min_value=1, max_value=alt['stock_total'], value=1, step=1, key=f"alt_compact_{alt['sku']}_{prod['sku']}", label_visibility="collapsed")
                            with col_btn_alt:
                                if st.button(f"➕ {alt['sku']}", key=f"add_alt_compact_{alt['sku']}_{prod['sku']}", use_container_width=True):
                                    item_carrito = {
                                        'sku': alt['sku'],
                                        'descripcion': alt['descripcion'],
                                        'cantidad': cant_alt,
                                        'precio': alt['precio'],
                                        'total': alt['precio'] * cant_alt,
                                        'stock_yessica': alt['stock_yessica'],
                                        'stock_apri004': alt['stock_apri004'],
                                        'stock_apri001': alt['stock_apri001']
                                    }
                                    st.session_state.carrito.append(item_carrito)
                                    st.success(f"✅ Agregado {cant_alt}x {alt['sku']}")
                                    st.rerun()
                    
                    st.markdown("---")
            else:
                st.info("No se encontraron productos. Prueba con otra palabra o SKU.")

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown('<div class="footer">⚡ QTC Smart Sales Pro v4.1 | Con detección de SKU equivalentes</div>', unsafe_allow_html=True)
