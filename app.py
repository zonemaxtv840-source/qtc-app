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
.origin-badge-apri004 { background-color: #E1BEE7; color: #4A148C; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; margin-right: 5px; }
.origin-badge-yessica { background-color: #BBDEFB; color: #0D47A1; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; margin-right: 5px; }
.origin-badge-both { background-color: #C8E6C9; color: #1B5E20; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; margin-right: 5px; }
.metric-card { background: white; border-radius: 20px; padding: 1.5rem; text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,0.05); border: 1px solid #C8E6C9; }
.metric-value { font-size: 2rem; font-weight: bold; color: #4CAF50 !important; }
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
    
    st.markdown("---")
    
    # Botones para cambiar de modo
    st.markdown("### 🎯 Modo de Cotización")
    col_modo1, col_modo2 = st.columns(2)
    with col_modo1:
        if st.button("🔋 XIAOMI", use_container_width=True):
            st.session_state.tipo_cotizacion = "XIAOMI"
            st.rerun()
    with col_modo2:
        if st.button("💼 GENERAL", use_container_width=True):
            st.session_state.tipo_cotizacion = "GENERAL"
            st.rerun()
    
    if st.session_state.get("tipo_cotizacion") == "XIAOMI":
        st.success("🔋 Modo XIAOMI")
        st.caption("Stock: APRI.004 + YESSICA")
    else:
        st.info("💼 Modo GENERAL")
        st.caption("Stock: APRI.001")
    
    st.markdown("---")
    
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False
    st.session_state.debug_mode = st.checkbox("🔧 Modo Depuración", value=st.session_state.debug_mode)

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

def mapear_columna_precio(columnas, nombre_buscar):
    for col in columnas:
        col_upper = str(col).upper()
        if nombre_buscar.upper() in col_upper:
            return col
        if nombre_buscar.upper() == "P. IR" and "MAYORISTA" in col_upper:
            return col
        if nombre_buscar.upper() == "P. BOX" and "CAJA" in col_upper:
            return col
        if nombre_buscar.upper() == "P. VIP" and ("VIP" in col_upper or "P.VIP" in col_upper):
            return col
    return None

def cargar_catalogo(archivo):
    try:
        nombre = archivo.name.lower()
        
        if nombre.endswith('.csv'):
            contenido = archivo.getvalue()
            if contenido.startswith(b'\xef\xbb\xbf'):
                contenido = contenido[3:]
            from io import BytesIO
            try:
                df_raw = pd.read_csv(BytesIO(contenido), encoding='utf-8', header=None, on_bad_lines='skip')
            except:
                try:
                    df_raw = pd.read_csv(BytesIO(contenido), encoding='latin-1', header=None, on_bad_lines='skip')
                except:
                    df_raw = pd.read_csv(BytesIO(contenido), encoding='iso-8859-1', header=None, on_bad_lines='skip')
            
            header_row = None
            for i in range(min(100, len(df_raw))):
                for cell in df_raw.iloc[i].values:
                    if pd.notna(cell) and 'SKU' in str(cell).upper():
                        header_row = i
                        break
                if header_row is not None:
                    break
            
            if header_row is None:
                st.error(f"No se encontró cabecera con SKU en {archivo.name}")
                return None
            
            nuevas_columnas = [str(c).strip() if pd.notna(c) else f"Col_{i}" for i, c in enumerate(df_raw.iloc[header_row].values)]
            df_raw.columns = nuevas_columnas
            df = df_raw.iloc[header_row + 1:].reset_index(drop=True)
            df = df.dropna(axis=1, how='all')
            df = df.fillna('')
            hoja_nombre = "CSV"
        else:
            xls = pd.ExcelFile(archivo)
            hojas = xls.sheet_names
            hoja_seleccionada = st.sidebar.selectbox(f"📗 Hoja {archivo.name}:", hojas, key=f"cat_{archivo.name}")
            df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)
            df = limpiar_cabeceras(df)
            hoja_nombre = hoja_seleccionada
        
        posibles_skus = ['SKU', 'COD', 'CODIGO', 'SAP', 'NUMERO', 'ARTICULO', 'COD SAP']
        posibles_desc = ['DESC', 'DESCRIPCION', 'NOMBRE', 'PRODUCTO', 'NOMBRE PRODUCTO']
        
        col_sku = next((c for c in df.columns if any(p in str(c).upper() for p in posibles_skus)), df.columns[0])
        col_desc = next((c for c in df.columns if any(p in str(c).upper() for p in posibles_desc)), df.columns[1] if len(df.columns) > 1 else df.columns[0])
        
        columnas_precio = {}
        col_ir = mapear_columna_precio(df.columns, "P. IR")
        if col_ir:
            columnas_precio['P. IR'] = col_ir
        col_box = mapear_columna_precio(df.columns, "P. BOX")
        if col_box:
            columnas_precio['P. BOX'] = col_box
        col_vip = mapear_columna_precio(df.columns, "P. VIP")
        if col_vip:
            columnas_precio['P. VIP'] = col_vip
        if not columnas_precio:
            for c in df.columns:
                if 'PRECIO' in str(c).upper():
                    columnas_precio['PRECIO'] = c
                    break
        
        with st.sidebar.expander(f"📋 {archivo.name[:25]}..."):
            st.caption(f"SKU: {col_sku} | Desc: {col_desc}")
            st.caption(f"Precios: {', '.join(columnas_precio.keys()) if columnas_precio else 'No detectados'}")
        
        return {
            'nombre': f"{archivo.name} [{hoja_nombre}]",
            'df': df,
            'col_sku': col_sku,
            'col_desc': col_desc,
            'columnas_precio': columnas_precio
        }
    except Exception as e:
        st.error(f"Error en {archivo.name}: {str(e)[:100]}")
        return None

def cargar_stock_completo(archivo):
    try:
        todas_hojas = []
        nombre = archivo.name.lower()
        
        if nombre.endswith('.csv'):
            contenido = archivo.getvalue()
            if contenido.startswith(b'\xef\xbb\xbf'):
                contenido = contenido[3:]
            from io import BytesIO
            try:
                df = pd.read_csv(BytesIO(contenido), encoding='utf-8', on_bad_lines='skip')
            except:
                try:
                    df = pd.read_csv(BytesIO(contenido), encoding='latin-1', on_bad_lines='skip')
                except:
                    df = pd.read_csv(BytesIO(contenido), encoding='iso-8859-1', on_bad_lines='skip')
            
            df = limpiar_cabeceras(df)
            
            posibles_skus = ['SKU', 'COD', 'CODIGO', 'NUMERO', 'ARTICULO', 'NÚMERO DE ARTÍCULO']
            posibles_stock = ['STOCK', 'DISPONIBLE', 'CANT', 'CANTIDAD', 'SALDO', 'EN STOCK']
            
            col_sku = next((c for c in df.columns if any(p in str(c).upper() for p in posibles_skus)), df.columns[0])
            col_stock = next((c for c in df.columns if any(p in str(c).upper() for p in posibles_stock)), df.columns[1] if len(df.columns) > 1 else df.columns[0])
            
            todas_hojas.append({
                'nombre': f"{archivo.name} [CSV]",
                'df': df,
                'col_sku': col_sku,
                'col_stock': col_stock,
                'hoja': "CSV"
            })
        else:
            xls = pd.ExcelFile(archivo)
            for hoja in xls.sheet_names:
                df = pd.read_excel(archivo, sheet_name=hoja)
                df = limpiar_cabeceras(df)
                
                posibles_skus = ['SKU', 'COD', 'CODIGO', 'NUMERO', 'ARTICULO', 'NÚMERO DE ARTÍCULO']
                posibles_stock = ['STOCK', 'DISPONIBLE', 'CANT', 'CANTIDAD', 'SALDO', 'EN STOCK']
                
                col_sku = next((c for c in df.columns if any(p in str(c).upper() for p in posibles_skus)), df.columns[0])
                col_stock = next((c for c in df.columns if any(p in str(c).upper() for p in posibles_stock)), df.columns[1] if len(df.columns) > 1 else df.columns[0])
                
                todas_hojas.append({
                    'nombre': f"{archivo.name} [{hoja}]",
                    'df': df,
                    'col_sku': col_sku,
                    'col_stock': col_stock,
                    'hoja': hoja
                })
        
        return todas_hojas
    except Exception as e:
        st.error(f"Error cargando {archivo.name}: {str(e)[:100]}")
        return []

def buscar_precio_con_descripcion_stock(catalogos, stocks, sku, col_precio_seleccionada, tipo_cotizacion):
    sku_limpio = sku.strip().upper()
    
    for cat in catalogos:
        df = cat['df']
        mask = df[cat['col_sku']].astype(str).str.strip().str.upper() == sku_limpio
        if not df[mask].empty:
            row = df[mask].iloc[0]
            col_precio_real = cat['columnas_precio'].get(col_precio_seleccionada)
            if col_precio_real and col_precio_real in df.columns:
                precio = corregir_numero(row[col_precio_real])
            else:
                precio = 0
            return {
                'encontrado': True,
                'catalogo': cat['nombre'],
                'precio': precio,
                'descripcion': str(row[cat['col_desc']])
            }
        mask = df[cat['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
        if not df[mask].empty:
            row = df[mask].iloc[0]
            col_precio_real = cat['columnas_precio'].get(col_precio_seleccionada)
            if col_precio_real and col_precio_real in df.columns:
                precio = corregir_numero(row[col_precio_real])
            else:
                precio = 0
            return {
                'encontrado': True,
                'catalogo': cat['nombre'],
                'precio': precio,
                'descripcion': str(row[cat['col_desc']])
            }
    
    for stock in stocks:
        hoja = stock['hoja'].upper()
        if tipo_cotizacion == "XIAOMI":
            if 'APRI.004' in hoja or 'YESSICA' in hoja:
                mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
                if not stock['df'][mask].empty:
                    row = stock['df'][mask].iloc[0]
                    for col in stock['df'].columns:
                        if any(p in str(col).upper() for p in ['DESC', 'NOMBRE', 'PRODUCTO', 'DESCRIPCION']):
                            return {'encontrado': False, 'precio': 0, 'descripcion': str(row[col])[:80]}
                    return {'encontrado': False, 'precio': 0, 'descripcion': f"SKU: {sku}"}
        else:
            if 'APRI.001' in hoja:
                mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
                if not stock['df'][mask].empty:
                    row = stock['df'][mask].iloc[0]
                    for col in stock['df'].columns:
                        if any(p in str(col).upper() for p in ['DESC', 'NOMBRE', 'PRODUCTO', 'DESCRIPCION']):
                            return {'encontrado': False, 'precio': 0, 'descripcion': str(row[col])[:80]}
                    return {'encontrado': False, 'precio': 0, 'descripcion': f"SKU: {sku}"}
    
    return {'encontrado': False, 'precio': 0, 'descripcion': f"SKU: {sku}"}

def buscar_stock_xiaomi(stocks, sku):
    sku_limpio = sku.strip().upper()
    stock_apri004 = 0
    stock_yessica = 0
    
    for stock in stocks:
        hoja = stock['hoja'].upper()
        if 'APRI.004' in hoja:
            mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
            if not stock['df'][mask].empty:
                row = stock['df'][mask].iloc[0]
                stock_apri004 = int(corregir_numero(row[stock['col_stock']]))
        elif 'YESSICA' in hoja:
            mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
            if not stock['df'][mask].empty:
                row = stock['df'][mask].iloc[0]
                stock_yessica = int(corregir_numero(row[stock['col_stock']]))
    
    stock_total = stock_apri004 + stock_yessica
    return stock_total, stock_apri004, stock_yessica

def buscar_stock_general(stocks, sku):
    sku_limpio = sku.strip().upper()
    stock_total = 0
    for stock in stocks:
        hoja = stock['hoja'].upper()
        if 'APRI.001' in hoja:
            mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
            if not stock['df'][mask].empty:
                row = stock['df'][mask].iloc[0]
                stock_total = int(corregir_numero(row[stock['col_stock']]))
                break
    return stock_total, 0, 0

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
                        col_precio_real = cat['columnas_precio'].get(col_precio_consulta)
                        if col_precio_real and col_precio_real in df.columns:
                            precio = corregir_numero(row[col_precio_real])
                        else:
                            precio = 0
                    
                    if tipo_cotizacion == "XIAOMI":
                        stock_total, stock_apri004, stock_yessica = buscar_stock_xiaomi(stocks, sku)
                    else:
                        stock_total, stock_apri004, stock_yessica = buscar_stock_general(stocks, sku)
                    
                    resultados_dict[sku] = {
                        'SKU': sku,
                        'Descripcion': str(row[cat['col_desc']])[:100],
                        'Catalogo': cat['nombre'],
                        'Precio': precio,
                        'Stock_Total': stock_total,
                        'Stock_APRI004': stock_apri004,
                        'Stock_YESSICA': stock_yessica
                    }
    
    return list(resultados_dict.values())

def generar_excel(items, cliente, ruc):
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
try:
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        st.image("logo.png", width="70px")
    with col_title:
        st.title("QTC Smart Sales Pro")
except:
    st.title("QTC Smart Sales Pro")

st.markdown("---")

if 'tipo_cotizacion' not in st.session_state:
    st.session_state.tipo_cotizacion = "XIAOMI"

if st.session_state.tipo_cotizacion == "XIAOMI":
    st.success("🔋 **Modo XIAOMI** - Buscará stock en: **APRI.004** y **YESSICA SEPARADO**")
else:
    st.info("💼 **Modo GENERAL** - Buscará stock en: **APRI.001**")

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

tab_cotizacion, tab_buscar, tab_dashboard = st.tabs(["📦 Cotización", "🔍 Buscar Productos", "📊 Dashboard"])

with tab_cotizacion:
    with st.sidebar:
        st.markdown("### 📂 Archivos")
        
        st.markdown("**📚 Catálogos de Precios**")
        archivos_catalogos = st.file_uploader("Sube catálogos", type=['xlsx', 'xls', 'csv'], accept_multiple_files=True, key="cat_upload")
        if archivos_catalogos:
            st.session_state.catalogos = []
            for archivo in archivos_catalogos:
                resultado = cargar_catalogo(archivo)
                if resultado:
                    st.session_state.catalogos.append(resultado)
                    st.success(f"✅ {resultado['nombre'][:50]}")
        
        st.markdown("**📦 Reportes de Stock**")
        st.caption("💡 El sistema cargará TODAS las hojas automáticamente")
        archivos_stock = st.file_uploader("Sube stocks", type=['xlsx', 'xls', 'csv'], accept_multiple_files=True, key="stock_upload")
        if archivos_stock:
            st.session_state.stocks = []
            for archivo in archivos_stock:
                hojas_cargadas = cargar_stock_completo(archivo)
                if hojas_cargadas:
                    st.session_state.stocks.extend(hojas_cargadas)
                    st.success(f"✅ {archivo.name}: {len(hojas_cargadas)} hojas")
                    for h in hojas_cargadas:
                        st.caption(f"   └─ {h['hoja']}")
    
    if not st.session_state.catalogos:
        st.warning("🌿 Carga catálogos en el panel izquierdo")
    else:
        with st.expander("📋 Catálogos cargados"):
            for cat in st.session_state.catalogos:
                st.caption(f"• {cat['nombre']}")
        
        if st.session_state.stocks:
            with st.expander("📋 Stock cargado (todas las hojas)"):
                for stock in st.session_state.stocks:
                    st.caption(f"   📄 {stock['nombre']}")
        
        opciones_precio = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio'].keys():
                opciones_precio.add(col)
        
        if opciones_precio:
            col_precio = st.selectbox("💰 Columna de precio:", sorted(list(opciones_precio)))
        else:
            col_precio = None
            st.warning("⚠️ No se detectaron columnas de precio")
        
        st.markdown("---")
        st.markdown("### 📝 Ingresa los productos")
        st.caption("Formato: SKU:CANTIDAD (uno por línea)")
        
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
            with st.spinner("🔍 Procesando..."):
                resultados = []
                for pedido in pedidos:
                    sku = pedido['sku']
                    cant = pedido['cantidad']
                    
                    precio_info = buscar_precio_con_descripcion_stock(st.session_state.catalogos, st.session_state.stocks, sku, col_precio, st.session_state.tipo_cotizacion)
                    
                    if st.session_state.tipo_cotizacion == "XIAOMI":
                        stock_total, stock_apri004, stock_yessica = buscar_stock_xiaomi(st.session_state.stocks, sku)
                    else:
                        stock_total, stock_apri004, stock_yessica = buscar_stock_general(st.session_state.stocks, sku)
                    
                    # Generar badge de origen
                    if st.session_state.tipo_cotizacion == "XIAOMI":
                        if stock_apri004 > 0 and stock_yessica > 0:
                            origen_html = f'<span class="origin-badge-both">📦 APRI.004: {stock_apri004} | 📋 YESSICA: {stock_yessica}</span>'
                        elif stock_apri004 > 0:
                            origen_html = f'<span class="origin-badge-apri004">📦 APRI.004: {stock_apri004}</span>'
                        elif stock_yessica > 0:
                            origen_html = f'<span class="origin-badge-yessica">📋 YESSICA: {stock_yessica}</span>'
                        else:
                            origen_html = '<span style="color: #999;">❌ Sin stock</span>'
                    else:
                        origen_html = f'<span class="origin-badge-apri004">📦 Stock: {stock_total}</span>' if stock_total > 0 else '<span style="color: #999;">❌ Sin stock</span>'
                    
                    if precio_info['encontrado'] and stock_total > 0:
                        a_cotizar = min(cant, stock_total)
                        total = precio_info['precio'] * a_cotizar
                        badge = "badge-ok"
                        estado = "✅ OK"
                    elif precio_info['en
