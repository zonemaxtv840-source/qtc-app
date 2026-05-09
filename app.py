import streamlit as st
import pandas as pd
import re
import io
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
    st.set_page_config(
        page_title="QTC Smart Sales Pro", 
        page_icon=img_logo, 
        layout="wide",
        initial_sidebar_state="expanded"
    )
except:
    st.set_page_config(
        page_title="QTC Smart Sales Pro", 
        page_icon="💼", 
        layout="wide",
        initial_sidebar_state="expanded"
    )

# Inicializar variables de sesión
def init_session_state():
    defaults = {
        'auth': False,
        'tipo_cotizacion': None,
        'catalogos': [],
        'stocks': [],
        'resultados': None,
        'cotizaciones': 0,
        'total_prods': 0,
        'productos_seleccionados': {}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ============================================
# FUNCIONES DE UTILIDAD
# ============================================
def corregir_numero(valor):
    """Convierte valores a número de forma robusta"""
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
    """Detecta y limpia cabeceras de archivos"""
    for i in range(min(20, len(df))):
        fila = [str(x).upper() for x in df.iloc[i].values]
        if any(h in item for h in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO', 'COD SAP'] for item in fila):
            df.columns = [str(c).strip() for c in df.iloc[i]]
            return df.iloc[i+1:].reset_index(drop=True)
    return df

def mapear_columna_precio(columnas, nombre_buscar):
    """Busca columnas de precio por nombre"""
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

def cargar_archivo_dataframe(archivo, tipo="catalogo"):
    """Carga archivos Excel o CSV y devuelve dataframe limpio"""
    try:
        nombre = archivo.name.lower()
        
        if nombre.endswith('.csv'):
            for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-8-sig']:
                try:
                    contenido = archivo.getvalue().decode(encoding)
                    lines = contenido.split('\n')
                    if ';' in lines[0]:
                        sep = ';'
                    else:
                        sep = ','
                    
                    df = pd.read_csv(io.StringIO(contenido), encoding=encoding, sep=sep)
                    break
                except:
                    continue
            else:
                raise Exception("No se pudo leer el archivo CSV")
        elif nombre.endswith(('.xlsx', '.xls')):
            if tipo == "catalogo":
                xls = pd.ExcelFile(archivo)
                hojas = xls.sheet_names
                hoja_seleccionada = st.sidebar.selectbox(f"📗 Hoja {archivo.name}:", hojas, key=f"cat_{archivo.name}_{tipo}")
                df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)
            else:
                df = pd.read_excel(archivo)
        else:
            raise Exception(f"Formato no soportado: {nombre}")
        
        df = limpiar_cabeceras(df)
        return df
        
    except Exception as e:
        st.error(f"Error en {archivo.name}: {str(e)[:100]}")
        return None

def cargar_catalogo(archivo):
    """Carga un catálogo desde Excel o CSV"""
    try:
        df = cargar_archivo_dataframe(archivo, "catalogo")
        if df is None:
            return None
            
        posibles_skus = ['SKU', 'COD', 'CODIGO', 'SAP', 'NUMERO', 'ARTICULO', 'COD SAP', 'ID']
        posibles_desc = ['DESC', 'DESCRIPCION', 'NOMBRE', 'PRODUCTO', 'NOMBRE PRODUCTO', 'DESCRIPTION']
        
        col_sku = next((c for c in df.columns if any(p in str(c).upper() for p in posibles_skus)), df.columns[0])
        col_desc = next((c for c in df.columns if any(p in str(c).upper() for p in posibles_desc)), df.columns[1] if len(df.columns) > 1 else df.columns[0])
        
        columnas_precio = {}
        for precio_nombre in ['P. IR', 'P. BOX', 'P. VIP']:
            col = mapear_columna_precio(df.columns, precio_nombre)
            if col:
                columnas_precio[precio_nombre] = col
        
        if not columnas_precio:
            for c in df.columns:
                if 'PRECIO' in str(c).upper() or 'PRICE' in str(c).upper():
                    columnas_precio['PRECIO'] = c
                    break
        
        nombre_archivo = archivo.name
        if nombre_archivo.lower().endswith(('.xlsx', '.xls')):
            xls = pd.ExcelFile(archivo)
            hoja_seleccionada = st.session_state.get(f"cat_{archivo.name}_catalogo", xls.sheet_names[0])
            nombre_completo = f"{archivo.name} [{hoja_seleccionada}]"
        else:
            nombre_completo = archivo.name
        
        with st.sidebar.expander(f"📋 {nombre_completo[:30]}..."):
            st.caption(f"SKU: {col_sku}")
            st.caption(f"Desc: {col_desc}")
            st.caption(f"Precios: {', '.join(columnas_precio.keys()) if columnas_precio else 'No detectados'}")
        
        return {
            'nombre': nombre_completo,
            'df': df,
            'col_sku': col_sku,
            'col_desc': col_desc,
            'columnas_precio': columnas_precio
        }
    except Exception as e:
        st.error(f"Error en {archivo.name}: {str(e)[:100]}")
        return None

def cargar_stock_completo(archivo):
    """Carga archivo de stock (Excel con múltiples hojas o CSV)"""
    try:
        todas_hojas = []
        
        if archivo.name.lower().endswith('.csv'):
            df = cargar_archivo_dataframe(archivo, "stock")
            if df is not None:
                posibles_skus = ['SKU', 'COD', 'CODIGO', 'NUMERO', 'ARTICULO', 'NÚMERO DE ARTÍCULO', 'ID']
                posibles_stock = ['STOCK', 'DISPONIBLE', 'CANT', 'CANTIDAD', 'SALDO', 'EN STOCK', 'QUANTITY', 'AVAILABLE']
                
                col_sku = next((c for c in df.columns if any(p in str(c).upper() for p in posibles_skus)), df.columns[0])
                col_stock = next((c for c in df.columns if any(p in str(c).upper() for p in posibles_stock)), df.columns[1] if len(df.columns) > 1 else df.columns[0])
                
                todas_hojas.append({
                    'nombre': archivo.name,
                    'df': df,
                    'col_sku': col_sku,
                    'col_stock': col_stock,
                    'hoja': 'Datos'
                })
        else:
            xls = pd.ExcelFile(archivo)
            
            for hoja in xls.sheet_names:
                df = pd.read_excel(archivo, sheet_name=hoja)
                df = limpiar_cabeceras(df)
                
                posibles_skus = ['SKU', 'COD', 'CODIGO', 'NUMERO', 'ARTICULO', 'NÚMERO DE ARTÍCULO', 'ID']
                posibles_stock = ['STOCK', 'DISPONIBLE', 'CANT', 'CANTIDAD', 'SALDO', 'EN STOCK', 'QUANTITY']
                
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

def buscar_precio(catalogos, sku, col_precio_seleccionada):
    """Busca precio en catálogos"""
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
    return {'encontrado': False, 'precio': 0, 'descripcion': ''}

def buscar_descripcion_en_stock(stocks, sku):
    """Busca descripción en archivos de stock"""
    sku_limpio = sku.strip().upper()
    for stock in stocks:
        df = stock['df']
        col_sku = stock['col_sku']
        mask = df[col_sku].astype(str).str.contains(sku_limpio, case=False, na=False)
        if not df[mask].empty:
            row = df[mask].iloc[0]
            for col in df.columns:
                if any(p in str(col).upper() for p in ['DESC', 'NOMBRE', 'PRODUCTO', 'DESCRIPCION', 'DESCRIPTION']):
                    desc = str(row[col])
                    if desc and desc != 'nan':
                        return desc[:100]
            return f"SKU: {sku}"
    return f"SKU: {sku}"

def buscar_stock_xiaomi(stocks, sku):
    """Busca stock para Xiaomi (APRI.004 y YESSICA)"""
    sku_limpio = sku.strip().upper()
    stock_apri004 = 0
    stock_yessica = 0
    origen_apri004 = ""
    origen_yessica = ""
    
    for stock in stocks:
        hoja = stock['hoja'].upper()
        if 'APRI.004' in hoja or 'APRI004' in hoja:
            mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
            if not stock['df'][mask].empty:
                row = stock['df'][mask].iloc[0]
                stock_apri004 = int(corregir_numero(row[stock['col_stock']]))
                origen_apri004 = stock['nombre']
        elif 'YESSICA' in hoja:
            mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
            if not stock['df'][mask].empty:
                row = stock['df'][mask].iloc[0]
                stock_yessica = int(corregir_numero(row[stock['col_stock']]))
                origen_yessica = stock['nombre']
    
    stock_total = stock_apri004 + stock_yessica
    detalles = {}
    if stock_apri004 > 0:
        detalles[origen_apri004] = stock_apri004
    if stock_yessica > 0:
        detalles[origen_yessica] = stock_yessica
    
    return stock_total, detalles, stock_apri004, stock_yessica

def buscar_stock_general(stocks, sku):
    """Busca stock general (APRI.001)"""
    sku_limpio = sku.strip().upper()
    stock_total = 0
    detalles = {}
    
    for stock in stocks:
        hoja = stock['hoja'].upper()
        if 'APRI.001' in hoja or 'APRI001' in hoja:
            mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
            if not stock['df'][mask].empty:
                row = stock['df'][mask].iloc[0]
                stock_total = int(corregir_numero(row[stock['col_stock']]))
                detalles[stock['nombre']] = stock_total
                break
    
    return stock_total, detalles

def buscar_en_catalogos(catalogos, termino, stocks, col_precio_consulta=None, tipo_cotizacion="XIAOMI"):
    """Busca productos en catálogos"""
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
                        stock_total, stock_detalle, stock_apri004, stock_yessica = buscar_stock_xiaomi(stocks, sku)
                    else:
                        stock_total, stock_detalle = buscar_stock_general(stocks, sku)
                        stock_apri004 = 0
                        stock_yessica = 0
                    
                    resultados_dict[sku] = {
                        'SKU': sku,
                        'Descripcion': str(row[cat['col_desc']])[:100],
                        'Catalogo': cat['nombre'],
                        'Precio': precio,
                        'Stock_Total': stock_total,
                        'Stock_APRI004': stock_apri004,
                        'Stock_YESSICA': stock_yessica,
                        'Stock_Detalle': stock_detalle
                    }
    
    return list(resultados_dict.values())

def generar_excel(items, cliente, ruc):
    """Genera archivo Excel de cotización"""
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    pd.DataFrame(items).to_excel(writer, sheet_name='Cotizacion', index=False, startrow=5)
    
    workbook = writer.book
    ws = writer.sheets['Cotizacion']
    
    fmt_header = workbook.add_format({'bg_color': '#1B5E20', 'bold': True, 'border': 1, 'align': 'center', 'font_color': 'white', 'font_size': 11})
    fmt_money = workbook.add_format({'num_format': '"S/." #,##0.00', 'border': 1, 'align': 'right'})
    fmt_border = workbook.add_format({'border': 1})
    fmt_bold = workbook.add_format({'bold': True, 'font_size': 11})
    fmt_title = workbook.add_format({'bold': True, 'font_size': 12, 'font_color': '#1B5E20'})
    
    ws.set_column('A:A', 20)
    ws.set_column('B:B', 75)
    ws.set_column('C:C', 12)
    ws.set_column('D:D', 18)
    ws.set_column('E:E', 18)
    
    ws.write('A1', 'QTC SMART SALES PRO', fmt_title)
    ws.write('A2', 'Sistema Profesional de Cotizacion', fmt_title)
    
    ws.write('A4', 'FECHA:', fmt_bold)
    ws.write('B4', datetime.now().strftime("%d/%m/%Y %H:%M"))
    ws.write('A5', 'CLIENTE:', fmt_bold)
    ws.write('B5', cliente.upper())
    ws.write('A6', 'RUC:', fmt_bold)
    ws.write('B6', ruc)
    
    ws.merge_range('G1:I1', 'DATOS BANCARIOS', fmt_header)
    ws.write('G2', 'BBVA SOLES:', workbook.add_format({'font_color': '#D32F2F', 'bold': True, 'border': 1}))
    ws.write('H2', '0011-0616-0100012617', fmt_border)
    ws.write('G3', 'CCI:', workbook.add_format({'bold': True, 'border': 1}))
    ws.write('H3', '011-0616-000100012617-95', fmt_border)
    
    headers = ['Codigo SAP', 'Descripcion', 'Cantidad', 'Precio Unit.', 'Total']
    for i, header in enumerate(headers):
        ws.write(8, i, header, fmt_header)
    
    for row_idx, item in enumerate(items):
        ws.write_row(row_idx + 9, 0, [item['sku'], item['desc'], item['cant'], item['p_u'], item['total']], fmt_border)
        ws.write(row_idx + 9, 3, item['p_u'], fmt_money)
        ws.write(row_idx + 9, 4, item['total'], fmt_money)
    
    total_row = len(items) + 9
    ws.write(total_row, 3, 'TOTAL S/.', fmt_header)
    ws.write(total_row, 4, sum(item['total'] for item in items), fmt_money)
    
    ws.write(total_row + 2, 0, 'Gracias por su compra!', workbook.add_format({'italic': True, 'font_color': '#666666'}))
    
    writer.close()
    return output.getvalue()

def obtener_clase_stock(stock):
    """Devuelve la clase CSS según el stock"""
    if stock == 0:
        return "stock-rojo"
    elif stock <= 5:
        return "stock-amarillo"
    else:
        return "stock-verde"

def obtener_icono_stock(stock):
    """Devuelve el ícono según el stock"""
    if stock == 0:
        return "🔴"
    elif stock <= 5:
        return "🟡"
    else:
        return "🟢"

def obtener_mensaje_stock(stock):
    """Devuelve mensaje según el stock"""
    if stock == 0:
        return "Sin stock disponible"
    elif stock <= 5:
        return f"Stock bajo! Solo quedan {stock} unidades"
    else:
        return "Stock suficiente"

# ============================================
# ESTILOS CSS
# ============================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%) !important;
    }
    
    .modern-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
        margin-bottom: 1rem;
    }
    
    .modern-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .metric-premium {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%);
        border-radius: 20px;
        padding: 1rem;
        text-align: center;
        color: white;
    }
    
    .metric-premium .label {
        font-size: 0.85rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }
    
    .metric-premium .value {
        font-size: 2rem;
        font-weight: bold;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D3B0F 0%, #1B5E20 100%) !important;
        border-right: none !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.3s ease !important;
        padding: 0.6rem 1rem !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(76,175,80,0.3) !important;
    }
    
    .stock-verde {
        background: #C8E6C9;
        color: #1B5E20;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }
    
    .stock-amarillo {
        background: #FFE0B2;
        color: #E65100;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }
    
    .stock-rojo {
        background: #FFCDD2;
        color: #C62828;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }
    
    .origin-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 2px;
    }
    
    .origin-apri004 {
        background: #E1BEE7;
        color: #4A148C;
    }
    
    .origin-yessica {
        background: #BBDEFB;
        color: #0D47A1;
    }
    
    .origin-both {
        background: #C8E6C9;
        color: #1B5E20;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: white;
        border-radius: 16px;
        padding: 6px;
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white !important;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: slideIn 0.4s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# LOGIN
# ============================================
if not st.session_state.auth:
    st.markdown("""
    <style>
    .login-wrapper {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .login-card-premium {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 32px;
        padding: 3rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        text-align: center;
        max-width: 450px;
        margin: auto;
        animation: slideIn 0.5s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="login-card-premium">
            <h1 style="color: #667eea; margin-bottom: 0.5rem;">✨ QTC Smart Sales</h1>
            <p style="color: #764ba2; margin-bottom: 2rem;">Sistema Profesional de Cotizacion</p>
        """, unsafe_allow_html=True)
        
        user = st.text_input("USUARIO", placeholder="admin", key="login_user")
        pw = st.text_input("CONTRASENA", type="password", placeholder="••••••", key="login_pass")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("INGRESAR", use_container_width=True):
            if user == "admin" and pw == "qtc2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
        
        st.markdown("""
        <div style="margin-top: 1.5rem; font-size: 0.8rem; color: #999;">
            <span>💡 Usuario: <strong>admin</strong> | Contraseña: <strong>qtc2026</strong></span>
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.stop()

# ============================================
# HEADER
# ============================================
col1, col2, col3 = st.columns([1, 10, 2])
with col1:
    try:
        st.image("logo.png", width=70)
    except:
        st.markdown("<h1 style='margin:0;'>💼</h1>", unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div>
        <h1 style="margin:0; background: linear-gradient(135deg, #1B5E20 0%, #4CAF50 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            QTC Smart Sales Pro
        </h1>
        <p style="margin:0; color: #666;">Sistema Inteligente de Cotizacion</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div style="text-align: right; background: white; padding: 10px 20px; border-radius: 30px; margin-top: 10px;">
        <span style="font-weight: 600;">👤 Admin</span><br>
        <span style="font-size: 0.7rem; color: #4CAF50;">● Activo</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Cerrar Sesion", key="logout", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

st.markdown("---")

# ============================================
# SELECCIÓN DE TIPO DE COTIZACIÓN
# ============================================
if st.session_state.tipo_cotizacion is None:
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2>🎯 Que vas a cotizar hoy?</h2>
        <p style="color: #666;">Selecciona el tipo de cotizacion para continuar</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown("""
            <div class="modern-card" style="text-align: center;">
                <h1 style="font-size: 3rem;">🔋</h1>
                <h3>XIAOMI</h3>
                <p>Stock en APRI.004 y YESSICA</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Seleccionar XIAOMI", key="btn_xiaomi", use_container_width=True):
                st.session_state.tipo_cotizacion = "XIAOMI"
                st.rerun()
    with col2:
        with st.container():
            st.markdown("""
            <div class="modern-card" style="text-align: center;">
                <h1 style="font-size: 3rem;">💼</h1>
                <h3>GENERAL</h3>
                <p>Stock en APRI.001</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Seleccionar GENERAL", key="btn_general", use_container_width=True):
                st.session_state.tipo_cotizacion = "GENERAL"
                st.rerun()
    st.stop()

if st.session_state.tipo_cotizacion == "XIAOMI":
    st.success("Modo XIAOMI Activo - Buscara stock en APRI.004 y YESSICA SEPARADO")
else:
    st.info("Modo GENERAL Activo - Buscara stock en APRI.001")

st.markdown("---")

# ============================================
# TABS PRINCIPALES
# ============================================
tab_cotizacion, tab_buscar, tab_dashboard = st.tabs([
    "Cotizacion", 
    "Buscar Productos", 
    "Dashboard"
])

# ============================================
# TAB COTIZACIÓN
# ============================================
with tab_cotizacion:
    with st.sidebar:
        st.markdown("## Gestion de Archivos")
        st.markdown("---")
        
        st.markdown("### Catalogos de Precios")
        st.caption("Formatos: Excel (.xlsx, .xls) y CSV (.csv)")
        
        archivos_catalogos = st.file_uploader(
            "Sube tus catalogos", 
            type=['xlsx', 'xls', 'csv'], 
            accept_multiple_files=True, 
            key="cat_upload"
        )
        
        if archivos_catalogos:
            with st.spinner("Cargando catalogos..."):
                st.session_state.catalogos = []
                for archivo in archivos_catalogos:
                    resultado = cargar_catalogo(archivo)
                    if resultado:
                        st.session_state.catalogos.append(resultado)
                        st.success(f"OK {resultado['nombre'][:40]}")
        
        st.markdown("---")
        
        st.markdown("### Reportes de Stock")
        st.caption("Formatos: Excel (.xlsx, .xls) y CSV (.csv)")
        
        archivos_stock = st.file_uploader(
            "Sube tus reportes de stock", 
            type=['xlsx', 'xls', 'csv'], 
            accept_multiple_files=True, 
            key="stock_upload"
        )
        
        if archivos_stock:
            with st.spinner("Cargando stocks..."):
                st.session_state.stocks = []
                for archivo in archivos_stock:
                    hojas_cargadas = cargar_stock_completo(archivo)
                    if hojas_cargadas:
                        st.session_state.stocks.extend(hojas_cargadas)
                        st.success(f"OK {archivo.name}: {len(hojas_cargadas)} seccion(es)")
        
        if st.session_state.catalogos or st.session_state.stocks:
            st.markdown("---")
            st.markdown("### Resumen Cargado")
            if st.session_state.catalogos:
                st.markdown(f"**Catalogos:** {len(st.session_state.catalogos)}")
            if st.session_state.stocks:
                st.markdown(f"**Stocks:** {len(st.session_state.stocks)} secciones")
    
    if not st.session_state.catalogos:
        st.warning("Bienvenido a QTC Smart Sales Pro - Carga tus catalagos de precios en el panel izquierdo")
        
        with st.expander("Guia: Como cargar archivos CSV correctamente", expanded=True):
            st.markdown("""
            ### Para cargar archivos CSV correctamente:
            
            1. **Formato del archivo CSV**:
               - Usa separador: coma (,) o punto y coma (;)
               - La primera fila debe contener los nombres de las columnas
               - Ejemplo:
