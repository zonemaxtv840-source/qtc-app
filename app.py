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

def obtener_stock_segun_tipo(sku, stock_data, es_xiaomi):
    """
    Busca stock según el tipo de cotización:
    - es_xiaomi=True: busca en hojas APRI.004 y YESSICA
    - es_xiaomi=False: busca en hoja APRI.001
    """
    if not stock_data:
        return 0, "Sin stock cargado"
    
    for hoja_nombre, hoja_info in stock_data['hojas'].items():
        hoja_upper = hoja_nombre.upper()
        
        if es_xiaomi:
            # Buscar en APRI.004 o YESSICA
            if 'APRI.004' in hoja_upper or 'YESSICA' in hoja_upper:
                mask = hoja_info['df'][hoja_info['col_sku']].astype(str).str.contains(sku, case=False, na=False, regex=False)
                if not hoja_info['df'][mask].empty:
                    row = hoja_info['df'][mask].iloc[0]
                    cantidad = int(corregir_numero(row[hoja_info['col_stock']])) if hoja_info['col_stock'] else 0
                    return cantidad, f"{stock_data['nombre']} → {hoja_nombre}"
        else:
            # Buscar en APRI.001
            if 'APRI.001' in hoja_upper or 'APRI1' in hoja_upper:
                mask = hoja_info['df'][hoja_info['col_sku']].astype(str).str.contains(sku, case=False, na=False, regex=False)
                if not hoja_info['df'][mask].empty:
                    row = hoja_info['df'][mask].iloc[0]
                    cantidad = int(corregir_numero(row[hoja_info['col_stock']])) if hoja_info['col_stock'] else 0
                    return cantidad, f"{stock_data['nombre']} → {hoja_nombre}"
    
    return 0, f"No encontrado en {'XIAOMI' if es_xiaomi else 'GENERAL'}"

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
        
        st.markdown("**📦 Reporte de Stock (único archivo con múltiples hojas)**")
        archivo_stock = st.file_uploader(
            "Sube el archivo de stock (Excel con hojas: APRI.001, APRI.004, YESSICA)",
            type=['xlsx', 'xls'],
            key="stock_upload"
        )
        if archivo_stock:
            resultado = cargar_stock_completo(archivo_stock)
            if resultado:
                st.session_state.stock_data = resultado
                st.success(f"✅ {resultado['nombre']}: {len(resultado['hojas'])} hojas")
                st.caption(f"Hojas encontradas: {', '.join(resultado['hojas'].keys())}")
        
        st.markdown("---")
        st.markdown("### 🎯 Tipo de Cotización")
        
        tipo_cotizacion = st.radio(
            "¿Qué tipo de productos vas a cotizar?",
            ["📱 XIAOMI", "💼 GENERALES (Ugreen, Innos, etc.)"],
            help="XIAOMI: Busca stock en hojas APRI.004 y YESSICA\nGENERALES: Busca stock en hoja APRI.001"
        )
        
        if tipo_cotizacion == "📱 XIAOMI":
            st.session_state.es_xiaomi = True
            st.info("🔋 Modo XIAOMI - Buscando stock en hojas: APRI.004, YESSICA")
        else:
            st.session_state.es_xiaomi = False
            st.info("💼 Modo GENERAL - Buscando stock en hoja: APRI.001")
    
    if not st.session_state.catalogos:
        st.warning("⚠️ Carga catálogos en el panel izquierdo")
    elif not st.session_state.stock_data:
        st.warning("⚠️ Carga el archivo de stock en el panel izquierdo")
    else:
        with st.expander("📋 Catálogos cargados"):
            for cat in st.session_state.catalogos:
                st.caption(f"• {cat['nombre']}")
        
        with st.expander("📋 Stock cargado (todas las hojas)"):
            st.caption(f"📁 {st.session_state.stock_data['nombre']}")
            for hoja in st.session_state.stock_data['hojas'].keys():
                icono = "🔋" if ('APRI.004' in hoja.upper() or 'YESSICA' in hoja.upper()) else ("💙" if 'APRI.001' in hoja.upper() else "📄")
                st.caption(f"  {icono} {hoja}")
        
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
        
        # Si vienen productos transferidos desde búsqueda
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
                            'Stock_Disponible': 0,
                            'A_Cotizar': 0, 'Total': 0,
                            'Estado': '❌ No encontrado', 'Color_Estado': 'red',
                            'Origen_Stock': '-'
                        })
                        continue
                    
                    precio = obtener_precio(producto['row'], producto['columnas_precio'], col_precio)
                    stock_disponible, origen_stock = obtener_stock_segun_tipo(sku, st.session_state.stock_data, st.session_state.es_xiaomi)
                    
                    resultados.append({
                        'id': sku,
                        'SKU': sku,
                        'Descripción': producto['descripcion'][:80],
                        'Precio': precio,
                        'Solicitado': cant_solicitada,
                        'Stock_Disponible': stock_disponible,
                        'A_Cotizar': min(cant_solicitada, stock_disponible) if stock_disponible > 0 else 0,
                        'Total': precio * min(cant_solicitada, stock_disponible) if stock_disponible > 0 else 0,
                        'Estado': '✅ OK' if stock_disponible >= cant_solicitada and precio > 0 else ('⚠️ Stock bajo' if stock_disponible > 0 else '❌ Sin stock'),
                        'Color_Estado': 'green' if stock_disponible >= cant_solicitada and precio > 0 else ('orange' if stock_disponible > 0 else 'red'),
                        'Origen_Stock': origen_stock
                    })
                
                st.session_state.resultados = resultados
        
        if st.session_state.resultados:
            st.markdown("---")
            st.markdown("### 📊 Resultados (edita cantidades)")
            resultados_editados = []
            
            cols = st.columns([2, 3, 1, 1, 1, 1.2, 1.5])
            cols[0].markdown("**SKU**")
            cols[1].markdown("**Descripción**")
            cols[2].markdown("**Precio**")
            cols[3].markdown("**Sol.**")
            cols[4].markdown("**Stock**")
            cols[5].markdown("**A Cotizar**")
            cols[6].markdown("**Estado**")
            st.divider()
            
            for i, item in enumerate(st.session_state.resultados):
                col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 3, 1, 1, 1, 1.2, 1.5])
                
                col1.markdown(f"`{item['SKU']}`")
                col2.markdown(item['Descripción'][:50])
                col3.markdown(f"S/. {item['Precio']:,.2f}" if item['Precio'] > 0 else "-")
                col4.markdown(str(item['Solicitado']))
                col5.markdown(str(item['Stock_Disponible']))
                
                nueva_cantidad = col6.number_input(
                    "Cant", min_value=0, max_value=9999,
                    value=int(item['A_Cotizar']),
                    key=f"cant_{item['id']}_{i}",
                    label_visibility="collapsed"
                )
                nuevo_total = item['Precio'] * nueva_cantidad
                
                if nueva_cantidad == 0:
                    estado_texto = "⏸️ Excluido"
                    color_estado = "gray"
                elif item['Precio'] == 0:
                    estado_texto = "⚠️ Sin precio"
                    color_estado = "orange"
                elif nueva_cantidad <= item['Stock_Disponible']:
                    estado_texto = "✅ OK"
                    color_estado = "green"
                else:
                    estado_texto = f"⚠️ Excede stock ({item['Stock_Disponible']} disp.)"
                    color_estado = "orange"
                
                col7.markdown(f"<span style='color:{color_estado}'>{estado_texto}</span>", unsafe_allow_html=True)
                col7.caption(f"📦 {item['Origen_Stock'][:30]}" if item['Origen_Stock'] else "")
                
                item_editado = item.copy()
                item_editado['A_Cotizar'] = nueva_cantidad
                item_editado['Total'] = nuevo_total
                resultados_editados.append(item_editado)
                st.divider()
            
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
# TAB 2: BUSCAR PRODUCTOS
# ============================================
with tab_buscar:
    st.markdown("### 🔍 Buscar y Agregar Productos")
    
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
        
        st.markdown("#### 🔎 Buscar por descripción o SKU")
        busqueda = st.text_input("Buscar productos:", placeholder="Ej: cable, cargador, CN0900009WH8")
        
        if busqueda and len(busqueda) >= 3:
            with st.spinner("Buscando..."):
                precio_seleccionado = None if col_precio_consulta == "(No mostrar precio)" else col_precio_consulta
                resultados = buscar_en_catalogos(st.session_state.catalogos, busqueda, precio_seleccionado)
            
            if resultados:
                st.success(f"✅ {len(resultados)} resultados encontrados")
                
                for res in resultados:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([2, 4, 1, 1.5])
                        with col1:
                            st.markdown(f"**📦 {res['SKU']}**")
                        with col2:
                            st.markdown(res['Descripción'][:60])
                        with col3:
                            precio_text = f"S/. {res['Precio']:,.2f}" if res['Precio'] else "Sin precio"
                            st.markdown(f"💰 {precio_text}")
                        with col4:
                            cantidad = st.number_input(
                                "Cant", min_value=0, max_value=999, value=0,
                                key=f"multi_{res['SKU']}",
                                label_visibility="collapsed"
                            )
                            if cantidad > 0:
                                st.session_state.productos_seleccionados[res['SKU']] = st.session_state.productos_seleccionados.get(res['SKU'], 0) + cantidad
                        st.divider()
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
st.markdown("*💚 QTC Smart Sales Pro - Sistema Profesional de Cotización*")
