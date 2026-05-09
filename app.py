import streamlit as st
import pandas as pd
import re, io, chardet
from datetime import datetime
from PIL import Image
import numpy as np
import warnings
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
# INICIALIZACIÓN DE VARIABLES DE SESIÓN
# ============================================
if "auth" not in st.session_state:
    st.session_state.auth = False
if "tipo_cotizacion" not in st.session_state:
    st.session_state.tipo_cotizacion = None
if "catalogos" not in st.session_state:
    st.session_state.catalogos = []
if "stocks" not in st.session_state:
    st.session_state.stocks = []
if "resultados" not in st.session_state:
    st.session_state.resultados = None
if "cotizaciones" not in st.session_state:
    st.session_state.cotizaciones = 0
if "total_prods" not in st.session_state:
    st.session_state.total_prods = 0
if "productos_seleccionados" not in st.session_state:
    st.session_state.productos_seleccionados = {}
if "skus_transferidos" not in st.session_state:
    st.session_state.skus_transferidos = {}

# ============================================
# FUNCIONES PARA LEER CSV CON DETECCIÓN DE ENCODING
# ============================================
def detectar_encoding(archivo):
    """Detecta el encoding de un archivo"""
    raw_data = archivo.read(10000)
    archivo.seek(0)
    resultado = chardet.detect(raw_data)
    return resultado['encoding'] if resultado['encoding'] else 'utf-8'

def leer_archivo_flexible(archivo):
    """Lee archivos Excel o CSV de forma flexible"""
    nombre_archivo = archivo.name.lower()
    
    # Para archivos CSV
    if nombre_archivo.endswith('.csv'):
        try:
            # Detectar encoding automáticamente
            encoding = detectar_encoding(archivo)
            st.caption(f"📄 Detectado encoding: {encoding}")
            
            # Intentar leer con diferentes separadores
            separadores = [',', ';', '\t', '|']
            df = None
            
            for sep in separadores:
                try:
                    archivo.seek(0)
                    df = pd.read_csv(archivo, encoding=encoding, sep=sep, dtype=str)
                    if df.shape[1] > 1:  # Si tiene más de 1 columna, probablemente es correcto
                        break
                except:
                    continue
            
            if df is None or df.shape[1] == 1:
                # Fallback: dejar que pandas detecte automáticamente
                archivo.seek(0)
                df = pd.read_csv(archivo, encoding=encoding, engine='python')
            
            # Limpiar nombres de columnas
            df.columns = [str(col).strip().replace('\ufeff', '') for col in df.columns]
            return df
            
        except Exception as e:
            st.error(f"Error leyendo CSV: {str(e)}")
            return None
    
    # Para archivos Excel
    elif nombre_archivo.endswith(('.xlsx', '.xls')):
        try:
            return pd.read_excel(archivo, dtype=str)
        except Exception as e:
            st.error(f"Error leyendo Excel: {str(e)}")
            return None
    
    else:
        st.error(f"Formato no soportado: {nombre_archivo}. Use .xlsx, .xls o .csv")
        return None

def mapear_columnas_flexible(df, tipo_archivo="catalogo"):
    """Mapea columnas automáticamente según su contenido semántico"""
    
    columnas = {str(col).upper().strip() for col in df.columns}
    
    # Mapeo de SKU (todas las variantes posibles)
    sku_keywords = ['SKU', 'COD', 'CODIGO', 'SAP', 'NUMERO', 'ARTICULO', 'COD SAP', 
                    'NO.', 'MODEL', 'MODEL MARK', 'MODELO', 'PART NUMBER', 'PN']
    
    # Mapeo de descripción
    desc_keywords = ['DESC', 'DESCRIPCION', 'NOMBRE', 'PRODUCTO', 'GOODS', 
                     'GOODS DESCRIPTION', 'DESCRITPION', 'DESCRIPTION', 'ITEM NAME']
    
    # Mapeo de precios para catálogo
    precio_keywords = {
        'Mayor': ['MAYOR', 'MAYORISTA', 'WHOLESALE', 'P.IR', 'P. IR', 'PRECIO MAYOR'],
        'Caja': ['CAJA', 'BOX', 'P.BOX', 'P. BOX', 'PRECIO CAJA', 'BOX PRICE'],
        'Vip': ['VIP', 'P.VIP', 'P. VIP', 'PRECIO VIP', 'VIP PRICE'],
        'PVP': ['PVP', 'PRECIO VENTA', 'LIST PRICE', 'RETAIL', 'PUBLICO']
    }
    
    # Mapeo de stock
    stock_keywords = ['STOCK', 'DISPONIBLE', 'CANT', 'CANTIDAD', 'SALDO', 
                      'STOCK TTL', 'TTL', 'INVENTARIO', 'QTY']
    
    # Encontrar columna SKU
    col_sku = None
    for col in df.columns:
        col_upper = str(col).upper()
        for keyword in sku_keywords:
            if keyword in col_upper:
                col_sku = col
                break
        if col_sku:
            break
    if not col_sku:
        col_sku = df.columns[0]  # Usar primera columna como fallback
    
    # Encontrar columna descripción
    col_desc = None
    for col in df.columns:
        col_upper = str(col).upper()
        for keyword in desc_keywords:
            if keyword in col_upper:
                col_desc = col
                break
        if col_desc:
            break
    if not col_desc:
        col_desc = df.columns[1] if len(df.columns) > 1 else df.columns[0]
    
    # Encontrar columnas de precio
    columnas_precio = {}
    for precio_tipo, keywords in precio_keywords.items():
        for col in df.columns:
            col_upper = str(col).upper()
            for keyword in keywords:
                if keyword in col_upper:
                    columnas_precio[precio_tipo] = col
                    break
            if precio_tipo in columnas_precio:
                break
    
    # Si no se encontraron precios específicos, buscar cualquier columna con "PRECIO"
    if not columnas_precio and tipo_archivo == "catalogo":
        for col in df.columns:
            if 'PRECIO' in str(col).upper():
                columnas_precio['PRECIO'] = col
                break
    
    # Encontrar columna de stock
    col_stock = None
    for col in df.columns:
        col_upper = str(col).upper()
        for keyword in stock_keywords:
            if keyword in col_upper:
                col_stock = col
                break
        if col_stock:
            break
    if not col_stock:
        col_stock = df.columns[-1] if len(df.columns) > 0 else None
    
    return {
        'col_sku': col_sku,
        'col_desc': col_desc,
        'columnas_precio': columnas_precio,
        'col_stock': col_stock
    }

# ============================================
# ESTILOS CSS (comprimido para ahorrar espacio)
# ============================================
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #E8F5E9 50%, #C8E6C9 100%) !important; }
.main .block-container { background-color: transparent !important; }
h1, h2, h3, h4, h5, h6 { color: #0A0A0A !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0D3B0F 50%, #1B5E20 100%) !important; }
[data-testid="stSidebar"] * { color: #FFFFFF !important; }
.stButton > button { background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%) !important; color: white !important; border-radius: 12px; font-weight: 600; }
.badge-ok { background-color: #C8E6C9; color: #1B5E20; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; }
.badge-warning { background-color: #FFF3E0; color: #E65100; padding: 4px 10px; border-radius: 20px; }
.badge-danger { background-color: #FFCDD2; color: #C62828; padding: 4px 10px; border-radius: 20px; }
.stock-verde { color: #2E7D32; background-color: #C8E6C9; padding: 2px 8px; border-radius: 20px; }
.stock-amarillo { color: #E65100; background-color: #FFE0B2; padding: 2px 8px; border-radius: 20px; }
.stock-rojo { color: #C62828; background-color: #FFCDD2; padding: 2px 8px; border-radius: 20px; }
</style>
""", unsafe_allow_html=True)

# ============================================
# LOGIN
# ============================================
if not st.session_state.auth:
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #FFF8E1 0%, #FFE0B2 50%, #FFCC80 100%) !important; }
    .login-card { background: #FFFDF5; border-radius: 28px; padding: 2.5rem; box-shadow: 0 25px 50px rgba(0,0,0,0.15); text-align: center; }
    .stButton button { background: linear-gradient(135deg, #E65100 0%, #FF9800 100%) !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:
        st.markdown("""
        <div class="login-card">
            <h1 style="color: #E65100;">QTC Smart Sales</h1>
            <p style="color: #F57C00;">Sistema Profesional de Cotización</p>
        """, unsafe_allow_html=True)
        
        user = st.text_input("👤 USUARIO", placeholder="Ingresa tu usuario", key="login_user")
        pw = st.text_input("🔒 CONTRASEÑA", type="password", placeholder="Ingresa tu contraseña", key="login_pass")
        
        if st.button("🚀 INGRESAR", use_container_width=True):
            if user == "admin" and pw == "qtc2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")
                st.info("💡 Usuario: admin | Contraseña: qtc2026")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.stop()

# ============================================
# FUNCIONES PRINCIPALES
# ============================================
def corregir_numero(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "0", "0.0", "-", "nan"]:
        return 0.0
    try:
        s = str(valor).upper().replace('S/', '').replace('$', '').replace(' ', '').strip()
        if ',' in s and s.count(',') == 1:
            s = s.replace(',', '.')
        elif ',' in s:
            s = s.replace(',', '')
        s = re.sub(r'[^\d.]', '', s)
        return float(s) if s else 0.0
    except:
        return 0.0

def cargar_catalogo_flexible(archivo):
    """Carga catálogo desde Excel o CSV de forma flexible"""
    try:
        df = leer_archivo_flexible(archivo)
        if df is None:
            return None
        
        # Limpiar datos nulos
        df = df.dropna(how='all')
        
        # Mapear columnas
        mapeo = mapear_columnas_flexible(df, tipo_archivo="catalogo")
        
        st.sidebar.success(f"✅ Detectado: SKU={mapeo['col_sku']}, Desc={mapeo['col_desc']}")
        if mapeo['columnas_precio']:
            st.sidebar.caption(f"💰 Precios: {', '.join(mapeo['columnas_precio'].keys())}")
        
        return {
            'nombre': archivo.name,
            'df': df,
            'col_sku': mapeo['col_sku'],
            'col_desc': mapeo['col_desc'],
            'columnas_precio': mapeo['columnas_precio']
        }
    except Exception as e:
        st.error(f"Error cargando {archivo.name}: {str(e)}")
        return None

def cargar_stock_flexible(archivo):
    """Carga stock desde Excel o CSV de forma flexible"""
    try:
        # Si es CSV, cargar como una sola "hoja"
        if archivo.name.lower().endswith('.csv'):
            df = leer_archivo_flexible(archivo)
            if df is None:
                return []
            
            mapeo = mapear_columnas_flexible(df, tipo_archivo="stock")
            
            return [{
                'nombre': archivo.name,
                'df': df,
                'col_sku': mapeo['col_sku'],
                'col_stock': mapeo['col_stock'],
                'hoja': archivo.name
            }]
        
        # Para Excel, cargar todas las hojas
        else:
            xls = pd.ExcelFile(archivo)
            todas_hojas = []
            
            for hoja in xls.sheet_names:
                df = pd.read_excel(archivo, sheet_name=hoja, dtype=str)
                df = df.dropna(how='all')
                mapeo = mapear_columnas_flexible(df, tipo_archivo="stock")
                
                todas_hojas.append({
                    'nombre': f"{archivo.name} [{hoja}]",
                    'df': df,
                    'col_sku': mapeo['col_sku'],
                    'col_stock': mapeo['col_stock'],
                    'hoja': hoja
                })
            
            return todas_hojas
    except Exception as e:
        st.error(f"Error cargando stock {archivo.name}: {str(e)}")
        return []

def buscar_precio(catalogos, sku, col_precio_seleccionada):
    sku_limpio = sku.strip().upper()
    for cat in catalogos:
        df = cat['df']
        col_sku = cat['col_sku']
        
        # Buscar coincidencia exacta
        mask = df[col_sku].astype(str).str.strip().str.upper() == sku_limpio
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
                'descripcion': str(row[cat['col_desc']]) if cat['col_desc'] in df.columns else f"SKU: {sku}"
            }
        
        # Buscar coincidencia parcial
        mask = df[col_sku].astype(str).str.contains(sku_limpio, case=False, na=False)
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
                'descripcion': str(row[cat['col_desc']]) if cat['col_desc'] in df.columns else f"SKU: {sku}"
            }
    
    return {'encontrado': False, 'precio': 0, 'descripcion': f"SKU: {sku}"}

def buscar_stock_general(stocks, sku):
    sku_limpio = sku.strip().upper()
    stock_total = 0
    detalles = {}
    
    for stock in stocks:
        df = stock['df']
        col_sku = stock['col_sku']
        col_stock = stock['col_stock']
        
        if col_stock is None:
            continue
            
        mask = df[col_sku].astype(str).str.contains(sku_limpio, case=False, na=False)
        if not df[mask].empty:
            row = df[mask].iloc[0]
            stock_qty = int(corregir_numero(row[col_stock]))
            stock_total += stock_qty
            detalles[stock['nombre']] = stock_qty
    
    return stock_total, detalles

def buscar_en_catalogos(catalogos, termino, stocks, col_precio_consulta=None, tipo_cotizacion="GENERAL"):
    resultados_dict = {}
    
    if ',' in termino:
        terminos = [t.strip() for t in termino.split(',') if len(t.strip()) >= 2]
    else:
        terminos = [t.strip() for t in termino.split() if len(t.strip()) >= 2]
    
    if not terminos:
        terminos = [termino.strip()]
    
    for cat in catalogos:
        df = cat['df']
        col_sku = cat['col_sku']
        col_desc = cat['col_desc']
        
        for term in terminos:
            mask_sku = df[col_sku].astype(str).str.contains(term, case=False, na=False)
            mask_desc = df[col_desc].astype(str).str.contains(term, case=False, na=False)
            
            for idx, row in df[mask_sku | mask_desc].iterrows():
                sku = str(row[col_sku])
                
                if sku not in resultados_dict:
                    precio = None
                    if col_precio_consulta and col_precio_consulta != "(No mostrar precio)":
                        col_precio_real = cat['columnas_precio'].get(col_precio_consulta)
                        if col_precio_real and col_precio_real in df.columns:
                            precio = corregir_numero(row[col_precio_real])
                        else:
                            precio = 0
                    
                    stock_total, stock_detalle = buscar_stock_general(stocks, sku)
                    
                    resultados_dict[sku] = {
                        'SKU': sku,
                        'Descripcion': str(row[col_desc])[:100] if col_desc in df.columns else sku,
                        'Catalogo': cat['nombre'],
                        'Precio': precio,
                        'Stock_Total': stock_total,
                        'Stock_Detalle': stock_detalle
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

def obtener_clase_stock(stock):
    if stock == 0:
        return "stock-rojo"
    elif stock <= 5:
        return "stock-amarillo"
    else:
        return "stock-verde"

def obtener_icono_stock(stock):
    if stock == 0:
        return "❌"
    elif stock <= 5:
        return "⚠️"
    else:
        return "✅"

def obtener_mensaje_stock(stock):
    if stock == 0:
        return "Sin stock disponible"
    elif stock <= 5:
        return f"¡Stock bajo! Solo quedan {stock} unidades"
    else:
        return "Stock suficiente"

# ============================================
# HEADER
# ============================================
try:
    col_logo, col_title, col_user = st.columns([1, 4, 2])
    with col_logo:
        st.image("logo.png", width="60px")
    with col_title:
        st.title("QTC Smart Sales Pro")
    with col_user:
        if st.button("🚪 Cerrar Sesión", key="logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
except:
    st.title("QTC Smart Sales Pro")

st.markdown("---")

# ============================================
# SELECCIÓN DEL TIPO DE COTIZACIÓN
# ============================================
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

# Forzar modo GENERAL para tu caso
st.session_state.tipo_cotizacion = "GENERAL"
st.info("💼 **Modo GENERAL** - Compatible con archivos Excel y CSV (UTF-8, ANSI, Latin-1)")

st.markdown("---")

# ============================================
# TABS PRINCIPALES
# ============================================
tab_cotizacion, tab_buscar, tab_dashboard = st.tabs(["📦 Cotización", "🔍 Buscar Productos", "📊 Dashboard"])

# ============================================
# TAB 1: COTIZACIÓN
# ============================================
with tab_cotizacion:
    with st.sidebar:
        st.markdown("### 📂 Archivos")
        st.markdown("**📚 Catálogos de Precios** (Excel o CSV)")
        st.caption("💡 Columnas soportadas: SKU, GOODS DESCRIPTION, Mayor, Caja, Vip, PVP")
        
        archivos_catalogos = st.file_uploader(
            "Sube catálogos", 
            type=['xlsx', 'xls', 'csv'], 
            accept_multiple_files=True, 
            key="cat_upload"
        )
        
        if archivos_catalogos:
            st.session_state.catalogos = []
            for archivo in archivos_catalogos:
                resultado = cargar_catalogo_flexible(archivo)
                if resultado:
                    st.session_state.catalogos.append(resultado)
                    st.success(f"✅ {archivo.name}")
        
        st.markdown("---")
        st.markdown("**📦 Reportes de Stock** (Excel o CSV)")
        st.caption("💡 Columnas soportadas: SKU, STOCK TTL, CANTIDAD")
        
        archivos_stock = st.file_uploader(
            "Sube stocks", 
            type=['xlsx', 'xls', 'csv'], 
            accept_multiple_files=True, 
            key="stock_upload"
        )
        
        if archivos_stock:
            st.session_state.stocks = []
            for archivo in archivos_stock:
                hojas_cargadas = cargar_stock_flexible(archivo)
                if hojas_cargadas:
                    st.session_state.stocks.extend(hojas_cargadas)
                    st.success(f"✅ {archivo.name}: {len(hojas_cargadas)} sección(es)")
    
    if not st.session_state.catalogos:
        st.warning("🌿 Carga catálogos en el panel izquierdo (Excel o CSV)")
    else:
        # Mostrar columnas detectadas
        with st.expander("📋 Columnas detectadas en catálogos"):
            for cat in st.session_state.catalogos:
                st.markdown(f"**{cat['nombre']}**")
                st.caption(f"  SKU: `{cat['col_sku']}`")
                st.caption(f"  Descripción: `{cat['col_desc']}`")
                if cat['columnas_precio']:
                    st.caption(f"  Precios: {', '.join(cat['columnas_precio'].keys())}")
                st.divider()
        
        # Selección de columna de precio
        opciones_precio = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio'].keys():
                opciones_precio.add(col)
        
        if opciones_precio:
            col_precio = st.selectbox(
                "💰 Columna de precio:", 
                sorted(list(opciones_precio)),
                help="Selecciona qué precio usar (Mayor, Caja, Vip, PVP)"
            )
        else:
            col_precio = None
            st.warning("⚠️ No se detectaron columnas de precio. Asegúrate que tu archivo tenga: Mayor, Caja, Vip o PVP")
        
        st.markdown("---")
        st.markdown("### 📝 Ingresa los productos")
        st.caption("Formato: SKU:CANTIDAD (uno por línea) - Los SKUs duplicados se suman automáticamente")
        
        if st.session_state.get('skus_transferidos'):
            texto_defecto = "\n".join([f"{sku}:{cant}" for sku, cant in st.session_state.skus_transferidos.items()])
            st.session_state.skus_transferidos = {}
        else:
            texto_defecto = ""
        
        texto_skus = st.text_area("", height=150, value=texto_defecto, 
                                   placeholder="Ejemplo:\nABC-123:5\nXYZ-789:2\nPROD-001:10")
        
        pedidos_dict = {}
        if texto_skus:
            for line in texto_skus.split('\n'):
                line = line.strip()
                if not line:
                    continue
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) == 2:
                        try:
                            sku = parts[0].strip().upper()
                            cantidad = int(parts[1].strip())
                            if cantidad > 0:
                                pedidos_dict[sku] = pedidos_dict.get(sku, 0) + cantidad
                        except:
                            pass
                elif line:
                    sku = line.strip().upper()
                    pedidos_dict[sku] = pedidos_dict.get(sku, 0) + 1
        
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
                        stock_total, stock_detalle = buscar_stock_general(st.session_state.stocks, sku)
                        
                        if stock_total == 0:
                            badge_estado = "badge-danger"
                            estado_texto = "❌ Sin stock"
                            a_cotizar = 0
                            total = 0
                        elif cant > stock_total:
                            badge_estado = "badge-warning"
                            estado_texto = f"⚠️ Stock: {stock_total}"
                            a_cotizar = stock_total
                            total = precio_info['precio'] * a_cotizar if precio_info['precio'] else 0
                        else:
                            badge_estado = "badge-ok"
                            estado_texto = "✅ OK"
                            a_cotizar = cant
                            total = precio_info['precio'] * a_cotizar if precio_info['precio'] else 0
                        
                        if not precio_info['encontrado']:
                            badge_estado = "badge-danger"
                            estado_texto = "❌ Sin precio"
                            a_cotizar = 0
                            total = 0
                        
                        # Mostrar origen del stock
                        stock_origen = ""
                        if stock_detalle:
                            for origen, qty in stock_detalle.items():
                                stock_origen += f'<span class="badge-ok" style="margin-right:5px;">📁 {origen[:30]}: {qty}</span>'
                        else:
                            stock_origen = '<span class="badge-danger">❌ Sin stock</span>'
                        
                        resultados.append({
                            'SKU': sku,
                            'Descripción': precio_info['descripcion'][:80],
                            'Precio': precio_info['precio'],
                            'Pedido': cant,
                            'Stock': stock_total,
                            'Origen': stock_origen,
                            'A Cotizar': a_cotizar,
                            'Total': total,
                            'Estado': estado_texto,
                            'Badge_Estado': badge_estado
                        })
                    
                    st.session_state.resultados = resultados
        
        if st.session_state.resultados:
            st.markdown("---")
            st.markdown("### 📊 Resultados")
            
            # Mostrar tabla de resultados
            for item in st.session_state.resultados:
                precio_str = f"S/. {item['Precio']:,.2f}" if item['Precio'] > 0 else "Sin precio"
                total_str = f"S/. {item['Total']:,.2f}"
                
                col1, col2, col3, col4, col5 = st.columns([2, 3, 1, 1, 1.5])
                with col1:
                    st.markdown(f"**{item['SKU']}**")
                with col2:
                    st.markdown(item['Descripción'][:50])
                with col3:
                    st.markdown(precio_str)
                with col4:
                    st.markdown(f"Pedido: {item['Pedido']}")
                with col5:
                    st.markdown(f"Stock: {obtener_icono_stock(item['Stock'])} {item['Stock']}")
                
                st.markdown(f"**A Cotizar:** {item['A Cotizar']} | **Total:** {total_str}")
                st.markdown(f"**Estado:** <span class='{item['Badge_Estado']}'>{item['Estado']}</span>", unsafe_allow_html=True)
                st.markdown(f"**Origen Stock:** {item['Origen']}", unsafe_allow_html=True)
                st.divider()
            
            # Tabla editable para ajustar cantidades
            st.markdown("### ✏️ Ajustar cantidades")
            
            df_ajuste = pd.DataFrame(st.session_state.resultados)
            df_editor = df_ajuste[['SKU', 'Descripción', 'Precio', 'Stock', 'A Cotizar']].copy()
            
            edited_df = st.data_editor(
                df_editor,
                column_config={
                    "SKU": st.column_config.TextColumn("SKU", disabled=True),
                    "Descripción": st.column_config.TextColumn("Descripción", disabled=True),
                    "Precio": st.column_config.NumberColumn("Precio", disabled=True),
                    "Stock": st.column_config.NumberColumn("Stock", disabled=True),
                    "A Cotizar": st.column_config.NumberColumn("A Cotizar", min_value=0, step=1),
                },
                hide_index=True,
                key="editor_cantidades"
            )
            
            # Actualizar resultados
            for idx, row in edited_df.iterrows():
                if idx < len(st.session_state.resultados):
                    nueva_cant = int(row['A Cotizar']) if pd.notna(row['A Cotizar']) else 0                    stock_disp = st.session_state.resultados[idx]['Stock']
                    precio = st.session_state.resultados[idx]['Precio']
                    
                    if nueva_cant > stock_disp and stock_disp > 0:
                        nueva_cant = stock_disp
                        st.warning(f"⚠️ {st.session_state.resultados[idx]['SKU']}: Ajustado a {stock_disp} (stock máximo)")
                    
                    st.session_state.resultados[idx]['A Cotizar'] = nueva_cant
                    st.session_state.resultados[idx]['Total'] = precio * nueva_cant if precio else 0
            
            # Resumen y generación de Excel
            items_validos = [r for r in st.session_state.resultados if r['A Cotizar'] > 0 and r['Precio'] > 0]
            total_general = sum(r['Total'] for r in items_validos)
            
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("✅ A cotizar", len(items_validos))
            col_m2.metric("💰 Total", f"S/. {total_general:,.2f}")
            col_m3.metric("📦 Total productos", len(st.session_state.resultados))
            
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
                        'cant': r['A Cotizar'], 
                        'p_u': r['Precio'], 
                        'total': r['Total']
                    } for r in items_validos]
                    
                    excel = generar_excel(items_excel, cliente, ruc_cliente)
                    st.download_button(
                        "💾 DESCARGAR", 
                        data=excel, 
                        file_name=f"Cotizacion_{cliente}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        use_container_width=True
                    )
                    st.session_state.cotizaciones += 1
                    st.session_state.total_prods = len(items_validos)
                    st.balloons()
                    st.success("✅ Cotización generada exitosamente")

# ============================================
# TAB 2: BUSCAR PRODUCTOS (simplificado)
# ============================================
with tab_buscar:
    st.markdown("### 🔍 Buscar Productos")
    
    if not st.session_state.catalogos:
        st.warning("🌿 Primero carga catálogos en la pestaña Cotización")
    else:
        busqueda = st.text_input("🔎 Buscar por SKU o descripción:", 
                                  placeholder="Ej: ABC-123 o nombre del producto")
        
        if busqueda and len(busqueda) >= 2:
            with st.spinner("Buscando..."):
                resultados = buscar_en_catalogos(
                    st.session_state.catalogos, 
                    busqueda, 
                    st.session_state.stocks, 
                    None,  # No mostrar precio en búsqueda
                    "GENERAL"
                )
            
            if resultados:
                st.success(f"✅ {len(resultados)} resultados")
                for res in resultados[:20]:
                    with st.expander(f"📦 {res['SKU']} - {res['Descripcion'][:50]}"):
                        st.markdown(f"**Stock total:** {res['Stock_Total']} unidades")
                        if res['Precio']:
                            st.markdown(f"**Precio:** S/. {res['Precio']:,.2f}")
                        
                        # Botón para agregar
                        cantidad = st.number_input("Cantidad", min_value=0, max_value=res['Stock_Total'] if res['Stock_Total'] > 0 else 100, 
                                                    value=1, key=f"buscar_add_{res['SKU']}")
                        if st.button(f"➕ Agregar {res['SKU']}", key=f"btn_add_{res['SKU']}"):
                            if res['SKU'] in st.session_state.productos_seleccionados:
                                st.session_state.productos_seleccionados[res['SKU']] += cantidad
                            else:
                                st.session_state.productos_seleccionados[res['SKU']] = cantidad
                            st.success(f"✅ {cantidad}x {res['SKU']} agregado")
                            st.rerun()
            else:
                st.warning("No se encontraron productos")
        
        # Mostrar productos seleccionados
        if st.session_state.productos_seleccionados:
            st.markdown("---")
            st.markdown("### 🛒 Productos seleccionados")
            for sku, cant in st.session_state.productos_seleccionados.items():
                st.markdown(f"- **{sku}**: {cant} unidades")
            
            if st.button("📋 Transferir a Cotización", use_container_width=True):
                st.session_state.skus_transferidos = st.session_state.productos_seleccionados.copy()
                st.session_state.productos_seleccionados = {}
                st.success("✅ Productos transferidos a la pestaña Cotización")
                st.info("👉 Ve a la pestaña Cotización y haz clic en PROCESAR")

# ============================================
# TAB 3: DASHBOARD
# ============================================
with tab_dashboard:
    st.markdown("### 📊 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📄 Cotizaciones", st.session_state.get('cotizaciones', 0))
    col2.metric("🌿 Productos cotizados", st.session_state.get('total_prods', 0))
    col3.metric("📚 Catálogos", len(st.session_state.get('catalogos', [])))
    
    st.markdown("---")
    st.markdown("### 📁 Archivos cargados")
    
    st.markdown("**Catálogos:**")
    for cat in st.session_state.get('catalogos', []):
        st.markdown(f"- {cat['nombre']}")
    
    st.markdown("**Stocks:**")
    for stock in st.session_state.get('stocks', []):
        st.markdown(f"- {stock['nombre']}")

st.markdown("---")
st.markdown("*💚 QTC Smart Sales Pro - Multi-format (Excel/CSV) | Flexible Column Mapping*")
