# app.py - QTC Smart Sales Pro v5.2
# PROFESSIONAL EDITION WITH MULTI-CATALOG SUPPORT
# Búsqueda HÍBRIDA en MÚLTIPLES catálogos + STOCK
# Cards con diseño profesional y texto legible

import streamlit as st
import pandas as pd
import re
import io
from datetime import datetime
import warnings
from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher

warnings.filterwarnings('ignore')

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================

st.set_page_config(
    page_title="QTC Smart Sales Pro v5.2",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS V5.2 - MEJORADO PARA LEGIBILIDAD
# ============================================

st.markdown("""
<style>
    /* FONDO DE PÁGINA */
    .stApp {
        background: linear-gradient(135deg, #0d47a1 0%, #1565c0 50%, #1e88e5 100%);
    }
    
    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8a35e 0%, #e87a2d 50%, #d45a1a 100%);
        border-right: 1px solid #ffcc80;
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* TARJETAS DE RESULTADOS - BLANCAS CON TEXTO OSCURO */
    .result-card {
        background: #ffffff !important;
        border-radius: 16px !important;
        padding: 1.2rem !important;
        margin-bottom: 1rem !important;
        color: #1a1a2e !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        border-left: 5px solid #4CAF50 !important;
    }
    
    .result-card-warning {
        background: #ffffff !important;
        border-radius: 16px !important;
        padding: 1.2rem !important;
        margin-bottom: 1rem !important;
        color: #1a1a2e !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        border-left: 5px solid #ff9800 !important;
    }
    
    .result-card-danger {
        background: #ffffff !important;
        border-radius: 16px !important;
        padding: 1.2rem !important;
        margin-bottom: 1rem !important;
        color: #1a1a2e !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        border-left: 5px solid #f44336 !important;
    }
    
    /* TEXTOS DENTRO DE TARJETAS */
    .result-card *,
    .result-card-warning *,
    .result-card-danger * {
        color: #1a1a2e !important;
    }
    
    .result-card strong,
    .result-card-warning strong,
    .result-card-danger strong {
        color: #1a1a2e !important;
        font-weight: 700 !important;
    }
    
    .result-sku {
        font-size: 1.1rem;
        font-weight: bold;
        color: #1565c0 !important;
        font-family: monospace;
    }
    
    .result-desc {
        font-size: 0.9rem;
        color: #333333 !important;
        margin-top: 8px;
        margin-bottom: 8px;
    }
    
    .result-price {
        font-size: 1rem;
        font-weight: bold;
        color: #2e7d32 !important;
    }
    
    /* BADGES */
    .badge-yessica { background: #4CAF50; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    .badge-apri004 { background: #FF9800; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    .badge-apri001 { background: #f44336; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    .badge-warning { background: #ff9800; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; }
    .badge-ugreen { background: #00BCD4; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    .badge-stock { background: #2196F3; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    
    /* CHAT ASISTENTE */
    .chat-message-user {
        background: #0084ff;
        color: white;
        padding: 10px 15px;
        border-radius: 20px;
        margin: 5px 0;
        align-self: flex-end;
        max-width: 80%;
    }
    .chat-message-assistant {
        background: #e4e6eb;
        color: black;
        padding: 10px 15px;
        border-radius: 20px;
        margin: 5px 0;
        align-self: flex-start;
        max-width: 80%;
    }
    .chat-message-warning {
        background: #fff3e0;
        color: #e65100;
        padding: 10px 15px;
        border-radius: 20px;
        margin: 5px 0;
        align-self: flex-start;
        max-width: 80%;
        border-left: 4px solid #ff9800;
    }
    
    /* FOOTER */
    .footer {
        text-align: center;
        padding: 1rem;
        color: rgba(255,255,255,0.7);
        font-size: 0.7rem;
        border-top: 1px solid rgba(255,255,255,0.2);
        margin-top: 2rem;
    }
    
    /* TEXTOS BLANCOS EN GENERAL */
    .stMarkdown, .stText, .stNumberInput label, .stSelectbox label, 
    .stRadio label, .stTextInput label, .stTextArea label, h1, h2, h3, h4 {
        color: #ffffff !important;
    }
    
    /* ALERTAS */
    div[data-testid="stAlert"][data-kind="success"] { background: #2e7d32 !important; border-left: 4px solid #1b5e20 !important; border-radius: 12px !important; }
    div[data-testid="stAlert"][data-kind="warning"] { background: #f9a825 !important; border-left: 4px solid #f57f17 !important; border-radius: 12px !important; }
    div[data-testid="stAlert"][data-kind="error"] { background: #d32f2f !important; border-left: 4px solid #b71c1c !important; border-radius: 12px !important; }
    div[data-testid="stAlert"][data-kind="info"] { background: #0288d1 !important; border-left: 4px solid #01579b !important; border-radius: 12px !important; }
    
    /* TABLA DE RESULTADOS */
    .dataframe {
        background: white !important;
        border-radius: 12px !important;
    }
    .dataframe th {
        background: #1565c0 !important;
        color: white !important;
    }
    .dataframe td {
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

# ============================================
# CARGA INTELIGENTE DE CATÁLOGO (MÚLTIPLES)
# ============================================

def cargar_catalogo_inteligente(archivo, nombre_personalizado=None) -> Optional[Dict]:
    """Carga un catálogo detectando automáticamente todas las columnas"""
    df = cargar_archivo(archivo)
    if df is None:
        return None
    
    columnas = {}
    
    # Detectar SKU
    posibles_sku = ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO', 'CODIGO', 'ID', 'COD_SAP', 'MODEL']
    for col in df.columns:
        col_upper = str(col).upper()
        for posible in posibles_sku:
            if posible.upper() in col_upper:
                columnas['sku'] = col
                break
        if 'sku' in columnas:
            break
    if 'sku' not in columnas:
        columnas['sku'] = df.columns[0]
    
    # Detectar Descripción
    posibles_desc = ['DESC', 'DESCRIPCION', 'NOMBRE', 'PRODUCTO', 'GOODS', 'TITLE', 'DESCRIPTION', 'NOMBRE PRODUCTO']
    for col in df.columns:
        col_upper = str(col).upper()
        for posible in posibles_desc:
            if posible.upper() in col_upper:
                columnas['descripcion'] = col
                break
        if 'descripcion' in columnas:
            break
    
    # Detectar Código de Barras
    posibles_barcode = ['BARCODE', 'EAN', 'UPC', 'CODIGO_BARRAS', 'GTIN', 'COD_BARRA']
    for col in df.columns:
        col_upper = str(col).upper()
        for posible in posibles_barcode:
            if posible.upper() in col_upper:
                columnas['barcode'] = col
                break
        if 'barcode' in columnas:
            break
    
    # Detectar Modelo
    posibles_modelo = ['MODELO', 'MODEL', 'PART', 'PART_NO', 'PN']
    for col in df.columns:
        col_upper = str(col).upper()
        for posible in posibles_modelo:
            if posible.upper() in col_upper:
                columnas['modelo'] = col
                break
        if 'modelo' in columnas:
            break
    
    # Detectar Marca/Categoría
    posibles_marca = ['MARCA', 'BRAND', 'CATEGORIA', 'CATEGORY', 'FAMILIA', 'FAMILY']
    for col in df.columns:
        col_upper = str(col).upper()
        for posible in posibles_marca:
            if posible.upper() in col_upper:
                columnas['marca'] = col
                break
        if 'marca' in columnas:
            break
    
    # Detectar precios
    precios = {}
    mapeo_precios = {'P. IR': ['IR', 'MAYORISTA', 'MAYOR', 'P.IR'], 
                     'P. BOX': ['BOX', 'CAJA', 'P.BOX'], 
                     'P. VIP': ['VIP', 'P.VIP']}
    
    for key, patrones in mapeo_precios.items():
        for col in df.columns:
            col_upper = str(col).upper()
            for patron in patrones:
                if patron in col_upper or patron.upper() == col_upper:
                    precios[key] = col
                    break
            if key in precios:
                break
    
    nombre_archivo = nombre_personalizado if nombre_personalizado else archivo.name
    
    return {
        'nombre': nombre_archivo,
        'df': df,
        'columnas': columnas,
        'precios': precios,
        'tiene_barcode': 'barcode' in columnas,
        'tiene_modelo': 'modelo' in columnas,
        'tiene_marca': 'marca' in columnas
    }

# ============================================
# BÚSQUEDA EN MÚLTIPLES CATÁLOGOS
# ============================================

def buscar_en_catalogos(termino: str, catalogos: List[Dict]) -> pd.DataFrame:
    """Busca en múltiples catálogos y combina resultados"""
    if not catalogos:
        return pd.DataFrame()
    
    todos_resultados = []
    
    for catalogo in catalogos:
        resultados = busqueda_unificada(termino, catalogo)
        if not resultados.empty:
            # Agregar información del catálogo
            resultados['_catalogo_nombre'] = catalogo['nombre']
            todos_resultados.append(resultados)
    
    if todos_resultados:
        df_final = pd.concat(todos_resultados, ignore_index=True)
        df_final = df_final.sort_values('_score', ascending=False)
        return df_final
    
    return pd.DataFrame()

def busqueda_unificada(termino: str, catalogo: Dict) -> pd.DataFrame:
    """Busca en un catálogo específico"""
    if not termino or len(termino) < 2:
        return pd.DataFrame()
    
    termino_limpio = termino.strip().upper()
    df = catalogo['df']
    columnas = catalogo['columnas']
    
    resultados = []
    
    for idx, row in df.iterrows():
        score = 0
        match_tipos = []
        
        sku = str(row.get(columnas.get('sku', ''), '')).upper()
        descripcion = str(row.get(columnas.get('descripcion', ''), '')).upper()
        barcode = str(row.get(columnas.get('barcode', ''), '')).upper() if 'barcode' in columnas else ''
        modelo = str(row.get(columnas.get('modelo', ''), '')).upper() if 'modelo' in columnas else ''
        marca = str(row.get(columnas.get('marca', ''), '')).upper() if 'marca' in columnas else ''
        
        # SKU exacto
        if termino_limpio == sku:
            score = 100
            match_tipos.append('SKU_EXACTO')
        elif termino_limpio in sku:
            score = max(score, 75)
            match_tipos.append('SKU_CONTIENE')
        
        # Código de barras
        if barcode and termino_limpio == barcode:
            score = 100
            match_tipos.append('BARCODE_EXACTO')
        elif barcode and termino_limpio in barcode:
            score = max(score, 85)
            match_tipos.append('BARCODE_CONTIENE')
        
        # Modelo
        if modelo:
            if termino_limpio == modelo:
                score = max(score, 85)
                match_tipos.append('MODELO_EXACTO')
            elif termino_limpio in modelo:
                score = max(score, 65)
                match_tipos.append('MODELO_CONTIENE')
        
        # Marca
        if marca and termino_limpio in marca:
            score = max(score, 50)
            match_tipos.append('MARCA')
        
        # Descripción - búsqueda por palabras
        if descripcion:
            # Búsqueda exacta en descripción
            if termino_limpio in descripcion:
                palabras_termino = termino_limpio.split()
                palabras_encontradas = sum(1 for p in palabras_termino if p in descripcion)
                score_palabras = (palabras_encontradas / len(palabras_termino)) * 60 if palabras_termino else 0
                score = max(score, score_palabras)
                match_tipos.append('DESCRIPCION')
            
            # Búsqueda difusa para términos cercanos
            elif len(termino_limpio) > 3:
                # Verificar si el término es similar a alguna palabra de la descripción
                palabras_desc = descripcion.split()
                for palabra in palabras_desc[:10]:
                    if len(palabra) > 3 and SequenceMatcher(None, termino_limpio, palabra).ratio() > 0.7:
                        score = max(score, 40)
                        match_tipos.append('DESCRIPCION_DIFUSA')
                        break
        
        if score > 0:
            # Obtener precios
            precios_valores = {}
            for nivel, col_precio in catalogo['precios'].items():
                precios_valores[nivel] = corregir_numero(row[col_precio]) if col_precio in row.index else 0
            
            resultados.append({
                'index': idx,
                'score': score,
                'match_tipos': ', '.join(match_tipos),
                'sku': sku,
                'descripcion': descripcion[:200],
                'descripcion_original': str(row.get(columnas.get('descripcion', ''), ''))[:200],
                'barcode': barcode,
                'modelo': modelo,
                'marca': marca,
                'precios': precios_valores,
                'row': row,
                'catalogo_nombre': catalogo['nombre']
            })
    
    resultados.sort(key=lambda x: x['score'], reverse=True)
    
    if resultados:
        df_resultados = pd.DataFrame(resultados)
        return df_resultados
    
    return pd.DataFrame()

# ============================================
# LECTURA DE STOCK (SIN DUPLICACIÓN)
# ============================================

def buscar_stock_para_sku(sku: str, stocks: List[Dict]) -> Dict:
    sku_limpio = sku.strip().upper()
    
    stock_yessica = 0
    stock_apri004 = 0
    stock_apri001 = 0
    detalle_apri001 = []
    ubicaciones = []
    
    for stock in stocks:
        df = stock['df']
        hoja_nombre = stock['hoja']
        col_sku = stock['col_sku']
        
        df_sku = df[col_sku].astype(str).str.strip().str.upper()
        mask = df_sku == sku_limpio
        
        if mask.any():
            col_cant = None
            for col in df.columns:
                col_upper = str(col).upper()
                if any(p in col_upper for p in ['CANT', 'STOCK', 'DISPONIBLE', 'UNIDADES']):
                    col_cant = col
                    break
            
            if col_cant:
                row = df[mask].iloc[0]
                cantidad = int(corregir_numero(row[col_cant]))
                col_nombre = str(col_cant).upper()
                hoja_upper = hoja_nombre.upper()
                
                ubicaciones.append({
                    'hoja': hoja_nombre,
                    'columna': col_cant,
                    'cantidad': cantidad
                })
                
                if 'YESSICA' in hoja_upper:
                    stock_yessica = cantidad
                elif 'APRI.004' in hoja_upper:
                    stock_apri004 = cantidad
                elif 'APRI.001' in hoja_upper:
                    if 'DISPONIBLE' in col_nombre:
                        stock_apri001 = cantidad
                        detalle = {'cantidad': cantidad, 'hoja': hoja_nombre}
                        for col in df.columns:
                            col_upper = str(col).upper()
                            if 'OBS' in col_upper or 'DETALLE' in col_upper or 'NOTA' in col_upper:
                                detalle['observacion'] = str(row[col])[:150]
                                break
                        detalle_apri001.append(detalle)
                    else:
                        stock_apri001 = cantidad
    
    return {
        'yessica': stock_yessica,
        'apri004': stock_apri004,
        'apri001': stock_apri001,
        'detalle_apri001': detalle_apri001,
        'total': stock_yessica + stock_apri004 + stock_apri001,
        'ubicaciones': ubicaciones
    }

# ============================================
# CÁLCULO DE CANTIDAD SEGURA
# ============================================

def calcular_cantidad_total_segura(cantidad_solicitada: int, stock_info: Dict) -> Tuple[int, str, Dict]:
    stock_yessica = stock_info.get('yessica', 0)
    stock_apri004 = stock_info.get('apri004', 0)
    stock_apri001 = stock_info.get('apri001', 0)
    
    stock_inmediato = stock_yessica + stock_apri004
    stock_inmediato_seguro = max(0, stock_inmediato - 2) if stock_inmediato > 0 else 0
    
    detalle = {
        'yessica': stock_yessica,
        'apri004': stock_apri004,
        'apri001': stock_apri001,
        'stock_inmediato': stock_inmediato,
        'stock_inmediato_seguro': stock_inmediato_seguro
    }
    
    if cantidad_solicitada <= stock_inmediato_seguro:
        return cantidad_solicitada, f"✅ Stock inmediato: {cantidad_solicitada} unidades", detalle
    
    restante = cantidad_solicitada - stock_inmediato_seguro
    
    if stock_apri001 < 20:
        if stock_inmediato_seguro > 0:
            return stock_inmediato_seguro, f"⚠️ Solo stock inmediato: {stock_inmediato_seguro} (APRI.001: {stock_apri001} < 20)", detalle
        else:
            return 0, f"❌ Sin stock (APRI.001: {stock_apri001} < 20)", detalle
    
    if restante < 5:
        if stock_inmediato_seguro > 0:
            return stock_inmediato_seguro, f"⚠️ Solo stock inmediato: {stock_inmediato_seguro} (pedido restante {restante} < 5)", detalle
        else:
            return 0, f"❌ Pedido muy pequeño ({restante} < 5)", detalle
    
    max_apri001 = min(int(stock_apri001 * 0.15), 100)
    
    if max_apri001 < 5:
        return stock_inmediato_seguro, f"⚠️ APRI.001 insuficiente (15% = {max_apri001})", detalle
    
    if restante <= max_apri001:
        total_final = stock_inmediato_seguro + restante
        return total_final, f"✅ Stock inmediato: {stock_inmediato_seguro} + APRI.001: {restante} = {total_final}", detalle
    else:
        if stock_inmediato_seguro > 0:
            return stock_inmediato_seguro, f"⚠️ Solo stock inmediato: {stock_inmediato_seguro} (APRI.001 máx {max_apri001})", detalle
        else:
            return 0, f"❌ Excede límite APRI.001 (máx {max_apri001})", detalle

def calcular_cantidad_apri001_only(cantidad_solicitada: int, stock_apri001: int) -> Tuple[int, str, Dict]:
    detalle = {'stock_apri001': stock_apri001}
    
    if stock_apri001 < 20:
        return 0, f"❌ Stock APRI.001 insuficiente ({stock_apri001} < 20)", detalle
    
    if cantidad_solicitada < 5:
        return 0, f"❌ Pedido muy pequeño ({cantidad_solicitada} < 5)", detalle
    
    max_apri001 = min(int(stock_apri001 * 0.15), 100)
    
    if max_apri001 < 5:
        return 0, f"❌ 15% de APRI.001 = {max_apri001} (<5)", detalle
    
    if cantidad_solicitada > max_apri001:
        return 0, f"❌ Excede límite APRI.001 (máx {max_apri001})", detalle
    
    return cantidad_solicitada, f"✅ APRI.001: {cantidad_solicitada} unidades", detalle

# ============================================
# FUNCIONES UGREEN
# ============================================

def cargar_ugreen_catalogo(archivo) -> Optional[Dict]:
    df = cargar_archivo(archivo)
    if df is None:
        return None
    
    col_sku = None
    col_desc = None
    col_mayor = None
    col_caja = None
    col_vip = None
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
        elif 'STOCK' in col_upper:
            col_stock = col
    
    if not col_sku:
        col_sku = df.columns[0]
    
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

def buscar_ugreen_producto(busqueda: str, ugreen_catalogo: Dict) -> Optional[List]:
    if not ugreen_catalogo:
        return None
    
    df = ugreen_catalogo['df']
    col_sku = ugreen_catalogo['col_sku']
    col_desc = ugreen_catalogo['col_desc']
    
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
        
        precio_mayor = corregir_numero(row.get('MAYOR', row.get('Mayor', 0)))
        precio_caja = corregir_numero(row.get('CAJA', row.get('Caja', 0)))
        precio_vip = corregir_numero(row.get('VIP', row.get('Vip', 0)))
        
        resultados.append({
            'sku': sku,
            'descripcion': descripcion,
            'precios': {'P. IR': precio_mayor, 'P. BOX': precio_caja, 'P. VIP': precio_vip},
            'tiene_precio': precio_vip > 0 or precio_caja > 0 or precio_mayor > 0,
            'tipo': 'UGREEN'
        })
    
    return resultados

# ============================================
# STOCK CARGAR
# ============================================

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
                
                col_sku = None
                for col in df.columns:
                    col_upper = str(col).upper()
                    if any(p in col_upper for p in ['SKU', 'COD', 'ARTICULO', 'NUMERO']):
                        col_sku = col
                        break
                if not col_sku:
                    col_sku = df.columns[0]
                
                stocks.append({
                    'nombre': f"{archivo.name} [{hoja}]",
                    'df': df,
                    'col_sku': col_sku,
                    'hoja': hoja
                })
                st.success(f"✅ {archivo.name} → {hoja}")
        except Exception as e:
            st.error(f"Error cargando {archivo.name}: {str(e)[:80]}")
    return stocks

# ============================================
# BADGE STOCK
# ============================================

def construir_badge_stock(yessica, apri004, apri001, detalle_apri001=None, ubicaciones=None):
    badges = []
    
    if ubicaciones:
        for ub in ubicaciones:
            hoja = ub.get('hoja', '')
            cantidad = ub.get('cantidad', 0)
            if 'YESSICA' in hoja.upper():
                badges.append(f'<span class="badge-yessica">🟢 YESSICA: {cantidad}</span>')
            elif 'APRI.004' in hoja.upper():
                badges.append(f'<span class="badge-apri004">🟡 APRI.004: {cantidad}</span>')
            elif 'APRI.001' in hoja.upper():
                texto = f'🔴 APRI.001: {cantidad}'
                if detalle_apri001 and len(detalle_apri001) > 0:
                    for det in detalle_apri001:
                        if det.get('observacion'):
                            texto += f' 📝 {det["observacion"][:40]}'
                            break
                badges.append(f'<span class="badge-apri001">{texto}</span>')
    else:
        if yessica > 0:
            badges.append(f'<span class="badge-yessica">🟢 YESSICA: {yessica}</span>')
        if apri004 > 0:
            badges.append(f'<span class="badge-apri004">🟡 APRI.004: {apri004}</span>')
        if apri001 > 0:
            texto = f'🔴 APRI.001: {apri001}'
            if detalle_apri001 and len(detalle_apri001) > 0:
                for det in detalle_apri001:
                    if det.get('observacion'):
                        texto += f' 📝 {det["observacion"][:40]}'
                        break
            badges.append(f'<span class="badge-apri001">{texto}</span>')
    
    if not badges:
        return '<span class="badge-warning">❌ Sin stock</span>'
    return ' '.join(badges)

# ============================================
# GENERAR EXCEL
# ============================================

def generar_excel(items: List[Dict], cliente: str, ruc: str) -> bytes:
    output = io.BytesIO()
    df = pd.DataFrame(items)
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Cotizacion', index=False, startrow=6)
        
        workbook = writer.book
        ws = writer.sheets['Cotizacion']
        
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="e67e22", end_color="e67e22", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        money_alignment = Alignment(horizontal="right", vertical="center")
        border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        
        ws['A1'] = 'QTC SMART SALES PRO'
        ws['A1'].font = Font(bold=True, size=14, color="e67e22")
        ws['A3'] = 'FECHA:'
        ws['B3'] = datetime.now().strftime("%d/%m/%Y %H:%M")
        ws['A4'] = 'CLIENTE:'
        ws['B4'] = cliente.upper()
        ws['A5'] = 'RUC:'
        ws['B5'] = ruc
        
        headers = ['SKU', 'DESCRIPCIÓN', 'CANTIDAD', 'PRECIO UNIT.', 'TOTAL']
        for i, header in enumerate(headers, start=1):
            cell = ws.cell(row=7, column=i, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = border
        
        for row_idx, item in enumerate(items, start=8):
            ws.cell(row=row_idx, column=1, value=item['sku']).border = border
            ws.cell(row=row_idx, column=2, value=item['descripcion'][:100]).border = border
            ws.cell(row=row_idx, column=3, value=item['cantidad']).border = border
            
            precio_cell = ws.cell(row=row_idx, column=4, value=item['precio'])
            precio_cell.number_format = '"S/." #,##0.00'
            precio_cell.alignment = money_alignment
            precio_cell.border = border
            
            total_cell = ws.cell(row=row_idx, column=5, value=item['total'])
            total_cell.number_format = '"S/." #,##0.00'
            total_cell.alignment = money_alignment
            total_cell.border = border
        
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
        
        ws.column_dimensions['A'].width = 22
        ws.column_dimensions['B'].width = 110
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 18
        ws.column_dimensions['E'].width = 18
        
        ws.freeze_panes = 'A8'
    
    return output.getvalue()

# ============================================
# ASISTENTE IA V4 - CON MÚLTIPLES CATÁLOGOS
# ============================================

def procesar_comando_asistente_v4(comando: str, catalogos: List[Dict], stocks: List, precio_key: str) -> str:
    comando_lower = comando.lower().strip()
    
    # Comandos de ayuda
    if any(p in comando_lower for p in ['ayuda', 'help', 'comandos', 'que puedes hacer']):
        return mostrar_ayuda()
    
    # Ver carrito
    if any(p in comando_lower for p in ['ver carrito', 'mi carrito', 'muestrame el carrito']):
        return ver_carrito()
    
    if any(p in comando_lower for p in ['limpiar carrito', 'vaciar carrito']):
        st.session_state.carrito = []
        return "🧹 Carrito limpiado correctamente."
    
    if any(p in comando_lower for p in ['total carrito', 'total del carrito']):
        total = sum(item['total'] for item in st.session_state.carrito)
        return f"💰 Total del carrito: **S/ {total:,.2f}**"
    
    # Quitar del carrito
    if any(p in comando_lower for p in ['quitar', 'eliminar', 'remover']):
        sku_match = re.search(r'([A-Z0-9]{8,})', comando.upper())
        if sku_match:
            sku = sku_match.group(1)
            for i, item in enumerate(st.session_state.carrito):
                if item['sku'] == sku:
                    st.session_state.carrito.pop(i)
                    return f"✅ Eliminado {sku} del carrito."
            return f"❌ No encontré {sku} en el carrito."
    
    # Precio
    if any(p in comando_lower for p in ['precio de', 'precio del', 'cual es el precio de', 'cuanto cuesta']):
        sku_match = re.search(r'([A-Z0-9]{8,})', comando.upper())
        if sku_match:
            sku = sku_match.group(1)
            return consultar_precio_sku(sku, catalogos, precio_key)
        else:
            termino = extraer_termino_despues_de(comando, ['precio de', 'precio del', 'cual es el precio de', 'cuanto cuesta'])
            if termino:
                return consultar_precio_descripcion(termino, catalogos, precio_key)
    
    # Stock
    if any(p in comando_lower for p in ['stock de', 'stock del', 'cuanto stock hay de', 'disponibilidad de']):
        sku_match = re.search(r'([A-Z0-9]{8,})', comando.upper())
        if sku_match:
            sku = sku_match.group(1)
            return consultar_stock_sku(sku, stocks)
        else:
            termino = extraer_termino_despues_de(comando, ['stock de', 'stock del', 'cuanto stock hay de', 'disponibilidad de'])
            if termino:
                return consultar_stock_descripcion(termino, catalogos, stocks)
    
    # Cotización
    if any(p in comando_lower for p in ['cotizame', 'cotiza', 'agrega al carrito', 'agrega', 'pon en el carrito']):
        cant_match = re.search(r'(\d+)\s*(unidades?|uds?|pzs?)?', comando)
        sku_match = re.search(r'([A-Z0-9]{8,})', comando.upper())
        
        cantidad = int(cant_match.group(1)) if cant_match else 1
        
        if sku_match:
            sku = sku_match.group(1)
            return cotizar_sku(sku, cantidad, catalogos, stocks, precio_key)
        else:
            termino = extraer_termino_despues_de_cotizacion(comando)
            if termino:
                return cotizar_descripcion(termino, cantidad, catalogos, stocks, precio_key)
    
    # Búsqueda general
    if len(comando) >= 3:
        return buscar_productos_general(comando, catalogos, stocks, precio_key)
    
    return "❓ No entendí tu consulta. Escribe 'ayuda' para ver los comandos disponibles."


# ============================================
# FUNCIONES AUXILIARES DEL ASISTENTE
# ============================================

def extraer_termino_despues_de(texto: str, palabras_clave: list) -> str:
    texto_lower = texto.lower()
    for palabra in palabras_clave:
        if palabra in texto_lower:
            idx = texto_lower.find(palabra) + len(palabra)
            return texto[idx:].strip()
    return texto.strip()

def extraer_termino_despues_de_cotizacion(texto: str) -> str:
    texto_lower = texto.lower()
    palabras_clave = ['cotizame', 'cotiza', 'agrega', 'pon']
    for palabra in palabras_clave:
        if palabra in texto_lower:
            idx = texto_lower.find(palabra) + len(palabra)
            resto = texto[idx:].strip()
            resto = re.sub(r'^\d+\s*(unidades?|uds?|pzs?)?\s*', '', resto)
            return resto.strip()
    return texto.strip()

def consultar_precio_sku(sku: str, catalogos: List[Dict], precio_key: str) -> str:
    if not catalogos:
        return "⚠️ No hay catálogos cargados."
    
    for catalogo in catalogos:
        df = catalogo['df']
        col_sku = catalogo['columnas']['sku']
        mask = df[col_sku].astype(str).str.upper() == sku
        
        if mask.any():
            row = df[mask].iloc[0]
            desc = row.get(catalogo['columnas'].get('descripcion', col_sku), sku)
            
            precios = {}
            for nivel, col_precio in catalogo['precios'].items():
                precios[nivel] = corregir_numero(row[col_precio]) if col_precio in row.index else 0
            
            response = f"💰 **{sku}** (Catálogo: {catalogo['nombre']})\n"
            response += f"📝 {str(desc)[:100]}\n\n"
            response += f"   • IR: S/ {precios.get('P. IR', 0):.2f}\n"
            response += f"   • BOX: S/ {precios.get('P. BOX', 0):.2f}\n"
            response += f"   • VIP: S/ {precios.get('P. VIP', 0):.2f}\n"
            
            if precios.get(precio_key, 0) > 0:
                response += f"\n✨ Precio {precio_key}: S/ {precios.get(precio_key, 0):.2f}"
            
            return response
    
    return f"❌ No encontré '{sku}' en ningún catálogo."

def consultar_precio_descripcion(termino: str, catalogos: List[Dict], precio_key: str) -> str:
    resultados = buscar_en_catalogos(termino, catalogos)
    if not resultados.empty:
        response = f"🔍 Productos encontrados para '{termino}':\n\n"
        for _, row in resultados.head(3).iterrows():
            response += f"📦 **{row['sku']}** ({row['catalogo_nombre']})\n"
            response += f"   📝 {row['descripcion_original'][:80]}\n"
            response += f"   💰 VIP: S/ {row['precios'].get('P. VIP', 0):.2f} | IR: S/ {row['precios'].get('P. IR', 0):.2f}\n\n"
        
        response += f"💡 Para cotizar: 'cotiza [SKU] [cantidad]'"
        return response
    else:
        return f"❌ No encontré productos relacionados con '{termino}'"

def consultar_stock_sku(sku: str, stocks: List) -> str:
    if not stocks:
        return "⚠️ No hay reportes de stock cargados."
    
    stock_info = buscar_stock_para_sku(sku, stocks)
    
    if stock_info['total'] == 0:
        return f"❌ SKU {sku} no tiene stock disponible."
    
    response = f"📦 **Stock de {sku}:**\n"
    response += f"   • YESSICA: {stock_info['yessica']} und\n"
    response += f"   • APRI.004: {stock_info['apri004']} und\n"
    response += f"   • APRI.001: {stock_info['apri001']} und\n"
    response += f"   • **TOTAL: {stock_info['total']} und**\n"
    
    if stock_info.get('ubicaciones'):
        response += f"\n📍 Ubicaciones:\n"
        for ub in stock_info['ubicaciones']:
            response += f"   • {ub['hoja']}: {ub['cantidad']} und\n"
    
    if stock_info['apri001'] > 0 and stock_info['yessica'] == 0 and stock_info['apri004'] == 0:
        max_apri001 = min(int(stock_info['apri001'] * 0.15), 100)
        response += f"\n⚠️ Stock solo en APRI.001\n"
        response += f"   • Máximo cotizable: {max_apri001} und (15%)\n"
        response += f"   • Stock mínimo: 20 und | Pedido mínimo: 5 und"
    else:
        stock_seguro = max(0, stock_info['total'] - 2)
        response += f"\n🔒 Stock cotizable (margen -2): {stock_seguro} und"
    
    return response

def consultar_stock_descripcion(termino: str, catalogos: List[Dict], stocks: List) -> str:
    resultados = buscar_en_catalogos(termino, catalogos)
    if not resultados.empty:
        response = f"🔍 Stock de productos para '{termino}':\n\n"
        for _, row in resultados.head(3).iterrows():
            sku = row['sku']
            stock_info = buscar_stock_para_sku(sku, stocks)
            
            response += f"📦 **{sku}** - {row['descripcion_original'][:60]}\n"
            if stock_info['total'] > 0:
                response += f"   📦 Stock: {stock_info['total']} und"
                if stock_info['apri001'] > 0 and stock_info['yessica'] == 0 and stock_info['apri004'] == 0:
                    response += f" (solo APRI.001)"
                response += f"\n   📍 Y:{stock_info['yessica']} | A4:{stock_info['apri004']} | A1:{stock_info['apri001']}\n"
            else:
                response += f"   ❌ Sin stock\n"
            response += "\n"
        return response
    else:
        return f"❌ No encontré productos relacionados con '{termino}'"

def cotizar_sku(sku: str, cantidad: int, catalogos: List[Dict], stocks: List, precio_key: str) -> str:
    if not catalogos or not stocks:
        return "⚠️ Primero carga catálogos y stock en el sidebar."
    
    # Buscar en todos los catálogos
    catalogo_encontrado = None
    row_encontrado = None
    desc_encontrada = None
    
    for catalogo in catalogos:
        df = catalogo['df']
        col_sku = catalogo['columnas']['sku']
        mask = df[col_sku].astype(str).str.upper() == sku
        if mask.any():
            catalogo_encontrado = catalogo
            row_encontrado = df[mask].iloc[0]
            desc_encontrada = row_encontrado.get(catalogo['columnas'].get('descripcion', col_sku), sku)
            break
    
    if not catalogo_encontrado:
        # Verificar si existe en stock
        stock_info = buscar_stock_para_sku(sku, stocks)
        if stock_info['total'] > 0:
            return f"⚠️ **{sku} tiene stock pero NO tiene precio en ningún catálogo.**\n\n📦 Stock: {stock_info['total']} und\n❌ No se puede cotizar sin precio.\n\n💡 Sugerencia: Agrega este SKU a un catálogo o verifica el SKU."
        return f"❌ No encontré '{sku}' en ningún catálogo."
    
    # Obtener precio
    precio = 0
    if precio_key in catalogo_encontrado['precios']:
        col_precio = catalogo_encontrado['precios'][precio_key]
        precio = corregir_numero(row_encontrado[col_precio])
    
    if precio == 0:
        return f"❌ SKU {sku} no tiene precio en nivel {precio_key}."
    
    stock_info = buscar_stock_para_sku(sku, stocks)
    
    if stock_info['total'] == 0:
        return f"❌ SKU {sku} no tiene stock disponible."
    
    solo_apri001 = stock_info['apri001'] > 0 and stock_info['yessica'] == 0 and stock_info['apri004'] == 0
    
    if solo_apri001:
        cant_final, msg, _ = calcular_cantidad_apri001_only(cantidad, stock_info['apri001'])
    else:
        cant_final, msg, _ = calcular_cantidad_total_segura(cantidad, stock_info)
    
    if cant_final == 0:
        return f"❌ No se puede cotizar: {msg}"
    
    item = {
        'sku': sku,
        'descripcion': str(desc_encontrada)[:150],
        'cantidad': cant_final,
        'precio': precio,
        'total': precio * cant_final,
        'stock_yessica': stock_info['yessica'],
        'stock_apri004': stock_info['apri004'],
        'stock_apri001': stock_info['apri001'],
        'detalle_apri001': stock_info.get('detalle_apri001', []),
        'ubicaciones': stock_info.get('ubicaciones', []),
        'catalogo': catalogo_encontrado['nombre']
    }
    st.session_state.carrito.append(item)
    
    response = f"✅ **Agregado al carrito**\n"
    response += f"   • {cant_final}x **{sku}**\n"
    response += f"   • 📝 {str(desc_encontrada)[:80]}\n"
    response += f"   • 💰 Precio: S/ {precio:.2f} c/u\n"
    response += f"   • 📦 Subtotal: S/ {precio * cant_final:,.2f}\n"
    response += f"   • {msg}\n"
    response += f"   • 📁 Catálogo: {catalogo_encontrado['nombre']}\n"
    
    total_carrito = sum(item['total'] for item in st.session_state.carrito)
    response += f"\n💰 Total carrito: S/ {total_carrito:,.2f}"
    
    return response

def cotizar_descripcion(termino: str, cantidad: int, catalogos: List[Dict], stocks: List, precio_key: str) -> str:
    resultados = buscar_en_catalogos(termino, catalogos)
    if resultados.empty:
        return f"❌ No encontré productos relacionados con '{termino}'"
    
    mejor = resultados.iloc[0]
    sku = mejor['sku']
    desc = mejor['descripcion_original']
    
    response = f"🔍 Encontré **{sku}** para tu búsqueda:\n📝 {desc[:80]}\n\n"
    response += cotizar_sku(sku, cantidad, catalogos, stocks, precio_key)
    
    return response

def buscar_productos_general(termino: str, catalogos: List[Dict], stocks: List, precio_key: str, limit: int = 8) -> str:
    """Búsqueda general en múltiples catálogos"""
    resultados = buscar_en_catalogos(termino, catalogos)
    
    if resultados.empty:
        return f"❌ No encontré resultados para '{termino}' en los catálogos cargados."
    
    response = f"🔍 **{len(resultados)} resultado(s) para '{termino}':**\n\n"
    
    for i, (_, row) in enumerate(resultados.head(limit).iterrows()):
        sku = row['sku']
        desc = row['descripcion_original'][:90]
        score = row['score']
        catalogo_nombre = row['catalogo_nombre']
        
        stock_info = buscar_stock_para_sku(sku, stocks)
        precio = row['precios'].get(precio_key, 0)
        
        stock_status = f"📦 Stock: {stock_info['total']} und" if stock_info['total'] > 0 else "❌ Sin stock"
        stock_status += f" (Y:{stock_info['yessica']} A4:{stock_info['apri004']} A1:{stock_info['apri001']})"
        
        response += f"{i+1}. **{sku}**\n"
        response += f"   📝 {desc}\n"
        response += f"   🎯 Coincidencia: {score:.0f}%\n"
        response += f"   {stock_status}\n"
        response += f"   💰 Precio {precio_key}: S/ {precio:.2f}\n"
        response += f"   📁 Catálogo: {catalogo_nombre}\n\n"
    
    if len(resultados) > limit:
        response += f"📋 Hay {len(resultados)} resultados en total.\n"
    
    response += f"\n💡 Para cotizar: 'cotiza [SKU] [cantidad]'"
    
    return response

def ver_carrito() -> str:
    if not st.session_state.carrito:
        return "🛒 Tu carrito está vacío."
    
    response = f"🛒 **Carrito ({len(st.session_state.carrito)} productos):**\n\n"
    for i, item in enumerate(st.session_state.carrito, 1):
        response += f"{i}. **{item['cantidad']}x {item['sku']}**\n"
        response += f"   📝 {item['descripcion'][:60]}\n"
        response += f"   💰 S/ {item['precio']:.2f} c/u → Subtotal: S/ {item['total']:,.2f}\n\n"
    
    total = sum(item['total'] for item in st.session_state.carrito)
    response += f"---\n💰 **TOTAL: S/ {total:,.2f}**"
    return response

def mostrar_ayuda() -> str:
    return """
📋 **COMANDOS DISPONIBLES**

💰 **Precio:**
   • `precio de RN0200065BK8` - Precio de SKU
   • `cuanto cuesta Redmi Buds` - Precio por descripción

📦 **Stock:**
   • `stock de RN0200065BK8` - Stock detallado
   • `disponibilidad de powerbank` - Stock por descripción

🛒 **Cotización:**
   • `cotiza RN0200065BK8 50` - Agrega al carrito
   • `cotizame 3 Redmi Buds 8` - Cotiza por descripción

🔍 **Búsqueda general:**
   • `powerbank` - Busca en todos los catálogos
   • `auriculares type-c` - Búsqueda en múltiples catálogos

🛒 **Carrito:**
   • `ver carrito` - Muestra cotización
   • `total carrito` - Solo el total
   • `limpiar carrito` - Vacía carrito
   • `quitar RN0200065BK8` - Elimina producto

❓ **Ayuda:**
   • `ayuda` / `que puedes hacer` - Esta ayuda
"""

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
    st.session_state.catalogos = []  # Lista de múltiples catálogos
if 'stocks' not in st.session_state:
    st.session_state.stocks = []
if 'carrito' not in st.session_state:
    st.session_state.carrito = []
if 'ugreen_catalogo' not in st.session_state:
    st.session_state.ugreen_catalogo = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ============================================
# LOGIN
# ============================================

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='color:#1a1a2e;'>QTC Smart Sales Pro v5.2</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#666;'>Múltiples catálogos | Búsqueda híbrida | Asistente IA</p>", unsafe_allow_html=True)
        user = st.text_input("👤 Usuario")
        pw = st.text_input("🔒 Contraseña", type="password")
        
        if st.button("🚀 Ingresar", use_container_width=True):
            if user == "admin" and pw == "qtc2026":
                st.session_state.auth = True
                st.session_state.user_name = "Administrador"
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")
    st.stop()

# ============================================
# HEADER
# ============================================

col1, col2, col3 = st.columns([1, 4, 2])
with col1:
    st.markdown("### 💼 QTC")
with col2:
    st.markdown("# Smart Sales Pro v5.2")
    st.caption("🔍 Múltiples catálogos | 📦 Stock: YESSICA/APRI.004 -2 | ⚠️ APRI.001: 15% máx 100")
with col3:
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 12px; text-align: right;">
        👤 {st.session_state.user_name}<br>
        <span style="font-size: 0.7rem;">{st.session_state.modo}</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 Salir"):
        st.session_state.auth = False
        st.rerun()

st.markdown("---")

# ============================================
# SIDEBAR - MÚLTIPLES CATÁLOGOS
# ============================================

with st.sidebar:
    st.markdown("### 🎯 Configuración")
    
    marca = st.radio("📌 Modo", ["XIAOMI", "UGREEN"], index=0)
    st.session_state.modo = marca
    
    st.markdown("---")
    precio_opcion = st.radio("💰 Nivel de precio", ["P. VIP", "P. BOX", "P. IR"], index=0)
    st.session_state.precio_key = precio_opcion
    
    st.markdown("---")
    st.markdown("### 📂 Catálogos de precios")
    st.caption("Puedes cargar múltiples archivos (XIAOMI, HONOR, etc.)")
    
    if marca == "XIAOMI":
        archivos_cat = st.file_uploader(
            "Uno o más archivos (Excel/CSV)",
            type=['xlsx', 'xls', 'csv'],
            accept_multiple_files=True,
            key="catalogos_v5"
        )
        if archivos_cat:
            st.session_state.catalogos = []
            for archivo in archivos_cat:
                # Permitir nombre personalizado
                nombre_personalizado = st.text_input(f"Nombre para {archivo.name[:20]}...", 
                                                      value=archivo.name.replace('.xlsx', '').replace('.xls', '').replace('.csv', ''),
                                                      key=f"nombre_{archivo.name}")
                catalogo = cargar_catalogo_inteligente(archivo, nombre_personalizado)
                if catalogo:
                    st.session_state.catalogos.append(catalogo)
                    st.success(f"✅ {nombre_personalizado}")
            if st.session_state.catalogos:
                st.info(f"📚 {len(st.session_state.catalogos)} catálogo(s) cargado(s)")
    
    if marca == "UGREEN":
        archivo_ugreen = st.file_uploader(
            "Catálogo UGREEN",
            type=['xlsx', 'xls'],
            accept_multiple_files=False,
            key="ugreen_v5"
        )
        if archivo_ugreen:
            ugreen_cat = cargar_ugreen_catalogo(archivo_ugreen)
            if ugreen_cat:
                st.session_state.ugreen_catalogo = ugreen_cat
                st.success(f"✅ UGREEN: {archivo_ugreen.name}")
    
    st.markdown("---")
    st.markdown("### 📦 Reportes de stock")
    st.caption("YESSICA/APRI.004: stock-2 | APRI.001: 15% máx 100")
    archivos_stock = st.file_uploader(
        "Excel con múltiples hojas",
        type=['xlsx', 'xls'],
        accept_multiple_files=True,
        key="stock_v5"
    )
    if archivos_stock:
        st.session_state.stocks = cargar_stock(archivos_stock, marca)
    
    st.markdown("---")
    
    if st.session_state.carrito:
        st.markdown(f"### 🛒 Carrito")
        st.metric("Productos", len(st.session_state.carrito))
        total = sum(item['total'] for item in st.session_state.carrito)
        st.metric("Total", f"S/ {total:,.2f}")
        if st.button("🧹 Limpiar", use_container_width=True):
            st.session_state.carrito = []
            st.rerun()

# ============================================
# TABS PRINCIPALES
# ============================================

tab1, tab2, tab3, tab4 = st.tabs(["🔍 BÚSQUEDA INTELIGENTE", "📦 MODO MASIVO", "🛒 CARRITO", "💬 ASISTENTE"])

# ========== TAB 1: BÚSQUEDA INTELIGENTE (MÚLTIPLES CATÁLOGOS) ==========
with tab1:
    if marca == "XIAOMI" and st.session_state.catalogos and st.session_state.stocks:
        st.markdown("### 🔍 Buscar productos")
        st.caption(f"🔎 Buscando en {len(st.session_state.catalogos)} catálogo(s): {', '.join([c['nombre'] for c in st.session_state.catalogos])}")
        
        col_f1, col_f2 = st.columns([3, 1])
        with col_f1:
            termino = st.text_input("", placeholder="Ej: powerbank | RN0200065BK8 | auriculares | cargador 67W")
        with col_f2:
            solo_stock = st.checkbox("📦 Solo con stock", value=False)
        
        if termino and len(termino) >= 2:
            with st.spinner("🔍 Buscando en todos los catálogos..."):
                resultados = buscar_en_catalogos(termino, st.session_state.catalogos)
                
                if not resultados.empty:
                    if solo_stock:
                        mascara = []
                        for _, row in resultados.iterrows():
                            sku = row['sku']
                            stock_info = buscar_stock_para_sku(sku, st.session_state.stocks)
                            mascara.append(stock_info['total'] > 0)
                        resultados = resultados[mascara]
                    
                    st.success(f"✅ {len(resultados)} resultados encontrados en {len(resultados['catalogo_nombre'].unique())} catálogo(s)")
                    
                    for idx, row in resultados.iterrows():
                        sku = row['sku']
                        desc = row['descripcion_original']
                        score = row['score']
                        match_tipos = row['match_tipos']
                        catalogo_nombre = row['catalogo_nombre']
                        precios = row['precios']
                        
                        stock_info = buscar_stock_para_sku(sku, st.session_state.stocks)
                        precio_seleccionado = precios.get(st.session_state.precio_key, 0)
                        
                        # Determinar clase de tarjeta según score y stock
                        if stock_info['total'] > 0 and precio_seleccionado > 0:
                            card_class = "result-card"
                        elif stock_info['total'] > 0 and precio_seleccionado == 0:
                            card_class = "result-card-warning"
                        else:
                            card_class = "result-card-danger"
                        
                        # Badge de stock
                        badge_stock = construir_badge_stock(
                            stock_info['yessica'], stock_info['apri004'], stock_info['apri001'],
                            stock_info.get('detalle_apri001', []), stock_info.get('ubicaciones', [])
                        )
                        
                        # Stock seguro (solo si hay stock)
                        stock_seguro_info = ""
                        if stock_info['total'] > 0:
                            if stock_info['apri001'] > 0 and stock_info['yessica'] == 0 and stock_info['apri004'] == 0:
                                max_apri001 = min(int(stock_info['apri001'] * 0.15), 100)
                                stock_seguro_info = f"<span class='badge-warning'>⚠️ APRI.001: máx {max_apri001} und (15%)</span>"
                            else:
                                stock_seguro = max(0, stock_info['total'] - 2)
                                stock_seguro_info = f"<span class='badge-stock'>🔒 Stock seguro: {stock_seguro} und</span>"
                        
                        st.markdown(f"""
                        <div class="{card_class}">
                            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                                <div>
                                    <span class="result-sku">📦 {sku}</span>
                                    <span style="background: {'#4CAF50' if score >= 80 else '#FF9800' if score >= 50 else '#2196F3'}; color:white; padding:2px 8px; border-radius:12px; font-size:0.65rem; margin-left:8px;">{score:.0f}%</span>
                                    <span style="background:#607d8b; color:white; padding:2px 8px; border-radius:12px; font-size:0.65rem; margin-left:4px;">📁 {catalogo_nombre[:20]}</span>
                                </div>
                                <span style="font-size:0.7rem; color:#666;">{match_tipos}</span>
                            </div>
                            
                            <div class="result-desc">
                                <strong>📝 Descripción:</strong> {desc[:150]}{'...' if len(desc) > 150 else ''}
                            </div>
                            
                            <div style="margin: 8px 0;">
                                {badge_stock}
                                {stock_seguro_info}
                            </div>
                            
                            <div class="result-price">
                                💰 Precio {st.session_state.precio_key}: <strong>S/ {precio_seleccionado:,.2f}</strong>
                            </div>
                            
                            <div style="margin-top: 6px; font-size:0.75rem; color:#666;">
                                💰 IR: S/ {precios.get('P. IR', 0):.2f} | BOX: S/ {precios.get('P. BOX', 0):.2f} | VIP: S/ {precios.get('P. VIP', 0):.2f}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Botones de acción (solo si tiene stock y precio)
                        if stock_info['total'] > 0 and precio_seleccionado > 0:
                            # Calcular máximo permitido
                            solo_apri001 = stock_info['apri001'] > 0 and stock_info['yessica'] == 0 and stock_info['apri004'] == 0
                            if solo_apri001:
                                max_cantidad = min(int(stock_info['apri001'] * 0.15), 100)
                                min_cantidad = 5
                            else:
                                max_cantidad = max(0, stock_info['total'] - 2)
                                min_cantidad = 1
                            
                            col1, col2, col3 = st.columns([1, 1, 2])
                            with col1:
                                cantidad_input = st.number_input("Cantidad", min_value=min_cantidad, max_value=max_cantidad, value=min_cantidad, step=1, key=f"busq_{sku}_{idx}")
                            with col2:
                                if st.button(f"➕ Agregar", key=f"add_{sku}_{idx}"):
                                    if solo_apri001:
                                        cant_final, msg, _ = calcular_cantidad_apri001_only(cantidad_input, stock_info['apri001'])
                                    else:
                                        cant_final, msg, _ = calcular_cantidad_total_segura(cantidad_input, stock_info)
                                    
                                    if cant_final > 0:
                                        item = {
                                            'sku': sku,
                                            'descripcion': desc[:150],
                                            'cantidad': cant_final,
                                            'precio': precio_seleccionado,
                                            'total': precio_seleccionado * cant_final,
                                            'stock_yessica': stock_info['yessica'],
                                            'stock_apri004': stock_info['apri004'],
                                            'stock_apri001': stock_info['apri001'],
                                            'detalle_apri001': stock_info.get('detalle_apri001', []),
                                            'ubicaciones': stock_info.get('ubicaciones', []),
                                            'catalogo': catalogo_nombre
                                        }
                                        st.session_state.carrito.append(item)
                                        st.success(f"✅ Agregado {cant_final}x {sku} - {msg[:100]}")
                                        st.rerun()
                                    else:
                                        st.warning(f"❌ {msg}")
                            with col3:
                                st.caption(f"📦 Máximo: {max_cantidad} und")
                        elif stock_info['total'] > 0 and precio_seleccionado == 0:
                            st.warning(f"⚠️ **{sku}** tiene stock pero NO tiene precio en nivel {st.session_state.precio_key}. Verifica el catálogo.")
                        elif stock_info['total'] == 0 and precio_seleccionado > 0:
                            st.info(f"📦 **{sku}** tiene precio pero NO tiene stock disponible.")
                        
                        st.markdown("---")
                else:
                    # Búsqueda solo en stock
                    st.info("🔍 No se encontraron resultados en catálogos. Buscando solo en stock...")
                    resultados_stock = []
                    for stock in st.session_state.stocks:
                        df = stock['df']
                        col_sku = stock['col_sku']
                        mask_sku = df[col_sku].astype(str).str.contains(termino, case=False, na=False)
                        if mask_sku.any():
                            for _, row in df[mask_sku].iterrows():
                                sku = str(row[col_sku]).strip().upper()
                                stock_info = buscar_stock_para_sku(sku, st.session_state.stocks)
                                if solo_stock and stock_info['total'] == 0:
                                    continue
                                
                                # Obtener descripción del stock
                                desc_stock = ""
                                for col in df.columns:
                                    if any(p in str(col).upper() for p in ['DESC', 'PRODUCTO', 'NOMBRE', 'GOODS']):
                                        desc_val = str(row[col])
                                        if desc_val and desc_val != 'nan' and len(desc_val) > len(desc_stock):
                                            desc_stock = desc_val[:150]
                                
                                resultados_stock.append({'sku': sku, 'desc': desc_stock, 'stock_info': stock_info})
                    
                    if resultados_stock:
                        st.warning(f"⚠️ {len(resultados_stock)} productos encontrados SOLO EN STOCK (sin precio en catálogos)")
                        for r in resultados_stock[:10]:
                            badge = construir_badge_stock(
                                r['stock_info']['yessica'], r['stock_info']['apri004'], r['stock_info']['apri001'],
                                r['stock_info'].get('detalle_apri001', []), r['stock_info'].get('ubicaciones', [])
                            )
                            st.markdown(f"""
                            <div class="result-card-warning">
                                <strong>📦 {r['sku']}</strong><br>
                                📝 {r['desc'][:100] if r['desc'] else 'Sin descripción'}<br>
                                {badge}<br>
                                ❌ <strong>SIN PRECIO EN CATÁLOGOS</strong><br>
                                💡 Verificar SKU o agregar a un catálogo
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No se encontraron resultados en catálogos ni en stock.")
    else:
        st.warning("Carga uno o más catálogos y stock en el sidebar para comenzar.")

# ========== TAB 2: MODO MASIVO (SIMPLIFICADO) ==========
with tab2:
    st.markdown("### 📦 Ingresa productos en formato masivo")
    st.caption("Formato: `SKU:CANTIDAD` (uno por línea)")
    
    texto_bulk = st.text_area("", height=200, placeholder="RN0200065BK8:50\nCN0200059BK8:30\nCN0601030BK0:100")
    
    if st.button("🚀 Procesar lista", type="primary"):
        if texto_bulk and st.session_state.catalogos and st.session_state.stocks:
            pedidos = []
            for line in texto_bulk.strip().split('\n'):
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
                resultados = []
                for pedido in pedidos:
                    # Buscar en todos los catálogos
                    catalogo_encontrado = None
                    row_encontrado = None
                    desc_encontrada = None
                    precio = 0
                    
                    for catalogo in st.session_state.catalogos:
                        df = catalogo['df']
                        col_sku = catalogo['columnas']['sku']
                        mask = df[col_sku].astype(str).str.upper() == pedido['sku']
                        if mask.any():
                            catalogo_encontrado = catalogo
                            row_encontrado = df[mask].iloc[0]
                            desc_encontrada = row_encontrado.get(catalogo['columnas'].get('descripcion', col_sku), pedido['sku'])
                            if st.session_state.precio_key in catalogo['precios']:
                                col_precio = catalogo['precios'][st.session_state.precio_key]
                                precio = corregir_numero(row_encontrado[col_precio])
                            break
                    
                    stock_info = buscar_stock_para_sku(pedido['sku'], st.session_state.stocks)
                    
                    if catalogo_encontrado and precio > 0 and stock_info['total'] > 0:
                        solo_apri001 = stock_info['apri001'] > 0 and stock_info['yessica'] == 0 and stock_info['apri004'] == 0
                        if solo_apri001:
                            cant_final, msg, _ = calcular_cantidad_apri001_only(pedido['cantidad'], stock_info['apri001'])
                        else:
                            cant_final, msg, _ = calcular_cantidad_total_segura(pedido['cantidad'], stock_info)
                    else:
                        cant_final = 0
                        if not catalogo_encontrado:
                            msg = "❌ SKU no encontrado en catálogos"
                        elif precio == 0:
                            msg = "⚠️ Sin precio en catálogo"
                        else:
                            msg = "❌ Sin stock"
                    
                    resultados.append({
                        'sku': pedido['sku'],
                        'desc': str(desc_encontrada)[:80] if desc_encontrada else 'No encontrado',
                        'solicitado': pedido['cantidad'],
                        'cotizable': cant_final,
                        'precio': precio,
                        'estado': msg,
                        'stock_info': stock_info,
                        'catalogo': catalogo_encontrado['nombre'] if catalogo_encontrado else 'No encontrado'
                    })
                
                st.success(f"✅ Procesados {len(pedidos)} productos")
                
                cotizables = sum(1 for r in resultados if r['cotizable'] > 0)
                st.metric("Productos cotizables", cotizables)
                
                if st.button("📋 Agregar cotizables al carrito"):
                    agregados = 0
                    for r in resultados:
                        if r['cotizable'] > 0 and r['precio'] > 0:
                            item = {
                                'sku': r['sku'],
                                'descripcion': r['desc'],
                                'cantidad': r['cotizable'],
                                'precio': r['precio'],
                                'total': r['precio'] * r['cotizable'],
                                'stock_yessica': r['stock_info'].get('yessica', 0),
                                'stock_apri004': r['stock_info'].get('apri004', 0),
                                'stock_apri001': r['stock_info'].get('apri001', 0),
                                'detalle_apri001': r['stock_info'].get('detalle_apri001', []),
                                'ubicaciones': r['stock_info'].get('ubicaciones', []),
                                'catalogo': r.get('catalogo', '')
                            }
                            st.session_state.carrito.append(item)
                            agregados += 1
                    st.success(f"✅ Agregados {agregados} productos")
                    st.rerun()
                
                # Mostrar resultados
                for r in resultados:
                    badge = construir_badge_stock(
                        r['stock_info'].get('yessica', 0),
                        r['stock_info'].get('apri004', 0),
                        r['stock_info'].get('apri001', 0),
                        r['stock_info'].get('detalle_apri001', []),
                        r['stock_info'].get('ubicaciones', [])
                    )
                    color_borde = "#4CAF50" if r['cotizable'] > 0 else "#f44336"
                    st.markdown(f"""
                    <div style="background:white;border-radius:12px;padding:0.75rem;margin-bottom:0.5rem;border-left:4px solid {color_borde};">
                        <strong>{r['sku']}</strong> - {r['desc']}<br>
                        📦 Solicitado: {r['solicitado']} → <strong>Cotizable: {r['cotizable']}</strong><br>
                        {badge}<br>
                        <span style="font-size:0.8rem;">{r['estado']}</span>
                        {f'<span style="font-size:0.7rem;color:#666;">📁 {r["catalogo"]}</span>' if r.get('catalogo') else ''}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No se encontraron productos válidos")
        else:
            st.warning("Carga catálogos y stock primero")

# ========== TAB 3: CARRITO ==========
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
                nueva_cant = st.number_input("Cant", min_value=0, value=item['cantidad'], step=1, key=f"cart_{idx}", label_visibility="collapsed")
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
            
            badge = construir_badge_stock(
                item.get('stock_yessica', 0),
                item.get('stock_apri004', 0),
                item.get('stock_apri001', 0),
                item.get('detalle_apri001', []),
                item.get('ubicaciones', [])
            )
            st.markdown(f'<div style="margin-bottom:0.5rem;">{badge}</div>', unsafe_allow_html=True)
            if item.get('catalogo'):
                st.caption(f"📁 Catálogo: {item['catalogo']}")
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
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("📥 Exportar Excel", type="primary"):
                if cliente:
                    items_export = [{'sku': i['sku'], 'descripcion': i['descripcion'], 'cantidad': i['cantidad'], 'precio': i['precio'], 'total': i['total']} for i in st.session_state.carrito]
                    excel = generar_excel(items_export, cliente, ruc)
                    st.download_button("💾 Descargar", data=excel, file_name=f"Cotizacion_{cliente}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx")
                    st.balloons()
                else:
                    st.warning("Ingresa el nombre del cliente")
        with col_btn2:
            if st.button("📋 Copiar CSV"):
                csv_text = "SKU,Descripción,Cantidad,Precio,Subtotal\n"
                for item in st.session_state.carrito:
                    csv_text += f"{item['sku']},{item['descripcion']},{item['cantidad']},{item['precio']:.2f},{item['total']:.2f}\n"
                csv_text += f"TOTAL,{total_general:.2f}"
                st.code(csv_text, language="csv")
        with col_btn3:
            if st.button("🧹 Limpiar todo"):
                st.session_state.carrito = []
                st.rerun()

# ========== TAB 4: ASISTENTE ==========
with tab4:
    st.markdown("### 💬 Asistente QTC")
    st.caption("🤖 Pregúntame sobre productos, stock o cotizaciones")
    st.caption(f"📚 Buscando en {len(st.session_state.catalogos)} catálogo(s)")
    
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                st.markdown(f'<div class="chat-message-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                if '⚠️' in msg['content'] or '❌' in msg['content']:
                    st.markdown(f'<div class="chat-message-warning">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message-assistant">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    
    col_chat1, col_chat2 = st.columns([5, 1])
    with col_chat1:
        user_input = st.text_input("", placeholder="Ej: powerbank | cotiza RN0200065BK8 50 | ayuda", key="chat_input", label_visibility="collapsed")
    with col_chat2:
        enviar = st.button("📤 Enviar", use_container_width=True)
    
    if enviar and user_input:
        st.session_state.chat_history.append({'role': 'user', 'content': user_input})
        
        if marca == "XIAOMI" and st.session_state.catalogos:
            response = procesar_comando_asistente_v4(
                user_input, 
                st.session_state.catalogos, 
                st.session_state.stocks, 
                st.session_state.precio_key
            )
        elif marca == "UGREEN" and st.session_state.ugreen_catalogo:
            response = "🟢 Modo UGREEN - Comandos básicos disponibles"
        else:
            response = "⚠️ Primero carga catálogos y stock en el sidebar."
        
        st.session_state.chat_history.append({'role': 'assistant', 'content': response})
        st.rerun()
    
    col_clear1, col_clear2 = st.columns([1, 4])
    with col_clear1:
        if st.button("🧹 Limpiar chat"):
            st.session_state.chat_history = []
            st.rerun()
    with col_clear2:
        st.caption("💡 El asistente guarda la conversación mientras la app esté abierta")
    
    st.markdown("### 💡 Comandos rápidos")
    sugerencias = [
        "powerbank", "precio de RN0200065BK8", "stock de RN0200065BK8",
        "cotiza RN0200065BK8 50", "ver carrito", "ayuda"
    ]
    cols = st.columns(3)
    for i, sug in enumerate(sugerencias[:6]):
        with cols[i % 3]:
            if st.button(sug, key=f"sug_{i}"):
                st.session_state.chat_history.append({'role': 'user', 'content': sug})
                if marca == "XIAOMI" and st.session_state.catalogos:
                    response = procesar_comando_asistente_v4(sug, st.session_state.catalogos, st.session_state.stocks, st.session_state.precio_key)
                else:
                    response = "⚠️ Primero carga catálogos y stock"
                st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                st.rerun()

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown(f"""
<div class="footer">
    ⚡ QTC Smart Sales Pro v5.2 | Modo: {st.session_state.modo} | 
    📚 Catálogos: {len(st.session_state.catalogos)} | 
    Stock: YESSICA/APRI.004 -2 | APRI.001: 15% máx 100 | 
    🔍 Búsqueda en múltiples catálogos | 
    {datetime.now().strftime("%Y-%m-%d %H:%M")}
</div>
""", unsafe_allow_html=True)
