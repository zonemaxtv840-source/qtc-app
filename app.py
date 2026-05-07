import streamlit as st
import pandas as pd
import re, io
from datetime import datetime
from PIL import Image
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ============================================
# CONFIGURACIÓN INICIAL
# ============================================
try:
    img_logo = Image.open("logo.png")
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon=img_logo, layout="wide")
except:
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon="💼", layout="wide")

# ============================================
# ESTILOS CSS
# ============================================
st.markdown("""
<style>
.stApp { background-color: #F1F8E9 !important; }
.main .block-container { background-color: #F1F8E9 !important; }
h1, h2, h3, h4, h5, h6 { color: #1B5E20 !important; }
p, div, span, label, .stMarkdown { color: #2E7D32 !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #1B5E20 0%, #0D3B0F 100%); }
[data-testid="stSidebar"] * { color: #F1F8E9 !important; }
.stButton > button { background: #4CAF50 !important; color: white !important; border-radius: 12px; font-weight: 600; border: none; transition: all 0.3s ease; }
.stButton > button:hover { background: #2E7D32 !important; transform: translateY(-2px); }
.stSelectbox > div > div { background-color: white !important; color: #1B5E20 !important; border: 1px solid #4CAF50 !important; border-radius: 10px !important; }
.stSelectbox label { color: #1B5E20 !important; }
div[data-baseweb="select"] ul { background-color: white !important; border: 1px solid #ddd !important; border-radius: 10px !important; }
div[data-baseweb="select"] li { color: #1B5E20 !important; background-color: white !important; }
div[data-baseweb="select"] li:hover { background-color: #E8F5E9 !important; }
div[data-baseweb="select"] li[aria-selected="true"] { background-color: #4CAF50 !important; color: white !important; }
.stFileUploader > div > div { background-color: white !important; border: 1px dashed #4CAF50 !important; border-radius: 12px !important; }
.stFileUploader button { background-color: #4CAF50 !important; color: white !important; }
.stTextInput input, .stTextArea textarea, .stNumberInput input { color: #1B5E20 !important; background-color: white !important; border: 1px solid #C8E6C9 !important; border-radius: 10px !important; }
.stTabs [data-baseweb="tab-list"] { background-color: white !important; border-radius: 12px !important; padding: 6px !important; }
.stTabs [data-baseweb="tab"] { color: #1B5E20 !important; background-color: #F5F5F5 !important; border-radius: 10px !important; padding: 10px 20px !important; }
.stTabs [aria-selected="true"] { background-color: #4CAF50 !important; color: white !important; }
.badge-ok { background-color: #C8E6C9; color: #1B5E20; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
.badge-warning { background-color: #FFF3E0; color: #E65100; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
.badge-danger { background-color: #FFCDD2; color: #C62828; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
.metric-card { background: white; border-radius: 20px; padding: 1.5rem; text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,0.05); border: 1px solid #C8E6C9; }
.metric-value { font-size: 2.2rem; font-weight: bold; color: #4CAF50 !important; }
.result-row { background: white; border-radius: 12px; padding: 1rem; margin-bottom: 0.8rem; border: 1px solid #C8E6C9; }
.result-sku { font-family: monospace; font-weight: bold; font-size: 1rem; color: #1B5E20; }
.result-price { font-size: 1.1rem; font-weight: bold; color: #4CAF50; }
.search-result-card { background: white; border-radius: 12px; padding: 1rem; margin: 0.5rem 0; border-left: 4px solid #4CAF50; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.stock-badge { display: inline-block; padding: 2px 8px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; margin-right: 5px; background-color: #E8F5E9; color: #1B5E20; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.markdown("## 💚 QTC Pro")
    st.markdown("---")
    if "cotizaciones" in st.session_state:
        st.metric("📄 Cotizaciones", st.session_state.get("cotizaciones", 0))
        st.metric("📦 Productos", st.session_state.get("total_prods", 0))

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        try:
            st.image("logo.png", width=120)
        except:
            pass
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 20px;">
            <h1 style="text-align: center; color: #4CAF50;">QTC Smart Sales</h1>
            <p style="text-align: center;">Sistema Profesional de Cotización</p>
        </div>
        """, unsafe_allow_html=True)
        user = st.text_input("Usuario")
        pw = st.text_input("Contraseña", type="password")
        if st.button("Ingresar", use_container_width=True):
            if user == "admin" and pw == "qtc2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
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
        if any(h in item for h in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO', 'COD SAP'] for item in fila):
            df.columns = [str(c).strip() for c in df.iloc[i]]
            return df.iloc[i+1:].reset_index(drop=True)
    return df

def cargar_catalogo(archivo):
    try:
        xls = pd.ExcelFile(archivo)
        hojas = xls.sheet_names
        hoja_seleccionada = st.sidebar.selectbox(f"📗 Hoja {archivo.name}:", hojas, key=f"cat_{archivo.name}")
        df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)
        df = limpiar_cabeceras(df)
        
        posibles_skus = ['SKU', 'COD', 'CODIGO', 'SAP', 'NUMERO', 'ARTICULO', 'COD SAP']
        posibles_desc = ['DESC', 'DESCRIPCION', 'NOMBRE', 'PRODUCTO']
        posibles_precios = ['PRECIO', 'CAJA', 'VIP', 'MAYOR', 'IR', 'BOX', 'SUGERIDO']
        
        col_sku = next((c for c in df.columns if any(p in str(c).upper() for p in posibles_skus)), df.columns[0])
        col_desc = next((c for c in df.columns if any(p in str(c).upper() for p in posibles_desc)), df.columns[1] if len(df.columns) > 1 else df.columns[0])
        columnas_precio = [c for c in df.columns if any(p in str(c).upper() for p in posibles_precios)]
        
        with st.sidebar.expander(f"📋 {archivo.name[:25]}..."):
            st.caption(f"SKU: {col_sku} | Desc: {col_desc}")
            if columnas_precio:
                st.caption(f"Precios: {', '.join(columnas_precio[:3])}")
        
        return {
            'nombre': f"{archivo.name} [{hoja_seleccionada}]",
            'df': df,
            'col_sku': col_sku,
            'col_desc': col_desc,
            'columnas_precio': columnas_precio
        }
    except:
        return None

def cargar_stock(archivo):
    try:
        xls = pd.ExcelFile(archivo)
        hojas = xls.sheet_names
        hoja_seleccionada = st.sidebar.selectbox(f"📦 Hoja {archivo.name}:", hojas, key=f"stock_{archivo.name}")
        df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)
        df = limpiar_cabeceras(df)
        
        posibles_skus = ['SKU', 'COD', 'CODIGO', 'NUMERO', 'ARTICULO']
        posibles_stock = ['STOCK', 'DISPONIBLE', 'CANT', 'CANTIDAD', 'SALDO']
        
        col_sku = next((c for c in df.columns if any(p in str(c).upper() for p in posibles_skus)), df.columns[0])
        col_stock = next((c for c in df.columns if any(p in str(c).upper() for p in posibles_stock)), df.columns[1] if len(df.columns) > 1 else df.columns[0])
        
        with st.sidebar.expander(f"📋 Stock {archivo.name[:25]}..."):
            st.caption(f"SKU: {col_sku} | Stock: {col_stock} | Hoja: {hoja_seleccionada}")
        
        return {
            'nombre': f"{archivo.name} [{hoja_seleccionada}]",
            'df': df,
            'col_sku': col_sku,
            'col_stock': col_stock,
            'hoja': hoja_seleccionada
        }
    except:
        return None

def buscar_precio(catalogos, sku, col_precio):
    sku_limpio = sku.strip().upper()
    for cat in catalogos:
        df = cat['df']
        mask = df[cat['col_sku']].astype(str).str.strip().str.upper() == sku_limpio
        if not df[mask].empty:
            row = df[mask].iloc[0]
            precio = corregir_numero(row[col_precio]) if col_precio in df.columns else 0
            return {
                'encontrado': True,
                'catalogo': cat['nombre'],
                'precio': precio,
                'descripcion': str(row[cat['col_desc']])
            }
        mask = df[cat['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
        if not df[mask].empty:
            row = df[mask].iloc[0]
            precio = corregir_numero(row[col_precio]) if col_precio in df.columns else 0
            return {
                'encontrado': True,
                'catalogo': cat['nombre'],
                'precio': precio,
                'descripcion': str(row[cat['col_desc']])
            }
    return {'encontrado': False, 'precio': 0, 'descripcion': ''}

def buscar_stock(stocks, sku, tipo_cotizacion):
    sku_limpio = sku.strip().upper()
    stock_total = 0
    detalles = {}
    
    for stock in stocks:
        hoja = stock['hoja'].upper()
        
        if tipo_cotizacion == "XIAOMI":
            if 'APRI.004' in hoja or 'YESSICA' in hoja:
                mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
                if not stock['df'][mask].empty:
                    row = stock['df'][mask].iloc[0]
                    cantidad = int(corregir_numero(row[stock['col_stock']]))
                    if cantidad > 0:
                        clave = f"{stock['nombre']}"
                        detalles[clave] = detalles.get(clave, 0) + cantidad
                        stock_total += cantidad
        else:
            if 'APRI.001' in hoja:
                mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
                if not stock['df'][mask].empty:
                    row = stock['df'][mask].iloc[0]
                    cantidad = int(corregir_numero(row[stock['col_stock']]))
                    if cantidad > 0:
                        clave = f"{stock['nombre']}"
                        detalles[clave] = detalles.get(clave, 0) + cantidad
                        stock_total += cantidad
    
    return stock_total, detalles

def buscar_en_catalogos(catalogos, termino, stocks, col_precio_consulta=None, tipo_cotizacion="XIAOMI"):
    resultados_dict = {}
    
    if ',' in termino:
        terminos = [t.strip() for t in termino.split(',') if len(t.strip()) >= 2]
    else:
        terminos = [t.strip() for t in termino.split() if len(t.strip()) >= 2]
    
    if not terminos:
        terminos = [termino.strip()]
    
    for cat in catalogos:
        df = cat['df']
        for term in terminos:
            mask_sku = df[cat['col_sku']].astype(str).str.contains(term, case=False, na=False)
            mask_desc = df[cat['col_desc']].astype(str).str.contains(term, case=False, na=False)
            for idx, row in df[mask_sku | mask_desc].iterrows():
                sku = str(row[cat['col_sku']])
                
                if sku not in resultados_dict:
                    precio = None
                    if col_precio_consulta and col_precio_consulta != "(No mostrar precio)":
                        precio = corregir_numero(row[col_precio_consulta]) if col_precio_consulta in df.columns else 0
                    
                    stock_total, stocks_detalle = buscar_stock(stocks, sku, tipo_cotizacion)
                    
                    resultados_dict[sku] = {
                        'SKU': sku,
                        'Descripcion': str(row[cat['col_desc']])[:100],
                        'Catalogo': cat['nombre'],
                        'Precio': precio,
                        'Stock_Total': stock_total,
                        'Stocks_Detalle': stocks_detalle
                    }
    
    return list(resultados_dict.values())

def generar_excel(items, cliente, ruc):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    pd.DataFrame(items).to_excel(writer, sheet_name='Cotizacion', index=False, startrow=5)
    
    workbook = writer.book
    ws = writer.sheets['Cotizacion']
    
    fmt_header = workbook.add_format({'bg_color': '#4CAF50', 'bold': True, 'border': 1, 'align': 'center', 'font_color': 'white'})
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
try:
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        st.image("logo.png", width="70px")
    with col_title:
        st.title("QTC Smart Sales Pro")
except:
    st.title("QTC Smart Sales Pro")

st.markdown("---")

# ============================================
# SELECCIÓN DE TIPO DE COTIZACIÓN
# ============================================
if 'tipo_cotizacion' not in st.session_state:
    st.session_state.tipo_cotizacion = None

if st.session_state.tipo_cotizacion is None:
    st.markdown("### 🎯 ¿Qué vas a cotizar hoy?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔋 PRODUCTOS XIAOMI", use_container_width=True):
            st.session_state.tipo_cotizacion = "XIAOMI"
            st.rerun()
    with col2:
        if st.button("💼 PRODUCTOS GENERALES", use_container_width=True):
            st.session_state.tipo_cotizacion = "GENERAL"
            st.rerun()
    st.stop()

if st.session_state.tipo_cotizacion == "XIAOMI":
    st.success("🔋 **Modo XIAOMI** - Buscando stock en: APRI.004 y YESSICA SEPARADO")
else:
    st.info("💼 **Modo GENERAL** - Buscando stock en: APRI.001")

st.markdown("---")

# ============================================
# INICIALIZAR SESSION STATE
# ============================================
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
if 'productos_seleccionados' not in st.session_state:
    st.session_state.productos_seleccionados = {}

tab_cotizacion, tab_buscar, tab_dashboard = st.tabs(["📦 Cotización", "🔍 Buscar Productos", "📊 Dashboard"])

# ============================================
# TAB 1: COTIZACIÓN
# ============================================
with tab_cotizacion:
    with st.sidebar:
        st.markdown("### 📂 Archivos")
        
        archivos_catalogos = st.file_uploader("📚 Catálogos de Precios", type=['xlsx', 'xls'], accept_multiple_files=True, key="cat_upload")
        if archivos_catalogos:
            st.session_state.catalogos = []
            for archivo in archivos_catalogos:
                resultado = cargar_catalogo(archivo)
                if resultado:
                    st.session_state.catalogos.append(resultado)
                    st.success(f"✅ {resultado['nombre'][:50]}")
        
        archivos_stock = st.file_uploader("📦 Reportes de Stock", type=['xlsx', 'xls'], accept_multiple_files=True, key="stock_upload")
        if archivos_stock:
            st.session_state.stocks = []
            for archivo in archivos_stock:
                resultado = cargar_stock(archivo)
                if resultado:
                    st.session_state.stocks.append(resultado)
                    st.success(f"✅ {resultado['nombre'][:50]}")
    
    if not st.session_state.catalogos:
        st.warning("🌿 Carga catálogos en el panel izquierdo")
    else:
        with st.expander("📋 Catálogos cargados"):
            for cat in st.session_state.catalogos:
                st.caption(f"• {cat['nombre']}")
        
        todas_columnas_precio = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio']:
                todas_columnas_precio.add(col)
        
        if todas_columnas_precio:
            col_precio = st.selectbox("💰 Columna de precio:", sorted(list(todas_columnas_precio)))
        else:
            col_precio = None
            st.warning("⚠️ No se detectaron columnas de precio")
        
        st.markdown("---")
        st.markdown("### 📝 Ingresa los productos")
        st.caption("Formato: SKU:CANTIDAD (uno por línea)")
        
        texto_skus = st.text_area("", height=150, placeholder="RN0200046BK8:5\nCN0900009WH8:2")
        
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
        
        if st.button("🚀 PROCESAR", use_container_width=True, type="primary") and pedidos:
            with st.spinner("🔍 Procesando..."):
                resultados = []
                for pedido in pedidos:
                    sku = pedido['sku']
                    cant = pedido['cantidad']
                    
                    precio_info = buscar_precio(st.session_state.catalogos, sku, col_precio)
                    stock_total, stock_detalle = buscar_stock(st.session_state.stocks, sku, st.session_state.tipo_cotizacion)
                    
                    icono = "🔋" if st.session_state.tipo_cotizacion == "XIAOMI" else "💼"
                    
                    if precio_info['encontrado'] and stock_total > 0:
                        a_cotizar = min(cant, stock_total)
                        total = precio_info['precio'] * a_cotizar
                        badge = "badge-ok"
                        estado = "✅ OK"
                    elif precio_info['encontrado'] and stock_total == 0:
                        a_cotizar = 0
                        total = 0
                        badge = "badge-warning"
                        estado = "⚠️ Sin stock"
                    elif not precio_info['encontrado'] and stock_total > 0:
                        a_cotizar = 0
                        total = 0
                        badge = "badge-warning"
                        estado = "⚠️ Sin precio"
                    else:
                        a_cotizar = 0
                        total = 0
                        badge = "badge-danger"
                        estado = "❌ No encontrado"
                    
                    resultados.append({
                        'SKU': sku,
                        'Tipo': f"{icono} {st.session_state.tipo_cotizacion}",
                        'Descripción': precio_info['descripcion'][:80] if precio_info['descripcion'] else f"SKU: {sku}",
                        'Precio': precio_info['precio'],
                        'Solicitado': cant,
                        'Stock': stock_total,
                        'Stock_Detalle': stock_detalle,
                        'A Cotizar': a_cotizar,
                        'Total': total,
                        'Estado': estado,
                        'Badge': badge
                    })
                
                st.session_state.resultados = resultados
        
        if st.session_state.resultados:
            st.markdown("---")
            st.markdown("### 📊 Resultados")
            
            # Mostrar resultados en filas individuales
            for i, item in enumerate(st.session_state.resultados):
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 1.5, 1, 2])
                    
                    with col1:
                        st.markdown(f"**📦 {item['SKU']}**")
                        st.caption(item['Descripción'][:60])
                        if item['Stock_Detalle']:
                            for origen, stock in item['Stock_Detalle'].items():
                                st.caption(f"📁 {origen}: {stock} uds")
                    
                    with col2:
                        st.markdown(f"💰 **Precio:** {f'S/. {item["Precio"]:,.2f}' if item['Precio'] > 0 else 'Sin precio'}")
                        st.markdown(f"📦 **Stock total:** {item['Stock']}")
                        st.markdown(f"📋 **Tipo:** {item['Tipo']}")
                    
                    with col3:
                        if item['Precio'] > 0:
                            nueva_cant = st.number_input(
                                "Cantidad",
                                min_value=0,
                                max_value=max(item['Stock'], 9999),
                                value=item['A Cotizar'],
                                key=f"cant_{i}",
                                label_visibility="collapsed"
                            )
                        else:
                            nueva_cant = 0
                            st.markdown("**No cotizable**")
                    
                    with col4:
                        if item['Precio'] > 0:
                            nuevo_total = item['Precio'] * nueva_cant
                            st.markdown(f"**💰 Total: S/. {nuevo_total:,.2f}**")
                            st.markdown(f"<span class='{item['Badge']}'>{item['Estado']}</span>", unsafe_allow_html=True)
                            item['A Cotizar'] = nueva_cant
                            item['Total'] = nuevo_total
                        else:
                            st.markdown(f"<span class='{item['Badge']}'>{item['Estado']}</span>", unsafe_allow_html=True)
                            item['A Cotizar'] = 0
                            item['Total'] = 0
                    
                    st.divider()
            
            # Resumen
            items_validos = [r for r in st.session_state.resultados if r['A Cotizar'] > 0 and r['Precio'] > 0]
            total_general = sum(r['Total'] for r in items_validos)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("✅ A cotizar", len(items_validos))
            col2.metric("💰 Total", f"S/. {total_general:,.2f}")
            col3.metric("⚠️ Excluidos", len(st.session_state.resultados) - len(items_validos))
            
            if items_validos:
                st.markdown("---")
                st.markdown("### 📥 Generar Cotización")
                col_cli1, col_cli2 = st.columns(2)
                with col_cli1:
                    cliente = st.text_input("🏢 Cliente", "CLIENTE NUEVO")
                with col_cli2:
                    ruc_cliente = st.text_input("📋 RUC/DNI", "-")
                
                if st.button("📥 GENERAR EXCEL", use_container_width=True, type="primary"):
                    items_excel = [{'sku': r['SKU'], 'desc': r['Descripción'], 'cant': r['A Cotizar'], 'p_u': r['Precio'], 'total': r['Total']} for r in items_validos]
                    excel = generar_excel(items_excel, cliente, ruc_cliente)
                    st.download_button("💾 DESCARGAR", data=excel, file_name=f"Cotizacion_{cliente}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", use_container_width=True)
                    st.session_state.cotizaciones += 1
                    st.session_state.total_prods = len(items_validos)
                    st.balloons()
                    st.success("✅ Cotización generada")

# ============================================
# TAB 2: BUSCAR PRODUCTOS
# ============================================
with tab_buscar:
    st.markdown("### 🔍 Buscar Productos")
    st.caption("💡 Busca por SKU o descripción - Muestra stock y precio en tiempo real")
    
    if not st.session_state.catalogos:
        st.warning("🌿 Primero carga catálogos en la pestaña Cotización")
    else:
        todas_columnas = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio']:
                todas_columnas.add(col)
        
        col_precio_consulta = st.selectbox(
            "💰 Mostrar precios en columna:",
            options=["(No mostrar precio)"] + sorted(list(todas_columnas)),
            key="precio_busqueda"
        )
        
        busqueda = st.text_input("🔎 Buscar:", placeholder="Ej: cable cargador RN0200046BK8")
        
        if busqueda and len(busqueda) >= 2:
            with st.spinner("🔍 Buscando..."):
                precio_seleccionado = None if col_precio_consulta == "(No mostrar precio)" else col_precio_consulta
                resultados = buscar_en_catalogos(
                    st.session_state.catalogos, 
                    busqueda, 
                    st.session_state.stocks, 
                    precio_seleccionado,
                    st.session_state.tipo_cotizacion
                )
            
            if resultados:
                st.success(f"✅ {len(resultados)} resultados encontrados")
                
                for res in resultados:
                    if res['Stock_Total'] <= 0:
                        stock_icon = "🔴 Sin stock"
                    elif res['Stock_Total'] < 10:
                        stock_icon = f"🟠 Stock bajo: {res['Stock_Total']}"
                    else:
                        stock_icon = f"🟢 Stock disponible: {res['Stock_Total']}"
                    
                    stock_detalle = ""
                    for origen, stock in res['Stocks_Detalle'].items():
                        if stock > 0:
                            stock_detalle += f'<span class="stock-badge">📁 {origen}: {stock} uds</span> '
                    
                    st.markdown(f"""
                    <div class="search-result-card">
                        <div>
                            <span class="search-sku">📦 {res['SKU']}</span><br>
                            <span class="search-desc">{res['Descripcion']}</span>
                            <span class="search-price">{f'S/. {res["Precio"]:,.2f}' if res["Precio"] else "💰 Sin precio"}</span>
                        </div>
                        <div class="search-stock">
                            {stock_icon}<br>
                            {stock_detalle}
                            <div style="font-size:0.7rem; color:#888; margin-top:5px;">📁 Catálogo: {res['Catalogo'][:50]}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown("**➕ Agregar a cotización**")
                    with col2:
                        cantidad = st.number_input("Cant", min_value=0, max_value=999, value=0, key=f"add_{res['SKU']}", label_visibility="collapsed")
                        if cantidad > 0:
                            st.session_state.productos_seleccionados[res['SKU']] = st.session_state.productos_seleccionados.get(res['SKU'], 0) + cantidad
                    st.divider()
            else:
                st.warning("No se encontraron productos")
        
        if st.session_state.productos_seleccionados:
            st.markdown("---")
            st.markdown(f"### ✅ Productos seleccionados ({len(st.session_state.productos_seleccionados)})")
            
            seleccionados_lista = []
            for sku, cant in st.session_state.productos_seleccionados.items():
                stock_total, _ = buscar_stock(st.session_state.stocks, sku, st.session_state.tipo_cotizacion)
                seleccionados_lista.append({
                    'SKU': sku,
                    'Cantidad': cant,
                    'Stock disponible': stock_total,
                    'Estado': '⚠️ Stock insuficiente' if cant > stock_total else '✅ OK'
                })
            
            st.dataframe(pd.DataFrame(seleccionados_lista), use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Limpiar todo", use_container_width=True):
                    st.session_state.productos_seleccionados = {}
                    st.rerun()
            with col2:
                if st.button("📋 TRANSFERIR A COTIZACIÓN", use_container_width=True, type="primary"):
                    st.session_state.skus_transferidos = st.session_state.productos_seleccionados.copy()
                    st.session_state.productos_seleccionados = {}
                    st.success(f"✅ {len(st.session_state.skus_transferidos)} productos transferidos!")
                    st.info("👉 Ve a la pestaña Cotización y haz clic en PROCESAR")

# ============================================
# TAB 3: DASHBOARD
# ============================================
with tab_dashboard:
    st.markdown("### 📊 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📄 Cotizaciones", st.session_state.get('cotizaciones', 0))
    col2.metric("🌿 Productos", st.session_state.get('total_prods', 0))
    col3.metric("📚 Catálogos", len(st.session_state.get('catalogos', [])))
    
    st.markdown("---")
    st.markdown("### 📋 Catálogos Cargados")
    for cat in st.session_state.get('catalogos', []):
        st.markdown(f"- {cat['nombre']}")
    
    st.markdown("---")
    st.markdown("### 📋 Stocks Cargados")
    for stock in st.session_state.get('stocks', []):
        st.markdown(f"- {stock['nombre']} - Hoja: {stock['hoja']}")
    
    st.markdown("---")
    st.markdown("### 🎯 Reglas actuales")
    if st.session_state.tipo_cotizacion == "XIAOMI":
        st.markdown("🔋 **Modo XIAOMI** → Stock en APRI.004 / YESSICA SEPARADO")
    else:
        st.markdown("💼 **Modo GENERAL** → Stock en APRI.001")

st.markdown("---")
st.markdown("*💚 QTC Smart Sales Pro - Sistema Robusto de Cotización*")
