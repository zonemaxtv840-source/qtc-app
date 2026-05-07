import streamlit as st
import pandas as pd
import re, io
from datetime import datetime
from PIL import Image
import numpy as np
import warnings
warnings.filterwarnings('ignore')

try:
    img_logo = Image.open("logo.png")
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon=img_logo, layout="wide")
except:
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon="💼", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #F1F8E9 !important; }
.main .block-container { background-color: #F1F8E9 !important; }
h1, h2, h3, h4, h5, h6, p, div, span, label, .stMarkdown { color: #1B5E20 !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #2E7D32 0%, #1B5E20 100%); }
[data-testid="stSidebar"] * { color: white !important; }
.stButton > button { background: #66BB6A !important; color: white !important; border-radius: 12px; font-weight: 600; border: none; }
.stButton > button:hover { background: #4CAF50 !important; }
.stSelectbox > div > div { background-color: white !important; color: black !important; border: 1px solid #66BB6A !important; border-radius: 10px !important; }
.stSelectbox label { color: #1B5E20 !important; }
div[data-baseweb="select"] ul { background-color: white !important; border: 1px solid #ddd !important; border-radius: 10px !important; }
div[data-baseweb="select"] li { color: black !important; background-color: white !important; }
div[data-baseweb="select"] li:hover { background-color: #E8F5E9 !important; }
div[data-baseweb="select"] li[aria-selected="true"] { background-color: #66BB6A !important; color: white !important; }
.stFileUploader > div > div { background-color: white !important; border: 1px dashed #66BB6A !important; border-radius: 12px !important; }
.stFileUploader button { background-color: #66BB6A !important; color: white !important; }
.stTextInput input, .stTextArea textarea, .stNumberInput input { color: black !important; background-color: white !important; border: 1px solid #ddd !important; border-radius: 10px !important; }
.stTabs [data-baseweb="tab-list"] { background-color: white !important; border-radius: 12px !important; padding: 6px !important; gap: 8px !important; }
.stTabs [data-baseweb="tab"] { color: #1B5E20 !important; background-color: #F5F5F5 !important; border-radius: 10px !important; padding: 10px 20px !important; }
.stTabs [aria-selected="true"] { background-color: #66BB6A !important; color: white !important; }
.metric-card { background: white; border-radius: 20px; padding: 1.5rem; text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,0.05); border: 1px solid #C8E6C9; }
.metric-value { font-size: 2.2rem; font-weight: bold; color: #66BB6A !important; }
.excluded-report { background: #FFF8E1; border-left: 4px solid #FFC107; padding: 0.8rem; margin: 0.5rem 0; border-radius: 8px; }
.excluded-sku { font-family: monospace; font-weight: bold; color: #E65100; }
.excluded-reason { color: #FF8F00; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.markdown("💚 QTC Pro")
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
            logo = Image.open("logo.png")
            st.image(logo, width=120)
        except:
            pass
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 20px;">
            <h1 style="text-align: center; color: #66BB6A;">QTC Smart Sales</h1>
            <p style="text-align: center;">Sistema Profesional de Cotizacion</p>
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
        hoja_seleccionada = st.sidebar.selectbox(f"Hoja {archivo.name}:", hojas, key=f"cat_{archivo.name}")
        df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)
        df = limpiar_cabeceras(df)
        
        posibles_skus = ['SKU', 'COD', 'CODIGO', 'SAP', 'NUMERO', 'ARTICULO', 'COD SAP']
        posibles_desc = ['DESC', 'DESCRIPCION', 'NOMBRE', 'PRODUCTO']
        posibles_precios = ['PRECIO', 'CAJA', 'VIP', 'MAYOR', 'IR', 'BOX', 'SUGERIDO']
        
        col_sku = df.columns[0]
        for c in df.columns:
            if any(p in str(c).upper() for p in posibles_skus):
                col_sku = c
                break
        
        col_desc = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        for c in df.columns:
            if any(p in str(c).upper() for p in posibles_desc):
                col_desc = c
                break
        
        columnas_precio = [c for c in df.columns if any(p in str(c).upper() for p in posibles_precios)]
        
        with st.sidebar.expander(f"Cols {archivo.name[:20]}"):
            st.caption(f"SKU: {col_sku}")
            st.caption(f"Desc: {col_desc}")
            if columnas_precio:
                st.caption(f"Precios: {', '.join(columnas_precio[:3])}")
        
        return {
            'nombre': f"{archivo.name} [{hoja_seleccionada}]",
            'df': df,
            'col_sku': col_sku,
            'col_desc': col_desc,
            'columnas_precio': columnas_precio
        }
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def cargar_stock(archivo):
    try:
        xls = pd.ExcelFile(archivo)
        hojas = xls.sheet_names
        hoja_seleccionada = st.sidebar.selectbox(f"Stock {archivo.name}:", hojas, key=f"stock_{archivo.name}")
        df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)
        df = limpiar_cabeceras(df)
        
        posibles_skus = ['SKU', 'COD', 'CODIGO', 'NUMERO', 'ARTICULO']
        posibles_stock = ['STOCK', 'DISPONIBLE', 'CANT', 'CANTIDAD', 'SALDO']
        
        col_sku = df.columns[0]
        for c in df.columns:
            if any(p in str(c).upper() for p in posibles_skus):
                col_sku = c
                break
        
        col_stock = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        for c in df.columns:
            if any(p in str(c).upper() for p in posibles_stock):
                col_stock = c
                break
        
        with st.sidebar.expander(f"Stock {archivo.name[:20]}"):
            st.caption(f"SKU: {col_sku}")
            st.caption(f"Stock: {col_stock}")
        
        return {
            'nombre': f"{archivo.name} [{hoja_seleccionada}]",
            'df': df,
            'col_sku': col_sku,
            'col_stock': col_stock
        }
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def buscar_precio(catalogos, sku):
    sku_limpio = sku.strip().upper()
    for cat in catalogos:
        df = cat['df']
        col_sku = cat['col_sku']
        mask = df[col_sku].astype(str).str.strip().str.upper() == sku_limpio
        if not df[mask].empty:
            row = df[mask].iloc[0]
            return {
                'encontrado': True,
                'catalogo': cat['nombre'],
                'row': row,
                'columnas_precio': cat['columnas_precio'],
                'descripcion': str(row[cat['col_desc']])
            }
        mask = df[col_sku].astype(str).str.contains(sku_limpio, case=False, na=False)
        if not df[mask].empty:
            row = df[mask].iloc[0]
            return {
                'encontrado': True,
                'catalogo': cat['nombre'],
                'row': row,
                'columnas_precio': cat['columnas_precio'],
                'descripcion': str(row[cat['col_desc']])
            }
    return {'encontrado': False}

def buscar_stock(stocks, sku):
    sku_limpio = sku.strip().upper()
    for stock in stocks:
        mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
        if not stock['df'][mask].empty:
            row = stock['df'][mask].iloc[0]
            cantidad = int(corregir_numero(row[stock['col_stock']]))
            return cantidad, stock['nombre']
    return 0, "Sin stock"

def obtener_precio(row, columnas_precio, col_seleccionada):
    if col_seleccionada and col_seleccionada in columnas_precio and col_seleccionada in row.index:
        return corregir_numero(row[col_seleccionada])
    return 0.0

def generar_excel(items, cliente, ruc):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    pd.DataFrame(items).to_excel(writer, sheet_name='Cotizacion', index=False, startrow=5)
    
    workbook = writer.book
    ws = writer.sheets['Cotizacion']
    
    fmt_header = workbook.add_format({'bg_color': '#66BB6A', 'bold': True, 'border': 1, 'align': 'center', 'font_color': 'white'})
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
    
    headers = ['Codigo SAP', 'Descripcion', 'Cantidad', 'Precio Unit.', 'Total']
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

# Interfaz principal
try:
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        st.image("logo.png", width=70)
    with col_title:
        st.title("QTC Smart Sales Pro")
except:
    st.title("QTC Smart Sales Pro")

st.markdown("---")

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

tab_cotizacion, tab_dashboard = st.tabs(["Cotizacion", "Dashboard"])

with tab_cotizacion:
    with st.sidebar:
        st.markdown("### Archivos")
        
        archivos_catalogos = st.file_uploader("Catalogos de Precios", type=['xlsx', 'xls'], accept_multiple_files=True, key="cat_upload")
        if archivos_catalogos:
            for archivo in archivos_catalogos:
                resultado = cargar_catalogo(archivo)
                if resultado:
                    st.session_state.catalogos.append(resultado)
                    st.success(f"OK {resultado['nombre'][:50]}")
        
        archivos_stock = st.file_uploader("Reportes de Stock", type=['xlsx', 'xls'], accept_multiple_files=True, key="stock_upload")
        if archivos_stock:
            for archivo in archivos_stock:
                resultado = cargar_stock(archivo)
                if resultado:
                    st.session_state.stocks.append(resultado)
                    st.success(f"OK {resultado['nombre'][:50]}")
    
    if not st.session_state.catalogos:
        st.warning("Carga catalogos en el panel izquierdo")
    else:
        with st.expander("Catalogos cargados"):
            for cat in st.session_state.catalogos:
                st.caption(f"- {cat['nombre'][:60]}")
        
        todas_columnas_precio = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio']:
                todas_columnas_precio.add(col)
        
        if todas_columnas_precio:
            col_precio = st.selectbox("Columna de precio:", sorted(list(todas_columnas_precio)))
        else:
            col_precio = None
            st.warning("No se detectaron columnas de precio")
        
        st.markdown("---")
        st.markdown("### Ingresa los productos")
        st.caption("Formato: SKU:CANTIDAD (uno por linea)")
        
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
        
        if st.button("PROCESAR COTIZACION", use_container_width=True, type="primary") and pedidos:
            with st.spinner("Procesando..."):
                resultados = []
                for pedido in pedidos:
                    sku = pedido['sku']
                    cant = pedido['cantidad']
                    precio_info = buscar_precio(st.session_state.catalogos, sku)
                    stock, origen_stock = buscar_stock(st.session_state.stocks, sku)
                    
                    if precio_info['encontrado'] and stock > 0:
                        precio = obtener_precio(precio_info['row'], precio_info['columnas_precio'], col_precio)
                        resultados.append({
                            'id': sku, 'SKU': sku, 'Descripcion': precio_info['descripcion'][:80],
                            'Precio': precio, 'Solicitado': cant, 'Stock': stock,
                            'A_Cotizar': min(cant, stock), 'Total': precio * min(cant, stock),
                            'Estado': 'OK', 'Color': 'green', 'Motivo': None
                        })
                    elif precio_info['encontrado'] and stock == 0:
                        precio = obtener_precio(precio_info['row'], precio_info['columnas_precio'], col_precio)
                        resultados.append({
                            'id': sku, 'SKU': sku, 'Descripcion': precio_info['descripcion'][:80],
                            'Precio': precio, 'Solicitado': cant, 'Stock': 0,
                            'A_Cotizar': 0, 'Total': 0, 'Estado': 'Sin stock', 'Color': 'orange',
                            'Motivo': 'Sin stock disponible'
                        })
                    elif not precio_info['encontrado'] and stock > 0:
                        resultados.append({
                            'id': sku, 'SKU': sku,
                            'Descripcion': f"Producto con stock ({stock} uds) pero sin precio",
                            'Precio': 0, 'Solicitado': cant, 'Stock': stock,
                            'A_Cotizar': 0, 'Total': 0, 'Estado': 'Sin precio', 'Color': 'orange',
                            'Motivo': 'No esta en lista de precios'
                        })
                    else:
                        resultados.append({
                            'id': sku, 'SKU': sku, 'Descripcion': 'Producto no encontrado',
                            'Precio': 0, 'Solicitado': cant, 'Stock': 0,
                            'A_Cotizar': 0, 'Total': 0, 'Estado': 'No encontrado', 'Color': 'red',
                            'Motivo': 'No existe en catalogos ni stock'
                        })
                
                st.session_state.resultados = resultados
        
        if st.session_state.resultados:
            st.markdown("---")
            st.markdown("### Resultados")
            
            resultados_editados = []
            
            c1, c2, c3, c4, c5, c6, c7 = st.columns([2, 3, 1.2, 1, 1, 1.2, 1.5])
            c1.markdown("**SKU**")
            c2.markdown("**Descripcion**")
            c3.markdown("**Precio**")
            c4.markdown("**Sol.**")
            c5.markdown("**Stock**")
            c6.markdown("**A Cotizar**")
            c7.markdown("**Estado**")
            st.divider()
            
            for i, item in enumerate(st.session_state.resultados):
                col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 3, 1.2, 1, 1, 1.2, 1.5])
                
                col1.markdown(f"`{item['SKU']}`")
                col2.markdown(item['Descripcion'][:50])
                col3.markdown(f"S/. {item['Precio']:,.2f}" if item['Precio'] > 0 else "X")
                col4.markdown(str(item['Solicitado']))
                col5.markdown(str(item['Stock']))
                
                if item['Precio'] > 0 and item['Stock'] > 0:
                    nueva_cant = col6.number_input("Cant", min_value=0, max_value=item['Stock'], value=int(item['A_Cotizar']), key=f"qty_{item['id']}_{i}", label_visibility="collapsed")
                else:
                    nueva_cant = 0
                    col6.markdown("0")
                
                col7.markdown(f"<span style='color:{item['Color']}'>{item['Estado']}</span>", unsafe_allow_html=True)
                
                item['A_Cotizar'] = nueva_cant
                item['Total'] = item['Precio'] * nueva_cant
                resultados_editados.append(item)
                st.divider()
            
            excluidos = [r for r in resultados_editados if r['A_Cotizar'] == 0 and r['Motivo']]
            if excluidos:
                st.markdown("### Productos no incluidos")
                for exc in excluidos:
                    st.markdown(f"""
                    <div class="excluded-report">
                        <span class="excluded-sku">SKU: {exc['SKU']}</span><br>
                        <span>{exc['Descripcion'][:60]}</span><br>
                        <span class="excluded-reason">Motivo: {exc['Motivo']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            items_validos = [r for r in resultados_editados if r['A_Cotizar'] > 0 and r['Precio'] > 0]
            total = sum(r['Total'] for r in items_validos)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("A cotizar", len(items_validos))
            col2.metric("Total", f"S/. {total:,.2f}")
            col3.metric("Excluidos", len(resultados_editados) - len(items_validos))
            
            if items_validos:
                st.markdown("---")
                st.markdown("### Generar Cotizacion")
                col_cli1, col_cli2 = st.columns(2)
                with col_cli1:
                    cliente = st.text_input("Cliente", "CLIENTE NUEVO")
                with col_cli2:
                    ruc_cliente = st.text_input("RUC/DNI", "-")
                
                if st.button("GENERAR EXCEL", use_container_width=True, type="primary"):
                    items_excel = [{'sku': r['SKU'], 'desc': r['Descripcion'], 'cant': r['A_Cotizar'], 'p_u': r['Precio'], 'total': r['Total']} for r in items_validos]
                    excel = generar_excel(items_excel, cliente, ruc_cliente)
                    st.download_button("DESCARGAR", data=excel, file_name=f"Cotizacion_{cliente}.xlsx", use_container_width=True)
                    st.session_state.cotizaciones += 1
                    st.session_state.total_prods = len(items_validos)
                    st.balloons()
                    st.success("Cotizacion generada")

with tab_dashboard:
    st.markdown("### Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("Cotizaciones", st.session_state.get('cotizaciones', 0))
    col2.metric("Productos", st.session_state.get('total_prods', 0))
    col3.metric("Catalogos", len(st.session_state.get('catalogos', [])))
    
    st.markdown("---")
    st.markdown("### Catalogos Cargados")
    for cat in st.session_state.get('catalogos', []):
        st.markdown(f"- {cat['nombre'][:60]}")
    
    st.markdown("---")
    st.markdown("### Stocks Cargados")
    for stock in st.session_state.get('stocks', []):
        st.markdown(f"- {stock['nombre'][:60]}")

st.markdown("---")
st.markdown("QTC Smart Sales Pro - Sistema de Cotizacion")
