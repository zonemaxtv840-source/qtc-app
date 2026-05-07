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

# --- ESTILOS CSS - NARANJA CORPORATIVO ---
st.markdown("""
    <style>
    /* Fondo general claro */
    .stApp { background-color: #F5F7FA; }
    .main .block-container { color: #1a1a2e !important; }
    
    /* Todos los textos oscuros para legibilidad */
    h1, h2, h3, h4, h5, h6, p, div, span, label, .stMarkdown {
        color: #1a1a2e !important;
    }
    
    /* Sidebar oscuro con texto blanco */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a472a 0%, #0d2818 100%);
    }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Botones naranja corporativo */
    .stButton > button {
        background: #F79646 !important;
        color: white !important;
        border-radius: 10px;
        font-weight: 600;
        border: none;
    }
    .stButton > button:hover {
        background: #e67e22 !important;
        transform: translateY(-2px);
        transition: all 0.3s;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background-color: white !important;
        color: black !important;
        border: 1px solid #F79646 !important;
        border-radius: 8px !important;
    }
    .stSelectbox label { color: #1a1a2e !important; }
    
    /* Dropdown */
    div[data-baseweb="select"] ul { background-color: white !important; }
    div[data-baseweb="select"] li { color: black !important; background-color: white !important; }
    div[data-baseweb="select"] li:hover { background-color: #FFF3E0 !important; }
    div[data-baseweb="select"] li[aria-selected="true"] { background-color: #F79646 !important; color: white !important; }
    
    /* Inputs */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        color: black !important;
        background-color: white !important;
        border: 1px solid #ddd !important;
        border-radius: 8px !important;
    }
    
    /* Tabs naranja */
    .stTabs [data-baseweb="tab-list"] { background-color: white !important; border-radius: 10px !important; padding: 4px !important; gap: 8px !important; }
    .stTabs [data-baseweb="tab"] { color: #1a1a2e !important; background-color: #f0f0f0 !important; border-radius: 8px !important; padding: 8px 16px !important; }
    .stTabs [aria-selected="true"] { background-color: #F79646 !important; color: white !important; }
    
    /* Tarjeta de producto */
    .product-card {
        background: white;
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #eee;
    }
    
    /* Badges de stock */
    .stock-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 6px;
    }
    .stock-good { background-color: #e8f5e9; color: #2e7d32 !important; border: 1px solid #a5d6a7; }
    .stock-low { background-color: #fff3e0; color: #e65100 !important; border: 1px solid #ffcc80; }
    .stock-none { background-color: #ffebee; color: #c62828 !important; border: 1px solid #ef9a9a; }
    .stock-selected { background-color: #F79646; color: white !important; border: 1px solid #e67e22; }
    
    /* Metric cards dashboard */
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-top: 4px solid #F79646;
    }
    .metric-value { font-size: 2.2rem; font-weight: bold; color: #F79646 !important; }
    .metric-label { font-size: 0.9rem; color: #666 !important; margin-top: 0.5rem; }
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
            <h1 style="text-align: center; color: #F79646;">💚 QTC Smart Sales</h1>
            <p style="text-align: center;">Sistema Profesional de Cotización</p>
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
# FUNCIONES
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
    try:
        xls = pd.ExcelFile(archivo)
        hojas = xls.sheet_names
        hoja_seleccionada = st.sidebar.selectbox(
            f"📗 {archivo.name}:",
            hojas,
            key=f"cat_{archivo.name}"
        )
        df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)
        df = limpiar_cabeceras(df)
        
        col_sku = None
        col_desc = None
        columnas_precio = []
        
        for c in df.columns:
            c_str = str(c).upper()
            if any(p in c_str for p in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO']):
                if col_sku is None: col_sku = c
            if any(p in c_str for p in ['DESC', 'NOMBRE', 'PRODUCTO']):
                if col_desc is None: col_desc = c
            if any(p in c_str for p in ['PRECIO', 'CAJA', 'VIP', 'MAYOR', 'IR', 'BOX']):
                columnas_precio.append(c)
        
        if col_sku is None and len(df.columns) > 0: col_sku = df.columns[0]
        if col_desc is None and len(df.columns) > 1: col_desc = df.columns[1]
        
        return {
            'nombre': f"{archivo.name} [{hoja_seleccionada}]",
            'df': df,
            'col_sku': col_sku,
            'col_desc': col_desc,
            'columnas_precio': columnas_precio
        }
    except:
        return None

def cargar_stock_completo(archivo):
    """Carga TODAS las hojas del archivo de stock"""
    try:
        xls = pd.ExcelFile(archivo)
        todas_hojas = {}
        
        for hoja in xls.sheet_names:
            df = pd.read_excel(archivo, sheet_name=hoja)
            df = limpiar_cabeceras(df)
            
            col_sku = None
            col_stock = None
            
            for c in df.columns:
                c_str = str(c).upper()
                if any(p in c_str for p in ['SKU', 'COD', 'NUMERO', 'ARTICULO']):
                    if col_sku is None: col_sku = c
                if any(p in c_str for p in ['STOCK', 'DISPONIBLE', 'CANT', 'SALDO']):
                    if col_stock is None: col_stock = c
            
            if col_sku is None and len(df.columns) > 0: col_sku = df.columns[0]
            if col_stock is None and len(df.columns) > 1: col_stock = df.columns[1]
            
            todas_hojas[hoja] = {
                'df': df,
                'col_sku': col_sku,
                'col_stock': col_stock,
                'nombre_hoja': hoja
            }
        
        return {
            'nombre': archivo.name,
            'hojas': todas_hojas
        }
    except:
        return None

def obtener_stock_todas_hojas(sku, stock_data):
    """Obtiene stock de TODAS las hojas disponibles"""
    resultados = []
    
    if not stock_data:
        return resultados
    
    for hoja_nombre, hoja_info in stock_data['hojas'].items():
        mask = hoja_info['df'][hoja_info['col_sku']].astype(str).str.contains(sku, case=False, na=False, regex=False)
        if not hoja_info['df'][mask].empty:
            row = hoja_info['df'][mask].iloc[0]
            cantidad = int(corregir_numero(row[hoja_info['col_stock']])) if hoja_info['col_stock'] else 0
            resultados.append({
                'hoja': hoja_nombre,
                'stock': cantidad,
                'origen': f"{hoja_nombre}"
            })
        else:
            resultados.append({
                'hoja': hoja_nombre,
                'stock': 0,
                'origen': f"{hoja_nombre}"
            })
    
    # Ordenar por stock descendente para preseleccionar la que más tiene
    resultados.sort(key=lambda x: x['stock'], reverse=True)
    return resultados

def buscar_producto(catalogos, sku_buscar):
    for catalogo in catalogos:
        df = catalogo['df']
        mask = df[catalogo['col_sku']].astype(str).str.contains(sku_buscar, case=False, na=False, regex=False)
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

def buscar_en_catalogos(catalogos, termino, col_precio_consulta=None):
    resultados_dict = {}
    for cat in catalogos:
        df = cat['df']
        mask_sku = df[cat['col_sku']].astype(str).str.contains(termino, case=False, na=False, regex=False)
        mask_desc = df[cat['col_desc']].astype(str).str.contains(termino, case=False, na=False, regex=False)
        for idx, row in df[mask_sku | mask_desc].iterrows():
            sku = str(row[cat['col_sku']])
            precio = None
            if col_precio_consulta and col_precio_consulta != "(No mostrar precio)":
                precio = corregir_numero(row[col_precio_consulta]) if col_precio_consulta in df.columns else 0
            if sku not in resultados_dict:
                resultados_dict[sku] = {
                    'SKU': sku,
                    'Descripción': str(row[cat['col_desc']])[:80],
                    'Catálogo': cat['nombre'],
                    'Precio': precio
                }
    return list(resultados_dict.values())

def obtener_precio(row, columnas_precio, col_seleccionada):
    if col_seleccionada and col_seleccionada in columnas_precio and col_seleccionada in row.index:
        return corregir_numero(row[col_seleccionada])
    return 0.0

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
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = None
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 'cotizaciones' not in st.session_state:
    st.session_state.cotizaciones = 0
if 'total_prods' not in st.session_state:
    st.session_state.total_prods = 0
if 'productos_seleccionados' not in st.session_state:
    st.session_state.productos_seleccionados = {}

tab_cotizacion, tab_buscar, tab_dashboard = st.tabs([
    "📦 Cotización", "🔍 Buscar Productos", "📊 Dashboard"
])

# ============================================
# TAB COTIZACIÓN
# ============================================
with tab_cotizacion:
    with st.sidebar:
        st.markdown("### 📂 Archivos")
        
        st.markdown("**📚 Catálogos de Precios**")
        archivos_catalogos = st.file_uploader(
            "Sube catálogos",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            key="cat_upload"
        )
        if archivos_catalogos:
            for archivo in archivos_catalogos:
                resultado = cargar_catalogo(archivo)
                if resultado:
                    st.session_state.catalogos.append(resultado)
                    st.success(f"✅ {resultado['nombre']}")
        
        st.markdown("**📦 Reporte de Stock**")
        archivo_stock = st.file_uploader(
            "Sube el archivo de stock (con hojas: APRI.001, APRI.004, YESSICA SEPARADO)",
            type=['xlsx', 'xls'],
            key="stock_upload"
        )
        if archivo_stock:
            resultado = cargar_stock_completo(archivo_stock)
            if resultado:
                st.session_state.stock_data = resultado
                st.success(f"✅ {resultado['nombre']}: {len(resultado['hojas'])} hojas")
                st.caption(f"Hojas: {', '.join(resultado['hojas'].keys())}")
    
    if not st.session_state.catalogos:
        st.warning("⚠️ Carga catálogos en el panel izquierdo")
    elif not st.session_state.stock_data:
        st.warning("⚠️ Carga el archivo de stock en el panel izquierdo")
    else:
        st.markdown("### 💰 Configuración de Precios")
        todas_columnas_precio = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio']:
                todas_columnas_precio.add(col)
        
        if todas_columnas_precio:
            col_precio = st.selectbox("Columna de precio:", sorted(list(todas_columnas_precio)))
        else:
            col_precio = None
            st.warning("No hay columnas de precio")
        
        st.markdown("---")
        st.markdown("### 📝 Ingresa los productos")
        st.caption("Formato: SKU:CANTIDAD (uno por línea)")
        
        if 'skus_transferidos' in st.session_state:
            texto_defecto = "\n".join([f"{sku}:{cant}" for sku, cant in st.session_state.skus_transferidos.items()])
            del st.session_state.skus_transferidos
        else:
            texto_defecto = ""
        
        texto_skus = st.text_area("SKU:CANTIDAD", height=150, value=texto_defecto,
                                   placeholder="Ejemplo:\nCN0900009WH8:5\nCN0903902WH0:2")
        
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
                    
                    producto = buscar_producto(st.session_state.catalogos, sku)
                    
                    if not producto['encontrado']:
                        resultados.append({
                            'id': sku,
                            'SKU': sku,
                            'Descripción': '❌ NO ENCONTRADO',
                            'Precio': 0,
                            'Solicitado': cant_solicitada,
                            'OpcionesStock': [],
                            'StockSeleccionado': 0,
                            'OrigenSeleccionado': '-',
                            'A_Cotizar': 0,
                            'Total': 0,
                            'Error': True
                        })
                        continue
                    
                    precio = obtener_precio(producto['row'], producto['columnas_precio'], col_precio)
                    
                    # Obtener stock de TODAS las hojas (ordenado por mayor stock)
                    opciones_stock = obtener_stock_todas_hojas(sku, st.session_state.stock_data)
                    
                    # Seleccionar automáticamente la hoja con más stock
                    mejor_opcion = opciones_stock[0] if opciones_stock else None
                    stock_seleccionado = mejor_opcion['stock'] if mejor_opcion else 0
                    origen_seleccionado = mejor_opcion['hoja'] if mejor_opcion else "-"
                    
                    resultados.append({
                        'id': sku,
                        'SKU': sku,
                        'Descripción': producto['descripcion'][:100],
                        'Precio': precio,
                        'Solicitado': cant_solicitada,
                        'OpcionesStock': opciones_stock,
                        'StockSeleccionado': stock_seleccionado,
                        'OrigenSeleccionado': origen_seleccionado,
                        'A_Cotizar': min(cant_solicitada, stock_seleccionado) if stock_seleccionado > 0 else 0,
                        'Total': precio * min(cant_solicitada, stock_seleccionado) if stock_seleccionado > 0 and precio > 0 else 0,
                        'Error': False
                    })
                
                st.session_state.resultados = resultados
        
        # Mostrar resultados en tarjetas
        if st.session_state.resultados:
            st.markdown("---")
            st.markdown("### 📊 Resultados de la cotización")
            st.markdown("*💡 Puedes cambiar el origen del stock para cada producto*")
            
            resultados_editados = []
            
            for i, item in enumerate(st.session_state.resultados):
                if item.get('Error', False):
                    with st.container():
                        st.error(f"❌ **{item['SKU']}** - {item['Descripción']}")
                    continue
                
                # Tarjeta de producto
                with st.container():
                    st.markdown(f"""
                    <div class="product-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <h3 style="margin: 0; color: #F79646;">📦 {item['SKU']}</h3>
                                <p style="margin: 5px 0 0 0; color: #555;">{item['Descripción']}</p>
                            </div>
                            <div style="text-align: right;">
                                <span style="font-size: 1.2rem; font-weight: bold; color: #F79646;">S/. {item['Precio']:,.2f}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Mostrar stock disponible por hoja
                    st.markdown("**📊 Stock disponible por ubicación:**")
                    
                    opciones_dict = {}
                    col_badges = st.columns(len(item['OpcionesStock']))
                    
                    for idx, opt in enumerate(item['OpcionesStock']):
                        stock = opt['stock']
                        hoja = opt['hoja']
                        
                        # Determinar clase CSS según stock
                        if stock > 10:
                            badge_class = "stock-good"
                        elif stock > 0:
                            badge_class = "stock-low"
                        else:
                            badge_class = "stock-none"
                        
                        # Resaltar la que está seleccionada
                        if hoja == item['OrigenSeleccionado']:
                            badge_class = "stock-selected"
                        
                        st.markdown(f"""
                        <span class="stock-badge {badge_class}">
                            📁 {hoja}: {stock} unidades
                        </span>
                        """, unsafe_allow_html=True)
                        
                        opciones_dict[hoja] = stock
                    
                    # Selector para cambiar el origen del stock
                    st.markdown("---")
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        nuevo_origen = st.selectbox(
                            f"🎯 Seleccionar origen de stock para {item['SKU']}:",
                            options=list(opciones_dict.keys()),
                            index=list(opciones_dict.keys()).index(item['OrigenSeleccionado']) if item['OrigenSeleccionado'] in opciones_dict else 0,
                            key=f"origen_{item['id']}_{i}"
                        )
                        nuevo_stock = opciones_dict[nuevo_origen]
                    
                    with col2:
                        cantidad_a_cotizar = st.number_input(
                            "📦 Cantidad a cotizar:",
                            min_value=0,
                            max_value=max(nuevo_stock, 999) if nuevo_stock > 0 else 999,
                            value=min(item['Solicitado'], nuevo_stock) if nuevo_stock > 0 else 0,
                            key=f"cant_{item['id']}_{i}"
                        )
                    
                    with col3:
                        total_producto = item['Precio'] * cantidad_a_cotizar
                        if cantidad_a_cotizar > 0 and item['Precio'] > 0:
                            st.markdown(f"""
                            <div style="background: #e8f5e9; padding: 0.5rem; border-radius: 8px; text-align: center;">
                                <span style="font-size: 0.8rem;">💰 TOTAL</span>
                                <br>
                                <span style="font-size: 1.2rem; font-weight: bold; color: #2e7d32;">S/. {total_producto:,.2f}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style="background: #ffebee; padding: 0.5rem; border-radius: 8px; text-align: center;">
                                <span style="font-size: 0.8rem;">⚠️ Sin precio</span>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Determinar estado final
                    if cantidad_a_cotizar == 0:
                        estado_final = "⏸️ Excluido"
                        color_estado = "#999"
                    elif item['Precio'] == 0:
                        estado_final = "⚠️ Sin precio"
                        color_estado = "#e65100"
                    elif cantidad_a_cotizar <= nuevo_stock:
                        estado_final = f"✅ OK - Usando stock de {nuevo_origen}"
                        color_estado = "#2e7d32"
                    else:
                        estado_final = f"⚠️ Stock insuficiente (máx {nuevo_stock})"
                        color_estado = "#c62828"
                    
                    st.markdown(f"""
                    <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid #eee;">
                        <span style="color: {color_estado}; font-weight: 500;">{estado_final}</span>
                    </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Guardar resultados editados
                    item_editado = item.copy()
                    item_editado['OrigenSeleccionado'] = nuevo_origen
                    item_editado['StockSeleccionado'] = nuevo_stock
                    item_editado['A_Cotizar'] = cantidad_a_cotizar
                    item_editado['Total'] = total_producto
                    item_editado['Estado'] = estado_final
                    resultados_editados.append(item_editado)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
            
            # Resumen final
            items_validos = [r for r in resultados_editados if r['A_Cotizar'] > 0 and r['Precio'] > 0 and not r.get('Error', False)]
            total_cotizacion = sum(r['Total'] for r in items_validos)
            
            st.markdown("---")
            st.markdown("### 📈 Resumen de la cotización")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{len(items_validos)}</div>
                    <div class="metric-label">📦 Productos a cotizar</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">S/. {total_cotizacion:,.2f}</div>
                    <div class="metric-label">💰 Total de la cotización</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                excluidos = len([r for r in resultados_editados if r['A_Cotizar'] == 0 or r.get('Error', False)])
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{excluidos}</div>
                    <div class="metric-label">⏸️ Productos excluidos</div>
                </div>
                """, unsafe_allow_html=True)
            
            if items_validos:
                st.markdown("---")
                st.markdown("### 📥 Generar Cotización")
                
                col_cli1, col_cli2 = st.columns(2)
                with col_cli1:
                    cliente = st.text_input("🏢 Cliente", "CLIENTE NUEVO")
                with col_cli2:
                    ruc_cliente = st.text_input("📋 RUC/DNI", "-")
                
                if st.button("📥 GENERAR EXCEL", use_container_width=True, type="primary"):
                    items_excel = [{
                        'sku': r['SKU'],
                        'desc': r['Descripción'],
                        'cant': r['A_Cotizar'],
                        'p_u': r['Precio'],
                        'total': r['Total']
                    } for r in items_validos]
                    
                    excel_data = generar_excel_cotizacion(items_excel, cliente, ruc_cliente)
                    
                    st.download_button(
                        label="💾 DESCARGAR COTIZACIÓN",
                        data=excel_data,
                        file_name=f"Cotizacion_{cliente}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        use_container_width=True
                    )
                    
                    st.session_state.cotizaciones += 1
                    st.session_state.total_prods = len(items_validos)
                    st.balloons()
                    st.success("✅ Cotización generada correctamente!")

# ============================================
# TAB 2: BUSCAR PRODUCTOS
# ============================================
with tab_buscar:
    st.markdown("### 🔍 Buscar Productos en Catálogos")
    
    if not st.session_state.catalogos:
        st.warning("⚠️ Primero carga catálogos en la pestaña 'Cotización'")
    else:
        todas_columnas = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio']:
                todas_columnas.add(col)
        
        col_precio_consulta = st.selectbox(
            "Mostrar precios en columna:",
            options=["(No mostrar precio)"] + sorted(list(todas_columnas)),
            key="precio_busqueda"
        )
        
        busqueda = st.text_input("Buscar por SKU o descripción:", placeholder="Ej: cable, cargador, CN0900009WH8")
        
        if busqueda and len(busqueda) >= 3:
            with st.spinner("Buscando..."):
                precio_seleccionado = None if col_precio_consulta == "(No mostrar precio)" else col_precio_consulta
                resultados = buscar_en_catalogos(st.session_state.catalogos, busqueda, precio_seleccionado)
            
            if resultados:
                st.success(f"✅ {len(resultados)} resultados encontrados")
                
                for res in resultados:
                    with st.expander(f"📦 {res['SKU']} - {res['Descripción'][:60]}"):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown(f"**📁 Catálogo:** {res['Catálogo']}")
                            if res['Precio']:
                                st.markdown(f"**💰 Precio:** S/. {res['Precio']:,.2f}")
                        with col2:
                            cantidad = st.number_input(
                                "➕ Cantidad a agregar:",
                                min_value=0, max_value=999, value=0,
                                key=f"add_{res['SKU']}",
                                label_visibility="collapsed"
                            )
                            if cantidad > 0:
                                st.session_state.productos_seleccionados[res['SKU']] = st.session_state.productos_seleccionados.get(res['SKU'], 0) + cantidad
                        
                        # Mostrar stock disponible en todas las hojas
                        if st.session_state.stock_data:
                            stocks_info = obtener_stock_todas_hojas(res['SKU'], st.session_state.stock_data)
                            if stocks_info:
                                st.markdown("**📊 Stock disponible en el sistema:**")
                                for s in stocks_info:
                                    if s['stock'] > 10:
                                        icono = "🟢"
                                    elif s['stock'] > 0:
                                        icono = "🟠"
                                    else:
                                        icono = "🔴"
                                    st.markdown(f"{icono} **{s['hoja']}:** {s['stock']} unidades")
                            else:
                                st.warning("⚠️ No se encontró stock en ninguna hoja")
            else:
                st.warning("No se encontraron productos")
        
        st.markdown("---")
        st.markdown("#### 📝 Agregar múltiples SKU manualmente")
        st.caption("Formato: SKU:CANTIDAD (uno por línea)")
        
        texto_multiple = st.text_area("Ingresa SKU:CANTIDAD", height=100, placeholder="CN0900009WH8:5\nCN0903902WH0:2")
        
        if st.button("➕ Agregar productos", use_container_width=True):
            lineas_agregadas = 0
            for line in texto_multiple.split('\n'):
                line = line.strip()
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) == 2:
                        try:
                            sku = parts[0].strip().upper()
                            cantidad = int(parts[1].strip())
                            if cantidad > 0:
                                st.session_state.productos_seleccionados[sku] = st.session_state.productos_seleccionados.get(sku, 0) + cantidad
                                lineas_agregadas += 1
                        except:
                            pass
                elif line:
                    st.session_state.productos_seleccionados[line.strip().upper()] = st.session_state.productos_seleccionados.get(line.strip().upper(), 0) + 1
                    lineas_agregadas += 1
            
            if lineas_agregadas > 0:
                st.success(f"✅ {lineas_agregadas} productos agregados!")
                st.rerun()
            else:
                st.warning("No se agregaron productos. Usa formato SKU:CANTIDAD")
        
        if st.session_state.productos_seleccionados:
            st.markdown("---")
            st.markdown(f"### ✅ Productos seleccionados ({len(st.session_state.productos_seleccionados)})")
            
            seleccionados_editables = []
            for sku, cant in list(st.session_state.productos_seleccionados.items()):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"`{sku}`")
                with col2:
                    nueva_cant = st.number_input("Cantidad", min_value=0, max_value=999, value=cant, key=f"edit_{sku}", label_visibility="collapsed")
                with col3:
                    if st.button("🗑️", key=f"del_{sku}"):
                        nueva_cant = 0
                if nueva_cant > 0:
                    seleccionados_editables.append({'SKU': sku, 'Cantidad': nueva_cant})
                st.divider()
            
            st.session_state.productos_seleccionados = {item['SKU']: item['Cantidad'] for item in seleccionados_editables}
            
            if st.session_state.productos_seleccionados:
                if st.button("📋 TRANSFERIR A COTIZACIÓN", use_container_width=True, type="primary"):
                    st.session_state.skus_transferidos = st.session_state.productos_seleccionados.copy()
                    st.session_state.productos_seleccionados = {}
                    st.success(f"✅ {len(st.session_state.skus_transferidos)} productos transferidos!")
                    st.info("👉 Ve a la pestaña 'Cotización' y haz clic en PROCESAR")

# ============================================
# TAB 3: DASHBOARD
# ============================================
with tab_dashboard:
    st.markdown("### 📊 Dashboard de Ventas")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.get('cotizaciones', 0)}</div>
            <div class="metric-label">📄 Cotizaciones Generadas</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.get('total_prods', 0)}</div>
            <div class="metric-label">🌿 Productos Cotizados</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        total_catalogos = len(st.session_state.get('catalogos', []))
        total_hojas = len(st.session_state.stock_data['hojas']) if st.session_state.stock_data else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_catalogos}</div>
            <div class="metric-label">📚 Catálogos</div>
            <div class="metric-label" style="font-size:0.7rem;">📑 {total_hojas} hojas de stock</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📋 Resumen de Catálogos Cargados")
    if st.session_state.catalogos:
        for cat in st.session_state.catalogos:
            st.markdown(f"- **{cat['nombre']}**")
    
    st.markdown("---")
    st.markdown("### 📋 Stock Disponible (Todas las hojas)")
    if st.session_state.stock_data:
        for hoja in st.session_state.stock_data['hojas'].keys():
            icono = "🔋" if 'APRI.004' in hoja.upper() else ("💜" if 'YESSICA' in hoja.upper() else "💙")
            st.markdown(f"- {icono} **{hoja}**")
    else:
        st.info("No hay stock cargado")
    
    st.markdown("---")
    st.markdown("### 🎯 Manual del Sistema")
    st.markdown("""
    **1. Cargar archivos:**
    - Sube tus catálogos de precios (Excel)
    - Sube tu archivo de stock (debe contener hojas: APRI.001, APRI.004, YESSICA SEPARADO)
    
    **2. Configurar:**
    - Selecciona la columna de precio (Caja, VIP, Mayor, etc.)
    - Ingresa SKU en formato `SKU:CANTIDAD`
    
    **3. Revisar resultados:**
    - El sistema muestra stock disponible en CADA hoja
    - Selecciona automáticamente la hoja con más stock
    - Puedes cambiar manualmente el origen para cada producto
    
    **4. Generar cotización:**
    - Ingresa datos del cliente
    - Descarga Excel con formato profesional
    """)

st.markdown("---")
st.markdown("*💚 QTC Smart Sales Pro - Con selección inteligente de stock*")
