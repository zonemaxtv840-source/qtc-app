import streamlit as st
import pandas as pd
import re, io
from datetime import datetime
from PIL import Image
import numpy as np
import warnings
import plotly.express as px
import plotly.graph_objects as go
warnings.filterwarnings('ignore')

# ============================================
# CONFIGURACIÓN DE PÁGINA
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
.dataframe-card { background: white; border-radius: 20px; padding: 1rem; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.origin-badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.65rem; font-weight: 600; margin-right: 5px; }
.origin-apri004 { background-color: #E1BEE7; color: #4A148C; }
.origin-yessica { background-color: #BBDEFB; color: #0D47A1; }
.origin-both { background-color: #C8E6C9; color: #1B5E20; }
.resultado-tabla { width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.resultado-tabla th { background-color: #4CAF50; color: white; padding: 12px; text-align: left; font-weight: 600; }
.resultado-tabla td { padding: 10px; border-bottom: 1px solid #E8F5E9; }
.resultado-tabla tr:hover { background-color: #F1F8E9; }
</style>
""", unsafe_allow_html=True)

# ============================================
# SISTEMA DE USUARIOS Y ROLES
# ============================================
USUARIOS = {
    "admin": {"password": "admin2026", "rol": "admin", "nombre": "Administrador"},
    "vendedor1": {"password": "ventas2026", "rol": "vendedor", "nombre": "Carlos Ventas"},
    "vendedor2": {"password": "ventas2026", "rol": "vendedor", "nombre": "Maria Lopez"},
    "invitado": {"password": "guest", "rol": "invitado", "nombre": "Usuario Invitado"}
}

def verificar_usuario(usuario, password):
    if usuario in USUARIOS and USUARIOS[usuario]["password"] == password:
        return USUARIOS[usuario]
    return None

def init_user_session():
    if "usuario_actual" not in st.session_state:
        st.session_state.usuario_actual = None
    if "historial_cotizaciones" not in st.session_state:
        st.session_state.historial_cotizaciones = []
    if "rol_actual" not in st.session_state:
        st.session_state.rol_actual = None

init_user_session()

# ============================================
# LOGIN CON ROLES
# ============================================
if st.session_state.usuario_actual is None:
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
        
        col_info, col_btn = st.columns([1,1])
        with col_info:
            st.caption("💡 Usuarios: admin / vendedor1 / vendedor2 / invitado")
        with col_btn:
            if st.button("Ingresar", use_container_width=True):
                usuario_data = verificar_usuario(user, pw)
                if usuario_data:
                    st.session_state.usuario_actual = user
                    st.session_state.rol_actual = usuario_data["rol"]
                    st.session_state.nombre_usuario = usuario_data["nombre"]
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
    st.stop()

# ============================================
# FUNCIONES EXISTENTES
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
        xls = pd.ExcelFile(archivo)
        hojas = xls.sheet_names
        hoja_seleccionada = st.sidebar.selectbox(f"📗 Hoja {archivo.name}:", hojas, key=f"cat_{archivo.name}")
        df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)
        df = limpiar_cabeceras(df)
        
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
            'nombre': f"{archivo.name} [{hoja_seleccionada}]",
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
        xls = pd.ExcelFile(archivo)
        todas_hojas = []
        
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

def buscar_precio(catalogos, sku, col_precio_seleccionada):
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
    # Buscar descripción en stocks si no está en catálogos
    return {'encontrado': False, 'precio': 0, 'descripcion': ''}

def buscar_descripcion_en_stock(stocks, sku):
    """Busca la descripción de un SKU en los archivos de stock"""
    sku_limpio = sku.strip().upper()
    for stock in stocks:
        df = stock['df']
        col_sku = stock['col_sku']
        mask = df[col_sku].astype(str).str.contains(sku_limpio, case=False, na=False)
        if not df[mask].empty:
            row = df[mask].iloc[0]
            # Buscar columna de descripción
            for col in df.columns:
                if any(p in str(col).upper() for p in ['DESC', 'NOMBRE', 'PRODUCTO', 'DESCRIPCION']):
                    return str(row[col])[:100]
            return f"SKU: {sku}"
    return f"SKU: {sku}"

def buscar_stock_xiaomi(stocks, sku):
    sku_limpio = sku.strip().upper()
    stock_total = 0
    stock_apri004 = 0
    stock_yessica = 0
    origen_apri004 = ""
    origen_yessica = ""
    
    for stock in stocks:
        hoja = stock['hoja'].upper()
        if 'APRI.004' in hoja:
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
    sku_limpio = sku.strip().upper()
    stock_total = 0
    detalles = {}
    
    for stock in stocks:
        hoja = stock['hoja'].upper()
        if 'APRI.001' in hoja:
            mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
            if not stock['df'][mask].empty:
                row = stock['df'][mask].iloc[0]
                stock_total = int(corregir_numero(row[stock['col_stock']]))
                detalles[stock['nombre']] = stock_total
                break
    
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

def generar_excel(items, cliente, ruc, usuario):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    pd.DataFrame(items).to_excel(writer, sheet_name='Cotizacion', index=False, startrow=7)
    
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
    
    ws.write('A1', 'EMPRESA:', fmt_bold)
    ws.write('B1', 'QTC SMART SALES')
    ws.write('A2', 'FECHA:', fmt_bold)
    ws.write('B2', datetime.now().strftime("%d/%m/%Y %H:%M"))
    ws.write('A3', 'VENDEDOR:', fmt_bold)
    ws.write('B3', usuario)
    ws.write('A4', 'CLIENTE:', fmt_bold)
    ws.write('B4', cliente.upper())
    ws.write('A5', 'RUC:', fmt_bold)
    ws.write('B5', ruc)
    
    ws.merge_range('F1:H1', 'DATOS BANCARIOS', fmt_header)
    ws.write('F2', 'BBVA SOLES:', workbook.add_format({'font_color': 'red', 'bold': True, 'border': 1}))
    ws.write('G2', '0011-0616-0100012617', fmt_border)
    ws.write('F3', 'INTERBANK:', workbook.add_format({'font_color': 'red', 'bold': True, 'border': 1}))
    ws.write('G3', '898-1234567890', fmt_border)
    
    headers = ['Código SAP', 'Descripción', 'Cantidad', 'Precio Unit.', 'Total']
    for i, header in enumerate(headers):
        ws.write(7, i, header, fmt_header)
    
    for row_idx, item in enumerate(items):
        ws.write_row(row_idx + 8, 0, [item['sku'], item['desc'], item['cant'], item['p_u'], item['total']], fmt_border)
        ws.write(row_idx + 8, 3, item['p_u'], fmt_money)
        ws.write(row_idx + 8, 4, item['total'], fmt_money)
    
    total_row = len(items) + 8
    ws.write(total_row, 3, 'TOTAL S/.', fmt_header)
    ws.write(total_row, 4, sum(item['total'] for item in items), fmt_money)
    
    ws.write(total_row + 2, 0, '* Cotización generada automáticamente por QTC Smart Sales Pro', workbook.add_format({'italic': True}))
    
    writer.close()
    return output.getvalue()

def buscar_producto_individual(catalogos, stocks, sku, col_precio, tipo_cotizacion):
    """Busca un producto individual y retorna su información completa"""
    sku_limpio = sku.strip().upper()
    
    # Buscar precio y descripción en catálogos
    precio_info = buscar_precio(catalogos, sku_limpio, col_precio)
    
    # Si no encontró descripción, buscar en stocks
    if not precio_info['descripcion']:
        precio_info['descripcion'] = buscar_descripcion_en_stock(stocks, sku_limpio)
    
    # Buscar stock
    if tipo_cotizacion == "XIAOMI":
        stock_total, stock_detalle, stock_apri004, stock_yessica = buscar_stock_xiaomi(stocks, sku_limpio)
    else:
        stock_total, stock_detalle = buscar_stock_general(stocks, sku_limpio)
        stock_apri004 = 0
        stock_yessica = 0
    
    # Determinar estado
    if precio_info['encontrado'] and stock_total > 0:
        estado = "✅ OK"
        badge = "badge-ok"
        estado_texto = "Disponible"
    elif precio_info['encontrado'] and stock_total == 0:
        estado = "⚠️ Sin stock"
        badge = "badge-warning"
        estado_texto = "Sin stock"
    elif not precio_info['encontrado'] and stock_total > 0:
        estado = "⚠️ Sin precio"
        badge = "badge-warning"
        estado_texto = "Sin precio"
    else:
        estado = "❌ No encontrado"
        badge = "badge-danger"
        estado_texto = "No encontrado"
    
    return {
        'SKU': sku_limpio,
        'Descripcion': precio_info['descripcion'][:100] if precio_info['descripcion'] else f"SKU: {sku_limpio}",
        'Precio': precio_info['precio'],
        'Stock': stock_total,
        'Stock_APRI004': stock_apri004,
        'Stock_YESSICA': stock_yessica,
        'Estado': estado,
        'Badge': badge,
        'Estado_Texto': estado_texto
    }

# ============================================
# INTERFAZ PRINCIPAL CON ROLES
# ============================================

# Header con info de usuario
col_logo, col_title, col_user = st.columns([1, 4, 2])
with col_logo:
    try:
        st.image("logo.png", width=60)
    except:
        st.markdown("💚")
with col_title:
    st.title("QTC Smart Sales Pro")
with col_user:
    rol_icon = "👑" if st.session_state.rol_actual == "admin" else "👤" if st.session_state.rol_actual == "vendedor" else "👋"
    st.markdown(f"""
    <div style="text-align: right; background: white; padding: 10px; border-radius: 12px;">
        <strong>{rol_icon} {st.session_state.nombre_usuario}</strong><br>
        <span style="font-size: 0.8rem;">Rol: {st.session_state.rol_actual.upper()}</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Cerrar Sesión", key="logout"):
        st.session_state.usuario_actual = None
        st.session_state.rol_actual = None
        st.rerun()

st.markdown("---")

# Selección de modo de cotización (solo admin puede cambiar?)
if st.session_state.rol_actual == "admin":
    if 'tipo_cotizacion' not in st.session_state:
        st.session_state.tipo_cotizacion = None
    
    if st.session_state.tipo_cotizacion is None:
        st.markdown("### 🎯 ¿Qué vas a cotizar hoy?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔋 XIAOMI", use_container_width=True):
                st.session_state.tipo_cotizacion = "XIAOMI"
                st.rerun()
        with col2:
            if st.button("💼 GENERAL", use_container_width=True):
                st.session_state.tipo_cotizacion = "GENERAL"
                st.rerun()
        st.stop()
else:
    if 'tipo_cotizacion' not in st.session_state:
        st.session_state.tipo_cotizacion = "XIAOMI"

if st.session_state.tipo_cotizacion == "XIAOMI":
    st.success("🔋 **Modo XIAOMI** - Buscará stock en: **APRI.004** y **YESSICA SEPARADO** (suma ambas)")
else:
    st.info("💼 **Modo GENERAL** - Buscará stock en: **APRI.001**")

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
if 'productos_seleccionados' not in st.session_state:
    st.session_state.productos_seleccionados = {}
if 'historial_cotizaciones' not in st.session_state:
    st.session_state.historial_cotizaciones = []
if 'dashboard_data' not in st.session_state:
    st.session_state.dashboard_data = []

# Crear tabs (ahora con 5 pestañas)
tab_cotizacion, tab_buscar, tab_busqueda_rapida, tab_dashboard, tab_usuarios = st.tabs(["📦 Cotización", "🔍 Buscar Productos", "⚡ Búsqueda Rápida Múltiple", "📊 Dashboard", "👥 Usuarios"])

# ============================================
# TAB COTIZACIÓN
# ============================================
with tab_cotizacion:
    with st.sidebar:
        st.markdown("### 📂 Archivos")
        
        st.markdown("**📚 Catálogos de Precios**")
        archivos_catalogos = st.file_uploader("Sube catálogos", type=['xlsx', 'xls'], accept_multiple_files=True, key="cat_upload")
        if archivos_catalogos:
            st.session_state.catalogos = []
            for archivo in archivos_catalogos:
                resultado = cargar_catalogo(archivo)
                if resultado:
                    st.session_state.catalogos.append(resultado)
                    st.success(f"✅ {resultado['nombre'][:50]}")
        
        st.markdown("**📦 Reportes de Stock**")
        st.caption("💡 El sistema cargará TODAS las hojas automáticamente")
        archivos_stock = st.file_uploader("Sube stocks", type=['xlsx', 'xls'], accept_multiple_files=True, key="stock_upload")
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
        
        # Procesar pedidos eliminando duplicados
        pedidos_dict = {}
        if texto_skus:
            for line in texto_skus.split('\n'):
                line = line.strip()
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) == 2:
                        try:
                            sku = parts[0].strip().upper()
                            cantidad = int(parts[1].strip())
                            if cantidad > 0:
                                if sku in pedidos_dict:
                                    pedidos_dict[sku] += cantidad
                                else:
                                    pedidos_dict[sku] = cantidad
                        except:
                            pass
                elif line:
                    sku = line.strip().upper()
                    if sku in pedidos_dict:
                        pedidos_dict[sku] += 1
                    else:
                        pedidos_dict[sku] = 1
        
        pedidos = [{'sku': sku, 'cantidad': cant} for sku, cant in pedidos_dict.items()]
        
        if st.button("🚀 PROCESAR", use_container_width=True, type="primary") and pedidos:
            if not col_precio:
                st.error("❌ Selecciona una columna de precio primero")
            else:
                with st.spinner("🔍 Procesando..."):
                    resultados = []
                    for pedido in pedidos:
                        sku = pedido['sku']
                        cant = pedido['cantidad']
                        
                        precio_info = buscar_precio(st.session_state.catalogos, sku, col_precio)
                        
                        # Si no tiene descripción, buscarla en stocks
                        if not precio_info['descripcion']:
                            precio_info['descripcion'] = buscar_descripcion_en_stock(st.session_state.stocks, sku)
                        
                        if st.session_state.tipo_cotizacion == "XIAOMI":
                            stock_total, stock_detalle, stock_apri004, stock_yessica = buscar_stock_xiaomi(st.session_state.stocks, sku)
                        else:
                            stock_total, stock_detalle = buscar_stock_general(st.session_state.stocks, sku)
                            stock_apri004 = 0
                            stock_yessica = 0
                        
                        icono = "🔋" if st.session_state.tipo_cotizacion == "XIAOMI" else "💼"
                        
                        if stock_apri004 > 0 and stock_yessica > 0:
                            origen_texto = f"📦 APRI.004: {stock_apri004} | 📋 YESSICA: {stock_yessica}"
                            origen_clase = "origin-both"
                        elif stock_apri004 > 0:
                            origen_texto = f"📦 APRI.004: {stock_apri004}"
                            origen_clase = "origin-apri004"
                        elif stock_yessica > 0:
                            origen_texto = f"📋 YESSICA: {stock_yessica}"
                            origen_clase = "origin-yessica"
                        else:
                            origen_texto = "❌ Sin stock"
                            origen_clase = ""
                        
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
                            'Descripción': precio_info['descripcion'][:100] if precio_info['descripcion'] else f"SKU: {sku}",
                            'Precio': precio_info['precio'],
                            'Solicitado': cant,
                            'Stock': stock_total,
                            'Stock_APRI004': stock_apri004,
                            'Stock_YESSICA': stock_yessica,
                            'Origen_Texto': origen_texto,
                            'Origen_Clase': origen_clase,
                            'A Cotizar': a_cotizar,
                            'Total': total,
                            'Estado': estado,
                            'Badge': badge,
                            'Tipo': st.session_state.tipo_cotizacion
                        })
                    
                    st.session_state.resultados = resultados
        
        # MOSTRAR RESULTADOS
        if st.session_state.resultados:
            st.markdown("---")
            st.markdown("### 📊 Resultados")
            
            # Tabla con formato profesional
            html = '<table class="resultado-tabla">'
            html += '<thead><tr>'
            html += '<th>SKU</th>'
            html += '<th>Descripción</th>'
            html += '<th>Precio</th>'
            html += '<th>Sol.</th>'
            html += '<th>Stock</th>'
            html += '<th>A Cotizar</th>'
            html += '<th>Total</th>'
            html += '<th>Estado</th>'
            html += '</tr></thead><tbody>'
            
            for item in st.session_state.resultados:
                precio_str = f"S/. {item['Precio']:,.2f}" if item['Precio'] > 0 else "Sin precio"
                total_str = f"S/. {item['Total']:,.2f}"
                
                html += '<tr>'
                html += f'<td style="font-family: monospace;">{item["SKU"]}</td>'
                html += f'<td style="max-width: 300px;">{item["Descripción"][:60]}</td>'
                html += f'<td>{precio_str}</td>'
                html += f'<td style="text-align: center;">{item["Solicitado"]}</td>'
                html += f'<td style="text-align: center;">{item["Stock"]}</td>'
                html += f'<td style="text-align: center;"><strong>{item["A Cotizar"]}</strong></td>'
                html += f'<td>{total_str}</td>'
                html += f'<td><span class="{item["Badge"]}">{item["Estado"]}</span></td>'
                html += '</tr>'
            
            html += '</tbody></table>'
            st.markdown(html, unsafe_allow_html=True)
            
            # ============================================
            # TABLA DE AJUSTE DE CANTIDADES
            # ============================================
            st.markdown("---")
            st.markdown("### ✏️ Ajustar cantidades")
            st.caption("💡 Modifica las cantidades usando los controles deslizantes")
            
            resultados_editados = []
            
            for i, item in enumerate(st.session_state.resultados):
                with st.container():
                    cols = st.columns([2, 2, 1, 1, 1.5, 1.5])
                    
                    with cols[0]:
                        st.markdown(f"**📦 {item['SKU']}**")
                        st.caption(item['Descripción'][:50])
                    
                    with cols[1]:
                        if item['Precio'] > 0:
                            st.markdown(f"💰 **S/. {item['Precio']:,.2f}**")
                        else:
                            st.markdown("💰 **Sin precio**")
                        st.caption(f"📦 Stock: {item['Stock']} unidades")
                    
                    with cols[2]:
                        st.markdown(f"**Solicitado:** {item['Solicitado']}")
                    
                    with cols[3]:
                        if item['Precio'] > 0 and item['Stock'] > 0:
                            max_cant = max(item['Stock'], item['Solicitado'])
                            nueva_cant = st.slider(
                                "Cantidad",
                                min_value=0,
                                max_value=max_cant,
                                value=min(item['A Cotizar'], max_cant),
                                key=f"slider_{i}_{item['SKU']}",
                                label_visibility="collapsed",
                                step=1
                            )
                        else:
                            nueva_cant = 0
                            st.markdown("❌ **No cotizable**")
                    
                    with cols[4]:
                        if item['Precio'] > 0 and nueva_cant > 0:
                            nuevo_total = item['Precio'] * nueva_cant
                            st.markdown(f"**💰 Total:**")
                            st.markdown(f"**S/. {nuevo_total:,.2f}**")
                        else:
                            nuevo_total = 0
                            st.markdown("**Total:**")
                            st.markdown("**S/. 0.00**")
                    
                    with cols[5]:
                        if nueva_cant > 0 and item['Precio'] > 0:
                            st.markdown(f'<span class="badge-ok">✅ Cotizable</span>', unsafe_allow_html=True)
                        elif item['Precio'] == 0:
                            st.markdown(f'<span class="badge-warning">⚠️ Sin precio</span>', unsafe_allow_html=True)
                        elif item['Stock'] == 0:
                            st.markdown(f'<span class="badge-warning">⚠️ Sin stock</span>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<span class="badge-danger">❌ Error</span>', unsafe_allow_html=True)
                    
                    item_editado = item.copy()
                    item_editado['A Cotizar'] = nueva_cant
                    item_editado['Total'] = nuevo_total
                    resultados_editados.append(item_editado)
                    
                    st.divider()
            
            # ============================================
            # REPORTE DE PRODUCTOS CON ISSUES
            # ============================================
            st.markdown("---")
            st.markdown("### ⚠️ Productos con Issues (No Cotizables)")
            
            items_con_issues = [r for r in resultados_editados if r['A Cotizar'] == 0 or r['Precio'] == 0]
            items_validos = [r for r in resultados_editados if r['A Cotizar'] > 0 and r['Precio'] > 0]
            total_general = sum(r['Total'] for r in items_validos)
            
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                st.metric("✅ A cotizar", len(items_validos))
            with col_m2:
                st.metric("💰 Total", f"S/. {total_general:,.2f}")
            with col_m3:
                st.metric("⚠️ Excluidos", len(items_con_issues))
            with col_m4:
                st.metric("📦 Total SKUs", len(resultados_editados))
            
            if items_con_issues:
                for item in items_con_issues:
                    if item['Precio'] == 0:
                        motivo = "💰 Sin precio en catálogo"
                    elif item['Stock'] == 0:
                        motivo = "📦 Sin stock disponible"
                    else:
                        motivo = "❓ Error en datos"
                    st.warning(f"**{item['SKU']}** - {item['Descripción'][:60]} → `{motivo}`")
            
            # ============================================
            # GENERAR COTIZACIÓN
            # ============================================
            if items_validos:
                st.markdown("---")
                st.markdown("### 📥 Generar Cotización")
                
                col_cli1, col_cli2 = st.columns(2)
                with col_cli1:
                    cliente = st.text_input("🏢 Cliente / Razón Social", value="CLIENTE NUEVO", key="cliente_nombre")
                with col_cli2:
                    ruc_cliente = st.text_input("📋 RUC / DNI", value="-", key="cliente_ruc")
                
                if st.button("📥 GENERAR EXCEL", use_container_width=True, type="primary"):
                    items_excel = [
                        {
                            'sku': r['SKU'], 
                            'desc': r['Descripción'], 
                            'cant': r['A Cotizar'], 
                            'p_u': r['Precio'], 
                            'total': r['Total']
                        } 
                        for r in items_validos
                    ]
                    
                    cotizacion_data = {
                        'fecha': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'cliente': cliente,
                        'usuario': st.session_state.nombre_usuario,
                        'total': total_general,
                        'productos': len(items_validos),
                        'items': items_excel
                    }
                    st.session_state.historial_cotizaciones.append(cotizacion_data)
                    st.session_state.dashboard_data.append(cotizacion_data)
                    
                    excel = generar_excel(items_excel, cliente, ruc_cliente, st.session_state.nombre_usuario)
                    st.download_button(
                        "💾 DESCARGAR EXCEL", 
                        data=excel, 
                        file_name=f"Cotizacion_{cliente}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", 
                        use_container_width=True,
                        key="download_btn"
                    )
                    st.session_state.cotizaciones += 1
                    st.session_state.total_prods = len(items_validos)
                    st.balloons()
                    st.success("✅ Cotización generada exitosamente!")
            
            st.markdown("---")
            if st.button("🗑️ LIMPIAR TODOS LOS RESULTADOS", use_container_width=True):
                st.session_state.resultados = None
                st.rerun()

# ============================================
# TAB BUSCAR (Individual)
# ============================================
with tab_buscar:
    st.markdown("### 🔍 Buscar Productos")
    st.caption("💡 Busca por SKU o descripción - Muestra stock y precio en tiempo real")
    
    if not st.session_state.catalogos:
        st.warning("🌿 Primero carga catálogos en la pestaña Cotización")
    else:
        opciones_precio_buscar = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio'].keys():
                opciones_precio_buscar.add(col)
        
        col_precio_consulta = st.selectbox(
            "💰 Mostrar precios en columna:",
            options=["(No mostrar precio)"] + sorted(list(opciones_precio_buscar)),
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
                    with st.container():
                        cols = st.columns([2, 2, 1, 1])
                        with cols[0]:
                            st.markdown(f"**📦 {res['SKU']}**")
                            st.caption(res['Descripcion'][:60])
                        with cols[1]:
                            if res['Precio']:
                                st.markdown(f"💰 **S/. {res['Precio']:,.2f}**")
                            else:
                                st.markdown("💰 **Sin precio**")
                            st.caption(f"📦 Stock: {res['Stock_Total']}")
                        with cols[2]:
                            cantidad = st.number_input(
                                "Cantidad", 
                                min_value=0, 
                                max_value=999, 
                                value=0, 
                                key=f"add_{res['SKU']}",
                                label_visibility="collapsed"
                            )
                        with cols[3]:
                            if cantidad > 0:
                                if st.button(f"➕ Agregar", key=f"btn_{res['SKU']}"):
                                    st.session_state.productos_seleccionados[res['SKU']] = st.session_state.productos_seleccionados.get(res['SKU'], 0) + cantidad
                                    st.success(f"✅ {cantidad}x {res['SKU']} agregado")
                                    st.rerun()
                        st.divider()
            else:
                st.warning("No se encontraron productos")
        
        if st.session_state.productos_seleccionados:
            st.markdown("---")
            st.markdown(f"### ✅ Productos seleccionados ({len(st.session_state.productos_seleccionados)})")
            
            seleccionados_lista = []
            for sku, cant in st.session_state.productos_seleccionados.items():
                if st.session_state.tipo_cotizacion == "XIAOMI":
                    stock_total, _, _, _ = buscar_stock_xiaomi(st.session_state.stocks, sku)
                else:
                    stock_total, _ = buscar_stock_general(st.session_state.stocks, sku)
                seleccionados_lista.append({'SKU': sku, 'Cantidad': cant, 'Stock disponible': stock_total})
            
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
# TAB BÚSQUEDA RÁPIDA MÚLTIPLE (NUEVA)
# ============================================
with tab_busqueda_rapida:
    st.markdown("### ⚡ Búsqueda Rápida Múltiple")
    st.caption("💡 Busca múltiples productos a la vez - Formato: SKU por línea o separados por comas")
    
    if not st.session_state.catalogos:
        st.warning("🌿 Primero carga catálogos en la pestaña Cotización")
    else:
        # Selector de columna de precio
        opciones_precio_rapido = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio'].keys():
                opciones_precio_rapido.add(col)
        
        col_precio_rapido = st.selectbox(
            "💰 Columna de precio para búsqueda:",
            sorted(list(opciones_precio_rapido)),
            key="precio_rapido"
        )
        
        st.markdown("---")
        st.markdown("### 📝 Ingresa los SKUs a buscar")
        st.caption("Formato: Un SKU por línea o separados por comas (ej: SKU1, SKU2, SKU3)")
        
        texto_busqueda_rapida = st.text_area(
            "", 
            height=150, 
            placeholder="RN0200046BK8\nCN0900009WH8\nCN0400005GY8\n\nO también:\nRN0200046BK8, CN0900009WH8, CN0400005GY8",
            key="busqueda_rapida_texto"
        )
        
        # Procesar SKUs ingresados
        skus_a_buscar = []
        if texto_busqueda_rapida:
            # Primero intentar separar por comas
            if ',' in texto_busqueda_rapida:
                for parte in texto_busqueda_rapida.split(','):
                    sku = parte.strip().upper()
                    if sku and len(sku) >= 3:
                        skus_a_buscar.append(sku)
            else:
                # Separar por líneas
                for line in texto_busqueda_rapida.split('\n'):
                    sku = line.strip().upper()
                    if sku and len(sku) >= 3:
                        skus_a_buscar.append(sku)
        
        # Eliminar duplicados manteniendo orden
        skus_a_buscar = list(dict.fromkeys(skus_a_buscar))
        
        if skus_a_buscar:
            st.info(f"📋 {len(skus_a_buscar)} SKU(s) para buscar")
            
            if st.button("🔍 BUSCAR PRODUCTOS", use_container_width=True, type="primary"):
                with st.spinner(f"🔍 Buscando {len(skus_a_buscar)} productos..."):
                    resultados_rapidos = []
                    
                    for sku in skus_a_buscar:
                        resultado = buscar_producto_individual(
                            st.session_state.catalogos,
                            st.session_state.stocks,
                            sku,
                            col_precio_rapido,
                            st.session_state.tipo_cotizacion
                        )
                        resultados_rapidos.append(resultado)
                    
                    st.session_state.resultados_rapidos = resultados_rapidos
            
            # Mostrar resultados con el mismo estilo visual que la tabla de cotización
            if st.session_state.get('resultados_rapidos'):
                st.markdown("---")
                st.markdown("### 📊 Resultados de la Búsqueda")
                
                # Tabla HTML con el mismo estilo
                html_rapido = '<table class="resultado-tabla">'
                html_rapido += '<thead><tr>'
                html_rapido += '<th>SKU</th>'
                html_rapido += '<th>Descripción</th>'
                html_rapido += '<th>Precio</th>'
                html_rapido += '<th>Stock</th>'
                html_rapido += '<th>Estado</th>'
                html_rapido += '<th>Acción</th>'
                html_rapido += '</tr></thead><tbody>'
                
                for item in st.session_state.resultados_rapidos:
                    precio_str = f"S/. {item['Precio']:,.2f}" if item['Precio'] > 0 else "Sin precio"
                    
                    html_rapido += '<tr>'
                    html_rapido += f'<td style="font-family: monospace;">{item["SKU"]}</td>'
                    html_rapido += f'<td style="max-width: 400px;">{item["Descripcion"][:80]}</td>'
                    html_rapido += f'<td>{precio_str}</td>'
                    html_rapido += f'<td style="text-align: center;">{item["Stock"]}</td>'
                    html_rapido += f'<td><span class="{item["Badge"]}">{item["Estado"]}</span></td>'
                    html_rapido += f'<td style="text-align: center;">'
                    html_rapido += f'<button class="add-to-cotizacion" data-sku="{item["SKU"]}" style="background: #4CAF50; color: white; border: none; padding: 4px 12px; border-radius: 8px; cursor: pointer;">➕ Agregar</button>'
                    html_rapido += f'</td>'
                    html_rapido += '</tr>'
                
                html_rapido += '</tbody></table>'
                st.markdown(html_rapido, unsafe_allow_html=True)
                
                # Controles para agregar cantidades (usando widgets de Streamlit)
                st.markdown("---")
                st.markdown("### ➕ Agregar a Cotización")
                
                col_add1, col_add2, col_add3 = st.columns([2, 1, 1])
                with col_add1:
                    sku_seleccionado = st.selectbox(
                        "Seleccionar SKU:", 
                        [r['SKU'] for r in st.session_state.resultados_rapidos],
                        key="sku_select_rapido"
                    )
                with col_add2:
                    cantidad_add = st.number_input("Cantidad:", min_value=1, value=1, step=1, key="cant_rapido")
                with col_add3:
                    if st.button("➕ AÑADIR A COTIZACIÓN", type="primary", key="btn_agregar_rapido"):
                        if 'skus_transferidos' not in st.session_state:
                            st.session_state.skus_transferidos = {}
                        if sku_seleccionado in st.session_state.skus_transferidos:
                            st.session_state.skus_transferidos[sku_seleccionado] += cantidad_add
                        else:
                            st.session_state.skus_transferidos[sku_seleccionado] = cantidad_add
                        st.success(f"✅ {cantidad_add}x {sku_seleccionado} añadido a la cotización")
                        st.info("👉 Ve a la pestaña Cotización y haz clic en PROCESAR")
                
                # Resumen de productos a agregar
                if st.session_state.get('skus_transferidos'):
                    st.markdown("---")
                    st.markdown("#### 📋 Productos pendientes para cotizar:")
                    for sku, cant in st.session_state.skus_transferidos.items():
                        st.markdown(f"- **{sku}**: {cant} unidad(es)")
                    
                    if st.button("🗑️ LIMPIAR LISTA DE ESPERA", use_container_width=True):
                        del st.session_state.skus_transferidos
                        st.rerun()
                
                # Botón para limpiar resultados de búsqueda
                if st.button("🗑️ LIMPIAR RESULTADOS DE BÚSQUEDA", use_container_width=True):
                    st.session_state.resultados_rapidos = None
                    st.rerun()

# ============================================
# TAB DASHBOARD CON GRÁFICOS
# ============================================
with tab_dashboard:
    st.markdown("### 📊 Dashboard de Ventas")
    
    if st.session_state.rol_actual == "invitado":
        st.warning("🔒 Los invitados no tienen acceso al Dashboard. Contacta al administrador para más permisos.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📄 Cotizaciones", st.session_state.get('cotizaciones', 0))
        with col2:
            st.metric("🌿 Productos Vendidos", st.session_state.get('total_prods', 0))
        with col3:
            st.metric("📚 Catálogos", len(st.session_state.get('catalogos', [])))
        with col4:
            total_ventas = sum(c.get('total', 0) for c in st.session_state.dashboard_data)
            st.metric("💰 Ventas Totales", f"S/. {total_ventas:,.2f}")
        
        st.markdown("---")
        
        if st.session_state.dashboard_data:
            df_historial = pd.DataFrame(st.session_state.dashboard_data)
            df_historial['fecha_dt'] = pd.to_datetime(df_historial['fecha'])
            df_historial['día'] = df_historial['fecha_dt'].dt.strftime('%Y-%m-%d')
            
            ventas_por_dia = df_historial.groupby('día')['total'].sum().reset_index()
            
            fig1 = px.bar(
                ventas_por_dia, 
                x='día', 
                y='total',
                title='💰 Ventas por Día',
                labels={'día': 'Fecha', 'total': 'Total S/.'},
                color_discrete_sequence=['#4CAF50']
            )
            fig1.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                title_font_color='#1B5E20',
                font_color='#2E7D32'
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 🏆 Top Productos Más Cotizados")
            
            productos_vendidos = []
            for cotizacion in st.session_state.dashboard_data:
                for item in cotizacion.get('items', []):
                    productos_vendidos.append({
                        'SKU': item['sku'],
                        'Descripción': item['desc'][:50],
                        'Cantidad': item['cant'],
                        'Total': item['total']
                    })
            
            if productos_vendidos:
                df_productos = pd.DataFrame(productos_vendidos)
                top_productos = df_productos.groupby('SKU').agg({
                    'Cantidad': 'sum',
                    'Total': 'sum',
                    'Descripción': 'first'
                }).reset_index().sort_values('Cantidad', ascending=False).head(10)
                
                fig2 = px.bar(
                    top_productos,
                    x='SKU',
                    y='Cantidad',
                    title='📦 Top 10 Productos Más Cotizados',
                    labels={'SKU': 'Producto', 'Cantidad': 'Unidades'},
                    color='Cantidad',
                    color_continuous_scale='Greens'
                )
                fig2.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    title_font_color='#1B5E20',
                    font_color='#2E7D32'
                )
                st.plotly_chart(fig2, use_container_width=True)
                
                st.markdown("#### 📋 Detalle de Top Productos")
                st.dataframe(top_productos[['SKU', 'Descripción', 'Cantidad', 'Total']], use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 👥 Ventas por Vendedor")
            
            ventas_por_usuario = df_historial.groupby('usuario')['total'].sum().reset_index()
            
            fig3 = px.pie(
                ventas_por_usuario,
                values='total',
                names='usuario',
                title='💰 Distribución de Ventas por Vendedor',
                color_discrete_sequence=px.colors.sequential.Greens_r,
                hole=0.4
            )
            fig3.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                title_font_color='#1B5E20',
                font_color='#2E7D32'
            )
            st.plotly_chart(fig3, use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 📜 Historial de Cotizaciones")
            
            df_historial_display = df_historial[['fecha', 'cliente', 'usuario', 'productos', 'total']].copy()
            df_historial_display['total'] = df_historial_display['total'].apply(lambda x: f"S/. {x:,.2f}")
            st.dataframe(df_historial_display, use_container_width=True, hide_index=True)
            
        else:
            st.info("📊 Aún no hay cotizaciones generadas. Comienza creando tu primera cotización en la pestaña 'Cotización'")
        
        if st.session_state.rol_actual == "admin" and st.session_state.stocks:
            st.markdown("---")
            st.markdown("### ⚠️ Alertas de Stock Bajo")
            
            stock_bajo = []
            for stock in st.session_state.stocks:
                df = stock['df']
                col_stock = stock['col_stock']
                for idx, row in df.iterrows():
                    try:
                        cantidad = int(corregir_numero(row[col_stock]))
                        if 0 < cantidad < 10:
                            sku = str(row[stock['col_sku']])
                            stock_bajo.append({
                                'SKU': sku,
                                'Stock': cantidad,
                                'Origen': stock['nombre']
                            })
                    except:
                        pass
            
            if stock_bajo:
                df_bajo = pd.DataFrame(stock_bajo).drop_duplicates(subset=['SKU'])
                st.warning(f"⚠️ {len(df_bajo)} productos con stock bajo (<10 unidades)")
                st.dataframe(df_bajo, use_container_width=True)
            else:
                st.success("✅ No hay productos con stock bajo")

# ============================================
# TAB USUARIOS (solo visible para admin)
# ============================================
with tab_usuarios:
    if st.session_state.rol_actual == "admin":
        st.markdown("### 👥 Gestión de Usuarios")
        st.caption("Administra los usuarios del sistema")
        
        st.markdown("#### 📋 Usuarios Registrados")
        df_usuarios = pd.DataFrame([
            {"Usuario": u, "Rol": USUARIOS[u]["rol"], "Nombre": USUARIOS[u]["nombre"]}
            for u in USUARIOS.keys()
        ])
        st.dataframe(df_usuarios, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("#### ➕ Agregar Nuevo Usuario")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            nuevo_usuario = st.text_input("Usuario", key="new_user")
        with col2:
            nueva_password = st.text_input("Contraseña", type="password", key="new_pass")
        with col3:
            nuevo_rol = st.selectbox("Rol", ["vendedor", "invitado"], key="new_rol")
        
        if st.button("➕ Crear Usuario", use_container_width=True):
            if nuevo_usuario and nueva_password:
                if nuevo_usuario not in USUARIOS:
                    USUARIOS[nuevo_usuario] = {
                        "password": nueva_password,
                        "rol": nuevo_rol,
                        "nombre": nuevo_usuario.capitalize()
                    }
                    st.success(f"✅ Usuario {nuevo_usuario} creado exitosamente!")
                    st.rerun()
                else:
                    st.error("❌ El usuario ya existe")
            else:
                st.warning("⚠️ Completa todos los campos")
        
        st.markdown("---")
        st.markdown("#### 🔧 Información del Sistema")
        st.caption(f"Versión: QTC Smart Sales Pro v3.0")
        st.caption(f"Última sesión: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        st.caption(f"Usuario actual: {st.session_state.nombre_usuario} ({st.session_state.rol_actual})")
    else:
        st.warning("🔒 Solo el Administrador puede acceder a esta sección")
        st.info("Contacta con el administrador para gestionar usuarios")

st.markdown("---")
st.markdown("*💚 QTC Smart Sales Pro - Sistema Robusto de Cotización*")
