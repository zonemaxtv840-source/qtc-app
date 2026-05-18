# app.py - QTC Smart Sales Pro v4.4
# Con soporte para XIAOMI, UGREEN y OTRAS MARCAS
# MODIFICADO: Lógica de stock APRI.004/YESSICA (Disponible/Cantidad) + APRI.001 (solo Disponible)
# MODIFICADO: Stock seguro = stock_disponible - 2 para YESSICA/APRI.004
# MODIFICADO: APRI.001 = 15% del stock (máx 100, stock mínimo 20, pedido mínimo 5)
# MODIFICADO: Corregida duplicación de stock

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
      /* ========== FONDO DE PÁGINA - AZUL MIRAMAR VIVO ========== */
    .stApp {
        background: linear-gradient(135deg, #0d47a1 0%, #1565c0 50%, #1e88e5 100%);
    }
    
    /* ========== TARJETAS GLASSMORPHISM ========== */
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
    
    [data-testid="stSidebar"] .stRadio > div {
        background: rgba(0,0,0,0.2);
        border-radius: 10px;
        padding: 8px;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.2);
        color: white;
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.3);
        border-color: rgba(255,255,255,0.5);
    }
    
    /* ========== TEXTOS GENERALES ========== */
    .stMarkdown, .stText, .stNumberInput label, .stSelectbox label, 
    .stRadio label, .stTextInput label, .stTextArea label {
        color: #ffffff !important;
    }
    
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #ffffff !important;
    }
    
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
    
    .badge-yessica { background: #4CAF50; color: white !important; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    .badge-apri004 { background: #FF9800; color: white !important; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    .badge-apri001 { background: #f44336; color: white !important; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    .badge-warning { background: #ff9800; color: white !important; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; }
    .badge-ugreen { background: #00BCD4; color: white !important; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    
    .footer {
        text-align: center;
        padding: 1rem;
        color: rgba(255,255,255,0.7) !important;
        font-size: 0.7rem;
        border-top: 1px solid rgba(255,255,255,0.2);
        margin-top: 2rem;
    }
    
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
    
    div[style*="border-radius:16px"][style*="margin-bottom:1rem"] {
        background: #ffffff !important;
    }
    
    .badge-yessica, .badge-apri004, .badge-apri001, .badge-warning, .badge-ugreen,
    .badge-yessica *, .badge-apri004 *, .badge-apri001 *, .badge-warning *, .badge-ugreen * {
        color: white !important;
    }
    
    div[style*="background:#FCE4EC"] * {
        color: #c62828 !important;
    }
    
    div[style*="border-radius:16px"] div[style*="margin-top"] *,
    div[style*="border-radius:16px"] div[style*="display:flex"] *,
    div[style*="border-radius:16px"] div[style*="justify-content"] * {
        color: #1a1a2e !important;
    }
    
    div[style*="border-radius:16px"] strong,
    div[style*="border-radius:16px"] b,
    div[style*="border-radius:16px"] code {
        color: #1a1a2e !important;
    }
    
    div[style*="border-radius:16px"] span[style*="background"] {
        color: white !important;
    }
    
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

# ============================================
# FUNCIÓN CORREGIDA: LECTURA DE STOCK (SIN DUPLICACIÓN)
# ============================================

def buscar_stock_para_sku(sku: str, stocks: List[Dict]) -> Dict:
    """
    Lee stock según reglas ESPECÍFICAS por tipo de hoja:
    - YESSICA: columna "Disponible" o "Cantidad"
    - APRI.004: columna "Disponible" o "Cantidad"  
    - APRI.001: SOLO columna "Disponible" (NO "En stock", NO "Cantidad")
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
        hoja_upper = hoja_nombre.upper()
        
        df_sku = df[stock['col_sku']].astype(str).str.strip().str.upper()
        mask = df_sku == sku_limpio
        
        if not mask.any():
            continue
        
        # ========== LÓGICA SEGÚN TIPO DE HOJA ==========
        
        # YESSICA: solo 'Disponible' o 'Cantidad'
        if 'YESSICA' in hoja_upper:
            col_cant = None
            for col in df.columns:
                col_upper = str(col).upper()
                if 'DISPONIBLE' in col_upper or 'CANTIDAD' in col_upper:
                    col_cant = col
                    break
            
            if col_cant and stock_yessica == 0:
                row = df[mask].iloc[0]
                cantidad = int(corregir_numero(row[col_cant]))
                stock_yessica = cantidad
                ubicaciones.append({'hoja': hoja_nombre, 'columna': col_cant, 'cantidad': cantidad})
        
        # APRI.004: solo 'Disponible' o 'Cantidad'
        elif 'APRI.004' in hoja_upper:
            col_cant = None
            for col in df.columns:
                col_upper = str(col).upper()
                if 'DISPONIBLE' in col_upper or 'CANTIDAD' in col_upper:
                    col_cant = col
                    break
            
            if col_cant and stock_apri004 == 0:
                row = df[mask].iloc[0]
                cantidad = int(corregir_numero(row[col_cant]))
                stock_apri004 = cantidad
                ubicaciones.append({'hoja': hoja_nombre, 'columna': col_cant, 'cantidad': cantidad})
        
        # APRI.001: SOLAMENTE columna 'DISPONIBLE' (NO 'STOCK', NO 'CANTIDAD')
        elif 'APRI.001' in hoja_upper:
            col_cant = None
            for col in df.columns:
                col_upper = str(col).upper()
                if 'DISPONIBLE' in col_upper:
                    col_cant = col
                    break
            
            if col_cant:
                if stock_apri001 == 0:
                    row = df[mask].iloc[0]
                    cantidad = int(corregir_numero(row[col_cant]))
                    stock_apri001 = cantidad
                    
                    detalle = {'cantidad': cantidad, 'hoja': hoja_nombre, 'columna_usada': col_cant}
                    for col in df.columns:
                        col_upper = str(col).upper()
                        if 'OBS' in col_upper or 'DETALLE' in col_upper or 'NOTA' in col_upper:
                            detalle['observacion'] = str(row[col])[:150]
                            break
                    detalle_apri001.append(detalle)
                    ubicaciones.append({'hoja': hoja_nombre, 'columna': col_cant, 'cantidad': cantidad})
            else:
                # Solo warning si REALMENTE no existe columna Disponible
                st.warning(f"⚠️ APRI.001 para SKU {sku} en hoja {hoja_nombre} no tiene columna 'Disponible'")
    
    return {
        'yessica': stock_yessica,
        'apri004': stock_apri004,
        'apri001': stock_apri001,
        'detalle_apri001': detalle_apri001,
        'total': stock_yessica + stock_apri004 + stock_apri001,
        'ubicaciones': ubicaciones
    }

# ============================================
# NUEVA FUNCIÓN: STOCK SEGURO COMBINADO (YESSICA/APRI.004 + APRI.001)
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
    
    # ========== CASO 1: Stock inmediato suficiente ==========
    if cantidad_solicitada <= stock_inmediato_seguro:
        return cantidad_solicitada, f"✅ OK - Stock inmediato (YESSICA/APRI.004): {cantidad_solicitada} unidades", detalle
    
    # ========== CASO 2: Stock inmediato insuficiente ==========
    restante = cantidad_solicitada - stock_inmediato_seguro
    
    # Regla APRI.001: Stock mínimo 20
    if stock_apri001 < 20:
        if stock_inmediato_seguro > 0:
            return stock_inmediato_seguro, f"⚠️ Stock inmediato insuficiente. Solo {stock_inmediato_seguro} unidades (APRI.001: {stock_apri001} < 20)", detalle
        else:
            return 0, f"❌ Sin stock disponible (YESSICA/APRI.004: {stock_inmediato}, APRI.001: {stock_apri001} < 20)", detalle
    
    # Regla APRI.001: Pedido mínimo 5 para justificar transferencia
    if restante < 5:
        if stock_inmediato_seguro > 0:
            return stock_inmediato_seguro, f"⚠️ Pedido restante muy pequeño ({restante} < 5). No se justifica transferencia. Solo {stock_inmediato_seguro} unidades", detalle
        else:
            return 0, f"❌ Pedido restante muy pequeño ({restante} < 5) y sin stock inmediato", detalle
    
    # Calcular máximo permitido de APRI.001 (15%, tope 100)
    max_apri001 = min(int(stock_apri001 * 0.15), 100)
    
    if max_apri001 < 5:
        return stock_inmediato_seguro, f"⚠️ APRI.001 con stock insuficiente para transferencia. Máximo: {max_apri001} unidades. Solo stock inmediato: {stock_inmediato_seguro}", detalle
    
    # Verificar si APRI.001 puede cubrir el restante
    if restante <= max_apri001:
        total_final = stock_inmediato_seguro + restante
        return total_final, f"✅ OK - Stock inmediato: {stock_inmediato_seguro} + APRI.001: {restante} (15% de {stock_apri001}) = {total_final} unidades", detalle
    else:
        if stock_inmediato_seguro > 0:
            return stock_inmediato_seguro, f"⚠️ APRI.001 no puede cubrir. Máximo: {max_apri001} unidades (15%). Solo stock inmediato: {stock_inmediato_seguro}", detalle
        else:
            return 0, f"❌ No se puede cotizar. APRI.001 máximo: {max_apri001} unidades, pero se necesitan {restante}", detalle

# ============================================
# FUNCIÓN PARA CASO SOLO APRI.001
# ============================================

def calcular_cantidad_apri001_only(cantidad_solicitada: int, stock_apri001: int) -> Tuple[int, str, Dict]:
    """
    Calcula cantidad cotizable cuando SOLO hay stock en APRI.001
    Reglas: stock mínimo 20, pedido mínimo 5, máximo 15% (tope 100)
    """
    
    detalle = {'stock_apri001': stock_apri001}
    
    if stock_apri001 < 20:
        return 0, f"❌ Stock APRI.001 insuficiente ({stock_apri001} < 20). No se puede cotizar desde transferencia", detalle
    
    if cantidad_solicitada < 5:
        return 0, f"❌ Pedido muy pequeño ({cantidad_solicitada} < 5). No se justifica transferencia desde APRI.001", detalle
    
    max_apri001 = min(int(stock_apri001 * 0.15), 100)
    
    if max_apri001 < 5:
        return 0, f"❌ Stock APRI.001 muy bajo para transferencia. 15% = {max_apri001} unidades (<5)", detalle
    
    if cantidad_solicitada > max_apri001:
        return 0, f"❌ Pedido excede límite de APRI.001. Máximo permitido: {max_apri001} unidades (15% de {stock_apri001}, tope 100)", detalle
    
    return cantidad_solicitada, f"✅ OK - APRI.001: {cantidad_solicitada}/{max_apri001} unidades permitidas (15% de {stock_apri001})", detalle

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

def cargar_ugreen_catalogo(archivo) -> Optional[Dict]:
    """Carga específica para archivo UGREEN con columnas Mayor/Caja/Vip"""
    df = cargar_archivo(archivo)
    if df is None:
        return None
    
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

def construir_badge_stock(stock_yessica, stock_apri004, stock_apri001, detalle_apri001=None, ubicaciones=None):
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
                badge_text = f'🔴 APRI.001: {cantidad} (Disponible)'
                if detalle_apri001 and len(detalle_apri001) > 0:
                    for det in detalle_apri001:
                        if det.get('observacion'):
                            badge_text += f' | 📝 {det["observacion"][:50]}'
                            break
                badges.append(f'<span class="badge-apri001">{badge_text} ⚠️</span>')
    else:
        if stock_yessica > 0:
            badges.append(f'<span class="badge-yessica">🟢 YESSICA: {stock_yessica}</span>')
        if stock_apri004 > 0:
            badges.append(f'<span class="badge-apri004">🟡 APRI.004: {stock_apri004}</span>')
        if stock_apri001 > 0:
            badge_text = f'🔴 APRI.001: {stock_apri001} (Disponible)'
            if detalle_apri001 and len(detalle_apri001) > 0:
                for det in detalle_apri001:
                    if det.get('observacion'):
                        badge_text += f' | 📝 {det["observacion"][:50]}'
                        break
            badges.append(f'<span class="badge-apri001">{badge_text} ⚠️</span>')
    
    if not badges:
        return '<span class="badge-warning">❌ Sin stock</span>'
    return ' '.join(badges)

# ============================================
# FUNCIÓN PRINCIPAL BUSCAR PRODUCTO
# ============================================

def buscar_producto(sku: str, catalogos: List[Dict], stocks: List[Dict], precio_key: str) -> Dict:
    """Busca producto por SKU para XIAOMI."""
    sku_limpio = sku.strip().upper()
    
    # PASO 1: BUSCAR STOCK (con nueva lógica sin duplicación)
    stock_info = buscar_stock_para_sku(sku_limpio, stocks)
    
    # PASO 2: BUSCAR DESCRIPCIÓN
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
    
    # PASO 3: SI TIENE STOCK PERO NO PRECIO → BUSCAR SKU EQUIVALENTE
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
    
    # PASO 4: BUSCAR ALTERNATIVAS
    alternativas = []
    if precio == 0 and stock_info['total'] > 0 and descripcion and descripcion != f"SKU: {sku}":
        alternativas = encontrar_alternativas_mismo_producto(
            sku, descripcion, catalogos, stocks, precio_key, umbral=70.0
        )
    
    # Determinar si solo tiene APRI.001
    tiene_apri001_only = stock_info['apri001'] > 0 and stock_info['yessica'] == 0 and stock_info['apri004'] == 0
    
    return {
        'sku': sku,
        'descripcion': descripcion,
        'precio': precio,
        'stock_yessica': stock_info['yessica'],
        'stock_apri004': stock_info['apri004'],
        'stock_apri001': stock_info['apri001'],
        'detalle_apri001': stock_info.get('detalle_apri001', []),
        'stock_total': stock_info['total'],
        'ubicaciones': stock_info.get('ubicaciones', []),
        'tiene_stock': stock_info['total'] > 0,
        'tiene_precio': precio > 0,
        'usa_apri001_only': tiene_apri001_only,
        'tiene_stock_inmediato': (stock_info['yessica'] + stock_info['apri004']) > 0,
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

def buscar_ugreen_producto(busqueda: str, ugreen_catalogo: Dict) -> Optional[Dict]:
    """Busca producto en catálogo UGREEN por SKU o descripción"""
    if not ugreen_catalogo:
        return None
    
    df = ugreen_catalogo['df']
    col_sku = ugreen_catalogo['col_sku']
    col_desc = ugreen_catalogo['col_desc']
    col_stock = ugreen_catalogo.get('col_stock')
    
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
        
        precio_mayor = corregir_numero(row.get('Mayor', 0))
        precio_caja = corregir_numero(row.get('Caja', 0))
        precio_vip = corregir_numero(row.get('Vip', 0))
        precio_pvp = corregir_numero(row.get('PVP', 0))
        
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
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
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
            ws.cell(row=row_idx, column=2, value=item['descripcion']).border = border
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
# LOGIN PREMIUM
# ============================================

if not st.session_state.auth:
    # CSS exclusivo para pantalla de login
    st.markdown("""
    <style>
        /* Fondo degradado premium */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%) !important;
        }
        
        /* Ocultar elementos no deseados en login */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Tarjeta de login glassmorphism */
        .login-premium {
            background: rgba(255, 255, 255, 0.07);
            backdrop-filter: blur(12px);
            border-radius: 32px;
            padding: 2.5rem 2rem;
            box-shadow: 0 25px 45px -12px rgba(0, 0, 0, 0.5);
            text-align: center;
            max-width: 420px;
            margin: 0 auto;
            border: 1px solid rgba(255, 255, 255, 0.15);
            transition: transform 0.3s ease;
        }
        
        .login-premium:hover {
            transform: translateY(-5px);
        }
        
        .login-premium h1 {
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #f0f9ff, #38bdf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            letter-spacing: -0.5px;
        }
        
        .login-premium .subtitle {
            color: #94a3b8;
            margin-bottom: 2rem;
            font-size: 0.85rem;
            font-weight: 400;
        }
        
        /* Inputs elegantes */
        .login-premium .stTextInput > div > div > input {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 16px;
            padding: 0.75rem 1rem;
            color: #f1f5f9;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }
        
        .login-premium .stTextInput > div > div > input:focus {
            border-color: #38bdf8;
            box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
            outline: none;
        }
        
        .login-premium .stTextInput > div > div > input::placeholder {
            color: #64748b;
        }
        
        /* Botón principal */
        .login-premium .stButton > button {
            background: linear-gradient(90deg, #0ea5e9, #3b82f6);
            color: white;
            border: none;
            border-radius: 40px;
            padding: 0.6rem 1.5rem;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s ease;
            margin-top: 0.5rem;
        }
        
        .login-premium .stButton > button:hover {
            transform: scale(1.02);
            box-shadow: 0 8px 20px rgba(14, 165, 233, 0.4);
            background: linear-gradient(90deg, #0284c7, #2563eb);
        }
        
        /* Botón secundario (invitado) */
        .login-premium .stButton > button:has(+ button) {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .login-premium .stButton > button:has(+ button):hover {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.02);
            box-shadow: none;
        }
        
        /* Separador */
        .login-premium .divider {
            display: flex;
            align-items: center;
            text-align: center;
            margin: 1.5rem 0;
            color: #64748b;
            font-size: 0.75rem;
        }
        
        .login-premium .divider::before,
        .login-premium .divider::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .login-premium .divider::before {
            margin-right: 0.75rem;
        }
        
        .login-premium .divider::after {
            margin-left: 0.75rem;
        }
        
        /* Footer login */
        .login-premium .login-footer {
            margin-top: 1.5rem;
            font-size: 0.7rem;
            color: #475569;
        }
        
        /* Logo placeholder */
        .logo-circle {
            width: 70px;
            height: 70px;
            background: linear-gradient(135deg, #0ea5e9, #3b82f6);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem auto;
            box-shadow: 0 8px 20px rgba(14, 165, 233, 0.3);
        }
        
        .logo-circle span {
            font-size: 2rem;
            font-weight: 700;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Centrar el login en la página
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-premium">
            <div class="logo-circle">
                <span>QTC</span>
            </div>
            <h1>Smart Sales Pro</h1>
            <div class="subtitle">Plataforma profesional de cotizaciones</div>
        """, unsafe_allow_html=True)
        
        # Inputs de login
        user = st.text_input("", placeholder="📧 Usuario", key="login_user")
        pw = st.text_input("", placeholder="🔒 Contraseña", type="password", key="login_pass")
        
        # Botones
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🚀 Ingresar", use_container_width=True, key="login_btn"):
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
        
        with col_btn2:
            if st.button("👤 Invitado", use_container_width=True, key="guest_btn"):
                st.session_state.auth = True
                st.session_state.user_role = "INVITADO"
                st.session_state.user_name = "Invitado"
                st.rerun()
        
        st.markdown("""
            <div class="divider">Acceso autorizado</div>
            <div class="login-footer">
                QTC Smart Sales Pro © 2026
            </div>
        </div>
        """, unsafe_allow_html=True)
    
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
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("### 🎯 Configuración")
    
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
    
    st.markdown("**📦 Reportes de stock**")
    st.caption("📌 YESSICA/APRI.004: lee 'Disponible' o 'Cantidad' | 📌 APRI.001: solo 'Disponible'")
    st.caption("🔒 Stock seguro: YESSICA/APRI.004 = stock - 2 | APRI.001 = 15% del stock (máx 100)")
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

# ========== TAB 1: MODO MASIVO (MODIFICADO CON FALLBACK POR DESCRIPCIÓN) ==========
with tab1:
    st.markdown("### 📦 Ingresa productos en formato masivo")
    st.caption(f"🔍 Modo: **{st.session_state.modo}** | Formato: `SKU:CANTIDAD` (uno por línea)")
    st.caption("🔒 **Reglas de stock:** YESSICA/APRI.004 = stock - 2 | APRI.001 = 15% del stock (máx 100, min 20)")
    
    texto_bulk = st.text_area(
        "",
        height=200,
        placeholder="Ejemplo:\nRN9401276NA8:100\nCN0200047BK8:100\nRN0200065BK8:50\nCN9406882NA8:25"
    )
    
    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        if st.button("🚀 Procesar lista", type="primary", use_container_width=True):
            if texto_bulk and st.session_state.modo == "XIAOMI" and st.session_state.catalogos and st.session_state.stocks:
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
                    with st.spinner("Procesando XIAOMI con nueva lógica de stock..."):
                        resultados_procesados = []
                        encontrados = 0
                        con_precio = 0
                        con_stock = 0
                        
                        for pedido in pedidos:
                            prod = buscar_producto(pedido['sku'], st.session_state.catalogos, st.session_state.stocks, st.session_state.precio_key)
                            
                            # ========== NUEVA LÓGICA: FALLBACK POR DESCRIPCIÓN ==========
                            # Si tiene stock pero no tiene precio, buscar por descripción
                            sku_usado = prod['sku']
                            precio_usado = prod['precio']
                            descripcion_usada = prod['descripcion']
                            
                            if prod['tiene_stock'] and not prod['tiene_precio']:
                                # Buscar por descripción en catálogos (usando la descripción del stock)
                                descripcion_stock = prod['descripcion']
                                if descripcion_stock and descripcion_stock != f"SKU: {pedido['sku']}":
                                    mejor_match = None
                                    mejor_similitud = 70.0
                                    
                                    for cat in st.session_state.catalogos:
                                        df_cat = cat['df']
                                        if not cat['col_desc']:
                                            continue
                                        
                                        for _, row in df_cat.iterrows():
                                            desc_catalogo = str(row[cat['col_desc']])[:200]
                                            similitud = calcular_similitud(descripcion_stock, desc_catalogo)
                                            
                                            if similitud >= mejor_similitud:
                                                mejor_similitud = similitud
                                                sku_match = str(row[cat['col_sku']]).strip().upper()
                                                
                                                if sku_match == pedido['sku']:
                                                    continue
                                                
                                                precio_match = 0.0
                                                if st.session_state.precio_key in cat['precios']:
                                                    col_precio = cat['precios'][st.session_state.precio_key]
                                                    precio_match = corregir_numero(row[col_precio])
                                                
                                                if precio_match > 0:
                                                    mejor_match = {
                                                        'sku': sku_match,
                                                        'descripcion': desc_catalogo,
                                                        'precio': precio_match,
                                                        'similitud': similitud
                                                    }
                                    
                                    if mejor_match:
                                        sku_usado = mejor_match['sku']
                                        precio_usado = mejor_match['precio']
                                        descripcion_usada = mejor_match['descripcion']
                                        prod['precio'] = precio_usado
                                        prod['tiene_precio'] = True
                                        st.session_state[f"fallback_{pedido['sku']}"] = mejor_match
                            
                            # También verificar si ya venía con sku_equivalente del buscar_producto
                            if prod['tiene_stock'] and not prod['tiene_precio'] and prod.get('sku_equivalente'):
                                # Buscar precio del SKU equivalente
                                for cat in st.session_state.catalogos:
                                    df_cat = cat['df']
                                    df_sku = df_cat[cat['col_sku']].astype(str).str.strip().str.upper()
                                    mask = df_sku == prod['sku_equivalente']
                                    if mask.any():
                                        row = df_cat[mask].iloc[0]
                                        if st.session_state.precio_key in cat['precios']:
                                            col_precio = cat['precios'][st.session_state.precio_key]
                                            precio_eq = corregir_numero(row[col_precio])
                                            if precio_eq > 0:
                                                sku_usado = prod['sku_equivalente']
                                                precio_usado = precio_eq
                                                prod['precio'] = precio_usado
                                                prod['tiene_precio'] = True
                                                if cat['col_desc']:
                                                    descripcion_usada = str(row[cat['col_desc']])[:200]
                                                break
                            
                            if prod['tiene_precio']:
                                encontrados += 1
                                con_precio += 1
                            
                            if prod['tiene_stock']:
                                con_stock += 1
                            
                            # APLICAR NUEVA LÓGICA DE STOCK SEGURO
                            if prod['tiene_precio'] and prod['tiene_stock']:
                                if prod.get('usa_apri001_only', False):
                                    cantidad_final, mensaje, _ = calcular_cantidad_apri001_only(pedido['cantidad'], prod['stock_apri001'])
                                    cantidad_cotizar = cantidad_final
                                    estado = mensaje
                                else:
                                    cantidad_final, mensaje, _ = calcular_cantidad_total_segura(
                                        pedido['cantidad'],
                                        {
                                            'yessica': prod['stock_yessica'],
                                            'apri004': prod['stock_apri004'],
                                            'apri001': prod['stock_apri001']
                                        }
                                    )
                                    cantidad_cotizar = cantidad_final
                                    estado = mensaje
                                    
                                    # Si se usó SKU alternativo, agregar nota
                                    if sku_usado != prod['sku'] and cantidad_cotizar > 0:
                                        estado = f"⚠️ SKU original sin precio, usando {sku_usado} | {mensaje}"
                            elif not prod['tiene_precio'] and prod['tiene_stock']:
                                cantidad_cotizar = 0
                                estado = "⚠️ Stock disponible - SIN PRECIO (No se encontró SKU alternativo)"
                            elif not prod['tiene_precio']:
                                cantidad_cotizar = 0
                                estado = "❌ Sin precio"
                            else:
                                cantidad_cotizar = 0
                                estado = "❌ Sin stock"
                            
                            resultados_procesados.append({
                                **prod,
                                'sku_usado': sku_usado,
                                'precio_usado': precio_usado,
                                'descripcion_usada': descripcion_usada,
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
                        <div style="background:rgba(0,0,0,0.3);border-radius:12px;padding:1rem;margin-bottom:1rem;">
                            <div style="display:flex;justify-content:space-around;flex-wrap:wrap;">
                                <div><span>📋 Ingresados:</span> <strong>{total_ingresados}</strong></div>
                                <div style="color:#4CAF50;"><span>✅ Con precio:</span> <strong>{total_encontrados}</strong></div>
                                <div><span>📦 Con stock:</span> <strong>{total_con_stock}</strong></div>
                                <div style="color:#f44336;"><span>❌ Sin precio:</span> <strong>{total_sin_precio}</strong></div>
                                <div style="color:#f44336;"><span>🚫 Sin stock:</span> <strong>{total_sin_stock}</strong></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.success(f"✅ Procesados {len(pedidos)} productos en modo XIAOMI")
                else:
                    st.warning("No se encontraron productos válidos")
                    
            elif texto_bulk and st.session_state.modo == "UGREEN" and st.session_state.ugreen_catalogo:
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
                    with st.spinner("Procesando UGREEN con búsqueda por descripción y stock APRI.001..."):
                        resultados_procesados = []
                        
                        for pedido in pedidos:
                            # BUSCAR POR SKU EXACTO EN CATÁLOGO UGREEN
                            resultados_ugreen = buscar_ugreen_producto(pedido['sku'], st.session_state.ugreen_catalogo)
                            
                            sku_usado = pedido['sku']
                            descripcion_usada = f"SKU: {pedido['sku']}"
                            precio_usado = 0.0
                            stock_ugreen = 0
                            encontrado = False
                            
                            if resultados_ugreen and len(resultados_ugreen) > 0:
                                prod = resultados_ugreen[0]
                                sku_usado = prod['sku']
                                descripcion_usada = prod['descripcion']
                                precio_usado = prod['precios'].get(st.session_state.precio_key, 0)
                                stock_ugreen = prod['stock']
                                encontrado = True
                            
                            # ========== NUEVA LÓGICA: BUSCAR STOCK EN APRI.001 ==========
                            # Buscar stock del SKU en APRI.001 (independientemente del catálogo)
                            stock_apri001 = 0
                            detalle_apri001 = []
                            ubicaciones = []
                            
                            if st.session_state.stocks:
                                for stock_file in st.session_state.stocks:
                                    df_stock = stock_file['df']
                                    hoja_nombre = stock_file.get('hoja', '')
                                    if 'APRI.001' in hoja_nombre.upper():
                                        col_sku_stock = stock_file['col_sku']
                                        df_sku = df_stock[col_sku_stock].astype(str).str.strip().str.upper()
                                        mask = df_sku == pedido['sku']
                                        if mask.any():
                                            for col in df_stock.columns:
                                                col_upper = str(col).upper()
                                                if 'DISPONIBLE' in col_upper:
                                                    stock_apri001 = int(corregir_numero(df_stock[mask].iloc[0][col]))
                                                    ubicaciones.append({'hoja': hoja_nombre, 'columna': col, 'cantidad': stock_apri001})
                                                    break
                            
                            # Si no se encontró por SKU exacto, buscar por descripción en catálogo UGREEN
                            if not encontrado and stock_apri001 > 0:
                                # Buscar por coincidencia de descripción en catálogo UGREEN
                                mejor_match_desc = None
                                mejor_similitud = 70.0
                                
                                df_ugreen = st.session_state.ugreen_catalogo['df']
                                col_sku_ugreen = st.session_state.ugreen_catalogo['col_sku']
                                col_desc_ugreen = st.session_state.ugreen_catalogo['col_desc']
                                
                                # Buscar una descripción de referencia (del stock o genérica)
                                desc_buscar = f"SKU: {pedido['sku']}"
                                
                                for _, row in df_ugreen.iterrows():
                                    desc_catalogo = str(row[col_desc_ugreen])[:200] if col_desc_ugreen else ""
                                    if desc_catalogo:
                                        similitud = calcular_similitud(desc_buscar, desc_catalogo)
                                        # También buscar por partes del SKU
                                        if pedido['sku'] in desc_catalogo.upper():
                                            similitud = max(similitud, 85.0)
                                        
                                        if similitud >= mejor_similitud:
                                            mejor_similitud = similitud
                                            sku_match = str(row[col_sku_ugreen]).strip().upper()
                                            precio_match = 0.0
                                            if st.session_state.precio_key in st.session_state.ugreen_catalogo['precios']:
                                                col_precio = st.session_state.ugreen_catalogo['precios'][st.session_state.precio_key]
                                                precio_match = corregir_numero(row[col_precio])
                                            
                                            if precio_match > 0:
                                                mejor_match_desc = {
                                                    'sku': sku_match,
                                                    'descripcion': desc_catalogo,
                                                    'precio': precio_match,
                                                    'stock': corregir_numero(row.get(st.session_state.ugreen_catalogo.get('col_stock', ''), 0)) if st.session_state.ugreen_catalogo.get('col_stock') else 0,
                                                    'similitud': similitud
                                                }
                                
                                if mejor_match_desc:
                                    sku_usado = mejor_match_desc['sku']
                                    descripcion_usada = mejor_match_desc['descripcion']
                                    precio_usado = mejor_match_desc['precio']
                                    stock_ugreen = mejor_match_desc['stock']
                                    encontrado = True
                            
                            # Calcular stock total y aplicar reglas
                            stock_total = stock_ugreen + stock_apri001
                            tiene_stock = stock_total > 0
                            tiene_precio = precio_usado > 0
                            
                            # Reglas de stock seguro para UGREEN + APRI.001
                            if tiene_precio and tiene_stock:
                                # Stock seguro UGREEN (stock - 2)
                                stock_ugreen_seguro = max(0, stock_ugreen - 2)
                                
                                # Reglas APRI.001: stock mínimo 20, 15% máx 100
                                stock_apri001_disponible = 0
                                if stock_apri001 >= 20:
                                    stock_apri001_disponible = min(int(stock_apri001 * 0.15), 100)
                                
                                stock_total_seguro = stock_ugreen_seguro + stock_apri001_disponible
                                
                                if pedido['cantidad'] <= stock_total_seguro:
                                    cantidad_cotizar = pedido['cantidad']
                                    estado = f"✅ OK - UGREEN: {stock_ugreen} (seguro: {stock_ugreen_seguro}) | APRI.001: {stock_apri001} (disp: {stock_apri001_disponible})"
                                elif stock_total_seguro > 0:
                                    cantidad_cotizar = stock_total_seguro
                                    estado = f"⚠️ Stock insuficiente. Ajustado a {cantidad_cotizar} unidades (UGREEN seguro: {stock_ugreen_seguro} + APRI.001: {stock_apri001_disponible})"
                                else:
                                    cantidad_cotizar = 0
                                    estado = "❌ Stock muy bajo. No se puede cotizar"
                            elif tiene_precio and not tiene_stock:
                                cantidad_cotizar = 0
                                estado = "❌ Sin stock (UGREEN + APRI.001)"
                            elif not tiene_precio and tiene_stock:
                                cantidad_cotizar = 0
                                estado = "⚠️ Stock disponible - SIN PRECIO"
                            else:
                                cantidad_cotizar = 0
                                estado = "❌ No encontrado (SKU no existe en catálogo ni en APRI.001)"
                            
                            # Si se usó SKU alternativo por descripción, agregar nota
                            if sku_usado != pedido['sku'] and cantidad_cotizar > 0:
                                estado = f"⚠️ SKU original no encontrado, usando {sku_usado} (similitud {mejor_match_desc.get('similitud', 0):.0f}%) | {estado}"
                            
                            resultados_procesados.append({
                                'sku': sku_usado,
                                'sku_original': pedido['sku'],
                                'descripcion': descripcion_usada,
                                'precio': precio_usado,
                                'stock_ugreen': stock_ugreen,
                                'stock_apri001': stock_apri001,
                                'stock_total': stock_total,
                                'tiene_stock': tiene_stock,
                                'tiene_precio': tiene_precio,
                                'cantidad_solicitada': pedido['cantidad'],
                                'cantidad_cotizar': cantidad_cotizar,
                                'estado': estado,
                                'ubicaciones': ubicaciones,
                                'tipo': 'UGREEN'
                            })
                        
                        st.session_state.resultados_bulk = resultados_procesados
                        
                        total_ingresados = len(pedidos)
                        total_con_precio = sum(1 for r in resultados_procesados if r['tiene_precio'])
                        total_con_stock = sum(1 for r in resultados_procesados if r['tiene_stock'])
                        
                        st.markdown(f"""
                        <div style="background:rgba(0,0,0,0.3);border-radius:12px;padding:1rem;margin-bottom:1rem;">
                            <div style="display:flex;justify-content:space-around;flex-wrap:wrap;">
                                <div><span>📋 Ingresados:</span> <strong>{total_ingresados}</strong></div>
                                <div style="color:#4CAF50;"><span>✅ Con precio:</span> <strong>{total_con_precio}</strong></div>
                                <div><span>📦 Con stock:</span> <strong>{total_con_stock}</strong></div>
                            </div>
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
                            'sku': prod.get('sku_usado', prod['sku']),
                            'descripcion': prod.get('descripcion_usada', prod['descripcion']),
                            'cantidad': prod['cantidad_cotizar'],
                            'precio': prod['precio'],
                            'total': prod['precio'] * prod['cantidad_cotizar'],
                            'stock_yessica': prod.get('stock_yessica', 0),
                            'stock_apri004': prod.get('stock_apri004', 0),
                            'stock_apri001': prod.get('stock_apri001', 0),
                            'stock_ugreen': prod.get('stock_ugreen', 0),
                            'detalle_apri001': prod.get('detalle_apri001', []),
                            'ubicaciones': prod.get('ubicaciones', []),
                            'tipo': prod.get('tipo', 'XIAOMI'),
                            'sku_original': prod.get('sku_original', prod['sku'])
                        }
                        st.session_state.carrito.append(item_carrito)
                        agregados += 1
                st.success(f"✅ Agregados {agregados} productos al carrito")
                st.rerun()
            else:
                st.warning("Primero procesa una lista de productos")
    
    # Mostrar resultados bulk (igual que antes, con la información actualizada)
    if 'resultados_bulk' in st.session_state and st.session_state.resultados_bulk:
        st.markdown("---")
        st.markdown("### 📋 Productos procesados")
        
        for prod in st.session_state.resultados_bulk:
            if prod.get('tipo') == 'UGREEN':
                # Badge para UGREEN con stock APRI.001
                badges = []
                if prod.get('stock_ugreen', 0) > 0:
                    stock_ugreen_seguro = max(0, prod['stock_ugreen'] - 2)
                    badges.append(f'<span class="badge-ugreen">📦 UGREEN: {prod["stock_ugreen"]} (seguro: {stock_ugreen_seguro})</span>')
                if prod.get('stock_apri001', 0) > 0:
                    badges.append(f'<span class="badge-apri001">🔴 APRI.001: {prod["stock_apri001"]}</span>')
                if not badges:
                    badges.append('<span class="badge-warning">❌ Sin stock</span>')
                
                badge_stock = ' '.join(badges)
                
                st.markdown(f"""
                <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #00BCD4;color:#1a1a2e;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div><strong style="color:#1a1a2e;">📦 {prod.get('sku_usado', prod['sku'])}</strong> 
                        <span style="background:#00BCD4;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">UGREEN</span>
                        {f'<span style="background:#ff9800;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">Original: {prod["sku_original"]}</span>' if prod.get('sku_original') and prod['sku_original'] != prod.get('sku_usado', prod['sku']) else ''}
                        </div>
                        <div><span style="background:#2196F3;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">Solicitado: {prod['cantidad_solicitada']} → Cotizar: {prod['cantidad_cotizar']}</span></div>
                    </div>
                    <div style="margin-top:8px;"><span style="font-size:0.85rem;color:#1a1a2e;">{prod['descripcion'][:100]}</span></div>
                    <div style="margin-top:8px;color:#1a1a2e;">💰 Precio: <strong>S/ {prod['precio']:,.2f}</strong> | 📦 Stock total: <strong>{prod['stock_total']}</strong></div>
                    <div style="margin-top:8px;">{badge_stock}</div>
                    <div style="margin-top:8px;color:#1a1a2e;"><strong>📌 Estado:</strong> {prod['estado']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # XIAOMI y OTRAS MARCAS
                badge_stock = construir_badge_stock(
                    prod.get('stock_yessica', 0), 
                    prod.get('stock_apri004', 0), 
                    prod.get('stock_apri001', 0),
                    prod.get('detalle_apri001', []),
                    prod.get('ubicaciones', [])
                )
                
                sku_mostrar = prod.get('sku_usado', prod['sku'])
                sku_original_nota = f" (Original: {prod['sku']})" if prod.get('sku_usado') and prod['sku_usado'] != prod['sku'] else ""
                
                if prod.get('tiene_stock') and not prod.get('tiene_precio'):
                    st.markdown(f"""
                    <div style="background:#FFEBEE;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #f44336;color:#1a1a2e;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><span style="background:#f44336;color:white;padding:4px 12px;border-radius:20px;font-size:0.75rem;font-weight:bold;">⚠️ PROBLEMA DETECTADO - ERROR DE SKU</span></div>
                            <div><span style="background:#ff9800;color:white;padding:2px 8px;border-radius:12px;font-size:0.6rem;">Solicitado: {prod['cantidad_solicitada']}</span></div>
                        </div>
                        <div style="margin-top:12px;color:#1a1a2e;">
                            <strong>📦 SKU BUSCADO:</strong> {prod['sku']}<br>
                            <strong>📝 Descripción:</strong> {prod['descripcion']}<br>
                            <strong>📦 Stock disponible:</strong> {prod.get('stock_total', 0)} unidades<br>
                            <strong>⚠️ Estado:</strong> {prod['estado']}
                        </div>
                        <div style="margin-top:8px;">{badge_stock}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
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
                
                elif prod.get('tiene_stock') and prod.get('tiene_precio'):
                    cantidad_final = prod['cantidad_cotizar']
                    st.markdown(f"""
                    <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #4CAF50;color:#1a1a2e;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong style="color:#1a1a2e;">📦 {sku_mostrar}</strong>{sku_original_nota} <span style="background:#4CAF50;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">✅ CON STOCK Y PRECIO</span></div>
                            <div><span style="background:#2196F3;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">Cotizar: {cantidad_final}/{prod['cantidad_solicitada']}</span></div>
                        </div>
                        <div style="margin-top:8px;"><span style="font-size:0.85rem;color:#1a1a2e;">{prod.get('descripcion_usada', prod['descripcion'])}</span></div>
                        <div style="margin-top:8px;color:#1a1a2e;">💰 Precio: <strong>S/ {prod['precio_usado'] if prod.get('precio_usado') else prod['precio']:,.2f}</strong> | 📦 Stock: YESSICA:{prod.get('stock_yessica',0)} APRI.004:{prod.get('stock_apri004',0)} APRI.001:{prod.get('stock_apri001',0)}</div>
                        <div style="margin-top:8px;">{badge_stock}</div>
                        <div style="margin-top:8px;color:#1a1a2e;"><strong>📌 Estado:</strong> {prod['estado']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                elif not prod.get('tiene_stock') and prod.get('tiene_precio'):
                    st.markdown(f"""
                    <div style="background:#E3F2FD;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #2196F3;color:#1a1a2e;">
                        <div><strong style="color:#1a1a2e;">📦 {prod['sku']}</strong> <span style="background:#2196F3;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">📋 SOLO PRECIO - SIN STOCK</span></div>
                        <div style="margin-top:8px;"><span style="font-size:0.85rem;color:#1a1a2e;">{prod['descripcion']}</span></div>
                        <div style="margin-top:8px;color:#1a1a2e;">💰 Precio: <strong>S/ {prod['precio']:,.2f}</strong></div>
                        <div style="margin-top:8px;">{badge_stock}</div>
                        <div style="margin-top:8px;color:#1a1a2e;"><strong>⚠️ Estado:</strong> {prod['estado']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
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
# ========== TAB 2: BÚSQUEDA INTELIGENTE (RESUMEN) ==========
with tab2:
    st.markdown("### 🔍 Buscar productos por SKU o descripción")
    st.caption(f"🔎 Modo: **{st.session_state.modo}** | Busca por SKU exacto o descripción")
    st.caption("🔒 **Reglas:** YESSICA/APRI.004 = stock-2 | APRI.001 = 15% del stock (máx 100, min 20, pedido min 5)")
    
    busqueda = st.text_input("", placeholder="Ej: 'RN9401276NA8' o 'Xiaomi Type-C Earphones Black'")
    
    if busqueda and len(busqueda) >= 2:
        if st.session_state.modo == "XIAOMI" and st.session_state.catalogos and st.session_state.stocks:
            with st.spinner("🔍 Buscando en XIAOMI..."):
                productos_por_sku = {}
                
                # Búsqueda en catálogos y stocks (código similar al original pero usando las nuevas funciones)
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
                            existente['stock_yessica'] = stock_info['yessica']
                            existente['stock_apri004'] = stock_info['apri004']
                            existente['stock_apri001'] = stock_info['apri001']
                            existente['stock_total'] = stock_info['total']
                            existente['tiene_stock'] = stock_info['total'] > 0
                            existente['tiene_precio'] = existente['tiene_precio'] or (precio > 0)
                        else:
                            productos_por_sku[sku] = {
                                'sku': sku,
                                'descripcion': descripcion,
                                'precio': precio,
                                'stock_yessica': stock_info['yessica'],
                                'stock_apri004': stock_info['apri004'],
                                'stock_apri001': stock_info['apri001'],
                                'detalle_apri001': stock_info.get('detalle_apri001', []),
                                'ubicaciones': stock_info.get('ubicaciones', []),
                                'stock_total': stock_info['total'],
                                'tiene_stock': stock_info['total'] > 0,
                                'tiene_precio': precio > 0,
                                'usa_apri001_only': stock_info['apri001'] > 0 and stock_info['yessica'] == 0 and stock_info['apri004'] == 0
                            }
                
                if productos_por_sku:
                    st.success(f"✅ {len(productos_por_sku)} productos encontrados en XIAOMI")
                    resultados_lista = list(productos_por_sku.values())
                    resultados_lista.sort(key=lambda x: (-x['tiene_stock'], -x['tiene_precio']))
                    
                    for prod in resultados_lista:
                        badge_stock = construir_badge_stock(
                            prod['stock_yessica'], 
                            prod['stock_apri004'], 
                            prod['stock_apri001'],
                            prod.get('detalle_apri001', []),
                            prod.get('ubicaciones', [])
                        )
                        
                        st.markdown(f"""
                        <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #4CAF50;color:#1a1a2e;">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <div><strong style="font-size:1rem;">📦 {prod['sku']}</strong></div>
                            </div>
                            <div style="margin-top:12px;"><strong>📝 Descripción:</strong> {prod['descripcion']}</div>
                            <div style="margin-top:8px;"><strong>💰 Precio {st.session_state.precio_key}:</strong> <span style="font-weight:bold;">S/ {prod['precio']:,.2f}</span></div>
                            <div style="margin-top:8px;">{badge_stock}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if prod['tiene_stock'] and prod['tiene_precio']:
                            if prod.get('usa_apri001_only', False):
                                _, mensaje, _ = calcular_cantidad_apri001_only(1, prod['stock_apri001'])
                                st.info(f"📌 {mensaje}")
                            else:
                                st.info("📌 Stock inmediato disponible (YESSICA/APRI.004)")
                            
                            col_cant, col_btn = st.columns([1, 2])
                            with col_cant:
                                if prod.get('usa_apri001_only', False):
                                    max_cant = min(int(prod['stock_apri001'] * 0.15), 100)
                                    cantidad = st.number_input("Cantidad", min_value=5 if max_cant >=5 else 0, max_value=max_cant, value=min(5, max_cant) if max_cant >=5 else 0, step=1, key=f"busq_{prod['sku']}")
                                else:
                                    stock_inmediato_seguro = max(0, (prod['stock_yessica'] + prod['stock_apri004']) - 2)
                                    cantidad = st.number_input("Cantidad", min_value=1, max_value=stock_inmediato_seguro + (min(int(prod['stock_apri001'] * 0.15), 100) if prod['stock_apri001'] >=20 else 0), value=1, step=1, key=f"busq_{prod['sku']}")
                            with col_btn:
                                if st.button(f"➕ Agregar a cotización", key=f"add_busq_{prod['sku']}"):
                                    item_carrito = {
                                        'sku': prod['sku'],
                                        'descripcion': prod['descripcion'],
                                        'cantidad': cantidad,
                                        'precio': prod['precio'],
                                        'total': prod['precio'] * cantidad,
                                        'stock_yessica': prod['stock_yessica'],
                                        'stock_apri004': prod['stock_apri004'],
                                        'stock_apri001': prod['stock_apri001'],
                                        'detalle_apri001': prod.get('detalle_apri001', []),
                                        'ubicaciones': prod.get('ubicaciones', [])
                                    }
                                    st.session_state.carrito.append(item_carrito)
                                    st.success(f"✅ Agregado {cantidad}x {prod['sku']}")
                                    st.rerun()
                        
                        st.divider()
                else:
                    st.info("No se encontraron productos.")
        
        elif st.session_state.modo == "UGREEN" and st.session_state.ugreen_catalogo:
            resultados_ugreen = buscar_ugreen_producto(busqueda, st.session_state.ugreen_catalogo)
            if resultados_ugreen:
                for prod in resultados_ugreen:
                    precio_seleccionado = prod['precios'].get(st.session_state.precio_key, 0)
                    stock_seguro = max(0, prod['stock'] - 2)
                    
                    st.markdown(f"""
                    <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #00BCD4;">
                        <strong>📦 {prod['sku']}</strong> <span style="background:#00BCD4;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">UGREEN</span><br>
                        <span style="font-size:0.85rem;">{prod['descripcion'][:100]}</span><br>
                        💰 Precio {st.session_state.precio_key}: S/ {precio_seleccionado:,.2f}<br>
                        📦 Stock: {prod['stock']} (seguro: {stock_seguro})
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if prod['tiene_stock'] and precio_seleccionado > 0 and stock_seguro > 0:
                        col_cant, col_btn = st.columns([1, 2])
                        with col_cant:
                            cantidad = st.number_input("Cantidad", min_value=1, max_value=stock_seguro, value=1, step=1, key=f"ugreen_busq_{prod['sku']}")
                        with col_btn:
                            if st.button(f"➕ Agregar", key=f"add_ugreen_busq_{prod['sku']}"):
                                item_carrito = {
                                    'sku': prod['sku'],
                                    'descripcion': prod['descripcion'],
                                    'cantidad': cantidad,
                                    'precio': precio_seleccionado,
                                    'total': precio_seleccionado * cantidad,
                                    'tipo': 'UGREEN'
                                }
                                st.session_state.carrito.append(item_carrito)
                                st.success(f"✅ Agregado {cantidad}x {prod['sku']}")
                                st.rerun()
                    st.divider()
            else:
                st.info("No se encontraron productos.")
        else:
            st.warning("Carga los archivos necesarios en el sidebar.")

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
                nueva_cant = st.number_input("Cant", min_value=0, value=item['cantidad'], step=1, key=f"edit_{idx}", label_visibility="collapsed")
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
                st.markdown('<span class="badge-ugreen">📦 UGREEN</span>', unsafe_allow_html=True)
            else:
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
st.markdown(f'<div class="footer">⚡ QTC Smart Sales Pro v4.4 | Modo: {st.session_state.modo} | YESSICA/APRI.004: stock-2 | APRI.001: 15% máx 100 | {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>', unsafe_allow_html=True)
