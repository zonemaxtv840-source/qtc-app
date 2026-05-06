import streamlit as st
import pandas as pd
import re, io
from datetime import datetime
from PIL import Image
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# --- CONFIGURACIÓN DE PÁGINA ---
try:
    img_logo = Image.open("logo.png")
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon=img_logo, layout="wide")
except:
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon="💼", layout="wide")

# --- ESTILOS CSS CORREGIDOS ---
st.markdown("""
    <style>
    /* Fondo general */
    .stApp {
        background-color: #F0F2F6;
    }
    
    /* Texto general en área principal (oscuro sobre fondo claro) */
    .main .block-container {
        color: #1a1a2e !important;
    }
    
    h1, h2, h3, h4, p, div, span, label {
        color: #1a1a2e !important;
    }
    
    /* Sidebar - fondo oscuro, texto blanco */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a472a 0%, #0d2818 100%);
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] div {
        color: white !important;
    }
    
    /* Botones */
    .stButton > button {
        background: #27AE60;
        color: white !important;
        border-radius: 10px;
        font-weight: 600;
    }
    .stButton > button:hover {
        background: #1E8449;
    }
    
    /* SELECTBOX - Fondo blanco, texto negro */
    .stSelectbox > div > div {
        background-color: white !important;
        color: black !important;
        border: 1px solid #27AE60 !important;
        border-radius: 8px !important;
    }
    .stSelectbox > div > div > div {
        color: black !important;
    }
    .stSelectbox label {
        color: #1a1a2e !important;
    }
    
    /* DROPDOWN MENU - Opciones desplegables */
    div[data-baseweb="select"] > div {
        background-color: white !important;
    }
    div[data-baseweb="select"] ul {
        background-color: white !important;
        border: 1px solid #ccc !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] li {
        color: black !important;
        background-color: white !important;
        padding: 8px 12px !important;
    }
    div[data-baseweb="select"] li:hover {
        background-color: #e8f5e9 !important;
    }
    div[data-baseweb="select"] li[aria-selected="true"] {
        background-color: #27AE60 !important;
        color: white !important;
    }
    
    /* FILE UPLOADER */
    .stFileUploader > div > div {
        background-color: white !important;
        border: 1px dashed #27AE60 !important;
        border-radius: 10px !important;
    }
    .stFileUploader > div > div > div {
        color: #1a1a2e !important;
    }
    .stFileUploader button {
        background-color: #27AE60 !important;
        color: white !important;
    }
    
    /* TEXT INPUT - fondo blanco, texto negro */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        color: black !important;
        background-color: white !important;
        border: 1px solid #ccc !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #27AE60 !important;
    }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        background-color: white !important;
        border-radius: 10px !important;
        padding: 4px !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #1a1a2e !important;
        background-color: #f0f0f0 !important;
        border-radius: 8px !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #27AE60 !important;
        color: white !important;
    }
    
    /* METRIC CARDS */
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #ddd;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #27AE60 !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        background-color: white !important;
        border-radius: 10px !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: white !important;
        color: #1a1a2e !important;
        border-radius: 10px !important;
    }
    
    /* Alertas */
    .stAlert {
        background-color: white !important;
        border-radius: 10px !important;
        color: #1a1a2e !important;
    }
    .stAlert > div {
        color: #1a1a2e !important;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #e8f5e9 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 💼 QTC Pro")
    st.markdown("---")
    if "cotizaciones" in st.session_state:
        st.metric("📄 Cotizaciones", st.session_state.get("cotizaciones", 0))
        st.metric("📦 Productos", st.session_state.get("total_prods", 0))

# --- LOGIN ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <h1 style="text-align: center; color: #27AE60;">💚 QTC Smart Sales</h1>
            <p style="text-align: center; color: #1a1a2e;">Sistema Profesional de Cotización</p>
        </div>
        """, unsafe_allow_html=True)
        user = st.text_input("👤 Usuario")
        pw = st.text_input("🔒 Contraseña", type="password")
        if st.button("Ingresar", use_container_width=True):
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
    for i in range(min(20, len(df))):
        fila = [str(x).upper() for x in df.iloc[i].values]
        if any(h in item for h in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO'] for item in fila):
            df.columns = [str(c).strip() for c in df.iloc[i]]
            return df.iloc[i+1:].reset_index(drop=True)
    return df

def cargar_catalogo(archivo):
    """Carga catálogo permitiendo elegir la hoja"""
    try:
        xls = pd.ExcelFile(archivo)
        hojas = xls.sheet_names
        
        hoja_seleccionada = st.sidebar.selectbox(
            f"📗 Hoja de {archivo.name}:",
            hojas,
            key=f"cat_hoja_{archivo.name}"
        )
        
        df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)
        df = limpiar_cabeceras(df)
        
        # Detectar columnas
        col_sku = None
        col_desc = None
        columnas_precio = []
        
        for c in df.columns:
            c_str = str(c).upper()
            if any(p in c_str for p in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO']):
                if col_sku is None:
                    col_sku = c
            if any(p in c_str for p in ['DESC', 'NOMBRE', 'PRODUCTO']):
                if col_desc is None:
                    col_desc = c
            if any(p in c_str for p in ['PRECIO', 'CAJA', 'VIP', 'MAYOR', 'IR', 'BOX', 'SUGERIDO']):
                columnas_precio.append(c)
        
        if col_sku is None and len(df.columns) > 0:
            col_sku = df.columns[0]
        if col_desc is None and len(df.columns) > 1:
            col_desc = df.columns[1]
        
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
    """Carga stock permitiendo elegir la hoja y detectando columnas"""
    try:
        xls = pd.ExcelFile(archivo)
        hojas = xls.sheet_names
        
        hoja_seleccionada = st.sidebar.selectbox(
            f"📦 Stock {archivo.name}:",
            hojas,
            key=f"stock_hoja_{archivo.name}"
        )
        
        df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)
        df = limpiar_cabeceras(df)
        
        # Detectar columnas
        col_sku = None
        col_stock = None
        col_comprometido = None
        col_solicitado = None
        
        for c in df.columns:
            c_str = str(c).upper()
            if any(p in c_str for p in ['SKU', 'COD', 'NUMERO', 'ARTICULO']):
                if col_sku is None:
                    col_sku = c
            if 'STOCK' in c_str or 'DISPONIBLE' in c_str or 'EN STOCK' in c_str:
                col_stock = c
            if 'COMPROMET' in c_str:
                col_comprometido = c
            if 'SOLICIT' in c_str:
                col_solicitado = c
        
        # Fallback
        if col_sku is None and len(df.columns) > 0:
            col_sku = df.columns[0]
        if col_stock is None and len(df.columns) > 1:
            col_stock = df.columns[1]
        
        return {
            'nombre': f"{archivo.name} [{hoja_seleccionada}]",
            'df': df,
            'col_sku': col_sku,
            'col_stock': col_stock,
            'col_comprometido': col_comprometido,
            'col_solicitado': col_solicitado
        }
    except Exception as e:
        st.error(f"Error en stock {archivo.name}: {str(e)}")
        return None

def buscar_producto(catalogos, sku_buscar):
    for catalogo in catalogos:
        df = catalogo['df']
        mask = df[catalogo['col_sku']].astype(str).str.contains(sku_buscar, case=False, na=False)
        if not df[mask].empty:
            row = df[mask].iloc[0]
            return {
                'encontrado': True,
                'catalogo': catalogo['nombre'],
                'sku': str(row[catalogo['col_sku']]),
                'descripcion': str(row[catalogo['col_desc']]),
                'row': row,
                'columnas_precio': catalogo['columnas_precio']
            }
    return {'encontrado': False}

def obtener_precio(row, columnas_precio, col_seleccionada):
    if col_seleccionada and col_seleccionada in columnas_precio and col_seleccionada in row.index:
        return corregir_numero(row[col_seleccionada])
    return 0.0

def obtener_stock(sku, stocks):
    stock_total = 0
    comprometido = 0
    solicitado = 0
    origen = ""
    
    for stock in stocks:
        mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku, case=False, na=False)
        if not stock['df'][mask].empty:
            row = stock['df'][mask].iloc[0]
            stock_total = int(corregir_numero(row[stock['col_stock']])) if stock['col_stock'] else 0
            if stock['col_comprometido'] and stock['col_comprometido'] in row.index:
                comprometido = int(corregir_numero(row[stock['col_comprometido']]))
            if stock['col_solicitado'] and stock['col_solicitado'] in row.index:
                solicitado = int(corregir_numero(row[stock['col_solicitado']]))
            origen = stock['nombre']
            break
    
    return stock_total, comprometido, solicitado, origen

def generar_excel_cotizacion(items, cliente, ruc):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    pd.DataFrame(items).to_excel(writer, sheet_name='Cotizacion', index=False, startrow=5)
    
    workbook = writer.book
    ws = writer.sheets['Cotizacion']
    
    fmt_header = workbook.add_format({'bg_color': '#F79646', 'bold': True, 'border': 1, 'align': 'center', 'font_color': 'white'})
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

tab_cotizacion, tab_config = st.tabs(["📦 Cotización", "⚙️ Configuración"])

# ============================================
# TAB CONFIGURACIÓN
# ============================================
with tab_config:
    st.markdown("### 📂 Carga de Archivos")
    st.info("Cada archivo te permite elegir qué hoja usar")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📚 Catálogos de Precios")
        archivos_catalogos = st.file_uploader(
            "Sube catálogos (Excel)",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            key="catalogos_upload"
        )
        
        if archivos_catalogos:
            for archivo in archivos_catalogos:
                resultado = cargar_catalogo(archivo)
                if resultado:
                    st.session_state.catalogos.append(resultado)
                    st.success(f"✅ {resultado['nombre']}")
    
    with col2:
        st.markdown("#### 📦 Reportes de Stock")
        archivos_stock = st.file_uploader(
            "Sube stocks (Excel)",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            key="stocks_upload"
        )
        
        if archivos_stock:
            for archivo in archivos_stock:
                resultado = cargar_stock(archivo)
                if resultado:
                    st.session_state.stocks.append(resultado)
                    st.success(f"✅ {resultado['nombre']}")

# ============================================
# TAB COTIZACIÓN
# ============================================
with tab_cotizacion:
    if not st.session_state.catalogos:
        st.warning("⚠️ Primero carga los catálogos en 'Configuración'")
    else:
        # Mostrar catálogos cargados
        with st.expander("📋 Catálogos cargados"):
            for cat in st.session_state.catalogos:
                st.caption(f"• {cat['nombre']}")
        
        # Selección de precio
        st.markdown("### 💰 Configuración de Precios")
        
        todas_columnas_precio = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio']:
                todas_columnas_precio.add(col)
        
        if todas_columnas_precio:
            col_precio = st.selectbox(
                "Selecciona la columna de precio:",
                options=sorted(list(todas_columnas_precio))
            )
        else:
            col_precio = None
            st.warning("No se detectaron columnas de precio")
        
        st.markdown("---")
        st.markdown("### 📝 Ingresa los productos")
        st.caption("Formato: SKU:CANTIDAD (uno por línea)")
        
        texto_skus = st.text_area(
            "SKU:CANTIDAD",
            height=150,
            placeholder="Ejemplo:\nCG0900004CLR8:5\nCN0900009WH8:2"
        )
        
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
            with st.spinner("Procesando..."):
                resultados = []
                
                for pedido in pedidos:
                    sku = pedido['sku']
                    cant_solicitada = pedido['cantidad']
                    
                    # Buscar en catálogos
                    producto = buscar_producto(st.session_state.catalogos, sku)
                    
                    if not producto['encontrado']:
                        resultados.append({
                            'SKU': sku,
                            'Descripción': '❌ NO ENCONTRADO',
                            'Precio': 0,
                            'Solicitado': cant_solicitada,
                            'Stock': 0,
                            'Comprometido': 0,
                            'Disponible': 0,
                            'Total': 0,
                            'Estado': '❌ No encontrado',
                            'Origen_Stock': '-'
                        })
                        continue
                    
                    # Obtener precio
                    precio = obtener_precio(producto['row'], producto['columnas_precio'], col_precio)
                    
                    # Obtener stock
                    stock, comprometido, solicitado, origen_stock = obtener_stock(sku, st.session_state.stocks)
                    disponible = stock - comprometido - solicitado
                    
                    # Determinar estado y cantidad a cotizar
                    if precio == 0:
                        estado = "⚠️ Sin precio"
                        cant_cotizar = 0
                        color_estado = "orange"
                    elif disponible >= cant_solicitada:
                        estado = "✅ OK"
                        cant_cotizar = cant_solicitada
                        color_estado = "green"
                    elif disponible > 0:
                        estado = f"⚠️ Stock insuficiente (solo {disponible})"
                        cant_cotizar = disponible
                        color_estado = "orange"
                    else:
                        estado = "❌ Sin stock disponible"
                        cant_cotizar = 0
                        color_estado = "red"
                    
                    resultados.append({
                        'id': sku,
                        'SKU': sku,
                        'Descripción': producto['descripcion'][:80],
                        'Catálogo': producto['catalogo'],
                        'Precio': precio,
                        'Solicitado': cant_solicitada,
                        'Stock_Total': stock,
                        'Comprometido': comprometido,
                        'Disponible': disponible,
                        'A_Cotizar': cant_cotizar,
                        'Total': precio * cant_cotizar,
                        'Estado': estado,
                        'Color_Estado': color_estado,
                        'Origen_Stock': origen_stock
                    })
                
                st.session_state.resultados = resultados
        
        # Mostrar resultados editables
        if st.session_state.resultados:
            st.markdown("---")
            st.markdown("### 📊 Resultados - Edita cantidades a cotizar")
            
            resultados_editados = []
            
            # Encabezados de la tabla
            cols = st.columns([2, 3, 1, 1, 1, 1, 1.2, 1.2, 1.5])
            cols[0].markdown("**SKU**")
            cols[1].markdown("**Descripción**")
            cols[2].markdown("**Precio**")
            cols[3].markdown("**Solicitado**")
            cols[4].markdown("**Stock**")
            cols[5].markdown("**Comprom.**")
            cols[6].markdown("**Disponible**")
            cols[7].markdown("**A Cotizar**")
            cols[8].markdown("**Estado**")
            
            st.divider()
            
            for i, item in enumerate(st.session_state.resultados):
                col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([2, 3, 1, 1, 1, 1, 1.2, 1.2, 1.5])
                
                col1.markdown(f"`{item['SKU']}`")
                col2.markdown(item['Descripción'][:50])
                col3.markdown(f"S/. {item['Precio']:,.2f}" if item['Precio'] > 0 else "-")
                col4.markdown(str(item['Solicitado']))
                col5.markdown(str(item['Stock_Total']))
                col6.markdown(str(item['Comprometido']))
                col7.markdown(str(item['Disponible']))
                
                # Input editable para cantidad a cotizar
                cant_a_cotizar = col8.number_input(
                    "Cant",
                    min_value=0,
                    max_value=item['Disponible'] if item['Disponible'] > 0 else 0,
                    value=item['A_Cotizar'],
                    key=f"cant_{item['id']}_{i}",
                    label_visibility="collapsed"
                )
                
                # Recalcular total
                nuevo_total = item['Precio'] * cant_a_cotizar
                estado = item['Estado']
                if cant_a_cotizar > 0 and item['Disponible'] >= cant_a_cotizar:
                    estado = "✅ OK"
                elif cant_a_cotizar == 0:
                    estado = "⏸️ Excluido"
                
                col9.markdown(f"<span style='color:{item['Color_Estado']}'>{estado}</span>", unsafe_allow_html=True)
                
                # Guardar editado
                item_editado = item.copy()
                item_editado['A_Cotizar'] = cant_a_cotizar
                item_editado['Total'] = nuevo_total
                item_editado['Estado'] = estado
                resultados_editados.append(item_editado)
                
                st.divider()
            
            # Resumen
            items_validos = [r for r in resultados_editados if r['A_Cotizar'] > 0 and r['Precio'] > 0]
            total_cotizacion = sum(r['Total'] for r in items_validos)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("📦 Productos a cotizar", len(items_validos))
            col2.metric("💰 Total Cotización", f"S/. {total_cotizacion:,.2f}")
            col3.metric("⚠️ Excluidos/Sin stock", len(resultados_editados) - len(items_validos))
            
            # Generar cotización
            if items_validos:
                st.markdown("---")
                st.markdown("### 📥 Generar Cotización")
                
                col_cli1, col_cli2 = st.columns(2)
                with col_cli1:
                    cliente = st.text_input("🏢 Cliente", "CLIENTE NUEVO")
                with col_cli2:
                    ruc_cliente = st.text_input("📋 RUC/DNI", "-")
                
                if st.button("📥 GENERAR COTIZACIÓN", use_container_width=True, type="primary"):
                    items_excel = [{
                        'sku': r['SKU'],
                        'desc': r['Descripción'],
                        'cant': r['A_Cotizar'],
                        'p_u': r['Precio'],
                        'total': r['Total']
                    } for r in items_validos]
                    
                    excel_data = generar_excel_cotizacion(items_excel, cliente, ruc_cliente)
                    
                    st.download_button(
                        label="💾 DESCARGAR EXCEL",
                        data=excel_data,
                        file_name=f"Cotizacion_{cliente}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        use_container_width=True
                    )
                    
                    st.session_state.cotizaciones += 1
                    st.session_state.total_prods = len(items_validos)
                    st.balloons()
                    st.success("✅ Cotización generada correctamente!")

st.markdown("---")
st.markdown("*💚 QTC Smart Sales Pro - Sistema Profesional de Cotización*")
