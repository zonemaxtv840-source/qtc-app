# app.py - QTC Smart Sales Pro v5.0
# PROFESSIONAL EDITION
# Búsqueda inteligente: SKU | Código de Barras | Descripción | Modelo | GOODS
# Stock: YESSICA/APRI.004 (stock-2) | APRI.001 (15% máx 100)
# Asistente IA integrado

import streamlit as st
import pandas as pd
import re
import io
from datetime import datetime
import warnings
from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher
import base64
from streamlit.components.v1 import html

warnings.filterwarnings('ignore')

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================

st.set_page_config(
    page_title="QTC Smart Sales Pro v5.0",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS COMPLETO V5.0
# ============================================

st.markdown("""
<style>
    /* FONDO DE PÁGINA - AZUL MIRAMAR VIVO */
    .stApp {
        background: linear-gradient(135deg, #0d47a1 0%, #1565c0 50%, #1e88e5 100%);
    }
    
    /* SIDEBAR - DURAZNO INTENSO */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8a35e 0%, #e87a2d 50%, #d45a1a 100%);
        border-right: 1px solid #ffcc80;
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* TARJETAS DE RESULTADOS */
    .result-card {
        background: white;
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 1rem;
        color: #1a1a2e;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* BADGES */
    .badge-yessica { background: #4CAF50; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    .badge-apri004 { background: #FF9800; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    .badge-apri001 { background: #f44336; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    .badge-warning { background: #ff9800; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; }
    .badge-ugreen { background: #00BCD4; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    
    /* CHAT ASISTENTE */
    .chat-container {
        background: #f0f2f6;
        border-radius: 16px;
        padding: 1rem;
        height: 400px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
    }
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
# CARGA INTELIGENTE DE CATÁLOGO
# ============================================

def cargar_catalogo_inteligente(archivo) -> Optional[Dict]:
    """
    Carga catálogo detectando automáticamente:
    - SKU | Código | SAP | Número
    - Descripción | Nombre | Producto | GOODS
    - Código de Barras (EAN/UPC/GTIN)
    - Modelo | Part Number
    - Precios (IR, BOX, VIP)
    """
    df = cargar_archivo(archivo)
    if df is None:
        return None
    
    columnas = {}
    
    # Detectar SKU
    posibles_sku = ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO', 'CODIGO', 'ID', 'COD_SAP']
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
    posibles_desc = ['DESC', 'DESCRIPCION', 'NOMBRE', 'PRODUCTO', 'GOODS', 'TITLE', 'DESCRIPTION']
    for col in df.columns:
        col_upper = str(col).upper()
        for posible in posibles_desc:
            if posible.upper() in col_upper:
                columnas['descripcion'] = col
                break
        if 'descripcion' in columnas:
            break
    
    # Detectar Código de Barras (NUEVO)
    posibles_barcode = ['BARCODE', 'EAN', 'UPC', 'CODIGO_BARRAS', 'GTIN', 'COD_BARRA', 'CODIGOBARRA']
    for col in df.columns:
        col_upper = str(col).upper()
        for posible in posibles_barcode:
            if posible.upper() in col_upper:
                columnas['barcode'] = col
                break
        if 'barcode' in columnas:
            break
    
    # Detectar Modelo / Part Number
    posibles_modelo = ['MODELO', 'MODEL', 'PART', 'PART_NO', 'PN', 'MODEL_NUMBER']
    for col in df.columns:
        col_upper = str(col).upper()
        for posible in posibles_modelo:
            if posible.upper() in col_upper:
                columnas['modelo'] = col
                break
        if 'modelo' in columnas:
            break
    
    # Detectar GOODS Description (si no se detectó como descripción principal)
    if 'descripcion' not in columnas:
        for col in df.columns:
            if 'GOODS' in str(col).upper():
                columnas['descripcion'] = col
                break
    
    # Detectar precios
    precios = {}
    mapeo_precios = {'P. IR': ['IR', 'MAYORISTA', 'MAYOR'], 
                     'P. BOX': ['BOX', 'CAJA'], 
                     'P. VIP': ['VIP']}
    
    for key, patrones in mapeo_precios.items():
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
    
    return {
        'nombre': archivo.name,
        'df': df,
        'columnas': columnas,
        'precios': precios,
        'tiene_barcode': 'barcode' in columnas,
        'tiene_modelo': 'modelo' in columnas
    }

# ============================================
# BÚSQUEDA UNIFICADA CON CÓDIGO DE BARRAS
# ============================================

def busqueda_unificada(termino: str, catalogo: Dict) -> pd.DataFrame:
    """
    Busca en múltiples columnas del catálogo:
    - SKU (exacto y parcial)
    - Descripción (texto libre)
    - Código de barras (exacto)
    - Modelo / Part Number
    - GOODS Description
    
    Retorna DataFrame con columna 'score' de relevancia
    """
    if not termino or len(termino) < 2:
        return pd.DataFrame()
    
    termino_limpio = termino.strip().upper()
    df = catalogo['df']
    columnas = catalogo['columnas']
    
    resultados = []
    
    for idx, row in df.iterrows():
        score = 0
        match_tipos = []
        
        # Obtener valores de las columnas
        sku = str(row.get(columnas.get('sku', ''), '')).upper()
        descripcion = str(row.get(columnas.get('descripcion', ''), '')).upper()
        barcode = str(row.get(columnas.get('barcode', ''), '')).upper() if 'barcode' in columnas else ''
        modelo = str(row.get(columnas.get('modelo', ''), '')).upper() if 'modelo' in columnas else ''
        
        # 1. Búsqueda por SKU (exacta = 100, contiene = 70)
        if termino_limpio == sku:
            score = 100
            match_tipos.append('SKU_EXACTO')
        elif termino_limpio in sku:
            score = max(score, 70)
            match_tipos.append('SKU_CONTIENE')
        
        # 2. Búsqueda por Código de Barras (exacta = 100, contiene = 85)
        if barcode:
            if termino_limpio == barcode:
                score = 100
                match_tipos.append('BARCODE_EXACTO')
            elif termino_limpio in barcode:
                score = max(score, 85)
                match_tipos.append('BARCODE_CONTIENE')
        
        # 3. Búsqueda por Modelo (exacta = 85, contiene = 60)
        if modelo:
            if termino_limpio == modelo:
                score = max(score, 85)
                match_tipos.append('MODELO_EXACTO')
            elif termino_limpio in modelo:
                score = max(score, 60)
                match_tipos.append('MODELO_CONTIENE')
        
        # 4. Búsqueda por Descripción (texto libre)
        if descripcion:
            if termino_limpio in descripcion:
                # Calcular puntaje basado en coincidencia de palabras
                palabras_termino = termino_limpio.split()
                palabras_encontradas = sum(1 for p in palabras_termino if p in descripcion)
                score_palabras = (palabras_encontradas / len(palabras_termino)) * 60 if palabras_termino else 0
                score = max(score, score_palabras)
                match_tipos.append('DESCRIPCION')
        
        if score > 0:
            resultados.append({
                'index': idx,
                'score': score,
                'match_tipos': ', '.join(match_tipos),
                'sku': sku,
                'descripcion': descripcion,
                'barcode': barcode,
                'modelo': modelo,
                'row': row
            })
    
    # Ordenar por score descendente
    resultados.sort(key=lambda x: x['score'], reverse=True)
    
    # Crear DataFrame de resultados
    if resultados:
        df_resultados = pd.DataFrame([r['row'] for r in resultados])
        df_resultados['_score'] = [r['score'] for r in resultados]
        df_resultados['_match_tipo'] = [r['match_tipos'] for r in resultados]
        df_resultados['_sku_display'] = [r['sku'] for r in resultados]
        df_resultados['_desc_display'] = [r['descripcion'][:100] for r in resultados]
        if catalogo['tiene_barcode']:
            df_resultados['_barcode_display'] = [r['barcode'] for r in resultados]
        return df_resultados
    
    return pd.DataFrame()

# ============================================
# LECTURA DE STOCK (SIN DUPLICACIÓN)
# ============================================

def buscar_stock_para_sku(sku: str, stocks: List[Dict]) -> Dict:
    """
    Lee stock según reglas:
    - YESSICA: columna "Disponible" o "Cantidad"
    - APRI.004: columna "Disponible" o "Cantidad"
    - APRI.001: SOLO columna "Disponible"
    - NO duplica: cada hoja aporta una sola vez
    """
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
        
        # Asegurar que col_sku es string
        df_sku = df[col_sku].astype(str).str.strip().str.upper()
        mask = df_sku == sku_limpio
        
        if mask.any():
            # Buscar columna de cantidad/disponible
            col_cant = None
            for col in df.columns:
                col_upper = str(col).upper()
                if any(p in col_upper for p in ['CANT', 'STOCK', 'DISPONIBLE', 'UNIDADES']):
                    col_cant = col
                    break
            
            if col_cant:
                # TOMAR SOLO LA PRIMERA FILA (evita duplicados)
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
    """
    Calcula la cantidad total a cotizar combinando:
    - Primero: YESSICA + APRI.004 (stock inmediato, regla stock-2)
    - Luego: APRI.001 (si falta, con regla 15%)
    
    Reglas APRI.001:
    - Stock mínimo: 20 unidades
    - Pedido mínimo: 5 unidades
    - Máximo: 15% del stock (tope 100 unidades)
    """
    
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
    
    # CASO 1: Stock inmediato suficiente
    if cantidad_solicitada <= stock_inmediato_seguro:
        return cantidad_solicitada, f"✅ OK - Stock inmediato: {cantidad_solicitada} unidades", detalle
    
    # CASO 2: Stock inmediato insuficiente
    restante = cantidad_solicitada - stock_inmediato_seguro
    
    # Regla APRI.001: Stock mínimo 20
    if stock_apri001 < 20:
        if stock_inmediato_seguro > 0:
            return stock_inmediato_seguro, f"⚠️ Stock inmediato insuficiente. Solo {stock_inmediato_seguro} unidades (APRI.001: {stock_apri001} < 20)", detalle
        else:
            return 0, f"❌ Sin stock disponible (APRI.001: {stock_apri001} < 20)", detalle
    
    # Regla APRI.001: Pedido mínimo 5
    if restante < 5:
        if stock_inmediato_seguro > 0:
            return stock_inmediato_seguro, f"⚠️ Pedido restante muy pequeño ({restante} < 5). Solo stock inmediato: {stock_inmediato_seguro}", detalle
        else:
            return 0, f"❌ Pedido muy pequeño ({restante} < 5) para transferencia APRI.001", detalle
    
    # Calcular máximo permitido (15%, tope 100)
    max_apri001 = min(int(stock_apri001 * 0.15), 100)
    
    if max_apri001 < 5:
        return stock_inmediato_seguro, f"⚠️ APRI.001 insuficiente (15% = {max_apri001} < 5). Solo stock inmediato: {stock_inmediato_seguro}", detalle
    
    if restante <= max_apri001:
        total_final = stock_inmediato_seguro + restante
        return total_final, f"✅ OK - Stock inmediato: {stock_inmediato_seguro} + APRI.001: {restante} = {total_final} unidades", detalle
    else:
        if stock_inmediato_seguro > 0:
            return stock_inmediato_seguro, f"⚠️ APRI.001 no puede cubrir. Máximo: {max_apri001}. Solo stock inmediato: {stock_inmediato_seguro}", detalle
        else:
            return 0, f"❌ No se puede cotizar. APRI.001 máximo: {max_apri001}, se necesitan {restante}", detalle

def calcular_cantidad_apri001_only(cantidad_solicitada: int, stock_apri001: int) -> Tuple[int, str, Dict]:
    """Calcula cantidad cotizable cuando SOLO hay stock en APRI.001"""
    
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
    
    return cantidad_solicitada, f"✅ OK - APRI.001: {cantidad_solicitada} unidades", detalle

# ============================================
# FUNCIONES UGREEN
# ============================================

def cargar_ugreen_catalogo(archivo) -> Optional[Dict]:
    """Carga específica para archivo UGREEN"""
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
    """Busca producto en catálogo UGREEN"""
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
                
                # Detectar columna SKU
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
        
        # Estilos
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="e67e22", end_color="e67e22", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        money_alignment = Alignment(horizontal="right", vertical="center")
        border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        
        # Encabezados
        ws['A1'] = 'QTC SMART SALES PRO'
        ws['A1'].font = Font(bold=True, size=14, color="e67e22")
        ws['A3'] = 'FECHA:'
        ws['B3'] = datetime.now().strftime("%d/%m/%Y %H:%M")
        ws['A4'] = 'CLIENTE:'
        ws['B4'] = cliente.upper()
        ws['A5'] = 'RUC:'
        ws['B5'] = ruc
        
        # Tabla
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
        
        # Total
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
        
        # Ajustar columnas
        ws.column_dimensions['A'].width = 22
        ws.column_dimensions['B'].width = 110
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 18
        ws.column_dimensions['E'].width = 18
        
        ws.freeze_panes = 'A8'
    
    return output.getvalue()

# ============================================
# ASISTENTE IA V2 - COMANDOS AVANZADOS
# ============================================

def procesar_comando_asistente_v2(comando: str, catalogo: Dict, stocks: List, precio_key: str) -> str:
    """
    Procesa comandos naturales del asistente con soporte para:
    - Búsqueda por SKU, descripción, código de barras, modelo
    - Consulta de precio y stock
    - Cotización rápida
    - Alternativas inteligentes
    - Gestión del carrito
    """
    comando_lower = comando.lower().strip()
    
    # ============================================
    # 1. COMANDOS DE PRECIO
    # ============================================
    if any(p in comando_lower for p in ['precio de', 'precio del', 'cual es el precio de', 'cuanto cuesta']):
        # Extraer SKU o término
        import re
        sku_match = re.search(r'([A-Z0-9]{8,})', comando.upper())
        if sku_match:
            sku = sku_match.group(1)
            return consultar_precio_sku(sku, catalogo, precio_key)
        else:
            # Buscar por descripción
            termino = extraer_termino_despues_de(comando, ['precio de', 'precio del', 'cual es el precio de', 'cuanto cuesta'])
            if termino:
                return consultar_precio_descripcion(termino, catalogo, precio_key)
    
    # ============================================
    # 2. COMANDOS DE STOCK
    # ============================================
    elif any(p in comando_lower for p in ['stock de', 'stock del', 'cuanto stock hay de', 'disponibilidad de']):
        import re
        sku_match = re.search(r'([A-Z0-9]{8,})', comando.upper())
        if sku_match:
            sku = sku_match.group(1)
            return consultar_stock_sku(sku, catalogo, stocks)
        else:
            termino = extraer_termino_despues_de(comando, ['stock de', 'stock del', 'cuanto stock hay de', 'disponibilidad de'])
            if termino:
                return consultar_stock_descripcion(termino, catalogo, stocks)
    
    # ============================================
    # 3. COMANDOS DE COTIZACIÓN RÁPIDA
    # ============================================
    elif any(p in comando_lower for p in ['cotizame', 'cotiza', 'agrega al carrito', 'agrega', 'pon en el carrito']):
        import re
        # Buscar cantidad y SKU o descripción
        cant_match = re.search(r'(\d+)\s*(unidades?|uds?|pzs?|unid)?', comando)
        sku_match = re.search(r'([A-Z0-9]{8,})', comando.upper())
        
        cantidad = int(cant_match.group(1)) if cant_match else 1
        
        if sku_match:
            sku = sku_match.group(1)
            return cotizar_sku(sku, cantidad, catalogo, stocks, precio_key)
        else:
            # Buscar por descripción
            termino = extraer_termino_despues_de_cotizacion(comando)
            if termino:
                return cotizar_descripcion(termino, cantidad, catalogo, stocks, precio_key)
    
    # ============================================
    # 4. COMANDOS DE BÚSQUEDA
    # ============================================
    elif any(p in comando_lower for p in ['busca', 'buscar', 'encuentra', 'encuentrame', 'dame', 'muestrame']):
        termino = extraer_termino_despues_de(comando, ['busca', 'buscar', 'encuentra', 'encuentrame', 'dame', 'muestrame'])
        if termino:
            return buscar_productos(termino, catalogo, stocks, precio_key, limit=5)
    
    # ============================================
    # 5. COMANDOS DE ALTERNATIVAS
    # ============================================
    elif any(p in comando_lower for p in ['alternativas', 'opciones', 'similares', 'parecidos', 'reemplazo de', 'sustituto de']):
        import re
        sku_match = re.search(r'([A-Z0-9]{8,})', comando.upper())
        if sku_match:
            sku = sku_match.group(1)
            return buscar_alternativas(sku, catalogo, stocks, precio_key)
        else:
            termino = extraer_termino_despues_de(comando, ['alternativas de', 'opciones para', 'similares a', 'reemplazo de'])
            if termino:
                return buscar_alternativas_por_descripcion(termino, catalogo, stocks, precio_key)
    
    # ============================================
    # 6. COMANDOS DE VARIANTES POR COLUMNA
    # ============================================
    elif any(p in comando_lower for p in ['variantes de', 'versiones de', 'modelos de']):
        termino = extraer_termino_despues_de(comando, ['variantes de', 'versiones de', 'modelos de'])
        if termino:
            return buscar_variantes(termino, catalogo, stocks, precio_key)
    
    # ============================================
    # 7. COMANDOS DE CATEGORÍA/FAMILIA
    # ============================================
    elif any(p in comando_lower for p in ['categoria', 'familia', 'productos de la categoria', 'todo de']):
        termino = extraer_termino_despues_de(comando, ['categoria', 'familia', 'productos de la categoria', 'todo de'])
        if termino:
            return buscar_por_categoria(termino, catalogo, stocks, precio_key)
    
    # ============================================
    # 8. COMANDOS DE CARRITO
    # ============================================
    elif any(p in comando_lower for p in ['ver carrito', 'mi carrito', 'muestrame el carrito', 'que tengo en el carrito']):
        return ver_carrito()
    
    elif any(p in comando_lower for p in ['limpiar carrito', 'vaciar carrito', 'borrar carrito']):
        st.session_state.carrito = []
        return "🧹 Carrito limpiado correctamente."
    
    elif any(p in comando_lower for p in ['total del carrito', 'total carrito', 'suma del carrito']):
        total = sum(item['total'] for item in st.session_state.carrito)
        return f"💰 El total de tu carrito es: **S/ {total:,.2f}**"
    
    elif 'quitar' in comando_lower or 'eliminar' in comando_lower or 'remover' in comando_lower:
        import re
        sku_match = re.search(r'([A-Z0-9]{8,})', comando.upper())
        if sku_match:
            sku = sku_match.group(1)
            return quitar_del_carrito(sku)
    
    # ============================================
    # 9. COMANDOS DE AYUDA
    # ============================================
    elif any(p in comando_lower for p in ['ayuda', 'help', 'comandos', 'que puedes hacer', 'que sabes hacer']):
        return mostrar_ayuda()
    
    # ============================================
    # 10. BÚSQUEDA POR DEFECTO (si no reconoce comando específico)
    # ============================================
    elif len(comando) >= 3:
        return buscar_productos(comando, catalogo, stocks, precio_key, limit=3)
    
    else:
        return "❓ No entendí tu consulta. Escribe 'ayuda' para ver los comandos disponibles."


# ============================================
# FUNCIONES AUXILIARES DEL ASISTENTE
# ============================================

def extraer_termino_despues_de(texto: str, palabras_clave: list) -> str:
    """Extrae el término después de una palabra clave"""
    texto_lower = texto.lower()
    for palabra in palabras_clave:
        if palabra in texto_lower:
            idx = texto_lower.find(palabra) + len(palabra)
            return texto[idx:].strip()
    return texto.strip()

def extraer_termino_despues_de_cotizacion(texto: str) -> str:
    """Extrae término para cotización (ej: 'cotizame 3 redmi buds 8')"""
    texto_lower = texto.lower()
    palabras_clave = ['cotizame', 'cotiza', 'agrega', 'pon']
    for palabra in palabras_clave:
        if palabra in texto_lower:
            idx = texto_lower.find(palabra) + len(palabra)
            resto = texto[idx:].strip()
            # Remover cantidad si está al inicio
            import re
            resto = re.sub(r'^\d+\s*(unidades?|uds?|pzs?)?\s*', '', resto)
            return resto.strip()
    return texto.strip()

def consultar_precio_sku(sku: str, catalogo: Dict, precio_key: str) -> str:
    """Consulta precio de un SKU específico"""
    if not catalogo:
        return "⚠️ No hay catálogo cargado."
    
    df = catalogo['df']
    col_sku = catalogo['columnas']['sku']
    mask = df[col_sku].astype(str).str.upper() == sku
    
    if mask.any():
        row = df[mask].iloc[0]
        desc = row.get(catalogo['columnas'].get('descripcion', col_sku), sku)
        
        # Obtener precios
        precios = {}
        for nivel, col_precio in catalogo['precios'].items():
            precios[nivel] = corregir_numero(row[col_precio]) if col_precio in row.index else 0
        
        response = f"💰 **{sku}** - {str(desc)[:80]}\n"
        response += f"   • Precio IR: S/ {precios.get('P. IR', 0):.2f}\n"
        response += f"   • Precio BOX: S/ {precios.get('P. BOX', 0):.2f}\n"
        response += f"   • Precio VIP: S/ {precios.get('P. VIP', 0):.2f}\n"
        
        if precios.get(precio_key, 0) > 0:
            response += f"\n✨ Precio seleccionado ({precio_key}): S/ {precios.get(precio_key, 0):.2f}"
        
        return response
    else:
        return f"❌ No encontré el SKU '{sku}' en el catálogo."

def consultar_precio_descripcion(termino: str, catalogo: Dict, precio_key: str) -> str:
    """Consulta precio por descripción"""
    resultados = busqueda_unificada(termino, catalogo)
    if not resultados.empty:
        response = f"🔍 Productos encontrados para '{termino}':\n\n"
        for _, row in resultados.head(3).iterrows():
            sku = row['_sku_display']
            desc = row['_desc_display']
            
            # Obtener precios
            precios = {}
            for nivel, col_precio in catalogo['precios'].items():
                precios[nivel] = corregir_numero(row[col_precio]) if col_precio in row.index else 0
            
            response += f"📦 **{sku}** - {desc}\n"
            response += f"   VIP: S/ {precios.get('P. VIP', 0):.2f} | IR: S/ {precios.get('P. IR', 0):.2f}\n\n"
        
        response += f"💡 Para cotizar escribe: 'cotiza [SKU] [cantidad]'"
        return response
    else:
        return f"❌ No encontré productos relacionados con '{termino}'"

def consultar_stock_sku(sku: str, catalogo: Dict, stocks: List) -> str:
    """Consulta stock de un SKU específico"""
    if not stocks:
        return "⚠️ No hay reportes de stock cargados."
    
    stock_info = buscar_stock_para_sku(sku, stocks)
    
    if stock_info['total'] == 0:
        return f"❌ SKU {sku} no tiene stock disponible."
    
    response = f"📦 **Stock de {sku}:**\n"
    response += f"   • YESSICA: {stock_info['yessica']} unidades\n"
    response += f"   • APRI.004: {stock_info['apri004']} unidades\n"
    response += f"   • APRI.001: {stock_info['apri001']} unidades\n"
    response += f"   • **TOTAL: {stock_info['total']} unidades**\n"
    
    # Mostrar ubicaciones
    if stock_info.get('ubicaciones'):
        response += f"\n📍 Ubicaciones encontradas:\n"
        for ub in stock_info['ubicaciones']:
            response += f"   • {ub['hoja']}: {ub['cantidad']} unidades\n"
    
    # Calcular stock seguro
    if stock_info['apri001'] > 0 and stock_info['yessica'] == 0 and stock_info['apri004'] == 0:
        max_apri001 = min(int(stock_info['apri001'] * 0.15), 100)
        response += f"\n⚠️ **Importante:** Este producto solo tiene stock en APRI.001\n"
        response += f"   • Máximo cotizable: {max_apri001} unidades (15% del stock, tope 100)\n"
        response += f"   • Stock mínimo requerido: 20 unidades\n"
        response += f"   • Pedido mínimo: 5 unidades"
    else:
        stock_seguro = max(0, stock_info['total'] - 2)
        response += f"\n🔒 **Stock cotizable (margen seguro -2):** {stock_seguro} unidades"
    
    return response

def consultar_stock_descripcion(termino: str, catalogo: Dict, stocks: List) -> str:
    """Consulta stock por descripción"""
    resultados = busqueda_unificada(termino, catalogo)
    if not resultados.empty:
        response = f"🔍 Productos encontrados para '{termino}':\n\n"
        for _, row in resultados.head(3).iterrows():
            sku = row['_sku_display']
            desc = row['_desc_display']
            stock_info = buscar_stock_para_sku(sku, stocks)
            
            response += f"📦 **{sku}** - {desc}\n"
            response += f"   Stock: "
            if stock_info['total'] > 0:
                response += f"{stock_info['total']} unidades"
                if stock_info['apri001'] > 0 and stock_info['yessica'] == 0 and stock_info['apri004'] == 0:
                    response += f" (solo APRI.001)"
            else:
                response += "SIN STOCK"
            response += f"\n   📍 YESSICA:{stock_info['yessica']} | APRI.004:{stock_info['apri004']} | APRI.001:{stock_info['apri001']}\n\n"
        
        response += f"💡 Para ver stock detallado escribe: 'stock de [SKU]'"
        return response
    else:
        return f"❌ No encontré productos relacionados con '{termino}'"

def cotizar_sku(sku: str, cantidad: int, catalogo: Dict, stocks: List, precio_key: str) -> str:
    """Cotiza un SKU específico y lo agrega al carrito"""
    if not catalogo or not stocks:
        return "⚠️ Primero carga catálogo y stock en el sidebar."
    
    # Buscar en catálogo
    df = catalogo['df']
    col_sku = catalogo['columnas']['sku']
    mask = df[col_sku].astype(str).str.upper() == sku
    
    if not mask.any():
        return f"❌ No encontré el SKU '{sku}' en el catálogo."
    
    row = df[mask].iloc[0]
    desc = row.get(catalogo['columnas'].get('descripcion', col_sku), sku)
    
    # Obtener precio
    precio = 0
    if precio_key in catalogo['precios']:
        col_precio = catalogo['precios'][precio_key]
        precio = corregir_numero(row[col_precio])
    
    if precio == 0:
        return f"❌ SKU {sku} no tiene precio en nivel {precio_key}."
    
    # Consultar stock
    stock_info = buscar_stock_para_sku(sku, stocks)
    
    if stock_info['total'] == 0:
        return f"❌ SKU {sku} no tiene stock disponible."
    
    # Aplicar reglas de stock
    solo_apri001 = stock_info['apri001'] > 0 and stock_info['yessica'] == 0 and stock_info['apri004'] == 0
    
    if solo_apri001:
        cant_final, msg, detalle = calcular_cantidad_apri001_only(cantidad, stock_info['apri001'])
    else:
        cant_final, msg, detalle = calcular_cantidad_total_segura(cantidad, stock_info)
    
    if cant_final == 0:
        return f"❌ No se puede cotizar: {msg}"
    
    # Agregar al carrito
    item = {
        'sku': sku,
        'descripcion': str(desc)[:150],
        'cantidad': cant_final,
        'precio': precio,
        'total': precio * cant_final,
        'stock_yessica': stock_info['yessica'],
        'stock_apri004': stock_info['apri004'],
        'stock_apri001': stock_info['apri001'],
        'detalle_apri001': stock_info.get('detalle_apri001', []),
        'ubicaciones': stock_info.get('ubicaciones', [])
    }
    st.session_state.carrito.append(item)
    
    response = f"✅ **Agregado al carrito:**\n"
    response += f"   • {cant_final}x {sku}\n"
    response += f"   • {str(desc)[:80]}\n"
    response += f"   • Precio unitario: S/ {precio:.2f}\n"
    response += f"   • Subtotal: S/ {precio * cant_final:,.2f}\n"
    response += f"   • {msg}\n"
    
    total_carrito = sum(item['total'] for item in st.session_state.carrito)
    response += f"\n💰 Total del carrito: S/ {total_carrito:,.2f}"
    
    return response

def cotizar_descripcion(termino: str, cantidad: int, catalogo: Dict, stocks: List, precio_key: str) -> str:
    """Cotiza el mejor producto encontrado por descripción"""
    resultados = busqueda_unificada(termino, catalogo)
    if resultados.empty:
        return f"❌ No encontré productos relacionados con '{termino}'"
    
    # Tomar el mejor resultado
    mejor = resultados.iloc[0]
    sku = mejor['_sku_display']
    desc = mejor['_desc_display']
    
    response = f"🔍 Encontré '{sku}' para tu búsqueda:\n"
    response += f"   📝 {desc}\n\n"
    response += cotizar_sku(sku, cantidad, catalogo, stocks, precio_key)
    
    return response

def buscar_productos(termino: str, catalogo: Dict, stocks: List, precio_key: str, limit: int = 5) -> str:
    """Búsqueda general de productos"""
    resultados = busqueda_unificada(termino, catalogo)
    if resultados.empty:
        return f"❌ No encontré productos relacionados con '{termino}'"
    
    response = f"🔍 **{len(resultados)} resultado(s) para '{termino}':**\n\n"
    
    for i, (_, row) in enumerate(resultados.head(limit).iterrows()):
        sku = row['_sku_display']
        desc = row['_desc_display']
        score = row['_score']
        match_tipo = row['_match_tipo']
        
        # Obtener stock
        stock_info = buscar_stock_para_sku(sku, stocks)
        stock_status = f"📦 Stock: {stock_info['total']} und"
        if stock_info['total'] == 0:
            stock_status = "❌ Sin stock"
        
        # Obtener precio
        precios = {}
        for nivel, col_precio in catalogo['precios'].items():
            precios[nivel] = corregir_numero(row[col_precio]) if col_precio in row.index else 0
        
        response += f"{i+1}. **{sku}** - {desc}\n"
        response += f"   🎯 Coincidencia: {score:.0f}% ({match_tipo})\n"
        response += f"   {stock_status} | 💰 {precio_key}: S/ {precios.get(precio_key, 0):.2f}\n"
        
        # Mostrar precios alternativos
        if precios.get('P. IR', 0) > 0:
            response += f"   💰 IR: S/ {precios['P. IR']:.2f} | BOX: S/ {precios['P. BOX']:.2f}\n"
        response += "\n"
    
    if len(resultados) > limit:
        response += f"📋 Hay {len(resultados)} resultados en total. Para ver más escribe 'busca {termino} mas'\n"
    
    response += f"💡 Para cotizar escribe: 'cotiza [SKU] [cantidad]' (ej: cotiza {resultados.iloc[0]['_sku_display']} 10)"
    
    return response

def buscar_alternativas(sku: str, catalogo: Dict, stocks: List, precio_key: str) -> str:
    """Busca productos alternativos al SKU dado"""
    if not catalogo:
        return "⚠️ No hay catálogo cargado."
    
    # Obtener descripción del SKU original
    df = catalogo['df']
    col_sku = catalogo['columnas']['sku']
    mask = df[col_sku].astype(str).str.upper() == sku
    
    if not mask.any():
        return f"❌ No encontré el SKU '{sku}' en el catálogo."
    
    row = df[mask].iloc[0]
    desc_original = str(row.get(catalogo['columnas'].get('descripcion', col_sku), sku)).upper()
    
    # Extraer palabras clave de la descripción
    palabras_clave = desc_original.split()[:5]
    termino_busqueda = ' '.join(palabras_clave)
    
    # Buscar alternativas excluyendo el SKU original
    resultados = busqueda_unificada(termino_busqueda, catalogo)
    resultados = resultados[resultados['_sku_display'] != sku]
    
    if resultados.empty:
        return f"❌ No encontré alternativas para {sku}"
    
    response = f"🔄 **Alternativas para {sku}**\n"
    response += f"📝 Producto original: {desc_original[:100]}\n\n"
    
    for i, (_, row) in enumerate(resultados.head(5).iterrows()):
        alt_sku = row['_sku_display']
        alt_desc = row['_desc_display']
        score = row['_score']
        
        stock_info = buscar_stock_para_sku(alt_sku, stocks)
        
        precios = {}
        for nivel, col_precio in catalogo['precios'].items():
            precios[nivel] = corregir_numero(row[col_precio]) if col_precio in row.index else 0
        
        response += f"{i+1}. **{alt_sku}** - {alt_desc[:60]}\n"
        response += f"   🎯 Coincidencia: {score:.0f}% | 📦 Stock: {stock_info['total']}\n"
        response += f"   💰 {precio_key}: S/ {precios.get(precio_key, 0):.2f}\n\n"
    
    response += f"💡 Para cotizar una alternativa escribe: 'cotiza [SKU] [cantidad]'"
    
    return response

def buscar_alternativas_por_descripcion(termino: str, catalogo: Dict, stocks: List, precio_key: str) -> str:
    """Busca alternativas por descripción"""
    resultados = busqueda_unificada(termino, catalogo)
    if resultados.empty:
        return f"❌ No encontré productos relacionados con '{termino}'"
    
    response = f"🔄 **Opciones para '{termino}':**\n\n"
    for i, (_, row) in enumerate(resultados.head(5).iterrows()):
        sku = row['_sku_display']
        desc = row['_desc_display']
        score = row['_score']
        
        stock_info = buscar_stock_para_sku(sku, stocks)
        
        precios = {}
        for nivel, col_precio in catalogo['precios'].items():
            precios[nivel] = corregir_numero(row[col_precio]) if col_precio in row.index else 0
        
        response += f"{i+1}. **{sku}**\n"
        response += f"   📝 {desc[:80]}\n"
        response += f"   🎯 Coincidencia: {score:.0f}% | 📦 Stock: {stock_info['total']}\n"
        response += f"   💰 {precio_key}: S/ {precios.get(precio_key, 0):.2f}\n\n"
    
    return response

def buscar_variantes(termino: str, catalogo: Dict, stocks: List, precio_key: str) -> str:
    """Busca variantes de un producto (diferentes colores, capacidades, etc.)"""
    # Buscar productos que contengan el término
    resultados = busqueda_unificada(termino, catalogo)
    if resultados.empty:
        return f"❌ No encontré variantes para '{termino}'"
    
    # Agrupar por base de nombre (sin sufijos de color/capacidad)
    variantes = {}
    for _, row in resultados.iterrows():
        sku = row['_sku_display']
        desc = row['_desc_display']
        
        # Extraer base del nombre (ignorar colores)
        base_nombre = desc.upper()
        for color in ['BLACK', 'WHITE', 'BLUE', 'RED', 'GREEN', 'PINK', 'PURPLE', 'GRAY', 'GREY', 'SILVER', 'GOLD']:
            base_nombre = base_nombre.replace(color, '').strip()
        
        if base_nombre not in variantes:
            variantes[base_nombre] = []
        variantes[base_nombre].append({'sku': sku, 'desc': desc, 'row': row})
    
    if not variantes:
        return f"❌ No encontré variantes para '{termino}'"
    
    response = f"🎨 **Variantes encontradas:**\n\n"
    for base, items in list(variantes.items())[:3]:
        response += f"📌 **{base[:60]}**\n"
        for item in items[:5]:
            sku = item['sku']
            desc = item['desc']
            stock_info = buscar_stock_para_sku(sku, stocks)
            
            precios = {}
            for nivel, col_precio in catalogo['precios'].items():
                precios[nivel] = corregir_numero(item['row'][col_precio]) if col_precio in item['row'].index else 0
            
            # Extraer variante (color, capacidad)
            variante_desc = desc.replace(base, '').strip() if len(desc) > len(base) else 'Estándar'
            response += f"   • **{variante_desc[:40]}** ({sku}) - Stock: {stock_info['total']} | {precio_key}: S/ {precios.get(precio_key, 0):.2f}\n"
        response += "\n"
    
    return response

def buscar_por_categoria(termino: str, catalogo: Dict, stocks: List, precio_key: str) -> str:
    """Busca productos por categoría o familia"""
    # Buscar en columna de categoría si existe
    df = catalogo['df']
    
    # Detectar columna de categoría
    col_categoria = None
    for col in df.columns:
        col_upper = str(col).upper()
        if any(p in col_upper for p in ['CATEGORIA', 'CATEGORY', 'FAMILIA', 'FAMILY']):
            col_categoria = col
            break
    
    if col_categoria:
        mask = df[col_categoria].astype(str).str.upper().str.contains(termino.upper(), na=False)
        resultados_cat = df[mask]
        
        if not resultados_cat.empty:
            response = f"📁 **Productos en categoría '{termino.upper()}':**\n\n"
            for _, row in resultados_cat.head(10).iterrows():
                sku = row[catalogo['columnas']['sku']]
                desc = row.get(catalogo['columnas'].get('descripcion', catalogo['columnas']['sku']), sku)
                stock_info = buscar_stock_para_sku(sku, stocks)
                
                precios = {}
                for nivel, col_precio in catalogo['precios'].items():
                    precios[nivel] = corregir_numero(row[col_precio]) if col_precio in row.index else 0
                
                response += f"📦 **{sku}** - {str(desc)[:60]}\n"
                response += f"   Stock: {stock_info['total']} | {precio_key}: S/ {precios.get(precio_key, 0):.2f}\n\n"
            
            if len(resultados_cat) > 10:
                response += f"📋 Hay {len(resultados_cat)} productos en total.\n"
            return response
    
    # Si no hay columna de categoría, buscar por descripción
    return buscar_productos(termino, catalogo, stocks, precio_key, limit=10)

def ver_carrito() -> str:
    """Muestra el contenido del carrito"""
    if not st.session_state.carrito:
        return "🛒 Tu carrito está vacío."
    
    response = f"🛒 **Tu carrito tiene {len(st.session_state.carrito)} producto(s):**\n\n"
    for i, item in enumerate(st.session_state.carrito, 1):
        response += f"{i}. **{item['cantidad']}x {item['sku']}**\n"
        response += f"   📝 {item['descripcion'][:60]}\n"
        response += f"   💰 S/ {item['precio']:.2f} c/u → Subtotal: S/ {item['total']:,.2f}\n\n"
    
    total = sum(item['total'] for item in st.session_state.carrito)
    response += f"---\n💰 **TOTAL: S/ {total:,.2f}**\n\n"
    response += f"💡 Para exportar, ve a la pestaña 'CARRITO'"
    
    return response

def quitar_del_carrito(sku: str) -> str:
    """Elimina un producto del carrito"""
    for i, item in enumerate(st.session_state.carrito):
        if item['sku'] == sku:
            st.session_state.carrito.pop(i)
            return f"✅ Eliminado {sku} del carrito."
    return f"❌ No encontré {sku} en el carrito."

def mostrar_ayuda() -> str:
    """Muestra todos los comandos disponibles"""
    return """
📋 **COMANDOS DISPONIBLES**

💰 **Precio:**
   • `precio de RN0200065BK8` - Precio de un SKU
   • `cuanto cuesta Redmi Buds 8` - Precio por descripción

📦 **Stock:**
   • `stock de RN0200065BK8` - Stock detallado de un SKU
   • `disponibilidad de Redmi Buds` - Stock por descripción

🛒 **Cotización:**
   • `cotiza RN0200065BK8 50` - Agrega SKU al carrito
   • `cotizame 3 Redmi Buds 8` - Cotiza por descripción
   • `agrega al carrito CN0200059BK8 30` - Alternativa

🔄 **Alternativas:**
   • `alternativas de RN0200065BK8` - Productos similares
   • `opciones para auriculares type-c` - Búsqueda de alternativas

🎨 **Variantes:**
   • `variantes de Redmi Buds 8` - Todos los colores/modelos

📁 **Categorías:**
   • `categoria AUDIO` - Productos por categoría

🔍 **Búsqueda general:**
   • `busca auriculares type-c` - Búsqueda flexible
   • `encuentrame cargador 67W` - Búsqueda natural

🛒 **Carrito:**
   • `ver carrito` - Muestra cotización actual
   • `total del carrito` - Solo el total
   • `limpiar carrito` - Vacía el carrito
   • `quitar RN0200065BK8` - Elimina producto

❓ **Ayuda:**
   • `ayuda` / `que puedes hacer` - Muestra esta ayuda

💡 **Consejos:**
   • Puedes combinar comandos: "cotiza y ver carrito"
   • La búsqueda funciona con SKU, código de barras, modelo o descripción
   • No necesitas escribir exactamente las palabras clave, el asistente entiende contextos
"""


# ============================================
# ACTUALIZAR EL TAB DEL ASISTENTE
# ============================================
# En el tab4, reemplazar la llamada a procesar_comando_asistente por:
# response = procesar_comando_asistente_v2(...)
# ============================================
# INICIALIZACIÓN DE SESIÓN
# ============================================

if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'modo' not in st.session_state:
    st.session_state.modo = "XIAOMI"
if 'precio_key' not in st.session_state:
    st.session_state.precio_key = "P. VIP"
if 'catalogo_actual' not in st.session_state:
    st.session_state.catalogo_actual = None
if 'catalogos' not in st.session_state:
    st.session_state.catalogos = []
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
        st.markdown("<h2 style='color:#1a1a2e;'>QTC Smart Sales Pro v5.0</h2>", unsafe_allow_html=True)
        user = st.text_input("👤 Usuario", placeholder="Ingresa tu usuario")
        pw = st.text_input("🔒 Contraseña", type="password", placeholder="Ingresa tu contraseña")
        
        credenciales = {
            "admin": {"password": "qtc2026", "role": "ADMIN", "name": "Administrador"},
            "kimberly": {"password": "kam2026", "role": "KAM", "name": "Kimberly"},
            "vendedor": {"password": "ventas2026", "role": "VENDEDOR", "name": "Vendedor"}
        }
        
        if st.button("🚀 Ingresar", use_container_width=True):
            if user in credenciales and pw == credenciales[user]["password"]:
                st.session_state.auth = True
                st.session_state.user_role = credenciales[user]["role"]
                st.session_state.user_name = credenciales[user]["name"]
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
    st.markdown("# Smart Sales Pro v5.0")
    st.caption("Búsqueda por SKU | Código de Barras | Descripción | Modelo | GOODS")
with col3:
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 12px; text-align: right;">
        👤 {st.session_state.user_name}<br>
        <span style="font-size: 0.7rem;">{st.session_state.user_role}</span>
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
    
    marca = st.radio("📌 Marca / Modo", ["XIAOMI", "UGREEN", "OTRAS MARCAS"], index=0)
    st.session_state.modo = marca
    
    st.markdown("---")
    precio_opcion = st.radio("💰 Nivel de precio", ["P. VIP", "P. BOX", "P. IR"], index=0)
    st.session_state.precio_key = precio_opcion
    
    st.markdown("---")
    st.markdown("### 📂 Archivos")
    
    # Catálogos XIAOMI/OTROS
    if marca != "UGREEN":
        st.markdown("**📚 Catálogo de precios**")
        archivo_cat = st.file_uploader(
            "Excel o CSV (SKU, Descripción, Precios)",
            type=['xlsx', 'xls', 'csv'],
            accept_multiple_files=False,
            key="cat_upload_v5"
        )
        if archivo_cat:
            catalogo = cargar_catalogo_inteligente(archivo_cat)
            if catalogo:
                st.session_state.catalogo_actual = catalogo
                st.success(f"✅ {archivo_cat.name}")
                if catalogo['tiene_barcode']:
                    st.info("📷 Se detectó columna de CÓDIGO DE BARRAS")
                if catalogo['tiene_modelo']:
                    st.info("🔧 Se detectó columna de MODELO/PART NO")
    
    # Catálogo UGREEN
    if marca == "UGREEN":
        st.markdown("**📚 Catálogo UGREEN**")
        archivo_ugreen = st.file_uploader(
            "Excel UGREEN",
            type=['xlsx', 'xls'],
            accept_multiple_files=False,
            key="ugreen_upload_v5"
        )
        if archivo_ugreen:
            ugreen_cat = cargar_ugreen_catalogo(archivo_ugreen)
            if ugreen_cat:
                st.session_state.ugreen_catalogo = ugreen_cat
                st.success(f"✅ UGREEN: {archivo_ugreen.name}")
    
    # Stock
    st.markdown("**📦 Reportes de stock**")
    st.caption("YESSICA/APRI.004: stock-2 | APRI.001: 15% máx 100")
    archivos_stock = st.file_uploader(
        "Excel con múltiples hojas",
        type=['xlsx', 'xls'],
        accept_multiple_files=True,
        key="stock_upload_v5"
    )
    if archivos_stock:
        st.session_state.stocks = cargar_stock(archivos_stock, marca)
    
    st.markdown("---")
    
    # Carrito resumen
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

tab1, tab2, tab3, tab4 = st.tabs(["🔍 BÚSQUEDA INTELIGENTE", "📦 MODO MASIVO", "🛒 CARRITO", "💬 ASISTENTE"])

# ========== TAB 1: BÚSQUEDA INTELIGENTE ==========
with tab1:
    if st.session_state.modo == "XIAOMI" and st.session_state.catalogo_actual and st.session_state.stocks:
        st.markdown("### 🔍 Buscar productos")
        st.caption("Busca por: **SKU** | **Nombre** | **Código de Barras** | **Modelo** | **Descripción**")
        
        col_f1, col_f2 = st.columns([3, 1])
        with col_f1:
            termino = st.text_input("", placeholder="Ej: 6971234567890 | RN0200065BK8 | auriculares type-c | Redmi Buds")
        with col_f2:
            solo_stock = st.checkbox("📦 Solo con stock", value=False)
        
        if termino and len(termino) >= 2:
            with st.spinner("🔍 Buscando..."):
                resultados = busqueda_unificada(termino, st.session_state.catalogo_actual)
                
                if not resultados.empty:
                    # Filtrar por stock si se solicita
                    if solo_stock:
                        mascara_stock = []
                        for _, row in resultados.iterrows():
                            sku = row[st.session_state.catalogo_actual['columnas']['sku']]
                            stock_info = buscar_stock_para_sku(sku, st.session_state.stocks)
                            mascara_stock.append(stock_info['total'] > 0)
                        resultados = resultados[mascara_stock]
                    
                    st.success(f"✅ {len(resultados)} resultados encontrados")
                    
                    for idx, row in resultados.iterrows():
                        sku = row[st.session_state.catalogo_actual['columnas']['sku']]
                        desc = row[st.session_state.catalogo_actual['columnas']['descripcion']] if 'descripcion' in st.session_state.catalogo_actual['columnas'] else sku
                        score = row.get('_score', 0)
                        match_tipo = row.get('_match_tipo', '')
                        barcode = row.get('_barcode_display', '') if st.session_state.catalogo_actual['tiene_barcode'] else ''
                        
                        # Consultar stock
                        stock_info = buscar_stock_para_sku(sku, st.session_state.stocks)
                        badge_stock = construir_badge_stock(
                            stock_info['yessica'], stock_info['apri004'], stock_info['apri001'],
                            stock_info.get('detalle_apri001', []), stock_info.get('ubicaciones', [])
                        )
                        
                        # Precios
                        precios = {}
                        for nivel, col_precio in st.session_state.catalogo_actual['precios'].items():
                            precio_val = row[col_precio] if col_precio in row.index else 0
                            precios[nivel] = corregir_numero(precio_val)
                        
                        # Determinar color según score
                        if score >= 80:
                            border_color = "#4CAF50"
                        elif score >= 50:
                            border_color = "#FF9800"
                        else:
                            border_color = "#2196F3"
                        
                        st.markdown(f"""
                        <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid {border_color};">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <div>
                                    <strong style="font-size:1.1rem;">📦 {sku}</strong>
                                    <span style="background:{border_color};color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;margin-left:8px;">{score:.0f}% match</span>
                                </div>
                                <span style="font-size:0.7rem;color:#666;">{match_tipo}</span>
                            </div>
                            <div style="margin-top:8px;"><strong>📝 {str(desc)[:150]}</strong></div>
                            {f'<div style="margin-top:4px;font-size:0.75rem;color:#666;">📷 Código de barras: {barcode}</div>' if barcode else ''}
                            <div style="margin-top:8px;">{badge_stock}</div>
                            <div style="margin-top:8px;">
                                💰 Precios: IR: S/ {precios.get('P. IR', 0):.2f} | 
                                BOX: S/ {precios.get('P. BOX', 0):.2f} | 
                                VIP: S/ {precios.get('P. VIP', 0):.2f}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Botones de acción
                        if stock_info['total'] > 0 and precios.get(st.session_state.precio_key, 0) > 0:
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                cantidad_input = st.number_input("Cantidad", min_value=1, value=1, step=1, key=f"busq_{sku}_{idx}")
                            with col2:
                                if st.button(f"➕ Agregar a cotización", key=f"add_busq_{sku}_{idx}"):
                                    # Aplicar reglas de stock
                                    solo_apri001 = stock_info['apri001'] > 0 and stock_info['yessica'] == 0 and stock_info['apri004'] == 0
                                    if solo_apri001:
                                        cant_final, msg, _ = calcular_cantidad_apri001_only(cantidad_input, stock_info['apri001'])
                                    else:
                                        cant_final, msg, _ = calcular_cantidad_total_segura(cantidad_input, stock_info)
                                    
                                    if cant_final > 0:
                                        item = {
                                            'sku': sku,
                                            'descripcion': str(desc)[:150],
                                            'cantidad': cant_final,
                                            'precio': precios.get(st.session_state.precio_key, 0),
                                            'total': precios.get(st.session_state.precio_key, 0) * cant_final,
                                            'stock_yessica': stock_info['yessica'],
                                            'stock_apri004': stock_info['apri004'],
                                            'stock_apri001': stock_info['apri001'],
                                            'detalle_apri001': stock_info.get('detalle_apri001', []),
                                            'ubicaciones': stock_info.get('ubicaciones', [])
                                        }
                                        st.session_state.carrito.append(item)
                                        st.success(f"✅ Agregado {cant_final}x {sku} - {msg[:100]}")
                                        st.rerun()
                                    else:
                                        st.warning(f"❌ {msg}")
                        elif precios.get(st.session_state.precio_key, 0) == 0:
                            st.warning(f"⚠️ SKU {sku} no tiene precio en nivel {st.session_state.precio_key}")
                        
                        st.divider()
                else:
                    st.info("No se encontraron resultados. Prueba con otro término de búsqueda.")
    elif st.session_state.modo == "UGREEN" and st.session_state.ugreen_catalogo:
        st.markdown("### 🔍 Buscar en UGREEN")
        termino = st.text_input("", placeholder="SKU o descripción")
        if termino and len(termino) >= 2:
            resultados = buscar_ugreen_producto(termino, st.session_state.ugreen_catalogo)
            if resultados:
                for prod in resultados:
                    st.markdown(f"""
                    <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;">
                        <strong>📦 {prod['sku']}</strong><br>
                        📝 {prod['descripcion'][:100]}<br>
                        💰 Precio {st.session_state.precio_key}: S/ {prod['precios'].get(st.session_state.precio_key, 0):.2f}
                    </div>
                    """, unsafe_allow_html=True)
                    if prod['tiene_precio']:
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            cantidad = st.number_input("Cantidad", min_value=1, value=1, step=1, key=f"ugreen_{prod['sku']}")
                        with col2:
                            if st.button(f"➕ Agregar", key=f"add_ugreen_{prod['sku']}"):
                                item = {
                                    'sku': prod['sku'],
                                    'descripcion': prod['descripcion'][:150],
                                    'cantidad': cantidad,
                                    'precio': prod['precios'].get(st.session_state.precio_key, 0),
                                    'total': prod['precios'].get(st.session_state.precio_key, 0) * cantidad,
                                    'tipo': 'UGREEN'
                                }
                                st.session_state.carrito.append(item)
                                st.success(f"✅ Agregado {cantidad}x {prod['sku']}")
                                st.rerun()
                    st.divider()
            else:
                st.info("No se encontraron resultados")
    else:
        st.warning("Carga los archivos necesarios en el sidebar para comenzar.")

# ========== TAB 2: MODO MASIVO ==========
with tab2:
    st.markdown("### 📦 Ingresa productos en formato masivo")
    st.caption("Formato: `SKU:CANTIDAD` (uno por línea)")
    
    texto_bulk = st.text_area("", height=200, placeholder="RN0200065BK8:50\nCN0200059BK8:30\nCN0200064BK8:100")
    
    if st.button("🚀 Procesar lista", type="primary"):
        if texto_bulk and st.session_state.catalogo_actual and st.session_state.stocks:
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
                resultados_procesados = []
                for pedido in pedidos:
                    # Buscar en catálogo
                    df = st.session_state.catalogo_actual['df']
                    col_sku = st.session_state.catalogo_actual['columnas']['sku']
                    mask = df[col_sku].astype(str).str.upper() == pedido['sku']
                    
                    if mask.any():
                        row = df[mask].iloc[0]
                        desc = row.get(st.session_state.catalogo_actual['columnas'].get('descripcion', col_sku), pedido['sku'])
                        precio = 0
                        if st.session_state.precio_key in st.session_state.catalogo_actual['precios']:
                            col_precio = st.session_state.catalogo_actual['precios'][st.session_state.precio_key]
                            precio = corregir_numero(row[col_precio])
                        
                        stock_info = buscar_stock_para_sku(pedido['sku'], st.session_state.stocks)
                        
                        if precio > 0 and stock_info['total'] > 0:
                            solo_apri001 = stock_info['apri001'] > 0 and stock_info['yessica'] == 0 and stock_info['apri004'] == 0
                            if solo_apri001:
                                cant_final, msg, _ = calcular_cantidad_apri001_only(pedido['cantidad'], stock_info['apri001'])
                            else:
                                cant_final, msg, _ = calcular_cantidad_total_segura(pedido['cantidad'], stock_info)
                        else:
                            cant_final = 0
                            msg = "Sin precio o sin stock"
                        
                        resultados_procesados.append({
                            'sku': pedido['sku'],
                            'descripcion': str(desc)[:100],
                            'cantidad_solicitada': pedido['cantidad'],
                            'cantidad_cotizar': cant_final,
                            'precio': precio,
                            'estado': msg,
                            'stock_info': stock_info
                        })
                    else:
                        resultados_procesados.append({
                            'sku': pedido['sku'],
                            'descripcion': 'No encontrado',
                            'cantidad_solicitada': pedido['cantidad'],
                            'cantidad_cotizar': 0,
                            'precio': 0,
                            'estado': '❌ SKU no encontrado en catálogo',
                            'stock_info': {'total': 0}
                        })
                
                st.session_state.resultados_bulk = resultados_procesados
                
                # Mostrar resumen
                total_ok = sum(1 for p in resultados_procesados if p['cantidad_cotizar'] > 0)
                st.success(f"✅ Procesados {len(pedidos)} productos. {total_ok} cotizables.")
                
                if st.button("📋 Agregar cotizables al carrito"):
                    agregados = 0
                    for prod in resultados_procesados:
                        if prod['cantidad_cotizar'] > 0 and prod['precio'] > 0:
                            item = {
                                'sku': prod['sku'],
                                'descripcion': prod['descripcion'],
                                'cantidad': prod['cantidad_cotizar'],
                                'precio': prod['precio'],
                                'total': prod['precio'] * prod['cantidad_cotizar'],
                                'stock_yessica': prod['stock_info'].get('yessica', 0),
                                'stock_apri004': prod['stock_info'].get('apri004', 0),
                                'stock_apri001': prod['stock_info'].get('apri001', 0),
                                'detalle_apri001': prod['stock_info'].get('detalle_apri001', []),
                                'ubicaciones': prod['stock_info'].get('ubicaciones', [])
                            }
                            st.session_state.carrito.append(item)
                            agregados += 1
                    st.success(f"✅ Agregados {agregados} productos al carrito")
                    st.rerun()
                
                # Mostrar resultados detallados
                st.markdown("### 📋 Resultados")
                for prod in resultados_procesados:
                    badge = construir_badge_stock(
                        prod['stock_info'].get('yessica', 0),
                        prod['stock_info'].get('apri004', 0),
                        prod['stock_info'].get('apri001', 0),
                        prod['stock_info'].get('detalle_apri001', []),
                        prod['stock_info'].get('ubicaciones', [])
                    )
                    color = "#4CAF50" if prod['cantidad_cotizar'] > 0 else "#f44336"
                    st.markdown(f"""
                    <div style="background:white;border-radius:12px;padding:0.75rem;margin-bottom:0.5rem;border-left:4px solid {color};">
                        <strong>{prod['sku']}</strong> - {prod['descripcion'][:80]}<br>
                        Solicitado: {prod['cantidad_solicitada']} → Cotizable: {prod['cantidad_cotizar']}<br>
                        {badge}<br>
                        <span style="font-size:0.8rem;">{prod['estado']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No se encontraron productos válidos")
        else:
            st.warning("Carga catálogo y stock primero")

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

# ========== TAB 4: ASISTENTE (VERSIÓN MEJORADA) ==========
with tab4:
    st.markdown("### 💬 Asistente QTC")
    st.caption("🤖 Pregúntame sobre productos, stock o cotizaciones. ¡Estoy para ayudarte!")
    st.caption("📋 Ejemplos: 'precio de RN0200065BK8' | 'stock de Redmi Buds' | 'cotiza CN0200059BK8 30' | 'alternativas de auriculares' | 'ayuda'")
    
    # Mostrar historial del chat
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                st.markdown(f'<div class="chat-message-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message-assistant">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    
    # Input del usuario
    col_chat1, col_chat2 = st.columns([5, 1])
    with col_chat1:
        user_input = st.text_input("", placeholder="Ej: cotiza RN0200065BK8 50", key="chat_input", label_visibility="collapsed")
    with col_chat2:
        enviar = st.button("📤 Enviar", use_container_width=True)
    
    if enviar and user_input:
        # Guardar mensaje del usuario
        st.session_state.chat_history.append({'role': 'user', 'content': user_input})
        
        # ========== AQUÍ VA EL CAMBIO ==========
        # Usar la NUEVA función con comandos avanzados
        if st.session_state.modo == "XIAOMI" and st.session_state.catalogo_actual:
            response = procesar_comando_asistente_v2(
                user_input, 
                st.session_state.catalogo_actual, 
                st.session_state.stocks, 
                st.session_state.precio_key
            )
        elif st.session_state.modo == "UGREEN" and st.session_state.ugreen_catalogo:
            # Versión simplificada para UGREEN (puedes expandir después)
            response = procesar_comando_asistente_ugreen(user_input, st.session_state.ugreen_catalogo, st.session_state.precio_key)
        else:
            response = "⚠️ Primero carga un catálogo y stock en el sidebar."
        # =====================================
        
        st.session_state.chat_history.append({'role': 'assistant', 'content': response})
        st.rerun()
    
    # Botón de limpiar chat
    col_clear1, col_clear2 = st.columns([1, 4])
    with col_clear1:
        if st.button("🧹 Limpiar conversación"):
            st.session_state.chat_history = []
            st.rerun()
    with col_clear2:
        st.caption("💡 El asistente recuerda la conversación mientras la app esté abierta")
    
    # Sugerencias rápidas (comandos de ejemplo)
    st.markdown("### 💡 Comandos rápidos")
    sugerencias = [
        "precio de RN0200065BK8",
        "stock de RN0200065BK8", 
        "cotiza RN0200065BK8 50",
        "alternativas de Redmi Buds",
        "variantes de Redmi Buds 8",
        "ver carrito"
    ]
    
    # Mostrar sugerencias en filas
    for i in range(0, len(sugerencias), 3):
        cols = st.columns(3)
        for j, sug in enumerate(sugerencias[i:i+3]):
            with cols[j]:
                if st.button(sug, key=f"sug_{i}_{j}"):
                    # Procesar el comando directamente
                    st.session_state.chat_history.append({'role': 'user', 'content': sug})
                    if st.session_state.modo == "XIAOMI" and st.session_state.catalogo_actual:
                        response = procesar_comando_asistente_v2(
                            sug, 
                            st.session_state.catalogo_actual, 
                            st.session_state.stocks, 
                            st.session_state.precio_key
                        )
                    else:
                        response = "⚠️ Primero carga un catálogo y stock en el sidebar."
                    st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                    st.rerun()

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown(f"""
<div class="footer">
    ⚡ QTC Smart Sales Pro v5.0 | Modo: {st.session_state.modo} | 
    Stock: YESSICA/APRI.004: stock-2 | APRI.001: 15% máx 100 | 
    {datetime.now().strftime("%Y-%m-%d %H:%M")}
</div>
""", unsafe_allow_html=True)
