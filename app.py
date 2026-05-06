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

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F6; }
    .main .block-container { color: #1a1a2e !important; }
    h1, h2, h3, h4, p, div, span, label { color: #1a1a2e !important; }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a472a 0%, #0d2818 100%);
    }
    [data-testid="stSidebar"] * { color: white !important; }
    
    .stButton > button {
        background: #27AE60;
        color: white !important;
        border-radius: 10px;
        font-weight: 600;
    }
    .stButton > button:hover { background: #1E8449; }
    
    .stSelectbox > div > div {
        background-color: white !important;
        color: black !important;
        border: 1px solid #27AE60 !important;
        border-radius: 8px !important;
    }
    .stSelectbox label { color: #1a1a2e !important; }
    
    div[data-baseweb="select"] ul { background-color: white !important; }
    div[data-baseweb="select"] li { color: black !important; background-color: white !important; }
    div[data-baseweb="select"] li:hover { background-color: #e8f5e9 !important; }
    div[data-baseweb="select"] li[aria-selected="true"] { background-color: #27AE60 !important; color: white !important; }
    
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        color: black !important;
        background-color: white !important;
        border: 1px solid #ccc !important;
        border-radius: 8px !important;
    }
    
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #ddd;
    }
    .metric-value { font-size: 2rem; font-weight: bold; color: #27AE60 !important; }
    
    .stock-card {
        background: white;
        border-radius: 10px;
        padding: 0.5rem;
        margin: 0.3rem 0;
        border-left: 3px solid #27AE60;
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
        <div style="background: white; padding: 2rem; border-radius: 20px;">
            <h1 style="text-align: center; color: #27AE60;">💚 QTC Smart Sales</h1>
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
                'origen': f"{stock_data['nombre']} → {hoja_nombre}"
            })
    
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
                # Obtener stock de todas las hojas para este SKU
                stocks_disponibles = obtener_stock_todas_hojas(sku, st.session_state.stock_data) if st.session_state.stock_data else []
                resultados_dict[sku] = {
                    'SKU': sku,
                    'Descripción': str(row[cat['col_desc']])[:80],
                    'Catálogo': cat['nombre'],
                    'Precio': precio,
                    'Stocks': stocks_disponibles
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
        
        st.markdown("**📦 Reporte de Stock (único archivo con múltiples hojas)**")
        archivo_stock = st.file_uploader(
            "Sube el archivo de stock",
            type=['xlsx', 'xls'],
            key="stock_upload"
        )
        if archivo_stock:
            resultado = cargar_stock_completo(archivo_stock)
            if resultado:
                st.session_state.stock_data = resultado
                st.success(f"✅ {resultado['nombre']}: {len(resultado['hojas'])} hojas")
        
        st.markdown("---")
        st.markdown("### 🎯 Tipo de Cotización")
        
        tipo_cotizacion = st.radio(
            "¿Qué tipo de productos vas a cotizar?",
            ["📱 XIAOMI", "💼 GENERALES"],
            help="XIAOMI: Sugiere stock de APRI.004/YESSICA\nGENERALES: Sugiere stock de APRI.001"
        )
        st.session_state.es_xiaomi = (tipo_cotizacion == "📱 XIAOMI")
    
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
                            'id': sku, 'SKU': sku, 'Descripción': '❌ NO ENCONTRADO',
                            'Precio': 0, 'Solicitado': cant_solicitada,
                            'Stock_Seleccionado': 0, 'Origen_Stock': '-',
                            'A_Cotizar': 0, 'Total': 0,
                            'Estado': '❌ No encontrado', 'Color_Estado': 'red',
                            'Opciones_Stock': []
                        })
                        continue
                    
                    precio = obtener_precio(producto['row'], producto['columnas_precio'], col_precio)
                    
                    # Obtener stock de TODAS las hojas
                    opciones_stock = obtener_stock_todas_hojas(sku, st.session_state.stock_data)
                    
                    # Determinar stock sugerido según el tipo
                    stock_sugerido = 0
                    origen_sugerido = "-"
                    for opt in opciones_stock:
                        if st.session_state.es_xiaomi:
                            if 'APRI.004' in opt['hoja'].upper() or 'YESSICA' in opt['hoja'].upper():
                                stock_sugerido = opt['stock']
                                origen_sugerido = opt['origen']
                                break
                        else:
                            if 'APRI.001' in opt['hoja'].upper():
                                stock_sugerido = opt['stock']
                                origen_sugerido = opt['origen']
                                break
                    
                    resultados.append({
                        'id': sku,
                        'SKU': sku,
                        'Descripción': producto['descripcion'][:80],
                        'Precio': precio,
                        'Solicitado': cant_solicitada,
                        'Stock_Seleccionado': stock_sugerido,
                        'Origen_Stock': origen_sugerido,
                        'Opciones_Stock': opciones_stock,
                        'A_Cotizar': 0,
                        'Total': 0,
                        'Estado': 'Pendiente',
                        'Color_Estado': 'orange'
                    })
                
                st.session_state.resultados = resultados
        
        if st.session_state.resultados:
            st.markdown("---")
            st.markdown("### 📊 Resultados - Selecciona stock por producto")
            
            resultados_editados = []
            
            for i, item in enumerate(st.session_state.resultados):
                st.markdown(f"#### Producto {i+1}: `{item['SKU']}`")
                st.markdown(f"**Descripción:** {item['Descripción']}")
                st.markdown(f"**Precio:** S/. {item['Precio']:,.2f}" if item['Precio'] > 0 else "**Precio:** Sin precio")
                
                # Mostrar opciones de stock disponibles
                if item['Opciones_Stock']:
                    st.markdown("**📦 Stock disponible en las siguientes hojas:**")
                    
                    opciones_dict = {}
                    for opt in item['Opciones_Stock']:
                        opciones_dict[opt['origen']] = opt['stock']
                    
                    origen_seleccionado = st.selectbox(
                        f"Seleccionar origen de stock para {item['SKU']}:",
                        options=list(opciones_dict.keys()),
                        index=0,
                        key=f"origen_{item['id']}_{i}"
                    )
                    
                    stock_seleccionado = opciones_dict[origen_seleccionado]
                    st.caption(f"📊 Stock disponible: {stock_seleccionado} unidades")
                else:
                    stock_seleccionado = 0
                    origen_seleccionado = "Sin stock disponible"
                    st.warning("⚠️ No hay stock disponible en ninguna hoja")
                
                # Cantidad a cotizar
                col1, col2 = st.columns([1, 3])
                with col1:
                    cantidad_a_cotizar = st.number_input(
                        "Cantidad a cotizar:",
                        min_value=0,
                        max_value=stock_seleccionado if stock_seleccionado > 0 else 999,
                        value=min(item['Solicitado'], stock_seleccionado) if stock_seleccionado > 0 else 0,
                        key=f"cant_{item['id']}_{i}"
                    )
                with col2:
                    if cantidad_a_cotizar > 0 and item['Precio'] > 0:
                        total_producto = item['Precio'] * cantidad_a_cotizar
                        st.markdown(f"**💰 Total: S/. {total_producto:,.2f}**")
                    elif cantidad_a_cotizar > 0 and item['Precio'] == 0:
                        st.warning("⚠️ Producto sin precio")
                
                # Estado
                if cantidad_a_cotizar == 0:
                    estado = "⏸️ Excluido"
                    color = "gray"
                elif item['Precio'] == 0:
                    estado = "⚠️ Sin precio"
                    color = "orange"
                elif cantidad_a_cotizar <= stock_seleccionado:
                    estado = "✅ OK"
                    color = "green"
                else:
                    estado = f"⚠️ Excede stock (máx {stock_seleccionado})"
                    color = "orange"
                
                st.markdown(f"<span style='color:{color}'>{estado}</span>", unsafe_allow_html=True)
                
                # Guardar
                item_editado = item.copy()
                item_editado['Stock_Seleccionado'] = stock_seleccionado
                item_editado['Origen_Stock'] = origen_seleccionado
                item_editado['A_Cotizar'] = cantidad_a_cotizar
                item_editado['Total'] = item['Precio'] * cantidad_a_cotizar
                item_editado['Estado'] = estado
                resultados_editados.append(item_editado)
                
                st.divider()
            
            # Resumen
            items_validos = [r for r in resultados_editados if r['A_Cotizar'] > 0 and r['Precio'] > 0]
            total_cotizacion = sum(r['Total'] for r in items_validos)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("📦 A cotizar", len(items_validos))
            col2.metric("💰 Total", f"S/. {total_cotizacion:,.2f}")
            col3.metric("⏸️ Excluidos", len(resultados_editados) - len(items_validos))
            
            if items_validos:
                st.markdown("---")
                st.markdown("### 📥 Generar Cotización")
                col_cli1, col_cli2 = st.columns(2)
                with col_cli1:
                    cliente = st.text_input("🏢 Cliente", "CLIENTE NUEVO")
                with col_cli2:
                    ruc_cliente = st.text_input("📋 RUC/DNI", "-")
                
                if st.button("📥 GENERAR EXCEL", use_container_width=True, type="primary"):
                    items_excel = [{'sku': r['SKU'], 'desc': r['Descripción'], 'cant': r['A_Cotizar'], 'p_u': r['Precio'], 'total': r['Total']} for r in items_validos]
                    excel_data = generar_excel_cotizacion(items_excel, cliente, ruc_cliente)
                    st.download_button(label="💾 DESCARGAR", data=excel_data, file_name=f"Cotizacion_{cliente}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", use_container_width=True)
                    st.session_state.cotizaciones += 1
                    st.session_state.total_prods = len(items_validos)
                    st.balloons()
                    st.success("✅ Cotización generada!")

# ============================================
# TAB 2: BUSCAR PRODUCTOS (MEJORADO)
# ============================================
with tab_buscar:
    st.markdown("### 🔍 Buscar Productos")
    
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
                            st.markdown(f"**Catálogo:** {res['Catálogo']}")
                            if res['Precio']:
                                st.markdown(f"**💰 Precio:** S/. {res['Precio']:,.2f}")
                        with col2:
                            cantidad = st.number_input(
                                "Cantidad a agregar:",
                                min_value=0, max_value=999, value=0,
                                key=f"agregar_{res['SKU']}",
                                label_visibility="collapsed"
                            )
                            if cantidad > 0:
                                st.session_state.productos_seleccionados[res['SKU']] = st.session_state.productos_seleccionados.get(res['SKU'], 0) + cantidad
                        
                        # Mostrar stock disponible en todas las hojas
                        if st.session_state.stock_data:
                            stocks_info = obtener_stock_todas_hojas(res['SKU'], st.session_state.stock_data)
                            if stocks_info:
                                st.markdown("**📊 Stock disponible:**")
                                for s in stocks_info:
                                    icono = "🔋" if ('APRI.004' in s['hoja'].upper() or 'YESSICA' in s['hoja'].upper()) else ("💙" if 'APRI.001' in s['hoja'].upper() else "📄")
                                    st.markdown(f"{icono} **{s['hoja']}:** {s['stock']} unidades")
                            else:
                                st.warning("⚠️ No se encontró stock en ninguna hoja")
            else:
                st.warning("No se encontraron productos")
        
        st.markdown("---")
        st.markdown("#### 📝 Agregar SKU específicos")
        st.caption("Formato: SKU:CANTIDAD (uno por línea)")
        
        texto_multiple = st.text_area("Ingresa SKU:CANTIDAD", height=100, placeholder="CN0900009WH8:5\nCN0903902WH0:2")
        
        if st.button("➕ Agregar productos", use_container_width=True):
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
                        except:
                            pass
                elif line:
                    st.session_state.productos_seleccionados[line.strip().upper()] = st.session_state.productos_seleccionados.get(line.strip().upper(), 0) + 1
            st.success(f"✅ Productos agregados! Total: {len(st.session_state.productos_seleccionados)}")
            st.rerun()
        
        if st.session_state.productos_seleccionados:
            st.markdown("---")
            st.markdown(f"### ✅ Productos seleccionados ({len(st.session_state.productos_seleccionados)})")
            
            seleccionados_editables = []
            for sku, cant in list(st.session_state.productos_seleccionados.items()):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"`{sku}`")
                with col2:
                    nueva_cant = st.number_input("Cant", min_value=0, max_value=999, value=cant, key=f"edit_{sku}", label_visibility="collapsed")
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
            <div class="metric-label">📄 Cotizaciones</div>
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
            <div style="font-size:0.8rem;">📑 {total_hojas} hojas de stock</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("*💚 QTC Smart Sales Pro - Selección manual de stock por producto*")
