# app.py - QTC Smart Sales Pro v4.1 (PREMIUM UI EDITION)
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
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS COMPLETO - ESTILO "MIDNIGHT GLASS" PREMIUM
# ============================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Fondo principal de la App */
    .stApp {
        background-color: #0B0F19;
        font-family: 'Inter', sans-serif;
        color: #E2E8F0;
    }
    
    /* Sidebar Moderno */
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    [data-testid="stSidebar"] * { color: #D1D5DB !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #E11D48 !important;
        font-weight: 600;
    }

    /* Inputs y Text Areas */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input {
        background-color: #1F2937 !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
    }
    
    /* Botones Premium */
    .stButton > button {
        background: linear-gradient(135deg, #E11D48 0%, #BE123C 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(225, 29, 72, 0.2);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(225, 29, 72, 0.4);
    }

    /* Estilo de las Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1F2937;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        color: #9CA3AF;
        border: 1px solid rgba(255,255,255,0.05);
        border-bottom: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #E11D48 !important;
        color: white !important;
        border-color: #E11D48;
    }

    /* Tarjetas de Producto / Glassmorphism */
    .card-premium {
        background: #1F2937;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.05);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s, border-color 0.2s;
    }
    .card-premium:hover {
        transform: translateY(-2px);
        border-color: rgba(255,255,255,0.15);
    }

    /* Badges Modernos tipo Pill */
    .badge-yessica { background: rgba(16, 185, 129, 0.15); color: #34D399 !important; border: 1px solid rgba(16, 185, 129, 0.3); padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 600; display: inline-block; margin: 2px; }
    .badge-apri004 { background: rgba(245, 158, 11, 0.15); color: #FBBF24 !important; border: 1px solid rgba(245, 158, 11, 0.3); padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 600; display: inline-block; margin: 2px; }
    .badge-apri001 { background: rgba(244, 63, 94, 0.15); color: #FB7185 !important; border: 1px solid rgba(244, 63, 94, 0.3); padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 600; display: inline-block; margin: 2px; }
    .badge-warning { background: rgba(156, 163, 175, 0.15); color: #9CA3AF !important; border: 1px solid rgba(156, 163, 175, 0.3); padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
    
    /* Resumen de Contadores (Tab 1) */
    .counter-summary {
        background: #1F2937;
        border-radius: 16px;
        padding: 1.2rem;
        margin: 1.5rem 0;
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .counter-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 0.9rem;
        padding: 0.6rem 1.2rem;
        border-radius: 10px;
        background: #111827;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .counter-number { font-weight: 700; font-size: 1.2rem; color: #E2E8F0; }
    .counter-label { color: #9CA3AF; font-size: 0.85rem; font-weight: 500; }

    /* Login Card Premium */
    .login-card {
        background: rgba(31, 41, 55, 0.7);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 24px;
        padding: 3rem;
        text-align: center;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        max-width: 420px;
        margin: 0 auto;
        animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(40px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .footer { text-align: center; padding: 1.5rem; color: #6B7280; font-size: 0.8rem; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 2rem; }
    
    /* Alternativas */
    .alternativa-item {
        background: #111827;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(245, 158, 11, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNCIONES DE UTILIDAD (SIN CAMBIOS DE LÓGICA)
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
# FUNCIONES DE SIMILITUD Y BÚSQUEDA (SIN CAMBIOS)
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

def buscar_producto(sku: str, catalogos: List[Dict], stocks: List[Dict], precio_key: str) -> Dict:
    sku_limpio = sku.strip().upper()
    
    stock_info = buscar_stock_para_sku(sku_limpio, stocks)
    
    descripcion = f"SKU: {sku}"
    precio = 0.0
    sku_equivalente = None
    similitud_equivalente = 0
    
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
# LOGIN PREMIUM
# ============================================

if not st.session_state.auth:
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%) !important; }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        try:
            st.image("logo.png", width=90)
        except:
            st.markdown("<h1 style='color:#E11D48; font-weight:700;'>QTC</h1>", unsafe_allow_html=True)
        
        st.markdown("<h2 style='color:#F1F5F9; font-weight:600; margin-top:10px;'>Smart Sales Pro</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#9CA3AF; margin-bottom:30px;'>Acceso al Sistema Central</p>", unsafe_allow_html=True)
        
        user = st.text_input("👤 Usuario", placeholder="Ingresa tu usuario")
        pw = st.text_input("🔒 Contraseña", type="password", placeholder="Ingresa tu contraseña")
        
        st.write("") # Espaciador
        if st.button("🚀 INGRESAR AL SISTEMA", use_container_width=True):
            if user == "admin" and pw == "qtc2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")
        
        st.markdown("<div class='footer'>⚡ Desarrollado para QTC Operations</div>", unsafe_allow_html=True)
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
        st.markdown("<h2 style='color:#E11D48;'>QTC</h2>", unsafe_allow_html=True)
with col2:
    st.markdown("## QTC Smart Sales Pro")
    st.caption("Panel Central de Cotizaciones y Diagnóstico")
with col3:
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.05); padding: 0.5rem 1rem; border-radius: 8px; text-align: right; border: 1px solid rgba(255,255,255,0.05);">
        <span style="color:#F1F5F9; font-weight:600;">👤 Admin Center</span><br>
        <span style="color:#9CA3AF; font-size: 0.75rem;">Conectado</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 Cerrar Sesión", key="logout", use_container_width=True):
        st.session_state.auth = False
        st.session_state.carrito = []
        st.rerun()

st.markdown("---")

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    
    modo = st.radio(
        "Modo de inventario",
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
        "💰 Estructura de Precio",
        ["P. VIP", "P. BOX", "P. IR"],
        index=0
    )
    st.session_state.precio_key = precio_opcion
    
    st.markdown("---")
    
    st.markdown("### 📂 Data Sources")
    
    st.markdown("<span style='color:#9CA3AF; font-size:0.85rem;'>📚 Catálogos Oficiales</span>", unsafe_allow_html=True)
    archivos_cat = st.file_uploader(
        "Formatos: Excel o CSV",
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
    
    st.markdown("<span style='color:#9CA3AF; font-size:0.85rem;'>📦 Reportes de Almacén</span>", unsafe_allow_html=True)
    archivos_stock = st.file_uploader(
        "Formatos: Excel",
        type=['xlsx', 'xls'],
        accept_multiple_files=True,
        key="stock_upload"
    )
    if archivos_stock:
        st.session_state.stocks = cargar_stock(archivos_stock, st.session_state.modo)
    
    st.markdown("---")
    
    if st.session_state.carrito:
        st.markdown(f"### 🛒 Resumen Carrito")
        st.metric("Ítems", len(st.session_state.carrito))
        total = sum(item['total'] for item in st.session_state.carrito)
        st.metric("Valor Total", f"S/ {total:,.2f}")
        
        if st.button("🧹 Limpiar Carrito", use_container_width=True):
            st.session_state.carrito = []
            st.rerun()

# ============================================
# TABS PRINCIPALES
# ============================================

tab1, tab2, tab3 = st.tabs(["🚀 MODO MASIVO", "🔍 BÚSQUEDA DIAGNÓSTICO", "🛒 CARRITO"])

# ========== TAB 1: MODO MASIVO ==========
with tab1:
    st.markdown("### 🚀 Procesamiento de Pedidos por Lotes")
    st.caption("Pega tu lista en formato `SKU:CANTIDAD` (uno por línea)")
    
    texto_bulk = st.text_area(
        "",
        height=200,
        placeholder="Ejemplo:\nRN9401276NA8:100\nCN0200047BK8:100"
    )
    
    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        if st.button("⚡ Iniciar Análisis", type="primary", use_container_width=True):
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
                    with st.spinner("Procesando lógicas de cruce..."):
                        resultados_procesados = []
                        encontrados = 0
                        con_precio = 0
                        con_stock = 0
                        
                        for pedido in pedidos:
                            prod = buscar_producto(pedido['sku'], st.session_state.catalogos, st.session_state.stocks, st.session_state.precio_key)
                            
                            if prod['tiene_precio']: encontrados += 1; con_precio += 1
                            if prod['tiene_stock']: con_stock += 1
                            
                            if prod['tiene_precio'] and prod['tiene_stock']:
                                cantidad_cotizar = min(pedido['cantidad'], prod['stock_total'])
                                estado = "✅ OK"
                                if cantidad_cotizar < pedido['cantidad']:
                                    estado = f"⚠️ Stock parcial ({cantidad_cotizar}/{pedido['cantidad']})"
                            elif not prod['tiene_precio'] and prod['tiene_stock']:
                                cantidad_cotizar = 0
                                estado = "⚠️ Stock sin precio (Error SKU)"
                            elif not prod['tiene_precio']:
                                cantidad_cotizar = 0; estado = "❌ Sin precio"
                            else:
                                cantidad_cotizar = 0; estado = "❌ Sin stock"
                            
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
                        
                        # NUEVO DISEÑO HTML PARA CONTADORES
                        st.markdown(f"""
                        <div class="counter-summary">
                            <div class="counter-item"><span class="counter-label">Ingresados</span><span class="counter-number">{total_ingresados}</span></div>
                            <div class="counter-item" style="border-left: 3px solid #10B981;"><span class="counter-label">Completos</span><span class="counter-number" style="color:#34D399;">{total_encontrados}</span></div>
                            <div class="counter-item" style="border-left: 3px solid #F59E0B;"><span class="counter-label">Con Stock</span><span class="counter-number" style="color:#FBBF24;">{total_con_stock}</span></div>
                            <div class="counter-item" style="border-left: 3px solid #F43F5E;"><span class="counter-label">Sin Precio</span><span class="counter-number" style="color:#FB7185;">{total_sin_precio}</span></div>
                            <div class="counter-item" style="border-left: 3px solid #9CA3AF;"><span class="counter-label">Sin Stock</span><span class="counter-number" style="color:#9CA3AF;">{total_sin_stock}</span></div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        error_sku = [p for p in resultados_procesados if p['tiene_stock'] and not p['tiene_precio']]
                        if error_sku:
                            st.markdown("""
                            <div style="background:rgba(244, 63, 94, 0.1); border-radius:12px; padding:1.2rem; margin:1rem 0; border:1px solid rgba(244, 63, 94, 0.3); border-left:4px solid #F43F5E;">
                                <strong style="color:#FB7185;">⚠️ DIAGNÓSTICO: ERRORES DE CATÁLOGO DETECTADOS</strong><br>
                                <span style="font-size:0.85rem; color:#D1D5DB;">Los siguientes productos tienen inventario físico, pero su SKU no existe en el catálogo de precios actual.</span>
                            </div>
                            """, unsafe_allow_html=True)
                            df_error = pd.DataFrame([{'SKU Físico': p['sku'], 'Descripción Detectada': p['descripcion'][:60], 'Unidades': p['stock_total']} for p in error_sku])
                            st.dataframe(df_error, use_container_width=True, hide_index=True)
                        
                        st.success(f"✅ Análisis completado para {len(pedidos)} SKUs.")
                        st.rerun()
                else:
                    st.warning("El formato de texto no es válido.")
            else:
                st.warning("⚠️ Debes cargar al menos un catálogo y un reporte de stock primero.")
    
    with col_b2:
        if st.button("📥 Trasladar Disponibles al Carrito", use_container_width=True):
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
                st.success(f"✅ Se han movido {agregados} líneas al carrito.")
                st.rerun()

# ========== TAB 2: BÚSQUEDA INTELIGENTE CON DIAGNÓSTICO ==========
with tab2:
    st.markdown("### 🔍 Motor de Búsqueda y Diagnóstico")
    st.caption("Explora el inventario o investiga problemas de SKU cruzando datos.")
    
    busqueda = st.text_input("", placeholder="🔍 Buscar por nombre de producto, modelo o código SKU...")
    
    if busqueda and len(busqueda) >= 2 and st.session_state.catalogos and st.session_state.stocks:
        with st.spinner("Ejecutando algoritmos de búsqueda y similitud..."):
            resultados_busqueda = []
            skus_vistos = set()
            
            for cat in st.session_state.catalogos:
                df = cat['df']
                mask_sku = df[cat['col_sku']].astype(str).str.contains(busqueda, case=False, na=False)
                mask_desc = pd.Series([False] * len(df))
                if cat['col_desc']: mask_desc = df[cat['col_desc']].astype(str).str.contains(busqueda, case=False, na=False)
                mask = mask_sku | mask_desc
                for _, row in df[mask].iterrows():
                    sku = str(row[cat['col_sku']]).strip().upper()
                    if sku in skus_vistos: continue
                    skus_vistos.add(sku)
                    prod = buscar_producto(sku, st.session_state.catalogos, st.session_state.stocks, st.session_state.precio_key)
                    prod['fuente'] = '📋 Catálogo'
                    resultados_busqueda.append(prod)
            
            for stock in st.session_state.stocks:
                df = stock['df']
                col_sku = stock['col_sku']
                mask_sku = df[col_sku].astype(str).str.contains(busqueda, case=False, na=False)
                mask_desc = pd.Series([False] * len(df))
                for col in df.columns:
                    col_upper = str(col).upper()
                    if any(p in col_upper for p in ['DESC', 'PRODUCTO', 'NOMBRE', 'ARTICULO']):
                        mask_desc = mask_desc | df[col].astype(str).str.contains(busqueda, case=False, na=False)
                mask = mask_sku | mask_desc
                for _, row in df[mask].iterrows():
                    sku = str(row[col_sku]).strip().upper()
                    if sku in skus_vistos: continue
                    skus_vistos.add(sku)
                    prod = buscar_producto(sku, st.session_state.catalogos, st.session_state.stocks, st.session_state.precio_key)
                    prod['fuente'] = f'📦 Stock ({stock["hoja"]})'
                    resultados_busqueda.append(prod)
            
            if resultados_busqueda:
                st.markdown(f"<div style='margin-bottom: 15px; color:#10B981; font-weight:600;'>✅ {len(resultados_busqueda)} resultados encontrados</div>", unsafe_allow_html=True)
                
                for prod in resultados_busqueda:
                    badge_stock = construir_badge_stock(prod['stock_yessica'], prod['stock_apri004'], prod['stock_apri001'])
                    
                    # CASO: STOCK SIN PRECIO - ERROR DE SKU (ROJO)
                    if prod['tiene_stock'] and not prod['tiene_precio']:
                        st.markdown(f"""
                        <div class="card-premium" style="border-left: 4px solid #F43F5E; background: rgba(244, 63, 94, 0.03);">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <div><span style="background:rgba(244, 63, 94, 0.2);color:#FB7185;padding:4px 12px;border-radius:6px;font-size:0.75rem;font-weight:600; border: 1px solid rgba(244, 63, 94, 0.3);">⚠️ ERROR DE CATÁLOGO DETECTADO</span></div>
                                <div><span style="background:rgba(255, 255, 255, 0.1);color:#D1D5DB;padding:4px 10px;border-radius:6px;font-size:0.7rem;">Fuente: {prod['fuente']}</span></div>
                            </div>
                            <div style="margin-top:16px;">
                                <strong style="color:#F8FAFC; font-size:1.1rem;">📦 {prod['sku']}</strong><br>
                                <span style="color:#9CA3AF; font-size:0.95rem;">{prod['descripcion']}</span><br>
                            </div>
                            <div style="margin-top:12px; display:flex; gap: 15px; font-weight: 500;">
                                <span style="color:#D1D5DB;">💰 Precio: <span style="color:#FB7185;">No Oficial</span></span>
                                <span style="color:#D1D5DB;">📦 Stock Total: {prod['stock_total']} ud.</span>
                            </div>
                            <div style="margin-top:12px;">{badge_stock}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if prod.get('sku_equivalente'):
                            precio_eq = 0
                            desc_eq = ""
                            for cat in st.session_state.catalogos:
                                df = cat['df']
                                df_sku = df[cat['col_sku']].astype(str).str.strip().str.upper()
                                mask = df_sku == prod['sku_equivalente']
                                if mask.any():
                                    row = df[mask].iloc[0]
                                    if st.session_state.precio_key in cat['precios']:
                                        col_precio = cat['precios'][st.session_state.precio_key]
                                        precio_eq = corregir_numero(row[col_precio])
                                    if cat['col_desc']:
                                        desc_eq = str(row[cat['col_desc']])[:100]
                                    break
                            
                            st.markdown(f"""
                            <div style="background:rgba(16, 185, 129, 0.05); border-radius:12px; padding:1.2rem; margin-top:-0.5rem; margin-bottom:1rem; border:1px solid rgba(16, 185, 129, 0.2); border-left:4px solid #10B981;">
                                <strong style="color:#34D399;">💡 SOLUCIÓN: SKU EQUIVALENTE ENCONTRADO</strong>
                                <div style="margin-top:10px; color:#D1D5DB;">
                                    El sistema detectó que <code>{prod['sku_equivalente']}</code> comparte la misma descripción.<br>
                                    <strong style="color:#F8FAFC;">Precio Oficial:</strong> S/ {precio_eq:,.2f} &nbsp;|&nbsp; <strong>Match:</strong> {prod['similitud_equivalente']:.0f}%
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            col_eq1, col_eq2 = st.columns(2)
                            with col_eq1:
                                if st.button(f"✅ Reemplazar con {prod['sku_equivalente']}", key=f"use_eq_{prod['sku']}"):
                                    item_carrito = {
                                        'sku': prod['sku_equivalente'], 'descripcion': desc_eq,
                                        'cantidad': 1, 'precio': precio_eq, 'total': precio_eq,
                                        'stock_yessica': 0, 'stock_apri004': prod['stock_apri004'], 'stock_apri001': prod['stock_apri001']
                                    }
                                    st.session_state.carrito.append(item_carrito)
                                    st.success("Reemplazo exitoso.")
                                    st.rerun()
                            with col_eq2:
                                if st.button(f"Ignorar y mantener ({prod['sku']})", key=f"use_orig_{prod['sku']}"):
                                    st.warning("SKU sin precio. Imposible cotizar.")
                        
                        elif prod.get('alternativas') and len(prod['alternativas']) > 0:
                            st.markdown('<div style="margin:1rem 0; color:#FBBF24; font-weight:600;">⚡ Otras alternativas tarifadas:</div>', unsafe_allow_html=True)
                            for alt in prod['alternativas'][:3]:
                                badge_alt = construir_badge_stock(alt['stock_yessica'], alt['stock_apri004'], alt['stock_apri001'])
                                st.markdown(f"""
                                <div class="alternativa-item">
                                    <strong style="color:#F8FAFC;">📦 {alt['sku']}</strong>
                                    <span style="background:rgba(245, 158, 11, 0.2);color:#FBBF24;padding:2px 8px;border-radius:6px;font-size:0.7rem; float:right;">Match: {alt['similitud']:.0f}%</span><br>
                                    <span style="font-size:0.85rem; color:#9CA3AF;">{alt['descripcion'][:80]}</span>
                                    <div style="margin-top:8px; color:#D1D5DB;">💰 S/ {alt['precio']:,.2f} &nbsp;|&nbsp; 📦 {alt['stock_total']} ud.</div>
                                    <div style="margin-top:8px;">{badge_alt}</div>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # CASO NORMAL: CON STOCK Y PRECIO (VERDE)
                    elif prod['tiene_stock'] and prod['tiene_precio']:
                        st.markdown(f"""
                        <div class="card-premium" style="border-left: 4px solid #10B981;">
                            <div><strong style="color:#F8FAFC; font-size:1.1rem;">📦 {prod['sku']}</strong> <span style="background:rgba(16, 185, 129, 0.2);color:#34D399;padding:4px 10px;border-radius:6px;font-size:0.7rem; font-weight:600; float:right;">✅ DISPONIBLE</span></div>
                            <div style="margin-top:12px;"><span style="color:#9CA3AF; font-size:0.95rem;">{prod['descripcion']}</span></div>
                            <div style="margin-top:12px; display:flex; gap: 15px; font-weight: 500;">
                                <span style="color:#D1D5DB;">💰 S/ <strong style="color:#34D399;">{prod['precio']:,.2f}</strong></span>
                                <span style="color:#D1D5DB;">📦 <strong style="color:#F8FAFC;">{prod['stock_total']}</strong> ud.</span>
                            </div>
                            <div style="margin-top:12px;">{badge_stock}</div>
                        """, unsafe_allow_html=True)
                        
                        col_cant, col_btn = st.columns([1, 3])
                        with col_cant:
                            cantidad = st.number_input("Cant.", min_value=1, max_value=prod['stock_total'], value=1, step=1, key=f"ok_{prod['sku']}")
                        with col_btn:
                            st.write("") # Spacer
                            if st.button(f"🛒 Añadir al Carrito", key=f"add_ok_{prod['sku']}"):
                                item_carrito = {
                                    'sku': prod['sku'], 'descripcion': prod['descripcion'], 'cantidad': cantidad,
                                    'precio': prod['precio'], 'total': prod['precio'] * cantidad,
                                    'stock_yessica': prod['stock_yessica'], 'stock_apri004': prod['stock_apri004'], 'stock_apri001': prod['stock_apri001']
                                }
                                st.session_state.carrito.append(item_carrito)
                                st.success("Añadido exitosamente.")
                                st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # CASO: SOLO PRECIO (AZUL)
                    elif not prod['tiene_stock'] and prod['tiene_precio']:
                        st.markdown(f"""
                        <div class="card-premium" style="border-left: 4px solid #3B82F6;">
                            <div><strong style="color:#F8FAFC; font-size:1.1rem;">📦 {prod['sku']}</strong> <span style="background:rgba(59, 130, 246, 0.2);color:#60A5FA;padding:4px 10px;border-radius:6px;font-size:0.7rem; font-weight:600; float:right;">📋 SOLO EN CATÁLOGO</span></div>
                            <div style="margin-top:12px;"><span style="color:#9CA3AF; font-size:0.95rem;">{prod['descripcion']}</span></div>
                            <div style="margin-top:12px; font-weight: 500;">
                                <span style="color:#D1D5DB;">💰 S/ <strong style="color:#60A5FA;">{prod['precio']:,.2f}</strong></span>
                            </div>
                            <div style="margin-top:12px;">{badge_stock}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # CASO: NO DISPONIBLE (GRIS)
                    else:
                        st.markdown(f"""
                        <div class="card-premium" style="border-left: 4px solid #6B7280; opacity: 0.7;">
                            <div><strong style="color:#F8FAFC; font-size:1.1rem;">📦 {prod['sku']}</strong> <span style="background:rgba(107, 114, 128, 0.2);color:#9CA3AF;padding:4px 10px;border-radius:6px;font-size:0.7rem; font-weight:600; float:right;">❌ AGOTADO / INACTIVO</span></div>
                            <div style="margin-top:12px;"><span style="color:#9CA3AF; font-size:0.95rem;">{prod['descripcion']}</span></div>
                            <div style="margin-top:12px;">{badge_stock}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("Sin coincidencias en la base de datos.")
    elif busqueda and len(busqueda) >= 2:
        st.warning("⚠️ Asegúrate de cargar Data Sources (Catálogo y Stock) en el panel izquierdo.")

# ========== TAB 3: CARRITO ==========
with tab3:
    st.markdown("### 🛒 Documento de Cotización")
    
    if not st.session_state.carrito:
        st.info("El carrito de cotización está vacío.")
    else:
        for idx, item in enumerate(st.session_state.carrito):
            st.markdown(f"""<div style="background:#1F2937; padding:1rem; border-radius:12px; margin-bottom:10px; border: 1px solid rgba(255,255,255,0.05);">""", unsafe_allow_html=True)
            col1, col2, col3, col4, col5, col6 = st.columns([1.5, 3, 1, 1, 1, 0.5])
            with col1:
                st.write(f"<span style='color:#F8FAFC; font-weight:600;'>{item['sku']}</span>", unsafe_allow_html=True)
                badge = construir_badge_stock(item['stock_yessica'], item['stock_apri004'], item['stock_apri001'])
                st.markdown(badge, unsafe_allow_html=True)
            with col2:
                st.write(f"<span style='color:#9CA3AF; font-size:0.9rem;'>{item['descripcion'][:60]}...</span>", unsafe_allow_html=True)
            with col3:
                nueva_cant = st.number_input("Cant", min_value=0, max_value=item['stock_yessica']+item['stock_apri004']+item['stock_apri001'], value=item['cantidad'], step=1, key=f"edit_{idx}", label_visibility="collapsed")
                if nueva_cant != item['cantidad']:
                    item['cantidad'] = nueva_cant
                    item['total'] = item['precio'] * nueva_cant
                    if nueva_cant == 0:
                        st.session_state.carrito.pop(idx)
                        st.rerun()
            with col4:
                st.write(f"<span style='color:#D1D5DB;'>S/ {item['precio']:,.2f}</span>", unsafe_allow_html=True)
            with col5:
                st.write(f"<span style='color:#34D399; font-weight:600;'>S/ {item['total']:,.2f}</span>", unsafe_allow_html=True)
            with col6:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.carrito.pop(idx)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        
        total_general = sum(item['total'] for item in st.session_state.carrito)
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #E11D48 0%, #BE123C 100%); border-radius:16px; padding:1.5rem; margin:1.5rem 0; text-align:right; box-shadow: 0 4px 15px rgba(225, 29, 72, 0.3);">
            <span style="color:rgba(255,255,255,0.8); font-size:1.2rem; margin-right: 15px;">IMPORTE TOTAL:</span>
            <span style="color:white; font-size:2rem; font-weight:700;">S/ {total_general:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📋 Emisión de Documento")
        col_cli1, col_cli2 = st.columns(2)
        with col_cli1:
            cliente = st.text_input("Razón Social", placeholder="Ej: Empresa SAC")
        with col_cli2:
            ruc = st.text_input("RUC / DNI", placeholder="Ej: 20123456789")
        
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        with col_exp1:
            if st.button("📥 Generar Excel Oficial", type="primary", use_container_width=True):
                if cliente:
                    items_export = [{'sku': i['sku'], 'descripcion': i['descripcion'], 'cantidad': i['cantidad'], 'precio': i['precio'], 'total': i['total']} for i in st.session_state.carrito]
                    excel = generar_excel(items_export, cliente, ruc)
                    st.download_button("💾 Descargar Archivo", data=excel, file_name=f"Cotizacion_{cliente}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", use_container_width=True)
                    st.success("✅ Documento listo.")
                else:
                    st.warning("⚠️ La Razón Social es obligatoria.")
        with col_exp2:
            if st.button("📋 Copiar formato CSV", use_container_width=True):
                csv_text = "SKU,Descripción,Cantidad,Precio,Subtotal\n"
                for item in st.session_state.carrito:
                    csv_text += f"{item['sku']},{item['descripcion']},{item['cantidad']},{item['precio']:.2f},{item['total']:.2f}\n"
                csv_text += f"TOTAL,{total_general:.2f}"
                st.code(csv_text, language="csv")
        with col_exp3:
            if st.button("🗑️ Vaciar Bandeja", use_container_width=True):
                st.session_state.carrito = []
                st.rerun()

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown('<div class="footer">⚙️ QTC Smart Sales Pro v4.1 | UI Premium Edition</div>', unsafe_allow_html=True)
