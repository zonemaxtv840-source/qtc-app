# app.py - QTC Smart Sales Pro v5.0
# Stock XIAOMI: YESSICA → APRI.004 → APRI.001 con mensaje de transferencia
# UGREEN y OTRAS marcas: lógica estándar

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
        background: linear-gradient(135deg, #0a2e5c 0%, #0d3b6e 50%, #0f4a80 100%);
    }
    
    .stMarkdown, .stText, .stNumberInput label, .stSelectbox label, 
    .stRadio label, .stTextInput label, .stTextArea label {
        color: #ffffff !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8a35e 0%, #e87a2d 50%, #d45a1a 100%);
        border-right: 2px solid #ffcc80;
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stRadio {
        background: rgba(0,0,0,0.15);
        border-radius: 12px;
        padding: 10px;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.2);
        color: white;
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    .badge-yessica { background: #4CAF50; color: white !important; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    .badge-apri004 { background: #FF9800; color: white !important; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    .badge-apri001 { background: #f44336; color: white !important; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    .badge-warning { background: #ff9800; color: white !important; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; }
    .badge-ugreen { background: #00BCD4; color: white !important; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
    
    div[data-testid="stAlert"][data-kind="success"] {
        background: #2e7d32 !important;
        border-left: 4px solid #1b5e20 !important;
        border-radius: 12px !important;
    }
    div[data-testid="stAlert"][data-kind="success"] .stMarkdown { color: #ffffff !important; font-weight: bold; }
    
    div[data-testid="stAlert"][data-kind="warning"] {
        background: #f9a825 !important;
        border-left: 4px solid #f57f17 !important;
        border-radius: 12px !important;
    }
    div[data-testid="stAlert"][data-kind="warning"] .stMarkdown { color: #000000 !important; font-weight: bold; }
    
    div[data-testid="stAlert"][data-kind="error"] {
        background: #d32f2f !important;
        border-left: 4px solid #b71c1c !important;
        border-radius: 12px !important;
    }
    div[data-testid="stAlert"][data-kind="error"] .stMarkdown { color: #ffffff !important; font-weight: bold; }
    
    .footer {
        text-align: center;
        padding: 1rem;
        color: rgba(255,255,255,0.6) !important;
        font-size: 0.7rem;
        border-top: 1px solid rgba(255,255,255,0.15);
        margin-top: 2rem;
    }
    
    .stButton > button { transition: all 0.3s ease; border-radius: 10px; font-weight: 500; }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 6px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 8px 20px;
        color: white;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1e88e5;
        color: white !important;
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
        col_sku = df.columns[5] if len(df.columns) > 5 else df.columns[0]
    
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
    return round((jaccard * 0.7 + sequence_match * 0.3) * 100, 1)

# ============================================
# NUEVA FUNCIÓN DE STOCK XIAOMI (MEJORADA)
# ============================================

def buscar_stock_xiaomi(sku: str, stocks: List[Dict]) -> Dict:
    """Busca stock para XIAOMI: YESSICA, APRI.004, APRI.001 por separado"""
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
    
    total = stock_yessica + stock_apri004 + stock_apri001
    
    return {
        'yessica': stock_yessica,
        'apri004': stock_apri004,
        'apri001': stock_apri001,
        'total': total,
        'requiere_transferencia': stock_apri001 > 0  # Si hay stock en APRI.001, requiere mensaje
    }

def buscar_precio_xiaomi(sku: str, catalogos: List[Dict], precio_key: str) -> Tuple[float, str]:
    """Busca precio y descripción para XIAOMI"""
    sku_limpio = sku.strip().upper()
    precio = 0.0
    descripcion = f"SKU: {sku}"
    
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
    
    return precio, descripcion

def buscar_ugreen_producto(busqueda: str, ugreen_catalogo: Dict) -> Optional[List[Dict]]:
    """Busca producto en catálogo UGREEN"""
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
        
        stock = 0
        if col_stock:
            stock = int(corregir_numero(row[col_stock])) if pd.notna(row[col_stock]) else 0
        
        resultados.append({
            'sku': sku,
            'descripcion': descripcion,
            'precios': {'P. IR': precio_mayor, 'P. BOX': precio_caja, 'P. VIP': precio_vip},
            'stock': stock,
            'tiene_stock': stock > 0,
            'tiene_precio': precio_vip > 0 or precio_caja > 0 or precio_mayor > 0,
            'tipo': 'UGREEN'
        })
    
    return resultados

def generar_excel(items: List[Dict], cliente: str, ruc: str) -> bytes:
    output = io.BytesIO()
    
    data = []
    for item in items:
        data.append({
            'SKU': item['sku'],
            'DESCRIPCIÓN': item['descripcion'],
            'CANTIDAD': item['cantidad'],
            'PRECIO UNITARIO': item['precio'],
            'TOTAL': item['total']
        })
    
    df = pd.DataFrame(data)
    
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
            
            # Si el producto requiere transferencia, agregar comentario
            if item.get('requiere_transferencia', False):
                nota_cell = ws.cell(row=row_idx, column=2, value=item['descripcion'] + " ⚠️ Solicitar transferencia")
                nota_cell.font = Font(color="FF0000", bold=True)
        
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
        
        # Nota general si hay productos con transferencia
        if any(item.get('requiere_transferencia', False) for item in items):
            nota_general_row = total_row + 2
            ws.cell(row=nota_general_row, column=1, value="NOTA:").font = Font(bold=True)
            ws.cell(row=nota_general_row, column=2, value="Los productos marcados con ⚠️ requieren solicitar transferencia a logística (APRI.001)")
    
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
if 'user_role' not in st.session_state:
    st.session_state.user_role = "INVITADO"
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Invitado"

# ============================================
# LOGIN
# ============================================

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown("""
            <div style="background: rgba(255,255,255,0.95); border-radius: 28px; padding: 2.5rem; text-align: center;">
                <h1 style="color:#e94560;">QTC</h1>
                <h2 style="color:#1a1a2e;">Smart Sales Pro</h2>
                <p style="color:#666;">Sistema Profesional de Cotización</p>
            </div>
            """, unsafe_allow_html=True)
            
            user = st.text_input("👤 Usuario", placeholder="admin / kimberly / vendedor")
            pw = st.text_input("🔒 Contraseña", type="password", placeholder="...2026")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🚀 Ingresar", use_container_width=True):
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
                if st.button("👤 Modo invitado", use_container_width=True):
                    st.session_state.auth = True
                    st.session_state.user_role = "INVITADO"
                    st.session_state.user_name = "Invitado"
                    st.rerun()
    
    st.stop()

# ============================================
# HEADER
# ============================================

col1, col2, col3 = st.columns([1, 5, 2])
with col1:
    st.markdown("**QTC**")
with col2:
    st.markdown("# QTC Smart Sales Pro")
    st.caption(f"Sistema Profesional | Modo: {st.session_state.modo} | Usuario: {st.session_state.user_name}")
with col3:
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
        index=0 if st.session_state.modo == "XIAOMI" else 1
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
        st.markdown("**📚 Catálogos (XIAOMI/OTROS)**")
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
            "Excel UGREEN",
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
    archivos_stock = st.file_uploader(
        "Excel (STOCKKKK)",
        type=['xlsx', 'xls'],
        accept_multiple_files=True,
        key="stock_upload"
    )
    if archivos_stock:
        st.session_state.stocks = cargar_stock(archivos_stock, st.session_state.modo)
    
    st.markdown("---")
    
    if st.session_state.carrito:
        st.markdown("### 🛒 Carrito")
        st.metric("Productos", len(st.session_state.carrito))
        total = sum(item['total'] for item in st.session_state.carrito)
        st.metric("Total", f"S/ {total:,.2f}")
        
        if st.button("🧹 Limpiar carrito", use_container_width=True):
            st.session_state.carrito = []
            st.rerun()

# ============================================
# TABS PRINCIPALES
# ============================================

tab1, tab2, tab3 = st.tabs(["📦 MODO MASIVO", "🔍 BÚSQUEDA INTELIGENTE", "🛒 CARRITO"])

# ========== TAB 1: MODO MASIVO ==========
with tab1:
    st.markdown("### 📦 Ingresa productos en formato masivo")
    st.caption(f"Modo: **{st.session_state.modo}** | Formato: `SKU:CANTIDAD`")
    
    texto_bulk = st.text_area("", height=150, placeholder="RN9401276NA8:100\nCN0200047BK8:50")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🚀 Procesar lista", type="primary", use_container_width=True):
            if texto_bulk and st.session_state.modo == "XIAOMI" and st.session_state.catalogos and st.session_state.stocks:
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
                    with st.spinner("Procesando..."):
                        resultados = []
                        for pedido in pedidos:
                            # Buscar stock en XIAOMI
                            stock_info = buscar_stock_xiaomi(pedido['sku'], st.session_state.stocks)
                            precio, descripcion = buscar_precio_xiaomi(pedido['sku'], st.session_state.catalogos, st.session_state.precio_key)
                            
                            tiene_stock = stock_info['total'] > 0
                            tiene_precio = precio > 0
                            cantidad_cotizar = min(pedido['cantidad'], stock_info['total']) if tiene_stock and tiene_precio else 0
                            
                            if tiene_stock and tiene_precio:
                                if cantidad_cotizar < pedido['cantidad']:
                                    estado = f"⚠️ Stock insuficiente ({cantidad_cotizar}/{pedido['cantidad']})"
                                else:
                                    estado = "✅ OK"
                            elif not tiene_precio and tiene_stock:
                                estado = "⚠️ Stock disponible - SIN PRECIO"
                            elif not tiene_precio:
                                estado = "❌ Sin precio"
                            else:
                                estado = "❌ Sin stock"
                            
                            resultados.append({
                                'sku': pedido['sku'],
                                'descripcion': descripcion,
                                'precio': precio,
                                'stock_yessica': stock_info['yessica'],
                                'stock_apri004': stock_info['apri004'],
                                'stock_apri001': stock_info['apri001'],
                                'stock_total': stock_info['total'],
                                'tiene_stock': tiene_stock,
                                'tiene_precio': tiene_precio,
                                'requiere_transferencia': stock_info['requiere_transferencia'],
                                'cantidad_solicitada': pedido['cantidad'],
                                'cantidad_cotizar': cantidad_cotizar,
                                'estado': estado
                            })
                        
                        st.session_state.resultados_bulk = resultados
                        st.success(f"✅ Procesados {len(pedidos)} productos")
                else:
                    st.warning("No se encontraron productos válidos")
            
            elif texto_bulk and st.session_state.modo == "UGREEN" and st.session_state.ugreen_catalogo:
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
                    with st.spinner("Procesando UGREEN..."):
                        resultados = []
                        for pedido in pedidos:
                            prod_list = buscar_ugreen_producto(pedido['sku'], st.session_state.ugreen_catalogo)
                            if prod_list and len(prod_list) > 0:
                                prod = prod_list[0]
                                precio = prod['precios'].get(st.session_state.precio_key, 0)
                                if precio > 0 and prod['tiene_stock']:
                                    cantidad_cotizar = min(pedido['cantidad'], prod['stock'])
                                    estado = "✅ OK" if cantidad_cotizar == pedido['cantidad'] else f"⚠️ Stock insuficiente ({cantidad_cotizar}/{pedido['cantidad']})"
                                elif precio > 0 and not prod['tiene_stock']:
                                    cantidad_cotizar = 0
                                    estado = "❌ Sin stock"
                                else:
                                    cantidad_cotizar = 0
                                    estado = "❌ Sin precio"
                                
                                resultados.append({
                                    'sku': prod['sku'],
                                    'descripcion': prod['descripcion'],
                                    'precio': precio,
                                    'stock_total': prod['stock'],
                                    'tiene_stock': prod['tiene_stock'],
                                    'tiene_precio': precio > 0,
                                    'requiere_transferencia': False,
                                    'cantidad_solicitada': pedido['cantidad'],
                                    'cantidad_cotizar': cantidad_cotizar,
                                    'estado': estado,
                                    'tipo': 'UGREEN'
                                })
                            else:
                                resultados.append({
                                    'sku': pedido['sku'],
                                    'descripcion': f"SKU: {pedido['sku']}",
                                    'precio': 0,
                                    'stock_total': 0,
                                    'tiene_stock': False,
                                    'tiene_precio': False,
                                    'requiere_transferencia': False,
                                    'cantidad_solicitada': pedido['cantidad'],
                                    'cantidad_cotizar': 0,
                                    'estado': "❌ No encontrado",
                                    'tipo': 'UGREEN'
                                })
                        
                        st.session_state.resultados_bulk = resultados
                        st.success(f"✅ Procesados {len(pedidos)} productos")
            else:
                if st.session_state.modo == "XIAOMI" and not st.session_state.catalogos:
                    st.warning("Carga catálogos de XIAOMI")
                elif st.session_state.modo == "UGREEN" and not st.session_state.ugreen_catalogo:
                    st.warning("Carga catálogo de UGREEN")
                elif not st.session_state.stocks:
                    st.warning("Carga reportes de stock")
                else:
                    st.warning("Ingresa productos en el formato correcto")
    
    with col_b2:
        if st.button("📋 Agregar al carrito", use_container_width=True):
            if 'resultados_bulk' in st.session_state and st.session_state.resultados_bulk:
                agregados = 0
                for prod in st.session_state.resultados_bulk:
                    if prod['cantidad_cotizar'] > 0 and prod['tiene_precio']:
                        item = {
                            'sku': prod['sku'],
                            'descripcion': prod['descripcion'],
                            'cantidad': prod['cantidad_cotizar'],
                            'precio': prod['precio'],
                            'total': prod['precio'] * prod['cantidad_cotizar'],
                            'requiere_transferencia': prod.get('requiere_transferencia', False),
                            'tipo': prod.get('tipo', 'XIAOMI')
                        }
                        st.session_state.carrito.append(item)
                        agregados += 1
                st.success(f"✅ Agregados {agregados} productos")
                st.rerun()
            else:
                st.warning("Procesa una lista primero")
    
    # Mostrar resultados
    if 'resultados_bulk' in st.session_state and st.session_state.resultados_bulk:
        st.markdown("---")
        st.markdown("### 📋 Resultados")
        
        for prod in st.session_state.resultados_bulk:
            if prod.get('tipo') == 'UGREEN':
                badge = f'<span class="badge-ugreen">📦 Stock: {prod["stock_total"]}</span>' if prod['stock_total'] > 0 else '<span class="badge-warning">❌ Sin stock</span>'
                st.markdown(f"""
                <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #00BCD4;color:#1a1a2e;">
                    <div><strong>📦 {prod['sku']}</strong> <span style="background:#00BCD4;color:white;padding:2px 8px;border-radius:12px;">UGREEN</span></div>
                    <div style="margin-top:8px;">{prod['descripcion'][:100]}</div>
                    <div style="margin-top:8px;">💰 Precio: <strong>S/ {prod['precio']:,.2f}</strong> | 📦 Stock: {prod['stock_total']}</div>
                    <div>{badge}</div>
                    <div><strong>Estado:</strong> {prod['estado']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # XIAOMI
                badges = []
                if prod['stock_yessica'] > 0:
                    badges.append(f'<span class="badge-yessica">🟢 YESSICA: {prod["stock_yessica"]}</span>')
                if prod['stock_apri004'] > 0:
                    badges.append(f'<span class="badge-apri004">🟡 APRI.004: {prod["stock_apri004"]}</span>')
                if prod['stock_apri001'] > 0:
                    badges.append(f'<span class="badge-apri001">🔴 APRI.001: {prod["stock_apri001"]}</span>')
                badges_html = ' '.join(badges) if badges else '<span class="badge-warning">❌ Sin stock</span>'
                
                st.markdown(f"""
                <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid {'#4CAF50' if prod['tiene_stock'] and prod['tiene_precio'] else '#f44336'};color:#1a1a2e;">
                    <div><strong>📦 {prod['sku']}</strong></div>
                    <div style="margin-top:8px;">{prod['descripcion'][:100]}</div>
                    <div style="margin-top:8px;">💰 Precio: <strong>S/ {prod['precio']:,.2f}</strong></div>
                    <div style="margin-top:8px;">📦 STOCK TOTAL: <strong>{prod['stock_total']}</strong> unidades</div>
                    <div style="margin-top:8px;">{badges_html}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if prod['requiere_transferencia'] and prod['tiene_stock'] and prod['tiene_precio']:
                    st.warning("⚠️ con stock pero debes solicitar transferencia")
                
                st.markdown(f'<div><strong>Estado:</strong> {prod["estado"]}</div><br>', unsafe_allow_html=True)
            
            st.divider()
        
        if st.button("🗑️ Limpiar resultados", key="clear_bulk"):
            del st.session_state.resultados_bulk
            st.rerun()

# ========== TAB 2: BÚSQUEDA SIMPLIFICADA ==========
with tab2:
    st.markdown("### 🔍 Buscar producto")
    busqueda = st.text_input("", placeholder="SKU o descripción")
    
    if busqueda and len(busqueda) >= 2:
        if st.session_state.modo == "XIAOMI" and st.session_state.catalogos and st.session_state.stocks:
            with st.spinner("Buscando..."):
                # Buscar coincidencias por SKU en stocks
                skus_encontrados = set()
                for stock in st.session_state.stocks:
                    df = stock['df']
                    col_sku = stock['col_sku']
                    mask = df[col_sku].astype(str).str.contains(busqueda, case=False, na=False)
                    for sku in df[mask][col_sku].values:
                        skus_encontrados.add(str(sku).strip().upper())
                
                if skus_encontrados:
                    for sku in list(skus_encontrados)[:10]:
                        stock_info = buscar_stock_xiaomi(sku, st.session_state.stocks)
                        precio, descripcion = buscar_precio_xiaomi(sku, st.session_state.catalogos, st.session_state.precio_key)
                        
                        badges = []
                        if stock_info['yessica'] > 0:
                            badges.append(f'<span class="badge-yessica">🟢 YESSICA: {stock_info["yessica"]}</span>')
                        if stock_info['apri004'] > 0:
                            badges.append(f'<span class="badge-apri004">🟡 APRI.004: {stock_info["apri004"]}</span>')
                        if stock_info['apri001'] > 0:
                            badges.append(f'<span class="badge-apri001">🔴 APRI.001: {stock_info["apri001"]}</span>')
                        badges_html = ' '.join(badges) if badges else '<span class="badge-warning">❌ Sin stock</span>'
                        
                        st.markdown(f"""
                        <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid {'#4CAF50' if stock_info['total'] > 0 and precio > 0 else '#f44336'};color:#1a1a2e;">
                            <div><strong>📦 {sku}</strong></div>
                            <div style="margin-top:8px;">{descripcion}</div>
                            <div style="margin-top:8px;">💰 Precio: <strong>S/ {precio:,.2f}</strong></div>
                            <div style="margin-top:8px;">📦 STOCK TOTAL: <strong>{stock_info['total']}</strong> unidades</div>
                            <div style="margin-top:8px;">{badges_html}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if stock_info['requiere_transferencia'] and stock_info['total'] > 0 and precio > 0:
                            st.warning("⚠️ con stock pero debes solicitar transferencia")
                        
                        if precio > 0 and stock_info['total'] > 0:
                            col_cant, col_btn = st.columns([1, 2])
                            with col_cant:
                                cantidad = st.number_input("Cantidad", min_value=1, max_value=stock_info['total'], value=1, key=f"busq_{sku}")
                            with col_btn:
                                if st.button(f"➕ Agregar", key=f"add_busq_{sku}"):
                                    item = {
                                        'sku': sku,
                                        'descripcion': descripcion,
                                        'cantidad': cantidad,
                                        'precio': precio,
                                        'total': precio * cantidad,
                                        'requiere_transferencia': stock_info['requiere_transferencia'],
                                        'tipo': 'XIAOMI'
                                    }
                                    st.session_state.carrito.append(item)
                                    st.success(f"✅ Agregado {cantidad}x {sku}")
                                    st.rerun()
                        st.divider()
                else:
                    st.info("No se encontraron productos")
        
        elif st.session_state.modo == "UGREEN" and st.session_state.ugreen_catalogo:
            resultados = buscar_ugreen_producto(busqueda, st.session_state.ugreen_catalogo)
            if resultados:
                for prod in resultados[:5]:
                    badge = f'<span class="badge-ugreen">📦 Stock: {prod["stock"]}</span>' if prod['stock'] > 0 else '<span class="badge-warning">❌ Sin stock</span>'
                    st.markdown(f"""
                    <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #00BCD4;color:#1a1a2e;">
                        <div><strong>📦 {prod['sku']}</strong> <span style="background:#00BCD4;color:white;padding:2px 8px;border-radius:12px;">UGREEN</span></div>
                        <div>{prod['descripcion']}</div>
                        <div>💰 Precio {st.session_state.precio_key}: <strong>S/ {prod['precios'].get(st.session_state.precio_key, 0):,.2f}</strong></div>
                        <div>{badge}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if prod['tiene_stock'] and prod['tiene_precio']:
                        col_cant, col_btn = st.columns([1, 2])
                        with col_cant:
                            cantidad = st.number_input("Cantidad", min_value=1, max_value=prod['stock'], value=1, key=f"ug_{prod['sku']}")
                        with col_btn:
                            if st.button(f"➕ Agregar", key=f"add_ug_{prod['sku']}"):
                                item = {
                                    'sku': prod['sku'],
                                    'descripcion': prod['descripcion'],
                                    'cantidad': cantidad,
                                    'precio': prod['precios'].get(st.session_state.precio_key, 0),
                                    'total': prod['precios'].get(st.session_state.precio_key, 0) * cantidad,
                                    'requiere_transferencia': False,
                                    'tipo': 'UGREEN'
                                }
                                st.session_state.carrito.append(item)
                                st.success(f"✅ Agregado {cantidad}x {prod['sku']}")
                                st.rerun()
                    st.divider()
            else:
                st.info("No se encontraron productos")
        else:
            st.warning("Carga los archivos necesarios")

# ========== TAB 3: CARRITO ==========
with tab3:
    st.markdown("### 🛒 Cotización actual")
    
    if not st.session_state.carrito:
        st.info("No hay productos en el carrito")
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
            
            if item.get('requiere_transferencia'):
                st.warning("⚠️ con stock pero debes solicitar transferencia")
            
            st.divider()
        
        total = sum(item['total'] for item in st.session_state.carrito)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#e94560 0%,#c73e54 100%);border-radius:12px;padding:1rem;text-align:center;margin:1rem 0;">
            <span style="color:white;font-size:1.5rem;font-weight:bold;">TOTAL: S/ {total:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📋 Cliente")
        col_cli1, col_cli2 = st.columns(2)
        with col_cli1:
            cliente = st.text_input("Nombre del cliente")
        with col_cli2:
            ruc = st.text_input("RUC/DNI")
        
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            if st.button("📥 Exportar Excel", type="primary", use_container_width=True):
                if cliente:
                    items_export = [{'sku': i['sku'], 'descripcion': i['descripcion'], 'cantidad': i['cantidad'], 'precio': i['precio'], 'total': i['total'], 'requiere_transferencia': i.get('requiere_transferencia', False)} for i in st.session_state.carrito]
                    excel = generar_excel(items_export, cliente, ruc)
                    st.download_button("💾 Descargar", data=excel, file_name=f"Cotizacion_{cliente}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", use_container_width=True)
                    st.balloons()
                else:
                    st.warning("Ingresa el nombre del cliente")
        with col_exp2:
            if st.button("🧹 Limpiar todo", use_container_width=True):
                st.session_state.carrito = []
                st.rerun()

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown(f'<div class="footer">QTC Smart Sales Pro v5.0 | {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>', unsafe_allow_html=True)
