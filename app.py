# app.py - QTC Smart Sales Pro v5.1
# PROFESSIONAL EDITION WITH HYBRID SEARCH
# Búsqueda HÍBRIDA: CATÁLOGO (precios) + STOCK (descripciones)
# Detección de inconsistencias: Stock sin precio | Precio sin stock

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
    page_title="QTC Smart Sales Pro v5.1",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS COMPLETO V5.1
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
    .badge-inconsistencia { background: #9c27b0; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    
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
    
    # Detectar Código de Barras
    posibles_barcode = ['BARCODE', 'EAN', 'UPC', 'CODIGO_BARRAS', 'GTIN', 'COD_BARRA', 'CODIGOBARRA']
    for col in df.columns:
        col_upper = str(col).upper()
        for posible in posibles_barcode:
            if posible.upper() in col_upper:
                columnas['barcode'] = col
                break
        if 'barcode' in columnas:
            break
    
    # Detectar Modelo
    posibles_modelo = ['MODELO', 'MODEL', 'PART', 'PART_NO', 'PN', 'MODEL_NUMBER']
    for col in df.columns:
        col_upper = str(col).upper()
        for posible in posibles_modelo:
            if posible.upper() in col_upper:
                columnas['modelo'] = col
                break
        if 'modelo' in columnas:
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
# BÚSQUEDA EN CATÁLOGO
# ============================================

def busqueda_unificada(termino: str, catalogo: Dict) -> pd.DataFrame:
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
        
        # SKU exacto
        if termino_limpio == sku:
            score = 100
            match_tipos.append('SKU_EXACTO')
        elif termino_limpio in sku:
            score = max(score, 70)
            match_tipos.append('SKU_CONTIENE')
        
        # Código de barras
        if barcode:
            if termino_limpio == barcode:
                score = 100
                match_tipos.append('BARCODE_EXACTO')
            elif termino_limpio in barcode:
                score = max(score, 85)
                match_tipos.append('BARCODE_CONTIENE')
        
        # Modelo
        if modelo:
            if termino_limpio == modelo:
                score = max(score, 85)
                match_tipos.append('MODELO_EXACTO')
            elif termino_limpio in modelo:
                score = max(score, 60)
                match_tipos.append('MODELO_CONTIENE')
        
        # Descripción
        if descripcion:
            if termino_limpio in descripcion:
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
                'row': row,
                'fuente': 'CATALOGO'
            })
    
    resultados.sort(key=lambda x: x['score'], reverse=True)
    
    if resultados:
        df_resultados = pd.DataFrame([r['row'] for r in resultados])
        df_resultados['_score'] = [r['score'] for r in resultados]
        df_resultados['_match_tipo'] = [r['match_tipos'] for r in resultados]
        df_resultados['_sku_display'] = [r['sku'] for r in resultados]
        df_resultados['_desc_display'] = [r['descripcion'][:100] for r in resultados]
        df_resultados['_fuente'] = 'CATALOGO'
        if catalogo['tiene_barcode']:
            df_resultados['_barcode_display'] = [r['barcode'] for r in resultados]
        return df_resultados
    
    return pd.DataFrame()

# ============================================
# NUEVA: BÚSQUEDA HÍBRIDA (CATÁLOGO + STOCK)
# ============================================

def busqueda_hibrida(termino: str, catalogo: Dict, stocks: List) -> pd.DataFrame:
    """
    Busca en CATÁLOGO (precios) y si no encuentra, busca en STOCK
    """
    if not termino or len(termino) < 2:
        return pd.DataFrame()
    
    # Primero buscar en catálogo
    resultados_catalogo = busqueda_unificada(termino, catalogo)
    
    if not resultados_catalogo.empty:
        return resultados_catalogo
    
    # Si no hay resultados en catálogo, buscar en STOCK
    termino_limpio = termino.strip().upper()
    resultados_stock = []
    
    for stock in stocks:
        df = stock['df']
        hoja = stock['hoja']
        col_sku = stock['col_sku']
        
        # Buscar en SKU
        mask_sku = df[col_sku].astype(str).str.contains(termino, case=False, na=False)
        
        # Buscar en columnas de descripción
        mask_desc = pd.Series([False] * len(df))
        columnas_desc = []
        for col in df.columns:
            col_upper = str(col).upper()
            if any(p in col_upper for p in ['DESC', 'PRODUCTO', 'NOMBRE', 'GOODS', 'ARTICULO']):
                columnas_desc.append(col)
                mask_desc = mask_desc | df[col].astype(str).str.contains(termino, case=False, na=False)
        
        mask = mask_sku | mask_desc
        
        for _, row in df[mask].iterrows():
            sku = str(row[col_sku]).strip().upper()
            
            # Obtener descripción del stock
            descripcion = ""
            for col in columnas_desc:
                desc_val = str(row[col])
                if desc_val and desc_val != 'nan' and len(desc_val) > len(descripcion):
                    descripcion = desc_val[:150]
            
            if not descripcion:
                descripcion = f"SKU: {sku}"
            
            resultados_stock.append({
                'sku': sku,
                'descripcion': descripcion,
                'fuente': f'STOCK ({hoja})',
                'tiene_precio': False,
                'stock_info': buscar_stock_para_sku(sku, stocks),
                'hoja': hoja
            })
    
    # Eliminar duplicados por SKU
    vistos = set()
    resultados_stock_unicos = []
    for r in resultados_stock:
        if r['sku'] not in vistos:
            vistos.add(r['sku'])
            resultados_stock_unicos.append(r)
    
    if resultados_stock_unicos:
        df_resultados = pd.DataFrame(resultados_stock_unicos)
        df_resultados['_score'] = 50  # Puntaje base
        df_resultados['_match_tipo'] = 'SOLO_EN_STOCK'
        df_resultados['_sku_display'] = df_resultados['sku']
        df_resultados['_desc_display'] = df_resultados['descripcion']
        df_resultados['_fuente'] = 'STOCK'
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
# DETECCIÓN DE INCONSISTENCIAS
# ============================================

def verificar_inconsistencia_stock_precio(sku: str, stock_info: Dict, precio: float, catalogo_nombre: str) -> Optional[str]:
    """Detecta inconsistencias entre stock y precio"""
    tiene_stock = stock_info['total'] > 0
    tiene_precio = precio > 0
    
    if tiene_stock and not tiene_precio:
        marcas_conocidas = ['HONOR', 'HUAWEI', 'POCO', 'REDMI', 'XIAOMI', 'UGREEN', 'BLACKVIEW', 'INNOS']
        marca_detectada = "Desconocida"
        for marca in marcas_conocidas:
            if marca in str(stock_info.get('ubicaciones', [])).upper():
                marca_detectada = marca
                break
        
        return f"""
⚠️ **INCONSISTENCIA DETECTADA: STOCK SIN PRECIO**

📦 SKU: **{sku}**
✅ Stock disponible: **{stock_info['total']}** unidades
   • YESSICA: {stock_info['yessica']}
   • APRI.004: {stock_info['apri004']}
   • APRI.001: {stock_info['apri001']}

❌ Sin precio en catálogo: **{catalogo_nombre}**

🔍 **Posibles causas:**
   1. ✏️ SKU incorrecto
   2. 📁 Producto no cargado en catálogo de precios
   3. 🏷️ Marca diferente: posible **{marca_detectada}**
   4. 🔄 Catálogo desactualizado

💡 **Recomendaciones:**
   • Buscar por descripción en lugar de SKU
   • Agregar este SKU al archivo de precios
   • Verificar SKU correcto en stock

❌ **Estado: NO COTIZABLE**
"""
    return None

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
# ASISTENTE IA V3 - COMANDOS AVANZADOS + BÚSQUEDA HÍBRIDA
# ============================================

def procesar_comando_asistente_v3(comando: str, catalogo: Dict, stocks: List, precio_key: str) -> str:
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
        import re
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
        import re
        sku_match = re.search(r'([A-Z0-9]{8,})', comando.upper())
        if sku_match:
            sku = sku_match.group(1)
            return consultar_precio_sku(sku, catalogo, precio_key)
        else:
            termino = extraer_termino_despues_de(comando, ['precio de', 'precio del', 'cual es el precio de', 'cuanto cuesta'])
            if termino:
                return consultar_precio_descripcion(termino, catalogo, precio_key)
    
    # Stock
    if any(p in comando_lower for p in ['stock de', 'stock del', 'cuanto stock hay de', 'disponibilidad de']):
        import re
        sku_match = re.search(r'([A-Z0-9]{8,})', comando.upper())
        if sku_match:
            sku = sku_match.group(1)
            return consultar_stock_sku(sku, catalogo, stocks)
        else:
            termino = extraer_termino_despues_de(comando, ['stock de', 'stock del', 'cuanto stock hay de', 'disponibilidad de'])
            if termino:
                return consultar_stock_descripcion(termino, catalogo, stocks)
    
    # Cotización
    if any(p in comando_lower for p in ['cotizame', 'cotiza', 'agrega al carrito', 'agrega', 'pon en el carrito']):
        import re
        cant_match = re.search(r'(\d+)\s*(unidades?|uds?|pzs?)?', comando)
        sku_match = re.search(r'([A-Z0-9]{8,})', comando.upper())
        
        cantidad = int(cant_match.group(1)) if cant_match else 1
        
        if sku_match:
            sku = sku_match.group(1)
            return cotizar_sku(sku, cantidad, catalogo, stocks, precio_key)
        else:
            termino = extraer_termino_despues_de_cotizacion(comando)
            if termino:
                return cotizar_descripcion(termino, cantidad, catalogo, stocks, precio_key)
    
    # Alternativas
    if any(p in comando_lower for p in ['alternativas', 'opciones', 'similares', 'parecidos']):
        import re
        sku_match = re.search(r'([A-Z0-9]{8,})', comando.upper())
        if sku_match:
            sku = sku_match.group(1)
            return buscar_alternativas(sku, catalogo, stocks, precio_key)
        else:
            termino = extraer_termino_despues_de(comando, ['alternativas de', 'opciones para', 'similares a'])
            if termino:
                return buscar_alternativas_por_descripcion(termino, catalogo, stocks, precio_key)
    
    # Variantes
    if any(p in comando_lower for p in ['variantes de', 'versiones de', 'modelos de']):
        termino = extraer_termino_despues_de(comando, ['variantes de', 'versiones de', 'modelos de'])
        if termino:
            return buscar_variantes(termino, catalogo, stocks, precio_key)
    
    # Búsqueda general (usando búsqueda híbrida)
    if len(comando) >= 3:
        return buscar_productos_hibrido(comando, catalogo, stocks, precio_key)
    
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

def consultar_precio_sku(sku: str, catalogo: Dict, precio_key: str) -> str:
    if not catalogo:
        return "⚠️ No hay catálogo cargado."
    
    df = catalogo['df']
    col_sku = catalogo['columnas']['sku']
    mask = df[col_sku].astype(str).str.upper() == sku
    
    if mask.any():
        row = df[mask].iloc[0]
        desc = row.get(catalogo['columnas'].get('descripcion', col_sku), sku)
        
        precios = {}
        for nivel, col_precio in catalogo['precios'].items():
            precios[nivel] = corregir_numero(row[col_precio]) if col_precio in row.index else 0
        
        response = f"💰 **{sku}** - {str(desc)[:80]}\n"
        response += f"   • IR: S/ {precios.get('P. IR', 0):.2f}\n"
        response += f"   • BOX: S/ {precios.get('P. BOX', 0):.2f}\n"
        response += f"   • VIP: S/ {precios.get('P. VIP', 0):.2f}\n"
        
        if precios.get(precio_key, 0) > 0:
            response += f"\n✨ Precio {precio_key}: S/ {precios.get(precio_key, 0):.2f}"
        
        return response
    else:
        return f"❌ No encontré '{sku}' en el catálogo. ¿Verifica el SKU?"

def consultar_precio_descripcion(termino: str, catalogo: Dict, precio_key: str) -> str:
    resultados = busqueda_unificada(termino, catalogo)
    if not resultados.empty:
        response = f"🔍 Productos encontrados para '{termino}':\n\n"
        for _, row in resultados.head(3).iterrows():
            sku = row['_sku_display']
            desc = row['_desc_display']
            
            precios = {}
            for nivel, col_precio in catalogo['precios'].items():
                precios[nivel] = corregir_numero(row[col_precio]) if col_precio in row.index else 0
            
            response += f"📦 **{sku}** - {desc}\n"
            response += f"   VIP: S/ {precios.get('P. VIP', 0):.2f} | IR: S/ {precios.get('P. IR', 0):.2f}\n\n"
        
        response += f"💡 Para cotizar: 'cotiza [SKU] [cantidad]'"
        return response
    else:
        return f"❌ No encontré productos relacionados con '{termino}'"

def consultar_stock_sku(sku: str, catalogo: Dict, stocks: List) -> str:
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

def consultar_stock_descripcion(termino: str, catalogo: Dict, stocks: List) -> str:
    resultados = busqueda_unificada(termino, catalogo)
    if not resultados.empty:
        response = f"🔍 Stock de productos para '{termino}':\n\n"
        for _, row in resultados.head(3).iterrows():
            sku = row['_sku_display']
            desc = row['_desc_display']
            stock_info = buscar_stock_para_sku(sku, stocks)
            
            response += f"📦 **{sku}** - {desc}\n"
            if stock_info['total'] > 0:
                response += f"   Stock: {stock_info['total']} und"
                if stock_info['apri001'] > 0 and stock_info['yessica'] == 0 and stock_info['apri004'] == 0:
                    response += f" (solo APRI.001)"
                response += f"\n   📍 Y:{stock_info['yessica']} | A4:{stock_info['apri004']} | A1:{stock_info['apri001']}\n"
            else:
                response += f"   ❌ Sin stock\n"
            response += "\n"
        return response
    else:
        return f"❌ No encontré productos relacionados con '{termino}'"

def cotizar_sku(sku: str, cantidad: int, catalogo: Dict, stocks: List, precio_key: str) -> str:
    if not catalogo or not stocks:
        return "⚠️ Primero carga catálogo y stock en el sidebar."
    
    df = catalogo['df']
    col_sku = catalogo['columnas']['sku']
    mask = df[col_sku].astype(str).str.upper() == sku
    
    if not mask.any():
        # Verificar si existe en stock (puede ser producto sin precio)
        stock_info = buscar_stock_para_sku(sku, stocks)
        if stock_info['total'] > 0:
            return f"⚠️ **{sku} tiene stock pero NO tiene precio en catálogo.**\n\n📦 Stock: {stock_info['total']} und\n❌ No se puede cotizar sin precio.\n\n💡 Sugerencia: Agrega este SKU al archivo de precios o verifica el SKU."
        return f"❌ No encontré '{sku}' en el catálogo."
    
    row = df[mask].iloc[0]
    desc = row.get(catalogo['columnas'].get('descripcion', col_sku), sku)
    
    precio = 0
    if precio_key in catalogo['precios']:
        col_precio = catalogo['precios'][precio_key]
        precio = corregir_numero(row[col_precio])
    
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
    response += f"   • Precio: S/ {precio:.2f} c/u\n"
    response += f"   • Subtotal: S/ {precio * cant_final:,.2f}\n"
    response += f"   • {msg}\n"
    
    total_carrito = sum(item['total'] for item in st.session_state.carrito)
    response += f"\n💰 Total carrito: S/ {total_carrito:,.2f}"
    
    return response

def cotizar_descripcion(termino: str, cantidad: int, catalogo: Dict, stocks: List, precio_key: str) -> str:
    resultados = busqueda_unificada(termino, catalogo)
    if resultados.empty:
        return f"❌ No encontré productos relacionados con '{termino}'"
    
    mejor = resultados.iloc[0]
    sku = mejor['_sku_display']
    desc = mejor['_desc_display']
    
    response = f"🔍 Encontré '{sku}' para tu búsqueda:\n📝 {desc}\n\n"
    response += cotizar_sku(sku, cantidad, catalogo, stocks, precio_key)
    
    return response

def buscar_productos_hibrido(termino: str, catalogo: Dict, stocks: List, precio_key: str, limit: int = 5) -> str:
    """Búsqueda HÍBRIDA: CATÁLOGO + STOCK"""
    
    # Buscar en catálogo (con precio)
    resultados_catalogo = busqueda_unificada(termino, catalogo)
    
    # Buscar en stock (productos sin precio)
    resultados_stock = []
    termino_limpio = termino.strip().upper()
    
    for stock in stocks:
        df = stock['df']
        hoja = stock['hoja']
        col_sku = stock['col_sku']
        
        mask_sku = df[col_sku].astype(str).str.contains(termino, case=False, na=False)
        
        mask_desc = pd.Series([False] * len(df))
        for col in df.columns:
            if any(p in str(col).upper() for p in ['DESC', 'PRODUCTO', 'NOMBRE', 'GOODS']):
                mask_desc = mask_desc | df[col].astype(str).str.contains(termino, case=False, na=False)
        
        mask = mask_sku | mask_desc
        
        for _, row in df[mask].iterrows():
            sku = str(row[col_sku]).strip().upper()
            
            # Verificar si ya está en resultados de catálogo
            if not resultados_catalogo.empty and sku in resultados_catalogo['_sku_display'].values:
                continue
            
            descripcion = ""
            for col in df.columns:
                if any(p in str(col).upper() for p in ['DESC', 'PRODUCTO', 'NOMBRE', 'GOODS']):
                    desc_val = str(row[col])
                    if desc_val and desc_val != 'nan' and len(desc_val) > len(descripcion):
                        descripcion = desc_val[:150]
            
            if not descripcion:
                descripcion = f"SKU: {sku}"
            
            resultados_stock.append({
                'sku': sku,
                'descripcion': descripcion,
                'fuente': hoja,
                'stock_info': buscar_stock_para_sku(sku, stocks)
            })
    
    # Eliminar duplicados en stock
    vistos = set()
    resultados_stock_unicos = []
    for r in resultados_stock:
        if r['sku'] not in vistos:
            vistos.add(r['sku'])
            resultados_stock_unicos.append(r)
    
    # Construir respuesta
    if resultados_catalogo.empty and not resultados_stock_unicos:
        return f"❌ No encontré resultados para '{termino}'"
    
    response = f"🔍 **Resultados para '{termino}':**\n\n"
    
    # Resultados de catálogo (con precio)
    if not resultados_catalogo.empty:
        response += f"📋 **Productos en catálogo (con precio):**\n"
        for i, (_, row) in enumerate(resultados_catalogo.head(limit).iterrows()):
            sku = row['_sku_display']
            desc = row['_desc_display']
            score = row['_score']
            
            stock_info = buscar_stock_para_sku(sku, stocks)
            precios = {}
            for nivel, col_precio in catalogo['precios'].items():
                precios[nivel] = corregir_numero(row[col_precio]) if col_precio in row.index else 0
            
            stock_status = f"📦 Stock: {stock_info['total']} und" if stock_info['total'] > 0 else "❌ Sin stock"
            
            response += f"\n{i+1}. **{sku}**\n"
            response += f"   📝 {desc[:80]}\n"
            response += f"   🎯 Coincidencia: {score:.0f}%\n"
            response += f"   {stock_status}\n"
            response += f"   💰 Precios: VIP: S/ {precios.get('P. VIP', 0):.2f} | IR: S/ {precios.get('P. IR', 0):.2f}\n"
        
        response += f"\n---\n"
    
    # Resultados solo en stock (sin precio)
    if resultados_stock_unicos:
        response += f"⚠️ **Productos SOLO EN STOCK (sin precio en catálogo):**\n"
        for i, r in enumerate(resultados_stock_unicos[:limit]):
            stock_info = r['stock_info']
            response += f"\n{i+1}. **{r['sku']}**\n"
            response += f"   📝 {r['descripcion'][:80]}\n"
            response += f"   📦 Stock: {stock_info['total']} und (fuente: {r['fuente']})\n"
            response += f"   ❌ **SIN PRECIO EN CATÁLOGO**\n"
            response += f"   💡 Verificar SKU o agregar precio\n"
    
    response += f"\n💡 **Comandos útiles:**\n"
    response += f"   • 'cotiza [SKU] [cantidad]' - Agregar al carrito\n"
    response += f"   • 'precio de [SKU]' - Ver precios\n"
    response += f"   • 'stock de [SKU]' - Ver stock detallado"
    
    return response

def buscar_alternativas(sku: str, catalogo: Dict, stocks: List, precio_key: str) -> str:
    if not catalogo:
        return "⚠️ No hay catálogo cargado."
    
    df = catalogo['df']
    col_sku = catalogo['columnas']['sku']
    mask = df[col_sku].astype(str).str.upper() == sku
    
    if not mask.any():
        return f"❌ No encontré '{sku}' en el catálogo."
    
    row = df[mask].iloc[0]
    desc_original = str(row.get(catalogo['columnas'].get('descripcion', col_sku), sku)).upper()
    
    palabras_clave = desc_original.split()[:4]
    termino_busqueda = ' '.join(palabras_clave)
    
    resultados = busqueda_unificada(termino_busqueda, catalogo)
    resultados = resultados[resultados['_sku_display'] != sku]
    
    if resultados.empty:
        return f"❌ No encontré alternativas para {sku}"
    
    response = f"🔄 **Alternativas para {sku}**\n📝 Original: {desc_original[:80]}\n\n"
    
    for i, (_, row) in enumerate(resultados.head(5).iterrows()):
        alt_sku = row['_sku_display']
        alt_desc = row['_desc_display']
        score = row['_score']
        
        stock_info = buscar_stock_para_sku(alt_sku, stocks)
        precios = {}
        for nivel, col_precio in catalogo['precios'].items():
            precios[nivel] = corregir_numero(row[col_precio]) if col_precio in row.index else 0
        
        stock_status = f"Stock: {stock_info['total']} und" if stock_info['total'] > 0 else "Sin stock"
        
        response += f"{i+1}. **{alt_sku}**\n"
        response += f"   📝 {alt_desc[:60]}\n"
        response += f"   🎯 {score:.0f}% coincidencia | {stock_status}\n"
        response += f"   💰 {precio_key}: S/ {precios.get(precio_key, 0):.2f}\n\n"
    
    response += f"💡 Para cotizar: 'cotiza [SKU] [cantidad]'"
    return response

def buscar_alternativas_por_descripcion(termino: str, catalogo: Dict, stocks: List, precio_key: str) -> str:
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
        
        stock_status = f"Stock: {stock_info['total']} und" if stock_info['total'] > 0 else "Sin stock"
        
        response += f"{i+1}. **{sku}**\n"
        response += f"   📝 {desc[:70]}\n"
        response += f"   🎯 {score:.0f}% | {stock_status} | {precio_key}: S/ {precios.get(precio_key, 0):.2f}\n\n"
    
    return response

def buscar_variantes(termino: str, catalogo: Dict, stocks: List, precio_key: str) -> str:
    resultados = busqueda_unificada(termino, catalogo)
    if resultados.empty:
        return f"❌ No encontré variantes para '{termino}'"
    
    response = f"🎨 **Variantes encontradas:**\n\n"
    
    for i, (_, row) in enumerate(resultados.head(8).iterrows()):
        sku = row['_sku_display']
        desc = row['_desc_display']
        
        stock_info = buscar_stock_para_sku(sku, stocks)
        precios = {}
        for nivel, col_precio in catalogo['precios'].items():
            precios[nivel] = corregir_numero(row[col_precio]) if col_precio in row.index else 0
        
        stock_status = f"📦 {stock_info['total']} und" if stock_info['total'] > 0 else "❌ Sin stock"
        
        response += f"{i+1}. **{sku}**\n"
        response += f"   📝 {desc[:70]}\n"
        response += f"   {stock_status} | 💰 {precio_key}: S/ {precios.get(precio_key, 0):.2f}\n\n"
    
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

🔄 **Alternativas:**
   • `alternativas de RN0200065BK8` - Productos similares
   • `opciones para auriculares` - Búsqueda de alternativas

🎨 **Variantes:**
   • `variantes de Redmi Buds 8` - Todos los colores/modelos

🔍 **Búsqueda general:**
   • `powerbank` - Busca en catálogo + stock
   • `cargador 67W` - Búsqueda híbrida

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
if 'catalogo_actual' not in st.session_state:
    st.session_state.catalogo_actual = None
if 'stocks' not in st.session_state:
    st.session_state.stocks = []
if 'carrito' not in st.session_state:
    st.session_state.carrito = []
if 'ugreen_catalogo' not in st.session_state:
    st.session_state.ugreen_catalogo = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ============================================
# LOGIN (SIMPLIFICADO)
# ============================================

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='color:#1a1a2e;'>QTC Smart Sales Pro v5.1</h2>", unsafe_allow_html=True)
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
    st.markdown("# Smart Sales Pro v5.1")
    st.caption("🔍 Búsqueda HÍBRIDA: Catálogo + Stock | 📦 Stock seguro: YESSICA/APRI.004 -2 | ⚠️ APRI.001: 15%")
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
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("### 🎯 Configuración")
    
    marca = st.radio("📌 Marca", ["XIAOMI", "UGREEN"], index=0)
    st.session_state.modo = marca
    
    st.markdown("---")
    precio_opcion = st.radio("💰 Nivel de precio", ["P. VIP", "P. BOX", "P. IR"], index=0)
    st.session_state.precio_key = precio_opcion
    
    st.markdown("---")
    st.markdown("### 📂 Archivos")
    
    if marca == "XIAOMI":
        st.markdown("**📚 Catálogo de precios**")
        archivo_cat = st.file_uploader(
            "Excel o CSV",
            type=['xlsx', 'xls', 'csv'],
            accept_multiple_files=False,
            key="cat_v5"
        )
        if archivo_cat:
            catalogo = cargar_catalogo_inteligente(archivo_cat)
            if catalogo:
                st.session_state.catalogo_actual = catalogo
                st.success(f"✅ {archivo_cat.name}")
    
    if marca == "UGREEN":
        st.markdown("**📚 Catálogo UGREEN**")
        archivo_ugreen = st.file_uploader(
            "Excel UGREEN",
            type=['xlsx', 'xls'],
            accept_multiple_files=False,
            key="ugreen_v5"
        )
        if archivo_ugreen:
            ugreen_cat = cargar_ugreen_catalogo(archivo_ugreen)
            if ugreen_cat:
                st.session_state.ugreen_catalogo = ugreen_cat
                st.success(f"✅ UGREEN: {archivo_ugreen.name}")
    
    st.markdown("**📦 Reportes de stock**")
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

# ========== TAB 1: BÚSQUEDA INTELIGENTE ==========
with tab1:
    if st.session_state.modo == "XIAOMI" and st.session_state.catalogo_actual and st.session_state.stocks:
        st.markdown("### 🔍 Buscar productos")
        st.caption("🔎 Busca por SKU, descripción, código de barras o modelo")
        
        col_f1, col_f2 = st.columns([3, 1])
        with col_f1:
            termino = st.text_input("", placeholder="Ej: powerbank | RN0200065BK8 | Redmi Buds 8 | 6971234567890")
        with col_f2:
            solo_stock = st.checkbox("📦 Solo con stock", value=False)
        
        if termino and len(termino) >= 2:
            with st.spinner("🔍 Buscando en catálogo y stock..."):
                # Usar búsqueda híbrida
                resultados_catalogo = busqueda_unificada(termino, st.session_state.catalogo_actual)
                
                if not resultados_catalogo.empty:
                    resultados_mostrar = resultados_catalogo
                    if solo_stock:
                        mascara = []
                        for _, row in resultados_catalogo.iterrows():
                            sku = row['_sku_display']
                            stock_info = buscar_stock_para_sku(sku, st.session_state.stocks)
                            mascara.append(stock_info['total'] > 0)
                        resultados_mostrar = resultados_catalogo[mascara]
                    
                    st.success(f"✅ {len(resultados_mostrar)} resultados encontrados")
                    
                    for idx, row in resultados_mostrar.iterrows():
                        sku = row['_sku_display']
                        desc = row['_desc_display']
                        score = row['_score']
                        match_tipo = row['_match_tipo']
                        
                        stock_info = buscar_stock_para_sku(sku, st.session_state.stocks)
                        
                        # Verificar inconsistencia
                        precios = {}
                        for nivel, col_precio in st.session_state.catalogo_actual['precios'].items():
                            precios[nivel] = corregir_numero(row[col_precio]) if col_precio in row.index else 0
                        
                        inconsistencia = verificar_inconsistencia_stock_precio(
                            sku, stock_info, precios.get(st.session_state.precio_key, 0), 
                            st.session_state.catalogo_actual.get('nombre', 'desconocido')
                        )
                        
                        if inconsistencia:
                            st.warning(inconsistencia)
                            continue
                        
                        badge_stock = construir_badge_stock(
                            stock_info['yessica'], stock_info['apri004'], stock_info['apri001'],
                            stock_info.get('detalle_apri001', []), stock_info.get('ubicaciones', [])
                        )
                        
                        border_color = "#4CAF50" if score >= 80 else "#FF9800" if score >= 50 else "#2196F3"
                        
                        st.markdown(f"""
                        <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid {border_color};">
                            <div style="display:flex;justify-content:space-between;">
                                <div><strong style="font-size:1.1rem;">📦 {sku}</strong>
                                <span style="background:{border_color};color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;margin-left:8px;">{score:.0f}%</span></div>
                                <span style="font-size:0.7rem;color:#666;">{match_tipo}</span>
                            </div>
                            <div style="margin-top:8px;"><strong>📝 {desc[:120]}</strong></div>
                            <div style="margin-top:8px;">{badge_stock}</div>
                            <div style="margin-top:8px;">
                                💰 Precios: IR: S/ {precios.get('P. IR', 0):.2f} | 
                                BOX: S/ {precios.get('P. BOX', 0):.2f} | 
                                VIP: S/ {precios.get('P. VIP', 0):.2f}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if stock_info['total'] > 0 and precios.get(st.session_state.precio_key, 0) > 0:
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                cantidad_input = st.number_input("Cantidad", min_value=1, value=1, step=1, key=f"busq_{sku}_{idx}")
                            with col2:
                                if st.button(f"➕ Agregar", key=f"add_{sku}_{idx}"):
                                    solo_apri001 = stock_info['apri001'] > 0 and stock_info['yessica'] == 0 and stock_info['apri004'] == 0
                                    if solo_apri001:
                                        cant_final, msg, _ = calcular_cantidad_apri001_only(cantidad_input, stock_info['apri001'])
                                    else:
                                        cant_final, msg, _ = calcular_cantidad_total_segura(cantidad_input, stock_info)
                                    
                                    if cant_final > 0:
                                        item = {
                                            'sku': sku,
                                            'descripcion': desc,
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
                                        st.success(f"✅ Agregado {cant_final}x {sku}")
                                        st.rerun()
                                    else:
                                        st.warning(f"❌ {msg}")
                        elif precios.get(st.session_state.precio_key, 0) == 0 and stock_info['total'] > 0:
                            st.warning(f"⚠️ {sku} tiene stock pero NO tiene precio en nivel {st.session_state.precio_key}")
                        elif stock_info['total'] == 0:
                            st.info(f"📦 {sku} sin stock disponible")
                        
                        st.divider()
                else:
                    # Buscar solo en stock
                    st.info("🔍 No se encontraron resultados en catálogo. Buscando solo en stock...")
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
                                resultados_stock.append({'sku': sku, 'stock_info': stock_info})
                    
                    if resultados_stock:
                        st.warning(f"⚠️ {len(resultados_stock)} productos encontrados SOLO EN STOCK (sin precio en catálogo)")
                        for r in resultados_stock[:10]:
                            st.markdown(f"""
                            <div style="background:#fff3e0;border-radius:12px;padding:0.75rem;margin-bottom:0.5rem;border-left:4px solid #ff9800;">
                                <strong>📦 {r['sku']}</strong><br>
                                📦 Stock: {r['stock_info']['total']} und<br>
                                ❌ <strong>SIN PRECIO EN CATÁLOGO</strong><br>
                                💡 Verificar SKU o agregar al catálogo
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No se encontraron resultados en catálogo ni en stock.")
    else:
        st.warning("Carga catálogo y stock en el sidebar para comenzar.")

# ========== TAB 2: MODO MASIVO ==========
with tab2:
    st.markdown("### 📦 Ingresa productos en formato masivo")
    st.caption("Formato: `SKU:CANTIDAD` (uno por línea)")
    
    texto_bulk = st.text_area("", height=200, placeholder="RN0200065BK8:50\nCN0200059BK8:30")
    
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
                resultados = []
                for pedido in pedidos:
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
                            msg = "Sin precio o sin stock" if precio == 0 else "Sin stock"
                        
                        resultados.append({
                            'sku': pedido['sku'],
                            'desc': str(desc)[:80],
                            'solicitado': pedido['cantidad'],
                            'cotizable': cant_final,
                            'precio': precio,
                            'estado': msg,
                            'stock_info': stock_info
                        })
                    else:
                        resultados.append({
                            'sku': pedido['sku'],
                            'desc': 'No encontrado',
                            'solicitado': pedido['cantidad'],
                            'cotizable': 0,
                            'precio': 0,
                            'estado': '❌ SKU no encontrado',
                            'stock_info': {'total': 0}
                        })
                
                st.success(f"✅ Procesados {len(pedidos)} productos")
                
                # Resumen
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
                                'ubicaciones': r['stock_info'].get('ubicaciones', [])
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
                    color = "#4CAF50" if r['cotizable'] > 0 else "#f44336"
                    st.markdown(f"""
                    <div style="background:white;border-radius:12px;padding:0.75rem;margin-bottom:0.5rem;border-left:4px solid {color};">
                        <strong>{r['sku']}</strong> - {r['desc']}<br>
                        📦 Solicitado: {r['solicitado']} → Cotizable: {r['cotizable']}<br>
                        {badge}<br>
                        <span style="font-size:0.8rem;">{r['estado']}</span>
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

# ========== TAB 4: ASISTENTE ==========
with tab4:
    st.markdown("### 💬 Asistente QTC")
    st.caption("🤖 Pregúntame sobre productos, stock o cotizaciones")
    st.caption("📋 Ej: 'powerbank' | 'cotiza RN0200065BK8 50' | 'stock de Redmi Buds' | 'alternativas'")
    
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
        
        if st.session_state.modo == "XIAOMI" and st.session_state.catalogo_actual:
            response = procesar_comando_asistente_v3(
                user_input, 
                st.session_state.catalogo_actual, 
                st.session_state.stocks, 
                st.session_state.precio_key
            )
        else:
            response = "⚠️ Primero carga un catálogo y stock en el sidebar."
        
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
        "cotiza RN0200065BK8 50", "alternativas de Redmi Buds", "ver carrito", "ayuda"
    ]
    cols = st.columns(4)
    for i, sug in enumerate(sugerencias[:4]):
        with cols[i]:
            if st.button(sug, key=f"sug_{i}"):
                st.session_state.chat_history.append({'role': 'user', 'content': sug})
                if st.session_state.modo == "XIAOMI" and st.session_state.catalogo_actual:
                    response = procesar_comando_asistente_v3(sug, st.session_state.catalogo_actual, st.session_state.stocks, st.session_state.precio_key)
                else:
                    response = "⚠️ Primero carga catálogo y stock"
                st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                st.rerun()
    
    cols2 = st.columns(3)
    for i, sug in enumerate(sugerencias[4:7]):
        with cols2[i]:
            if st.button(sug, key=f"sug2_{i}"):
                st.session_state.chat_history.append({'role': 'user', 'content': sug})
                if st.session_state.modo == "XIAOMI" and st.session_state.catalogo_actual:
                    response = procesar_comando_asistente_v3(sug, st.session_state.catalogo_actual, st.session_state.stocks, st.session_state.precio_key)
                else:
                    response = "⚠️ Primero carga catálogo y stock"
                st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                st.rerun()

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown(f"""
<div class="footer">
    ⚡ QTC Smart Sales Pro v5.1 | Modo: {st.session_state.modo} | 
    Stock: YESSICA/APRI.004 -2 | APRI.001: 15% máx 100 | 
    🔍 Búsqueda híbrida: Catálogo + Stock | 
    {datetime.now().strftime("%Y-%m-%d %H:%M")}
</div>
""", unsafe_allow_html=True)
