# app.py - QTC Smart Sales Pro v4.2
# Con soporte para XIAOMI, UGREEN y OTRAS marcas

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
# CSS COMPLETO (TUS ESTILOS ORIGINALES)
# ============================================

st.markdown("""
<style>
      /* ========== FONDO DE PÁGINA - AZUL MIRAMAR VIVO ========== */
    .stApp {
        background: linear-gradient(135deg, #0d47a1 0%, #1565c0 50%, #1e88e5 100%);
    }
    
    /* ========== TARJETAS GLASSMORPHISM (se mantienen) ========== */
    .result-card, div[style*="border-radius:16px"] {
        background: rgba(30, 30, 35, 0.85) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.15);
        color: #ffffff !important;
    }
    
       /* ========== 4. SIDEBAR - DURAZNO INTENSO ========== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8a35e 0%, #e87a2d 50%, #d45a1a 100%);
        border-right: 1px solid #ffcc80;
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    /* Selector de marca dentro del sidebar - fondo más oscuro para contraste */
    [data-testid="stSidebar"] .stRadio > div {
        background: rgba(0,0,0,0.2);
        border-radius: 10px;
        padding: 8px;
    }
    
    /* Botones dentro del sidebar */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.2);
        color: white;
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.3);
        border-color: rgba(255,255,255,0.5);
    }
    
    /* ========== TEXTOS GENERALES (blancos para contraste) ========== */
    .stMarkdown, .stText, .stNumberInput label, .stSelectbox label, 
    .stRadio label, .stTextInput label, .stTextArea label {
        color: #ffffff !important;
    }
    
    /* ========== TÍTULOS ========== */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #ffffff !important;
    }
    
    /* ========== MENSAJES DE STREAMLIT (editables) ========== */
    div[data-testid="stAlert"][data-kind="success"] {
        background: #2e7d32 !important;
        border-left: 4px solid #1b5e20 !important;
        border-radius: 12px !important;
    }
    div[data-testid="stAlert"][data-kind="success"] .stMarkdown {
        color: #ffffff !important;
        font-weight: bold;
    }
    
    div[data-testid="stAlert"][data-kind="warning"] {
        background: #f9a825 !important;
        border-left: 4px solid #f57f17 !important;
        border-radius: 12px !important;
    }
    div[data-testid="stAlert"][data-kind="warning"] .stMarkdown {
        color: #000000 !important;
        font-weight: bold;
    }
    
    div[data-testid="stAlert"][data-kind="error"] {
        background: #d32f2f !important;
        border-left: 4px solid #b71c1c !important;
        border-radius: 12px !important;
    }
    div[data-testid="stAlert"][data-kind="error"] .stMarkdown {
        color: #ffffff !important;
        font-weight: bold;
    }
    
    div[data-testid="stAlert"][data-kind="info"] {
        background: #0288d1 !important;
        border-left: 4px solid #01579b !important;
        border-radius: 12px !important;
    }
    div[data-testid="stAlert"][data-kind="info"] .stMarkdown {
        color: #ffffff !important;
        font-weight: bold;
    }
    
    /* ========== BADGES ========== */
    .badge-yessica { background: #4CAF50; color: white !important; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    .badge-apri004 { background: #FF9800; color: white !important; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    .badge-apri001 { background: #f44336; color: white !important; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    .badge-warning { background: #ff9800; color: white !important; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; }
    .badge-ugreen { background: #00BCD4; color: white !important; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    
    /* ========== FOOTER ========== */
    .footer {
        text-align: center;
        padding: 1rem;
        color: rgba(255,255,255,0.7) !important;
        font-size: 0.7rem;
        border-top: 1px solid rgba(255,255,255,0.2);
        margin-top: 2rem;
    }
       /* ========== 14. TARJETAS DEL TAB 1 - FORZADO EXTREMO ========== */
    
    /* Forzar que TODO el texto dentro de cualquier tarjeta del Tab 1 sea oscuro */
    div[style*="border-radius:16px"] *,
    div[style*="background:#FFEBEE"] *,
    div[style*="background:#E3F2FD"] *,
    div[style*="background:#F5F5F5"] *,
    div[style*="background:#E8F5E9"] *,
    div[style*="background:#FFF8E1"] *,
    div[style*="background:white"] *,
    div[style*="background:#ffffff"] * {
        color: #1a1a2e !important;
    }
    
    /* Forzar fondo blanco a las tarjetas principales */
    div[style*="border-radius:16px"][style*="margin-bottom:1rem"] {
        background: #ffffff !important;
    }
    
    /* EXCEPCIÓN: Los badges deben mantener texto blanco */
    .badge-yessica, .badge-apri004, .badge-apri001, .badge-warning, .badge-ugreen,
    .badge-yessica *, .badge-apri004 *, .badge-apri001 *, .badge-warning *, .badge-ugreen * {
        color: white !important;
    }
    
    /* EXCEPCIÓN: El texto dentro de la alerta de transferencia (fondo rosado) */
    div[style*="background:#FCE4EC"] * {
        color: #c62828 !important;
    }
    
    /* Forzar específicamente los textos principales dentro de cada tarjeta */
    div[style*="border-radius:16px"] div[style*="margin-top"] *,
    div[style*="border-radius:16px"] div[style*="display:flex"] *,
    div[style*="border-radius:16px"] div[style*="justify-content"] * {
        color: #1a1a2e !important;
    }
    
    /* Los códigos SKU y precios en negrita */
    div[style*="border-radius:16px"] strong,
    div[style*="border-radius:16px"] b,
    div[style*="border-radius:16px"] code {
        color: #1a1a2e !important;
    }
    
    /* Los spans con clases específicas */
    div[style*="border-radius:16px"] span[style*="background"] {
        color: white !important;  /* Esto son los badges, mantener blanco */
    }
    
    /* Cualquier otro span dentro de tarjetas */
    div[style*="border-radius:16px"] span:not([style*="background"]) {
        color: #1a1a2e !important;
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
                    # Solo hojas APRI y YESSICA
                    if not any(h in hoja_upper for h in ['APRI', 'YESSICA']):
                        continue
                else:
                    # Para UGREEN y OTROS, usar APRI.001 o todas las hojas según necesidad
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
# NUEVA: FUNCIÓN PARA CARGAR UGREEN
# ============================================

def cargar_ugreen_catalogo(archivo) -> Optional[Dict]:
    """Carga específica para archivo UGREEN con columnas Mayor/Caja/Vip"""
    df = cargar_archivo(archivo)
    if df is None:
        return None
    
    # Mapeo de columnas UGREEN
    col_sku = None
    col_desc = None
    col_mayor = None
    col_caja = None
    col_vip = None
    col_pvp = None
    col_stock = None
    
    for col in df.columns:
        col_upper = str(col).upper()
        if 'SKU' in col_upper:
            col_sku = col
        elif 'DESCRITPION' in col_upper or 'DESCRIPCION' in col_upper or 'GOODS' in col_upper:
            col_desc = col
        elif col_upper == 'MAYOR':
            col_mayor = col
        elif col_upper == 'CAJA':
            col_caja = col
        elif col_upper == 'VIP':
            col_vip = col
        elif col_upper == 'PVP':
            col_pvp = col
        elif 'STOCK' in col_upper:
            col_stock = col
    
    # Si no encontró por nombres exactos, buscar por patrones
    if not col_sku:
        for col in df.columns:
            if 'SKU' in str(col).upper():
                col_sku = col
                break
    if not col_sku:
        col_sku = df.columns[5] if len(df.columns) > 5 else df.columns[0]
    
    if not col_desc:
        for col in df.columns:
            if any(p in str(col).upper() for p in ['DESC', 'GOODS', 'PRODUCTO']):
                col_desc = col
                break
    
    precios = {}
    if col_mayor:
        precios['P. IR'] = col_mayor
    if col_caja:
        precios['P. BOX'] = col_caja
    if col_vip:
        precios['P. VIP'] = col_vip
    
    return {
        'nombre': archivo.name,
        'df': df,
        'col_sku': col_sku,
        'col_desc': col_desc,
        'col_stock': col_stock,
        'precios': precios,
        'tipo': 'UGREEN'
    }

# ============================================
# FUNCIONES DE SIMILITUD Y BÚSQUEDA (MODIFICADAS)
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

# ============================================
# NUEVA: BÚSQUEDA PARA UGREEN
# ============================================

def buscar_ugreen_producto(busqueda: str, ugreen_catalogo: Dict) -> Optional[Dict]:
    """Busca producto en catálogo UGREEN por SKU o descripción"""
    if not ugreen_catalogo:
        return None
    
    df = ugreen_catalogo['df']
    col_sku = ugreen_catalogo['col_sku']
    col_desc = ugreen_catalogo['col_desc']
    col_stock = ugreen_catalogo.get('col_stock')
    
    # Buscar por SKU o descripción
    mask_sku = df[col_sku].astype(str).str.contains(busqueda, case=False, na=False)
    mask_desc = pd.Series([False] * len(df))
    if col_desc:
        mask_desc = df[col_desc].astype(str).str.contains(busqueda, case=False, na=False)
    
    mask = mask_sku | mask_desc
    
    coincidencias = df[mask]
    
    if coincidencias.empty:
        return None
    
    resultados = []
    for _, row in coincidencias.iterrows():
        sku = str(row[col_sku]).strip().upper()
        descripcion = str(row[col_desc])[:200] if col_desc else f"SKU: {sku}"
        
        # Precios
        precio_mayor = corregir_numero(row.get('Mayor', 0))
        precio_caja = corregir_numero(row.get('Caja', 0))
        precio_vip = corregir_numero(row.get('Vip', 0))
        precio_pvp = corregir_numero(row.get('PVP', 0))
        
        # Stock
        stock = 0
        if col_stock:
            stock = int(corregir_numero(row[col_stock])) if pd.notna(row[col_stock]) else 0
        
        resultados.append({
            'sku': sku,
            'descripcion': descripcion,
            'precios': {
                'P. IR': precio_mayor,
                'P. BOX': precio_caja,
                'P. VIP': precio_vip,
                'PVP': precio_pvp
            },
            'stock': stock,
            'tiene_stock': stock > 0,
            'tiene_precio': precio_vip > 0 or precio_caja > 0 or precio_mayor > 0,
            'tipo': 'UGREEN'
        })
    
    return resultados

# ============================================
# FUNCIÓN PRINCIPAL MODIFICADA (XIAOMI)
# ============================================

def buscar_producto(sku: str, catalogos: List[Dict], stocks: List[Dict], precio_key: str) -> Dict:
    """Busca producto por SKU para XIAOMI. Si tiene stock pero no precio, busca SKU equivalente por descripción."""
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
    
    # Crear DataFrame con los datos
    df = pd.DataFrame(items)
    
    # Crear Excel sin formatos complejos
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Cotizacion', index=False, startrow=6)
        
        # Acceder al workbook y worksheet
        workbook = writer.book
        ws = writer.sheets['Cotizacion']
        
        # ========== ENCABEZADOS SIMPLES ==========
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        
        # Estilos básicos
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="e67e22", end_color="e67e22", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        money_alignment = Alignment(horizontal="right", vertical="center")
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Escribir encabezados de empresa
        ws['A1'] = 'QTC SMART SALES PRO'
        ws['A1'].font = Font(bold=True, size=14, color="e67e22")
        
        ws['A3'] = 'FECHA:'
        ws['B3'] = datetime.now().strftime("%d/%m/%Y %H:%M")
        ws['A4'] = 'CLIENTE:'
        ws['B4'] = cliente.upper()
        ws['A5'] = 'RUC:'
        ws['B5'] = ruc
        
        # Encabezados de tabla
        headers = ['SKU', 'DESCRIPCIÓN', 'CANTIDAD', 'PRECIO UNIT.', 'TOTAL']
        for i, header in enumerate(headers, start=1):
            cell = ws.cell(row=7, column=i, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = border
        
        # Datos
        for row_idx, item in enumerate(items, start=8):
            ws.cell(row=row_idx, column=1, value=item['sku']).border = border
            ws.cell(row=row_idx, column=2, value=item['descripcion']).border = border
            ws.cell(row=row_idx, column=3, value=item['cantidad']).border = border
            
            # Precio y total con formato moneda
            precio_cell = ws.cell(row=row_idx, column=4, value=item['precio'])
            precio_cell.number_format = '"S/." #,##0.00'
            precio_cell.alignment = money_alignment
            precio_cell.border = border
            
            total_cell = ws.cell(row=row_idx, column=5, value=item['total'])
            total_cell.number_format = '"S/." #,##0.00'
            total_cell.alignment = money_alignment
            total_cell.border = border
        
        # Total general
        total_row = len(items) + 8
        total_label = ws.cell(row=total_row, column=4, value='TOTAL S/.')
        total_label.font = Font(bold=True, color="FFFFFF")
        total_label.fill = PatternFill(start_color="e67e22", end_color="e67e22", fill_type="solid")
        total_label.alignment = Alignment(horizontal="center")
        total_label.border = border
        
        total_valor = ws.cell(row=total_row, column=5, value=sum(item['total'] for item in items))
        total_valor.number_format = '"S/." #,##0.00'
        total_valor.alignment = money_alignment
        total_valor.border = border
        
        # ========== AJUSTE DE COLUMNAS ==========
        # Anchos fijos
        ws.column_dimensions['A'].width = 22   # SKU
        ws.column_dimensions['B'].width = 110  # DESCRIPCIÓN
        ws.column_dimensions['C'].width = 12   # Cantidad
        ws.column_dimensions['D'].width = 18   # Precio
        ws.column_dimensions['E'].width = 18   # Total
        
        # Congelar panel
        ws.freeze_panes = 'A8'
    
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
if 'ugreen_catalogo' not in st.session_state:
    st.session_state.ugreen_catalogo = None

# ============================================
# LOGIN (TUS CREDENCIALES + ROLES)
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
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🚀 Ingresar", use_container_width=True):
                # Usuarios con roles
                credenciales = {
                    "admin": {"password": "qtc2026", "role": "ADMIN", "name": "Administrador"},
                    "kimberly": {"password": "kam2026", "role": "KAM", "name": "Kimberly - Key Account Manager"},
                    "vendedor": {"password": "ventas2026", "role": "VENDEDOR", "name": "Vendedor"}
                }
                if user in credenciales and pw == credenciales[user]["password"]:
                    st.session_state.auth = True
                    st.session_state.user_role = credenciales[user]["role"]
                    st.session_state.user_name = credenciales[user]["name"]
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
                    st.info("💡 Usuarios: admin / kimberly / vendedor | Contraseña: usuario+2026")
        with col_btn2:
            if st.button("👤 Modo invitado", use_container_width=True):
                st.session_state.auth = True
                st.session_state.user_role = "INVITADO"
                st.session_state.user_name = "Invitado"
                st.rerun()
        
        st.markdown("<div class='footer'>⚡ QTC Smart Sales Pro</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.stop()

# ============================================
# HEADER CON ROL
# ============================================

col1, col2, col3 = st.columns([1, 5, 2])
with col1:
    try:
        st.image("logo.png", width=60)
    except:
        st.markdown("**QTC**", unsafe_allow_html=True)
with col2:
    st.markdown("# QTC Smart Sales Pro")
    st.caption("Sistema Profesional de Cotización | Soporte XIAOMI · UGREEN · OTRAS MARCAS")
with col3:
    role_badge = {"ADMIN": "🔧", "KAM": "⭐", "VENDEDOR": "🛒", "INVITADO": "👤"}
    badge = role_badge.get(st.session_state.user_role, "👤")
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 12px; text-align: right;">
        <span>{badge} {st.session_state.user_name}</span><br>
        <span style="font-size: 0.7rem;">{st.session_state.user_role}</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 Cerrar Sesión", key="logout"):
        st.session_state.auth = False
        st.session_state.carrito = []
        st.rerun()

st.markdown("---")

# ============================================
# SIDEBAR CON SELECCIÓN DE MARCA
# ============================================

with st.sidebar:
    st.markdown("### 🎯 Configuración")
    
    # NUEVO: Selector de marca
    marca_seleccionada = st.radio(
        "📌 Marca / Modo",
        ["XIAOMI", "UGREEN", "OTRAS MARCAS"],
        index=0 if st.session_state.modo == "XIAOMI" else 1,
        help="XIAOMI: Lógica especial de búsqueda por hojas YESSICA → APRI.004 → APRI.001\nUGREEN: Archivo específico con columnas Mayor/Caja/Vip\nOTRAS MARCAS: Lógica estándar"
    )
    st.session_state.modo = marca_seleccionada
    
    st.markdown("---")
    
    precio_opcion = st.radio(
        "💰 Nivel de precio",
        ["P. VIP", "P. BOX", "P. IR"],
        index=0
    )
    st.session_state.precio_key = precio_opcion
    
    st.markdown("---")
    
    st.markdown("### 📂 Archivos")
    
    # Catálogos de precios (para XIAOMI y OTRAS)
    if marca_seleccionada != "UGREEN":
        st.markdown("**📚 Catálogos de precios (XIAOMI/OTROS)**")
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
    
    # Catálogo UGREEN
    if marca_seleccionada == "UGREEN":
        st.markdown("**📚 Catálogo UGREEN**")
        archivo_ugreen = st.file_uploader(
            "Excel UGREEN (con columnas Mayor/Caja/Vip)",
            type=['xlsx', 'xls'],
            accept_multiple_files=False,
            key="ugreen_upload"
        )
        if archivo_ugreen:
            ugreen_cat = cargar_ugreen_catalogo(archivo_ugreen)
            if ugreen_cat:
                st.session_state.ugreen_catalogo = ugreen_cat
                st.success(f"✅ UGREEN: {archivo_ugreen.name[:30]}")
    
    # Reportes de stock (para todas las marcas)
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

# ========== TAB 1: MODO MASIVO (CORREGIDO) ==========
with tab1:
    st.markdown("### 📦 Ingresa productos en formato masivo")
    st.caption(f"🔍 Modo: **{st.session_state.modo}** | Formato: `SKU:CANTIDAD` (uno por línea)")
    
    texto_bulk = st.text_area(
        "",
        height=200,
        placeholder="Ejemplo:\nRN9401276NA8:100\nCN0200047BK8:100\nRN0200065BK8:50\nCN9406882NA8:25"
    )
    
    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        if st.button("🚀 Procesar lista", type="primary", use_container_width=True):
            if texto_bulk and st.session_state.modo == "XIAOMI" and st.session_state.catalogos and st.session_state.stocks:
                # Lógica XIAOMI
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
                    with st.spinner("Procesando XIAOMI..."):
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
                            elif not prod['tiene_precio'] and prod['tiene_stock']:
                                cantidad_cotizar = 0
                                estado = "⚠️ Stock disponible - SIN PRECIO (Error de SKU)"
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
                            <div class="counter-item"><span>📋</span><span class="counter-label">Ingresados:</span><span class="counter-number">{total_ingresados}</span></div>
                            <div class="counter-item" style="background:#4CAF50;color:white;"><span>✅</span><span class="counter-label" style="color:white;">Encontrados:</span><span class="counter-number" style="color:white;">{total_encontrados}</span></div>
                            <div class="counter-item"><span>📦</span><span class="counter-label">Con stock:</span><span class="counter-number">{total_con_stock}</span></div>
                            <div class="counter-item" style="background:#ffebee;"><span>❌</span><span class="counter-label">Sin precio:</span><span class="counter-number" style="color:#f44336;">{total_sin_precio}</span></div>
                            <div class="counter-item" style="background:#ffebee;"><span>🚫</span><span class="counter-label">Sin stock:</span><span class="counter-number" style="color:#f44336;">{total_sin_stock}</span></div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.success(f"✅ Procesados {len(pedidos)} productos en modo XIAOMI")
                else:
                    st.warning("No se encontraron productos válidos")
                    
            elif texto_bulk and st.session_state.modo == "UGREEN" and st.session_state.ugreen_catalogo:
                # Lógica UGREEN
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
                    with st.spinner("Procesando UGREEN..."):
                        resultados_procesados = []
                        for pedido in pedidos:
                            resultados_ugreen = buscar_ugreen_producto(pedido['sku'], st.session_state.ugreen_catalogo)
                            if resultados_ugreen and len(resultados_ugreen) > 0:
                                prod = resultados_ugreen[0]
                                precio = prod['precios'].get(st.session_state.precio_key, 0)
                                if precio > 0 and prod['tiene_stock']:
                                    cantidad_cotizar = min(pedido['cantidad'], prod['stock'])
                                    estado = "✅ OK"
                                elif precio > 0 and not prod['tiene_stock']:
                                    cantidad_cotizar = 0
                                    estado = "❌ Sin stock"
                                else:
                                    cantidad_cotizar = 0
                                    estado = "❌ Sin precio"
                                
                                resultados_procesados.append({
                                    'sku': prod['sku'],
                                    'descripcion': prod['descripcion'],
                                    'precio': precio,
                                    'stock_total': prod['stock'],
                                    'tiene_stock': prod['tiene_stock'],
                                    'tiene_precio': precio > 0,
                                    'cantidad_solicitada': pedido['cantidad'],
                                    'cantidad_cotizar': cantidad_cotizar,
                                    'estado': estado,
                                    'tipo': 'UGREEN'
                                })
                            else:
                                resultados_procesados.append({
                                    'sku': pedido['sku'],
                                    'descripcion': f"SKU: {pedido['sku']}",
                                    'precio': 0,
                                    'stock_total': 0,
                                    'tiene_stock': False,
                                    'tiene_precio': False,
                                    'cantidad_solicitada': pedido['cantidad'],
                                    'cantidad_cotizar': 0,
                                    'estado': "❌ No encontrado",
                                    'tipo': 'UGREEN'
                                })
                        
                        st.session_state.resultados_bulk = resultados_procesados
                        
                        total_ingresados = len(pedidos)
                        total_encontrados = sum(1 for p in resultados_procesados if p['tiene_precio'])
                        total_con_stock = sum(1 for p in resultados_procesados if p['tiene_stock'])
                        
                        st.markdown(f"""
                        <div class="counter-summary">
                            <div class="counter-item"><span>📋</span><span class="counter-label">Ingresados:</span><span class="counter-number">{total_ingresados}</span></div>
                            <div class="counter-item" style="background:#4CAF50;color:white;"><span>✅</span><span class="counter-label" style="color:white;">Encontrados:</span><span class="counter-number" style="color:white;">{total_encontrados}</span></div>
                            <div class="counter-item"><span>📦</span><span class="counter-label">Con stock:</span><span class="counter-number">{total_con_stock}</span></div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.success(f"✅ Procesados {len(pedidos)} productos en modo UGREEN")
            else:
                if not st.session_state.catalogos and st.session_state.modo == "XIAOMI":
                    st.warning("Carga catálogos de XIAOMI primero")
                elif not st.session_state.ugreen_catalogo and st.session_state.modo == "UGREEN":
                    st.warning("Carga el catálogo de UGREEN primero")
                elif not st.session_state.stocks:
                    st.warning("Carga reportes de stock primero")
                else:
                    st.warning("Ingresa productos en el formato correcto")
    
    with col_b2:
        if st.button("📋 Agregar válidos al carrito", use_container_width=True):
            if hasattr(st.session_state, 'resultados_bulk') and st.session_state.resultados_bulk:
                agregados = 0
                for prod in st.session_state.resultados_bulk:
                    if prod['cantidad_cotizar'] > 0 and prod['tiene_precio']:
                        item_carrito = {
                            'sku': prod['sku'],
                            'descripcion': prod['descripcion'],
                            'cantidad': prod['cantidad_cotizar'],
                            'precio': prod['precio'],
                            'total': prod['precio'] * prod['cantidad_cotizar'],
                            'stock_yessica': prod.get('stock_yessica', 0),
                            'stock_apri004': prod.get('stock_apri004', 0),
                            'stock_apri001': prod.get('stock_apri001', 0),
                            'tipo': prod.get('tipo', 'XIAOMI')
                        }
                        st.session_state.carrito.append(item_carrito)
                        agregados += 1
                st.success(f"✅ Agregados {agregados} productos al carrito")
                st.rerun()
            else:
                st.warning("Primero procesa una lista de productos")
    
    # Mostrar resultados bulk (CORREGIDO con color en todas las tarjetas)
    if 'resultados_bulk' in st.session_state and st.session_state.resultados_bulk:
        st.markdown("---")
        st.markdown("### 📋 Productos procesados")
        
        for prod in st.session_state.resultados_bulk:
            if prod.get('tipo') == 'UGREEN':
                # Badge para UGREEN
                if prod['stock_total'] > 0:
                    badge_stock = f'<span class="badge-ugreen">📦 UGREEN: {prod["stock_total"]}</span>'
                else:
                    badge_stock = '<span class="badge-warning">❌ Sin stock</span>'
                
                st.markdown(f"""
                <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #00BCD4;color:#1a1a2e;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div><strong style="color:#1a1a2e;">📦 {prod['sku']}</strong> <span style="background:#00BCD4;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">UGREEN</span></div>
                        <div><span style="background:#2196F3;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">Solicitado: {prod['cantidad_solicitada']}</span></div>
                    </div>
                    <div style="margin-top:8px;"><span style="font-size:0.85rem;color:#1a1a2e;">{prod['descripcion'][:100]}</span></div>
                    <div style="margin-top:8px;color:#1a1a2e;">💰 Precio: <strong style="color:#1a1a2e;">S/ {prod['precio']:,.2f}</strong> | 📦 Stock: <strong style="color:#1a1a2e;">{prod['stock_total']}</strong></div>
                    <div style="margin-top:8px;">{badge_stock}</div>
                    <div style="margin-top:8px;color:#1a1a2e;"><strong>📌 Estado:</strong> {prod['estado']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Lógica XIAOMI
                badge_stock = construir_badge_stock(prod['stock_yessica'], prod['stock_apri004'], prod['stock_apri001'])
                
                # CASO 1: Stock sin precio (error de SKU)
                if prod['tiene_stock'] and not prod['tiene_precio']:
                    st.markdown(f"""
                    <div style="background:#FFEBEE;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #f44336;color:#1a1a2e;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><span style="background:#f44336;color:white;padding:4px 12px;border-radius:20px;font-size:0.75rem;font-weight:bold;">⚠️ PROBLEMA DETECTADO - ERROR DE SKU</span></div>
                            <div><span style="background:#ff9800;color:white;padding:2px 8px;border-radius:12px;font-size:0.6rem;">Solicitado: {prod['cantidad_solicitada']}</span></div>
                        </div>
                        <div style="margin-top:12px;color:#1a1a2e;">
                            <strong>📦 SKU BUSCADO:</strong> {prod['sku']}<br>
                            <strong>📝 Descripción:</strong> {prod['descripcion']}<br>
                            <strong>📦 Stock disponible:</strong> {prod['stock_total']} unidades<br>
                            <strong>⚠️ Estado:</strong> {prod['estado']}
                        </div>
                        <div style="margin-top:8px;">{badge_stock}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # SKU equivalente sugerido
                    if prod.get('sku_equivalente'):
                        st.markdown(f"""
                        <div style="background:#E8F5E9;border-radius:12px;padding:1rem;margin:0.5rem 0;border-left:4px solid #4CAF50;color:#1a1a2e;">
                            <strong style="color:#2E7D32;">💡 SE ENCONTRÓ EL ARTÍCULO CON MISMA DESCRIPCIÓN PERO OTRO SKU</strong>
                            <div style="margin-top:10px;color:#1a1a2e;">
                                <strong>SKU equivalente:</strong> <code>{prod['sku_equivalente']}</code><br>
                                <strong>Precio {st.session_state.precio_key}:</strong> S/ {prod.get('precio_equivalente', 0):,.2f}<br>
                                <strong>Coincidencia:</strong> {prod.get('similitud_equivalente', 0):.0f}%
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    elif prod.get('alternativas') and len(prod['alternativas']) > 0:
                        st.markdown('<div style="background:#FFF8E1;border-radius:12px;padding:0.75rem;margin:0.5rem 0;color:#1a1a2e;"><strong>💡 PRODUCTOS SIMILARES ENCONTRADOS:</strong></div>', unsafe_allow_html=True)
                        for alt in prod['alternativas'][:3]:
                            badge_alt = construir_badge_stock(alt['stock_yessica'], alt['stock_apri004'], alt['stock_apri001'])
                            st.markdown(f"""
                            <div class="alternativa-item">
                                <div style="color:#1a1a2e;"><strong>📦 {alt['sku']}</strong> <span style="background:#FF9800;color:white;padding:2px 6px;border-radius:10px;font-size:0.6rem;">{alt['similitud']:.0f}% coincidencia</span></div>
                                <div style="font-size:0.75rem;color:#1a1a2e;">{alt['descripcion'][:80]}</div>
                                <div style="margin-top:6px;color:#1a1a2e;">💰 Precio: S/ {alt['precio']:,.2f} | 📦 Stock: {alt['stock_total']}</div>
                                <div style="margin-top:6px;">{badge_alt}</div>
                            </div>
                            """, unsafe_allow_html=True)
                
                # CASO 2: Con stock y precio
                elif prod['tiene_stock'] and prod['tiene_precio']:
                    cantidad_final = prod['cantidad_cotizar']
                    st.markdown(f"""
                    <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #4CAF50;color:#1a1a2e;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong style="color:#1a1a2e;">📦 {prod['sku']}</strong> <span style="background:#4CAF50;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">✅ CON STOCK Y PRECIO</span></div>
                            <div><span style="background:#2196F3;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">Cotizar: {cantidad_final}/{prod['cantidad_solicitada']}</span></div>
                        </div>
                        <div style="margin-top:8px;"><span style="font-size:0.85rem;color:#1a1a2e;">{prod['descripcion']}</span></div>
                        <div style="margin-top:8px;color:#1a1a2e;">💰 Precio: <strong style="color:#1a1a2e;">S/ {prod['precio']:,.2f}</strong> | 📦 Stock: <strong style="color:#1a1a2e;">{prod['stock_total']}</strong></div>
                        <div style="margin-top:8px;">{badge_stock}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # CASO 3: Solo precio, sin stock
                elif not prod['tiene_stock'] and prod['tiene_precio']:
                    st.markdown(f"""
                    <div style="background:#E3F2FD;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #2196F3;color:#1a1a2e;">
                        <div><strong style="color:#1a1a2e;">📦 {prod['sku']}</strong> <span style="background:#2196F3;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">📋 SOLO PRECIO - SIN STOCK</span></div>
                        <div style="margin-top:8px;"><span style="font-size:0.85rem;color:#1a1a2e;">{prod['descripcion']}</span></div>
                        <div style="margin-top:8px;color:#1a1a2e;">💰 Precio: <strong style="color:#1a1a2e;">S/ {prod['precio']:,.2f}</strong></div>
                        <div style="margin-top:8px;">{badge_stock}</div>
                        <div style="margin-top:8px;color:#1a1a2e;"><strong>⚠️ Estado:</strong> {prod['estado']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # CASO 4: No disponible
                else:
                    st.markdown(f"""
                    <div style="background:#F5F5F5;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #9e9e9e;color:#1a1a2e;">
                        <div><strong style="color:#1a1a2e;">📦 {prod['sku']}</strong> <span style="background:#9e9e9e;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">❌ NO DISPONIBLE</span></div>
                        <div style="margin-top:8px;"><span style="font-size:0.85rem;color:#1a1a2e;">{prod['descripcion']}</span></div>
                        <div style="margin-top:8px;">{badge_stock}</div>
                        <div style="margin-top:8px;color:#1a1a2e;"><strong>⚠️ Estado:</strong> {prod['estado']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.divider()
        
        if st.button("🗑️ Limpiar resultados", key="clear_bulk_results", use_container_width=True):
            del st.session_state.resultados_bulk
            st.rerun()

# ========== TAB 2: BÚSQUEDA INTELIGENTE (MODIFICADA) ==========
with tab2:
    st.markdown("### 🔍 Buscar productos por SKU o descripción")
    st.caption(f"🔎 Modo: **{st.session_state.modo}** | Busca por SKU exacto o por cualquier palabra en la descripción")
    
    busqueda = st.text_input("", placeholder="Ej: 'RN9401276NA8' o 'Xiaomi Type-C Earphones Black' o 'CN9406882NA8'")
    
    if busqueda and len(busqueda) >= 2:
        if st.session_state.modo == "XIAOMI" and st.session_state.catalogos and st.session_state.stocks:
            with st.spinner("🔍 Buscando en XIAOMI..."):
                # Usar la lógica existente de tu código
                productos_por_sku = {}
                
                # Buscar en catálogos
                for cat in st.session_state.catalogos:
                    df = cat['df']
                    mask_sku = df[cat['col_sku']].astype(str).str.contains(busqueda, case=False, na=False)
                    mask_desc = pd.Series([False] * len(df))
                    if cat['col_desc']:
                        mask_desc = df[cat['col_desc']].astype(str).str.contains(busqueda, case=False, na=False)
                    mask = mask_sku | mask_desc
                    
                    for _, row in df[mask].iterrows():
                        sku = str(row[cat['col_sku']]).strip().upper()
                        descripcion = str(row[cat['col_desc']])[:200] if cat['col_desc'] else f"SKU: {sku}"
                        precio = 0.0
                        if st.session_state.precio_key in cat['precios']:
                            col_precio = cat['precios'][st.session_state.precio_key]
                            precio = corregir_numero(row[col_precio])
                        stock_info = buscar_stock_para_sku(sku, st.session_state.stocks)
                        
                        if sku in productos_por_sku:
                            existente = productos_por_sku[sku]
                            if precio > existente['precio']:
                                existente['precio'] = precio
                            existente['stock_yessica'] += stock_info['yessica']
                            existente['stock_apri004'] += stock_info['apri004']
                            existente['stock_apri001'] += stock_info['apri001']
                            existente['stock_total'] = existente['stock_yessica'] + existente['stock_apri004'] + existente['stock_apri001']
                            existente['tiene_stock'] = existente['stock_total'] > 0
                            existente['tiene_precio'] = existente['tiene_precio'] or (precio > 0)
                        else:
                            productos_por_sku[sku] = {
                                'sku': sku,
                                'descripcion': descripcion,
                                'precio': precio,
                                'stock_yessica': stock_info['yessica'],
                                'stock_apri004': stock_info['apri004'],
                                'stock_apri001': stock_info['apri001'],
                                'stock_total': stock_info['total'],
                                'tiene_stock': stock_info['total'] > 0,
                                'tiene_precio': precio > 0,
                                'usa_apri001': stock_info['apri001'] > 0 and stock_info['yessica'] == 0 and stock_info['apri004'] == 0
                            }
                
                # Buscar en stocks
                for stock in st.session_state.stocks:
                    df = stock['df']
                    col_sku = stock['col_sku']
                    mask_sku = df[col_sku].astype(str).str.contains(busqueda, case=False, na=False)
                    
                    columnas_desc = []
                    for col in df.columns:
                        col_upper = str(col).upper()
                        if any(p in col_upper for p in ['DESC', 'PRODUCTO', 'NOMBRE', 'ARTICULO', 'GOODS']):
                            columnas_desc.append(col)
                    mask_desc = pd.Series([False] * len(df))
                    for col_desc in columnas_desc:
                        mask_desc = mask_desc | df[col_desc].astype(str).str.contains(busqueda, case=False, na=False)
                    
                    mask = mask_sku | mask_desc
                    
                    for _, row in df[mask].iterrows():
                        sku = str(row[col_sku]).strip().upper()
                        cantidad = 0
                        for col in df.columns:
                            col_upper = str(col).upper()
                            if any(p in col_upper for p in ['CANT', 'STOCK', 'DISPONIBLE', 'UNIDADES']):
                                cantidad = int(corregir_numero(row[col]))
                                break
                        
                        hoja = stock['hoja'].upper()
                        stock_yessica = cantidad if 'YESSICA' in hoja else 0
                        stock_apri004 = cantidad if 'APRI.004' in hoja else 0
                        stock_apri001 = cantidad if 'APRI.001' in hoja else 0
                        
                        precio = 0.0
                        descripcion_stock = ""
                        for col_desc in columnas_desc:
                            desc_val = str(row[col_desc])
                            if desc_val and desc_val != 'nan' and len(desc_val) > len(descripcion_stock):
                                descripcion_stock = desc_val[:200]
                        
                        for cat in st.session_state.catalogos:
                            df_cat = cat['df']
                            df_sku = df_cat[cat['col_sku']].astype(str).str.strip().str.upper()
                            mask_cat = df_sku == sku
                            if mask_cat.any():
                                row_cat = df_cat[mask_cat].iloc[0]
                                if st.session_state.precio_key in cat['precios']:
                                    col_precio = cat['precios'][st.session_state.precio_key]
                                    precio = corregir_numero(row_cat[col_precio])
                                break
                        
                        descripcion_final = descripcion_stock if descripcion_stock else f"SKU: {sku}"
                        
                        if sku in productos_por_sku:
                            existente = productos_por_sku[sku]
                            existente['stock_yessica'] += stock_yessica
                            existente['stock_apri004'] += stock_apri004
                            existente['stock_apri001'] += stock_apri001
                            existente['stock_total'] = existente['stock_yessica'] + existente['stock_apri004'] + existente['stock_apri001']
                            existente['tiene_stock'] = existente['stock_total'] > 0
                            if precio > 0 and not existente['tiene_precio']:
                                existente['precio'] = precio
                                existente['tiene_precio'] = True
                            if len(descripcion_final) > len(existente['descripcion']):
                                existente['descripcion'] = descripcion_final
                            existente['usa_apri001'] = existente['stock_apri001'] > 0 and existente['stock_yessica'] == 0 and existente['stock_apri004'] == 0
                        else:
                            productos_por_sku[sku] = {
                                'sku': sku,
                                'descripcion': descripcion_final,
                                'precio': precio,
                                'stock_yessica': stock_yessica,
                                'stock_apri004': stock_apri004,
                                'stock_apri001': stock_apri001,
                                'stock_total': stock_yessica + stock_apri004 + stock_apri001,
                                'tiene_stock': (stock_yessica + stock_apri004 + stock_apri001) > 0,
                                'tiene_precio': precio > 0,
                                'usa_apri001': stock_apri001 > 0 and stock_yessica == 0 and stock_apri004 == 0
                            }
                
                # Detectar SKU con error (stock sin precio)
                for sku, prod in productos_por_sku.items():
                    if prod['tiene_stock'] and not prod['tiene_precio']:
                        mejor_match = None
                        mejor_similitud = 70.0
                        for cat in st.session_state.catalogos:
                            if not cat['col_desc']:
                                continue
                            df = cat['df']
                            for _, row in df.iterrows():
                                desc_catalogo = str(row[cat['col_desc']])[:200]
                                similitud = calcular_similitud(prod['descripcion'], desc_catalogo)
                                if similitud >= mejor_similitud:
                                    sku_match = str(row[cat['col_sku']]).strip().upper()
                                    if sku_match == sku:
                                        continue
                                    precio_match = 0.0
                                    if st.session_state.precio_key in cat['precios']:
                                        col_precio = cat['precios'][st.session_state.precio_key]
                                        precio_match = corregir_numero(row[col_precio])
                                    mejor_similitud = similitud
                                    mejor_match = {
                                        'sku': sku_match,
                                        'descripcion': desc_catalogo,
                                        'precio': precio_match,
                                        'similitud': similitud
                                    }
                        if mejor_match and mejor_match['precio'] > 0:
                            prod['sku_equivalente'] = mejor_match['sku']
                            prod['similitud_equivalente'] = mejor_match['similitud']
                            prod['precio_equivalente'] = mejor_match['precio']
                        
                        alternativas = encontrar_alternativas_mismo_producto(
                            sku, prod['descripcion'], st.session_state.catalogos,
                            st.session_state.stocks, st.session_state.precio_key, umbral=70.0
                        )
                        prod['alternativas'] = alternativas
                
                if productos_por_sku:
                    st.success(f"✅ {len(productos_por_sku)} productos encontrados en XIAOMI")
                    resultados_lista = list(productos_por_sku.values())
                    resultados_lista.sort(key=lambda x: (-x['tiene_stock'], -x['tiene_precio']))
                    
                    for prod in resultados_lista:
                        badges = []
                        if prod['stock_yessica'] > 0:
                            badges.append(f'<span class="badge-yessica">🟢 YESSICA: {prod["stock_yessica"]}</span>')
                        if prod['stock_apri004'] > 0:
                            badges.append(f'<span class="badge-apri004">🟡 APRI.004: {prod["stock_apri004"]}</span>')
                        if prod['stock_apri001'] > 0:
                            badges.append(f'<span class="badge-apri001">🔴 APRI.001: {prod["stock_apri001"]} {"⚠️ SOLICITAR TRANSFERENCIA" if st.session_state.modo == "XIAOMI" else ""}</span>')
                        badges_html = ' '.join(badges) if badges else '<span class="badge-warning">❌ Sin stock</span>'
                        
                        if prod['tiene_stock'] and not prod['tiene_precio']:
                            border_color = "#f44336"
                            bg_color = "#FFEBEE"
                        elif prod['tiene_stock'] and prod['tiene_precio']:
                            border_color = "#4CAF50"
                            bg_color = "white"
                        elif not prod['tiene_stock'] and prod['tiene_precio']:
                            border_color = "#2196F3"
                            bg_color = "#E3F2FD"
                        else:
                            border_color = "#9e9e9e"
                            bg_color = "#F5F5F5"
                        
                        st.markdown(f"""
                        <div style="background:{bg_color};border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid {border_color};color:#1a1a2e;">
                            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
                                <div><strong style="font-size:1rem;color:#1a1a2e;">📦 {prod['sku']}</strong></div>
                        """, unsafe_allow_html=True)
                        
                        if prod['tiene_stock'] and prod['tiene_precio']:
                            st.markdown('<span style="background:#4CAF50;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">✅ CON STOCK Y PRECIO</span>', unsafe_allow_html=True)
                        elif prod['tiene_stock'] and not prod['tiene_precio']:
                            st.markdown('<span style="background:#f44336;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">⚠️ STOCK SIN PRECIO - ERROR DE SKU</span>', unsafe_allow_html=True)
                        elif not prod['tiene_stock'] and prod['tiene_precio']:
                            st.markdown('<span style="background:#2196F3;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">📋 SOLO PRECIO - SIN STOCK</span>', unsafe_allow_html=True)
                        else:
                            st.markdown('<span style="background:#9e9e9e;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">❌ NO DISPONIBLE</span>', unsafe_allow_html=True)
                        
                        st.markdown(f"""
                            </div>
                            <div style="margin-top:12px;color:#333;"><strong>📝 Descripción:</strong> {prod['descripcion']}</div>
                            <div style="margin-top:8px;color:#333;"><strong>💰 Precio {st.session_state.precio_key}:</strong> <span style="font-weight:bold;">S/ {prod['precio']:,.2f}</span> <span style="margin-left:16px;"><strong>📦 Stock total:</strong> {prod['stock_total']}</span></div>
                            <div style="margin-top:8px;">{badges_html}</div>
                        """, unsafe_allow_html=True)
                        
                        if prod.get('usa_apri001') and st.session_state.modo == "XIAOMI":
                            st.markdown('<div style="background:#FCE4EC;padding:0.5rem;border-radius:8px;margin:0.5rem 0;color:#c62828;font-size:0.75rem;">⚠️ con stock pero debes solicitar transferencia</div>', unsafe_allow_html=True)
                        
                        if prod['tiene_stock'] and not prod['tiene_precio']:
                            if prod.get('sku_equivalente'):
                                st.markdown(f"""
                                <div style="background:#E8F5E9;border-radius:12px;padding:1rem;margin:0.5rem 0;border-left:4px solid #4CAF50;color:#1a1a2e;">
                                    <strong style="color:#2E7D32;">💡 SKU EQUIVALENTE SUGERIDO</strong>
                                    <div style="margin-top:8px;">
                                        <strong>SKU:</strong> <code>{prod['sku_equivalente']}</code><br>
                                        <strong>Precio:</strong> S/ {prod.get('precio_equivalente', 0):,.2f}<br>
                                        <strong>Coincidencia:</strong> {prod.get('similitud_equivalente', 0):.0f}%
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                col_eq1, col_eq2 = st.columns(2)
                                with col_eq1:
                                    if st.button(f"➕ Usar SKU equivalente ({prod['sku_equivalente']})", key=f"use_eq_{prod['sku']}"):
                                        item_carrito = {
                                            'sku': prod['sku_equivalente'],
                                            'descripcion': prod.get('descripcion', ''),
                                            'cantidad': 1,
                                            'precio': prod.get('precio_equivalente', 0),
                                            'total': prod.get('precio_equivalente', 0),
                                            'stock_yessica': prod['stock_yessica'],
                                            'stock_apri004': prod['stock_apri004'],
                                            'stock_apri001': prod['stock_apri001']
                                        }
                                        st.session_state.carrito.append(item_carrito)
                                        st.success(f"✅ Agregado {prod['sku_equivalente']} al carrito")
                                        st.rerun()
                                with col_eq2:
                                    if st.button(f"📝 Seguir con SKU original ({prod['sku']})", key=f"use_orig_{prod['sku']}"):
                                        st.warning(f"El SKU {prod['sku']} no tiene precio. No se puede agregar al carrito.")
                        
                        elif prod['tiene_stock'] and prod['tiene_precio']:
                            col_cant, col_btn = st.columns([1, 2])
                            with col_cant:
                                cantidad = st.number_input("Cantidad", min_value=1, max_value=prod['stock_total'], value=1, step=1, key=f"ok_{prod['sku']}")
                            with col_btn:
                                if st.button(f"➕ Agregar a cotización", key=f"add_ok_{prod['sku']}"):
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
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.divider()
                else:
                    st.info("No se encontraron productos en XIAOMI con esa búsqueda.")
        
        elif st.session_state.modo == "UGREEN" and st.session_state.ugreen_catalogo:
            with st.spinner("🔍 Buscando en UGREEN..."):
                resultados_ugreen = buscar_ugreen_producto(busqueda, st.session_state.ugreen_catalogo)
                
                if resultados_ugreen:
                    st.success(f"✅ {len(resultados_ugreen)} productos encontrados en UGREEN")
                    
                    for prod in resultados_ugreen:
                        precio_seleccionado = prod['precios'].get(st.session_state.precio_key, 0)
                        
                        badge_stock = '<span class="badge-ugreen">📦 UGREEN Stock: ' + str(prod['stock']) + '</span>' if prod['stock'] > 0 else '<span class="badge-warning">❌ Sin stock</span>'
                        
                        st.markdown(f"""
                        <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #00BCD4;color:#1a1a2e;">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <div><strong style="font-size:1rem;">📦 {prod['sku']}</strong> <span style="background:#00BCD4;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">UGREEN</span></div>
                            </div>
                            <div style="margin-top:12px;"><strong>📝 Descripción:</strong> {prod['descripcion']}</div>
                            <div style="margin-top:8px;">
                                <strong>💰 Precios:</strong><br>
                                • P. IR (Mayorista): S/ {prod['precios'].get('P. IR', 0):,.2f}<br>
                                • P. BOX (Caja): S/ {prod['precios'].get('P. BOX', 0):,.2f}<br>
                                • P. VIP: S/ {prod['precios'].get('P. VIP', 0):,.2f}
                            </div>
                            <div style="margin-top:8px;">{badge_stock}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if prod['tiene_stock'] and prod['tiene_precio'] and precio_seleccionado > 0:
                            col_cant, col_btn = st.columns([1, 2])
                            with col_cant:
                                cantidad = st.number_input("Cantidad", min_value=1, max_value=prod['stock'], value=1, step=1, key=f"ugreen_{prod['sku']}")
                            with col_btn:
                                if st.button(f"➕ Agregar a cotización (UGREEN)", key=f"add_ugreen_{prod['sku']}"):
                                    item_carrito = {
                                        'sku': prod['sku'],
                                        'descripcion': prod['descripcion'],
                                        'cantidad': cantidad,
                                        'precio': precio_seleccionado,
                                        'total': precio_seleccionado * cantidad,
                                        'stock_yessica': 0,
                                        'stock_apri004': 0,
                                        'stock_apri001': 0,
                                        'tipo': 'UGREEN'
                                    }
                                    st.session_state.carrito.append(item_carrito)
                                    st.success(f"✅ Agregado {cantidad}x {prod['sku']} (UGREEN)")
                                    st.rerun()
                        elif prod['tiene_stock'] and precio_seleccionado == 0:
                            st.warning("⚠️ El producto tiene stock pero el nivel de precio seleccionado no está disponible. Selecciona otro nivel de precio en el sidebar.")
                        else:
                            st.info("Producto no disponible para cotización (sin stock o sin precio).")
                        
                        st.divider()
                else:
                    st.info("No se encontraron productos en UGREEN con esa búsqueda.")
        
        elif st.session_state.modo == "OTRAS MARCAS":
            st.info("🔧 Modo 'OTRAS MARCAS' - Funcionalidad en desarrollo. Carga catálogos y stocks correspondientes.")
        
        else:
            if st.session_state.modo == "XIAOMI" and not st.session_state.catalogos:
                st.warning("⚠️ No hay catálogos de XIAOMI cargados.")
            if st.session_state.modo == "UGREEN" and not st.session_state.ugreen_catalogo:
                st.warning("⚠️ No hay catálogo de UGREEN cargado.")
            if not st.session_state.stocks:
                st.warning("⚠️ No hay stocks cargados.")
    
    elif busqueda and len(busqueda) >= 2:
        st.info("Carga los archivos necesarios en el sidebar para realizar búsquedas.")

# ========== TAB 3: CARRITO (SIN CAMBIOS) ==========
with tab3:
    st.markdown("### 🛒 Cotización actual")
    
    if not st.session_state.carrito:
        st.info("No hay productos en el carrito.")
    else:
        for idx, item in enumerate(st.session_state.carrito):
            col1, col2, col3, col4, col5, col6 = st.columns([2, 3, 1, 1, 1, 0.5])
            with col1:
                st.write(f"**{item['sku']}**")
            with col2:
                st.write(item['descripcion'][:50])
            with col3:
                nueva_cant = st.number_input("Cant", min_value=0, max_value=item.get('stock_yessica', 0)+item.get('stock_apri004', 0)+item.get('stock_apri001', 0) or 1000, value=item['cantidad'], step=1, key=f"edit_{idx}", label_visibility="collapsed")
                if nueva_cant != item['cantidad']:
                    item['cantidad'] = nueva_cant
                    item['total'] = item['precio'] * nueva_cant
                    if nueva_cant == 0:
                        st.session_state.carrito.pop(idx)
                        st.rerun()
            with col4:
                st.write(f"S/ {item['precio']:,.2f}")
            with col5:
                st.write(f"S/ {item['total']:,.2f}")
            with col6:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.carrito.pop(idx)
                    st.rerun()
            
            if item.get('tipo') == 'UGREEN':
                st.markdown(f'<div style="margin-bottom:0.5rem;"><span class="badge-ugreen">📦 UGREEN Stock: disponible</span></div>', unsafe_allow_html=True)
            else:
                badge = construir_badge_stock(item.get('stock_yessica', 0), item.get('stock_apri004', 0), item.get('stock_apri001', 0))
                st.markdown(f'<div style="margin-bottom:0.5rem;">{badge}</div>', unsafe_allow_html=True)
            st.divider()
        
        total_general = sum(item['total'] for item in st.session_state.carrito)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#e94560 0%,#c73e54 100%);border-radius:12px;padding:1rem;margin:1rem 0;text-align:center;">
            <span style="color:white;font-size:1.5rem;font-weight:bold;">TOTAL: S/ {total_general:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📋 Datos del cliente")
        col_cli1, col_cli2 = st.columns(2)
        with col_cli1:
            cliente = st.text_input("Nombre del cliente", placeholder="Ej: Empresa SAC")
        with col_cli2:
            ruc = st.text_input("RUC/DNI", placeholder="Ej: 20123456789")
        
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        with col_exp1:
            if st.button("📥 Exportar Excel", type="primary", use_container_width=True):
                if cliente:
                    items_export = [{'sku': i['sku'], 'descripcion': i['descripcion'], 'cantidad': i['cantidad'], 'precio': i['precio'], 'total': i['total']} for i in st.session_state.carrito]
                    excel = generar_excel(items_export, cliente, ruc)
                    st.download_button("💾 Descargar", data=excel, file_name=f"Cotizacion_{cliente}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", use_container_width=True)
                    st.balloons()
                    st.success("✅ Cotización generada")
                else:
                    st.warning("Ingresa el nombre del cliente")
        with col_exp2:
            if st.button("📋 Copiar CSV", use_container_width=True):
                csv_text = "SKU,Descripción,Cantidad,Precio,Subtotal\n"
                for item in st.session_state.carrito:
                    csv_text += f"{item['sku']},{item['descripcion']},{item['cantidad']},{item['precio']:.2f},{item['total']:.2f}\n"
                csv_text += f"TOTAL,{total_general:.2f}"
                st.code(csv_text, language="csv")
        with col_exp3:
            if st.button("🧹 Limpiar todo", use_container_width=True):
                st.session_state.carrito = []
                st.rerun()

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown(f'<div class="footer">⚡ QTC Smart Sales Pro v4.2 | Modo: {st.session_state.modo} | {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>', unsafe_allow_html=True)
