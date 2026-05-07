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
.stApp { background-color: #E8F5E9 !important; }
.main .block-container { background-color: #E8F5E9 !important; }
h1, h2, h3, h4, h5, h6 { color: #1B5E20 !important; }
p, div, span, label, .stMarkdown { color: #2E7D32 !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #1B5E20 0%, #0D3B0F 100%); }
[data-testid="stSidebar"] * { color: #F1F8E9 !important; }
.stButton > button { background: #4CAF50 !important; color: white !important; border-radius: 12px; font-weight: 600; border: none; }
.stButton > button:hover { background: #2E7D32 !important; }
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
.dataframe-container { background: white; border-radius: 16px; padding: 0; overflow-x: auto; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.dataframe-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.dataframe-table th { background-color: #4CAF50; color: white; padding: 12px 8px; text-align: left; font-weight: 600; }
.dataframe-table td { padding: 10px 8px; border-bottom: 1px solid #E8F5E9; color: #2E7D32; }
.dataframe-table tr:hover { background-color: #F1F8E9; }
.badge-ok { background-color: #C8E6C9; color: #1B5E20; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
.badge-warning { background-color: #FFF3E0; color: #E65100; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
.badge-danger { background-color: #FFCDD2; color: #C62828; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
.metric-card { background: white; border-radius: 20px; padding: 1.5rem; text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,0.05); border: 1px solid #C8E6C9; }
.metric-value { font-size: 2.2rem; font-weight: bold; color: #4CAF50 !important; }
.search-result-card { background: white; border-radius: 12px; padding: 1rem; margin: 0.5rem 0; border-left: 4px solid #4CAF50; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.search-sku { font-size: 1rem; font-weight: bold; font-family: monospace; color: #1B5E20; }
.search-desc { font-size: 0.85rem; color: #2E7D32; margin: 4px 0; }
.search-price { font-size: 1rem; font-weight: bold; color: #4CAF50; }
.stock-badge { display: inline-block; padding: 2px 8px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; margin-right: 5px; background-color: #E8F5E9; color: #1B5E20; }
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
            <h1 style="text-align: center; color: #4CAF50;">QTC Smart Sales</h1>
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

def cargar_excel(archivo):
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

def buscar_en_catalogos_multiple(catalogos, termino, stocks, col_precio_consulta=None):
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
                    
                    stock_total = 0
                    stocks_info = []
                    if stocks:
                        for stock in stocks:
                            mask_stock = stock['df'][stock['col_sku']].astype(str).str.contains(sku, case=False, na=False)
                            if not stock['df'][mask_stock].empty:
                                row_stock = stock['df'][mask_stock].iloc[0]
                                cantidad = int(corregir_numero(row_stock[stock['col_stock']])) if stock['col_stock'] else 0
                                stocks_info.append({'origen': stock['nombre'], 'stock': cantidad})
                                stock_total += cantidad
                    
                    resultados_dict[sku] = {
                        'SKU': sku,
                        'Descripcion': str(row[cat['col_desc']])[:100],
                        'Catalogo': cat['nombre'],
                        'Precio': precio,
                        'Stock_Total': stock_total,
                        'Stocks_Detalle': stocks_info
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
if 'productos_seleccionados' not in st.session_state:
    st.session_state.productos_seleccionados = {}

tab_cotizacion, tab_buscar, tab_dashboard = st.tabs(["📦 Cotizacion", "🔍 Buscar Productos", "📊 Dashboard"])

# ============================================
# TAB 1: COTIZACION
# ============================================
with tab_cotizacion:
    with st.sidebar:
        st.markdown("### 📂 Archivos")
        
        archivos_catalogos = st.file_uploader("Catalogos de Precios", type=['xlsx', 'xls'], accept_multiple_files=True, key="cat_upload")
        if archivos_catalogos:
            for archivo in archivos_catalogos:
                resultado = cargar_excel(archivo)
                if resultado:
                    st.session_state.catalogos.append(resultado)
                    st.success(f"✅ {resultado['nombre'][:50]}")
        
        archivos_stock = st.file_uploader("Reportes de Stock", type=['xlsx', 'xls'], accept_multiple_files=True, key="stock_upload")
        if archivos_stock:
            for archivo in archivos_stock:
                resultado = cargar_stock(archivo)
                if resultado:
                    st.session_state.stocks.append(resultado)
                    st.success(f"✅ {resultado['nombre'][:50]}")
    
    if not st.session_state.catalogos:
        st.warning("🌿 Carga catalogos en el panel izquierdo")
    else:
        with st.expander("📋 Catalogos cargados"):
            for cat in st.session_state.catalogos:
                st.caption(f"• {cat['nombre'][:60]}")
        
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
        st.caption("Formato: SKU:CANTIDAD (uno por linea)")
        
        if 'skus_transferidos' in st.session_state:
            texto_defecto = "\n".join([f"{sku}:{cant}" for sku, cant in st.session_state.skus_transferidos.items()])
            del st.session_state.skus_transferidos
        else:
            texto_defecto = ""
        
        texto_skus = st.text_area("", height=150, value=texto_defecto, placeholder="RN0200046BK8:5\nCN0900009WH8:2")
        
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
                            'SKU': sku,
                            'Descripcion': precio_info['descripcion'][:80],
                            'Precio': precio,
                            'Solicitado': cant,
                            'Stock': stock,
                            'A Cotizar': min(cant, stock),
                            'Total': precio * min(cant, stock),
                            'Estado': '✅ OK',
                            'Motivo': ''
                        })
                    elif precio_info['encontrado'] and stock == 0:
                        precio = obtener_precio(precio_info['row'], precio_info['columnas_precio'], col_precio)
                        resultados.append({
                            'SKU': sku,
                            'Descripcion': precio_info['descripcion'][:80],
                            'Precio': precio,
                            'Solicitado': cant,
                            'Stock': 0,
                            'A Cotizar': 0,
                            'Total': 0,
                            'Estado': '⚠️ Sin stock',
                            'Motivo': 'No hay unidades disponibles en stock'
                        })
                    elif not precio_info['encontrado'] and stock > 0:
                        resultados.append({
                            'SKU': sku,
                            'Descripcion': f"{sku} - Producto con stock ({stock} uds) pero sin precio",
                            'Precio': 0,
                            'Solicitado': cant,
                            'Stock': stock,
                            'A Cotizar': 0,
                            'Total': 0,
                            'Estado': '⚠️ Sin precio',
                            'Motivo': 'El SKU no esta registrado en el catalogo de precios'
                        })
                    else:
                        resultados.append({
                            'SKU': sku,
                            'Descripcion': 'Producto no encontrado',
                            'Precio': 0,
                            'Solicitado': cant,
                            'Stock': 0,
                            'A Cotizar': 0,
                            'Total': 0,
                            'Estado': '❌ No encontrado',
                            'Motivo': 'No existe en catalogos de precios ni en stock'
                        })
                
                st.session_state.resultados = resultados
        
        if st.session_state.resultados:
            st.markdown("---")
            st.markdown("### 📊 Resultados de la cotizacion")
            
            df_resultados = pd.DataFrame(st.session_state.resultados)
            
            df_resultados['Precio'] = df_resultados['Precio'].apply(lambda x: f"S/. {x:,.2f}" if x > 0 else "Sin precio")
            df_resultados['Total'] = df_resultados['Total'].apply(lambda x: f"S/. {x:,.2f}")
            
            html = '<div class="dataframe-container"><table class="dataframe-table">'
            html += '<tr>'
            for col in df_resultados.columns:
                html += f'<th>{col}</th>'
            html += '</tr>'
            
            for _, row in df_resultados.iterrows():
                estado = row['Estado']
                if '✅' in estado:
                    badge = 'badge-ok'
                elif '⚠️' in estado:
                    badge = 'badge-warning'
                else:
                    badge = 'badge-danger'
                
                html += '<tr>'
                html += f'<td style="font-family:monospace;">{row["SKU"]}</td>'
                html += f'<td style="max-width:300px;">{row["Descripcion"][:60]}</td>'
                html += f'<td>{row["Precio"]}</td>'
                html += f'<td>{row["Solicitado"]}</td>'
                html += f'<td>{row["Stock"]}</td>'
                html += f'<td>{row["A Cotizar"]}</td>'
                html += f'<td>{row["Total"]}</td>'
                html += f'<td><span class="{badge}">{row["Estado"]}</span></td>'
                html += f'<td style="color:#E65100; font-size:0.8rem;">{row["Motivo"]}</td>'
                html += '</tr>'
            html += '</table></div>'
            
            st.markdown(html, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### ✏️ Ajustar cantidades a cotizar")
            
            resultados_editados = []
            for i, item in enumerate(st.session_state.resultados):
                if item['Precio'] != "Sin precio" and item['Precio'] != 0 and item['Stock'] > 0:
                    col1, col2, col3 = st.columns([2, 1, 2])
                    with col1:
                        st.markdown(f"**{item['SKU']}** - {item['Descripcion'][:40]}")
                    with col2:
                        nueva_cant = st.number_input("Cantidad", min_value=0, max_value=item['Stock'], value=item['A Cotizar'], key=f"edit_{item['SKU']}_{i}", label_visibility="collapsed")
                    with col3:
                        nuevo_total = item['Precio'] * nueva_cant if isinstance(item['Precio'], (int, float)) else 0
                        st.markdown(f"💰 Total: S/. {nuevo_total:,.2f}")
                    
                    item['A Cotizar'] = nueva_cant
                    item['Total'] = nuevo_total
                resultados_editados.append(item)
            
            items_validos = [r for r in resultados_editados if r['A Cotizar'] > 0 and r['Precio'] != "Sin precio" and r['Precio'] != 0]
            total = sum(r['Total'] for r in items_validos)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("✅ A cotizar", len(items_validos))
            col2.metric("💰 Total", f"S/. {total:,.2f}")
            col3.metric("⚠️ Excluidos", len(resultados_editados) - len(items_validos))
            
            if items_validos:
                st.markdown("---")
                st.markdown("### 📥 Generar Cotizacion")
                col_cli1, col_cli2 = st.columns(2)
                with col_cli1:
                    cliente = st.text_input("🏢 Cliente", "CLIENTE NUEVO")
                with col_cli2:
                    ruc_cliente = st.text_input("📋 RUC/DNI", "-")
                
                if st.button("📥 GENERAR EXCEL", use_container_width=True, type="primary"):
                    items_excel = [{'sku': r['SKU'], 'desc': r['Descripcion'], 'cant': r['A Cotizar'], 'p_u': r['Precio'], 'total': r['Total']} for r in items_validos]
                    excel = generar_excel(items_excel, cliente, ruc_cliente)
                    st.download_button("💾 DESCARGAR", data=excel, file_name=f"Cotizacion_{cliente}.xlsx", use_container_width=True)
                    st.session_state.cotizaciones += 1
                    st.session_state.total_prods = len(items_validos)
                    st.balloons()
                    st.success("✅ Cotizacion generada")

# ============================================
# TAB 2: BUSCAR PRODUCTOS (CON NOMBRE COMPLETO)
# ============================================
with tab_buscar:
    st.markdown("### 🔍 Buscar Productos")
    st.caption("💡 Busca por SKU, nombre o descripcion - Separa terminos con espacios o comas")
    
    if not st.session_state.catalogos:
        st.warning("🌿 Primero carga catalogos en la pestaña Cotizacion")
    else:
        todas_columnas = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio']:
                todas_columnas.add(col)
        
        col_precio_consulta = st.selectbox("💰 Mostrar precios en columna:", options=["(No mostrar precio)"] + sorted(list(todas_columnas)), key="precio_busqueda")
        
        busqueda = st.text_input("🔎 Buscar:", placeholder="Ej: cable cargador RN0200046BK8")
        
        if busqueda and len(busqueda) >= 2:
            with st.spinner("🔍 Buscando..."):
                precio_seleccionado = None if col_precio_consulta == "(No mostrar precio)" else col_precio_consulta
                resultados = buscar_en_catalogos_multiple(st.session_state.catalogos, busqueda, st.session_state.stocks, precio_seleccionado)
            
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
                    for s in res['Stocks_Detalle']:
                        if s['stock'] > 0:
                            stock_detalle += f'<span class="stock-badge">📁 {s["origen"][:30]}: {s["stock"]}</span> '
                    
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
                            <div style="font-size:0.7rem; color:#888; margin-top:5px;">📁 Catalogo: {res['Catalogo']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown("**➕ Agregar a cotizacion**")
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
                stock_total, _ = buscar_stock(st.session_state.stocks, sku)
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
                if st.button("📋 TRANSFERIR A COTIZACION", use_container_width=True, type="primary"):
                    st.session_state.skus_transferidos = st.session_state.productos_seleccionados.copy()
                    st.session_state.productos_seleccionados = {}
                    st.success(f"✅ {len(st.session_state.skus_transferidos)} productos transferidos!")
                    st.info("👉 Ve a la pestaña Cotizacion y haz clic en PROCESAR")

# ============================================
# TAB 3: DASHBOARD
# ============================================
with tab_dashboard:
    st.markdown("### 📊 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📄 Cotizaciones", st.session_state.get('cotizaciones', 0))
    col2.metric("🌿 Productos", st.session_state.get('total_prods', 0))
    col3.metric("📚 Catalogos", len(st.session_state.get('catalogos', [])))
    
    st.markdown("---")
    st.markdown("### 📋 Catalogos Cargados")
    for cat in st.session_state.get('catalogos', []):
        st.markdown(f"- {cat['nombre'][:60]}")
    
    st.markdown("---")
    st.markdown("### 📋 Stocks Cargados")
    for stock in st.session_state.get('stocks', []):
        st.markdown(f"- {stock['nombre'][:60]}")
    
    st.markdown("---")
    st.markdown("### 🎯 Ayuda Rapida")
    st.markdown("**Formato de entrada:** SKU:CANTIDAD (uno por linea)")
    st.markdown("")
    st.markdown("**Ejemplo:**")
    st.markdown("```")
    st.markdown("RN0200046BK8:5")
    st.markdown("CN0900009WH8:2")
    st.markdown("```")
    st.markdown("")
    st.markdown("**Estados:**")
    st.markdown("- 🟢 OK → Tiene precio y stock")
    st.markdown("- 🟠 Sin stock → Tiene precio pero no hay stock")
    st.markdown("- 🟠 Sin precio → Tiene stock pero no esta en catalogo")
    st.markdown("- 🔴 No encontrado → No existe en ningun lado")

st.markdown("---")
st.markdown("*💚 QTC Smart Sales Pro - Sistema Profesional de Cotizacion*")
