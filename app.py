
# app.py - QTC Smart Sales Pro v3.0
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
    /* Fondo principal */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* Sidebar */
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
    
    /* Cards de resultados */
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
    
    /* Forzar texto negro en cards */
    .result-card, .result-card * {
        color: #1a1a2e !important;
    }
    
    .result-card strong, 
    .result-card span,
    .result-card div {
        color: #1a1a2e !important;
    }
    
    /* Badges de stock */
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
        background: #FFC107;
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
    
    /* Contador de SKU */
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
    
    /* Login card */
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
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 1rem;
        color: #888;
        font-size: 0.7rem;
        border-top: 1px solid #333;
        margin-top: 2rem;
    }
    
    /* Alternativas card */
    .alternativas-card {
        background: #FFF8E1;
        border-radius: 12px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-left: 4px solid #FF9800;
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
    posibles = ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO', 'CODIGO', 'Número de artículo', 'NÚMERO DE ARTÍCULO']
    for col in df.columns:
        col_upper = str(col).upper()
        for posible in posibles:
            if posible.upper() in col_upper:
                return col
    return df.columns[0]

def detectar_columna_descripcion(df: pd.DataFrame) -> str:
    posibles = ['DESC', 'DESCRIPCION', 'NOMBRE', 'PRODUCTO', 'GOODS', 'NOMBRE PRODUCTO', 'Descripción del artículo']
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
    """Calcula el porcentaje de similitud entre dos textos."""
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

def buscar_alternativas_por_descripcion(sku_buscado: str, descripcion: str, catalogos: List[Dict], 
                                         stocks: List[Dict], precio_key: str, umbral_minimo: float = 65.0) -> List[Dict]:
    """Busca productos alternativos con descripción similar."""
    alternativas = []
    sku_buscado_limpio = sku_buscado.strip().upper()
    
    if not descripcion or descripcion == f"SKU: {sku_buscado}":
        return alternativas
    
    for cat in catalogos:
        df = cat['df']
        
        for _, row in df.iterrows():
            sku_alternativo = str(row[cat['col_sku']]).strip().upper()
            
            if sku_alternativo == sku_buscado_limpio:
                continue
            
            desc_alternativa = ""
            if cat['col_desc']:
                desc_alternativa = str(row[cat['col_desc']])[:200]
            
            similitud = calcular_similitud(descripcion, desc_alternativa)
            
            if similitud >= umbral_minimo:
                prod_alternativo = buscar_producto(sku_alternativo, catalogos, stocks, precio_key, buscar_alternativas=False)
                
                if prod_alternativo['tiene_stock']:
                    alternativas.append({
                        **prod_alternativo,
                        'similitud': similitud,
                        'descripcion_match': desc_alternativa
                    })
    
    vistos = set()
    alternativas_unicas = []
    for alt in alternativas:
        if alt['sku'] not in vistos:
            vistos.add(alt['sku'])
            alternativas_unicas.append(alt)
    
    alternativas_unicas.sort(key=lambda x: (-x['similitud'], -x['stock_total']))
    return alternativas_unicas[:8]

def buscar_producto(sku: str, catalogos: List[Dict], stocks: List[Dict], precio_key: str, buscar_alternativas: bool = True) -> Dict:
    """Busca producto por SKU. Si no tiene stock, busca alternativas por descripción."""
    sku_limpio = sku.strip().upper()
    
    precio = 0.0
    descripcion = ""
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
    
    if not descripcion:
        descripcion = f"SKU: {sku}"
    
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
    
    stock_total = stock_yessica + stock_apri004 + stock_apri001
    
    resultado = {
        'sku': sku,
        'descripcion': descripcion,
        'precio': precio,
        'stock_yessica': stock_yessica,
        'stock_apri004': stock_apri004,
        'stock_apri001': stock_apri001,
        'stock_total': stock_total,
        'tiene_stock': stock_total > 0,
        'tiene_precio': precio > 0,
        'usa_apri001': stock_apri001 > 0 and stock_yessica == 0 and stock_apri004 == 0,
        'alternativas': []
    }
    
    if not resultado['tiene_stock'] and buscar_alternativas and descripcion and descripcion != f"SKU: {sku}":
        resultado['alternativas'] = buscar_alternativas_por_descripcion(
            sku, descripcion, catalogos, stocks, precio_key, umbral_minimo=65.0
        )
    
    return resultado

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
        
        col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
        with col_logo2:
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
        st.image("logo.png", width="60px")
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
        placeholder="Ejemplo:\nRN9401276NA8:100\nCN0200047BK8:100\nCN0200053NA8:10"
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

# ========== TAB 2: BÚSQUEDA INTELIGENTE MEJORADA ==========
with tab2:
    st.markdown("### 🔍 Buscar productos por SKU o descripción")
    st.caption("Escribe parte del nombre, modelo o SKU del producto")
    
    busqueda = st.text_input("", placeholder="Ej: 'cargador 33w', 'Type-C earphones', 'RN9401276NA8'")
    
    if busqueda and len(busqueda) >= 2 and st.session_state.catalogos and st.session_state.stocks:
        with st.spinner("🔍 Buscando en catálogos..."):
            resultados_busqueda = []
            skus_vistos = set()
            
            for cat in st.session_state.catalogos:
                df = cat['df']
                
                # Búsqueda por SKU
                mask_sku = df[cat['col_sku']].astype(str).str.contains(busqueda, case=False, na=False)
                
                # Búsqueda por descripción
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
            
            if resultados_busqueda:
                st.success(f"✅ {len(resultados_busqueda)} productos encontrados")
                
                for prod in resultados_busqueda:
                    badge_stock = construir_badge_stock(prod['stock_yessica'], prod['stock_apri004'], prod['stock_apri001'])
                    
                    # Determinar estado
                    if prod['tiene_stock'] and prod['tiene_precio']:
                        estado_principal = "✅ CON STOCK"
                        color_estado = "#4CAF50"
                        mensaje_estado = "Disponible para cotizar"
                    elif prod['tiene_stock'] and not prod['tiene_precio']:
                        estado_principal = "⚠️ STOCK DISPONIBLE - SIN PRECIO"
                        color_estado = "#ff9800"
                        mensaje_estado = "Tiene stock pero no tiene precio en catálogo"
                    elif not prod['tiene_stock'] and prod['tiene_precio']:
                        estado_principal = "❌ SIN STOCK"
                        color_estado = "#f44336"
                        mensaje_estado = "No hay stock disponible"
                    else:
                        estado_principal = "❌ SIN STOCK Y SIN PRECIO"
                        color_estado = "#9e9e9e"
                        mensaje_estado = "Producto no disponible"
                    
                    st.markdown(f"""
                    <div class="result-card">
                        <div>
                            <strong>📦 {prod['sku']}</strong>
                            <span style="background: {color_estado}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; margin-left: 8px;">
                                {estado_principal}
                            </span>
                            <br>
                            <span style="font-size: 0.85rem;">{prod['descripcion']}</span>
                            <br>
                            <span style="font-size: 0.7rem; color: #666;">{mensaje_estado}</span>
                        </div>
                        <div style="margin-top: 8px;">
                            💰 Precio {st.session_state.precio_key}: <strong>S/ {prod['precio']:,.2f}</strong> | 
                            📦 Stock total: <strong>{prod['stock_total']}</strong>
                        </div>
                        <div style="margin-top: 8px;">
                            {badge_stock}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # ===== SI TIENE STOCK Y PRECIO: Mostrar botón para agregar =====
                    if prod['tiene_stock'] and prod['tiene_precio']:
                        col_cant, col_btn = st.columns([1, 2])
                        with col_cant:
                            cantidad = st.number_input(
                                "Cantidad",
                                min_value=1,
                                max_value=prod['stock_total'],
                                value=min(1, prod['stock_total']),
                                step=1,
                                key=f"stock_{prod['sku']}"
                            )
                        with col_btn:
                            if st.button(f"➕ Agregar a cotización", key=f"add_stock_{prod['sku']}"):
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
                    
                    # ===== SI NO TIENE STOCK: Mostrar ALTERNATIVAS =====
                    elif not prod['tiene_stock'] and prod.get('alternativas') and len(prod['alternativas']) > 0:
                        st.markdown("""
                        <div style="background: #FFF8E1; border-radius: 12px; padding: 0.75rem; margin: 0.5rem 0; border-left: 4px solid #FF9800;">
                            <strong style="color: #E65100;">💡 PRODUCTOS ALTERNATIVOS CON STOCK</strong>
                            <span style="font-size: 0.7rem; margin-left: 8px;">(basado en descripción similar)</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        for alt in prod['alternativas']:
                            badge_alt = construir_badge_stock(alt['stock_yessica'], alt['stock_apri004'], alt['stock_apri001'])
                            
                            alerta_alt = ""
                            if alt['usa_apri001']:
                                alerta_alt = '<div style="background: #FCE4EC; padding: 0.25rem 0.5rem; border-radius: 8px; margin-top: 0.25rem; font-size: 0.7rem;">⚠️ Stock en APRI.001 - Solicitar transferencia</div>'
                            
                            st.markdown(f"""
                            <div style="background: white; border-radius: 10px; padding: 0.75rem; margin: 0.5rem 0; border: 1px solid #FFE0B2;">
                                <div>
                                    <strong>📦 {alt['sku']}</strong>
                                    <span style="background: #E8F5E9; color: #2E7D32; padding: 2px 6px; border-radius: 10px; font-size: 0.6rem; margin-left: 6px;">
                                        {alt['similitud']:.0f}% coincidencia
                                    </span>
                                    <br>
                                    <span style="font-size: 0.75rem;">{alt['descripcion'][:80]}</span>
                                </div>
                                <div style="margin-top: 6px;">
                                    💰 Precio: S/ {alt['precio']:,.2f} | 📦 Stock: {alt['stock_total']}
                                </div>
                                <div style="margin-top: 6px;">
                                    {badge_alt}
                                </div>
                                {alerta_alt}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            col_cant_alt, col_btn_alt = st.columns([1, 2])
                            with col_cant_alt:
                                cant_alt = st.number_input(
                                    f"Cantidad",
                                    min_value=1,
                                    max_value=alt['stock_total'],
                                    value=min(1, alt['stock_total']),
                                    step=1,
                                    key=f"alt_{alt['sku']}_{prod['sku']}"
                                )
                            with col_btn_alt:
                                if st.button(f"➕ Agregar alternativa", key=f"add_alt_{alt['sku']}_{prod['sku']}"):
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
                                    st.success(f"✅ Agregado {cant_alt}x {alt['sku']} (alternativa)")
                                    st.rerun()
                    
                    elif prod['tiene_stock'] and not prod['tiene_precio']:
                        st.warning(f"⚠️ Este producto tiene {prod['stock_total']} unidades en stock pero no tiene precio en los catálogos cargados.")
                    
                    st.divider()
            else:
                st.info("No se encontraron productos. Prueba con otra palabra o SKU.")

# ========== TAB 3: CARRITO ==========
with tab3:
    st.markdown("### 🛒 Cotización actual")
    
    if not st.session_state.carrito:
        st.info("No hay productos en el carrito. Agrega desde las pestañas anteriores.")
    else:
        for idx, item in enumerate(st.session_state.carrito):
            col1, col2, col3, col4, col5, col6 = st.columns([2, 3, 1, 1, 1, 0.5])
            
            with col1:
                st.write(f"**{item['sku']}**")
            with col2:
                st.write(item['descripcion'][:50])
            with col3:
                nueva_cant = st.number_input(
                    "Cant",
                    min_value=0,
                    max_value=item['stock_yessica'] + item['stock_apri004'] + item['stock_apri001'],
                    value=item['cantidad'],
                    step=1,
                    key=f"edit_{idx}_{item['sku']}",
                    label_visibility="collapsed"
                )
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
                if st.button("🗑️", key=f"del_{idx}_{item['sku']}"):
                    st.session_state.carrito.pop(idx)
                    st.rerun()
            
            badge = construir_badge_stock(item['stock_yessica'], item['stock_apri004'], item['stock_apri001'])
            st.markdown(f'<div style="margin-bottom: 0.5rem;">{badge}</div>', unsafe_allow_html=True)
            st.divider()
        
        total_general = sum(item['total'] for item in st.session_state.carrito)
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #e94560 0%, #c73e54 100%); 
                    border-radius: 12px; padding: 1rem; margin: 1rem 0; text-align: center;">
            <span style="color: white; font-size: 1.5rem; font-weight: bold;">
                TOTAL: S/ {total_general:,.2f}
            </span>
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
                    items_export = [{
                        'sku': item['sku'],
                        'descripcion': item['descripcion'],
                        'cantidad': item['cantidad'],
                        'precio': item['precio'],
                        'total': item['total']
                    } for item in st.session_state.carrito]
                    
                    excel = generar_excel(items_export, cliente, ruc)
                    st.download_button(
                        "💾 Descargar",
                        data=excel,
                        file_name=f"Cotizacion_{cliente}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        use_container_width=True
                    )
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
st.markdown('<div class="footer">⚡ QTC Smart Sales Pro | Sistema Profesional de Cotización</div>', unsafe_allow_html=True)
