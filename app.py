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

# ============================================
# COLORES CORPORATIVOS
# ============================================
COLORES = {
    "fondo_principal": "#F0F2F6",
    "fondo_tarjetas": "#FFFFFF",
    "fondo_sidebar": "#1a472a",
    "texto_principal": "#1a1a2e",
    "texto_secundario": "#666666",
    "texto_blanco": "#FFFFFF",
    "primario": "#27AE60",
    "primario_oscuro": "#1E8449",
    "peligro": "#e74c3c",
    "advertencia": "#f39c12",
    "borde": "#E0E0E0",
}

# --- ESTILOS CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLORES["fondo_principal"]}; }}
    .main .block-container {{ padding-top: 1rem; }}
    h1, h2, h3, h4, p, div, label {{ color: {COLORES["texto_principal"]} !important; }}
    
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORES["fondo_sidebar"]} 0%, #0d2818 100%);
    }}
    [data-testid="stSidebar"] * {{ color: {COLORES["texto_blanco"]} !important; }}
    
    .stButton > button {{
        background: {COLORES["primario"]};
        color: white !important;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s;
    }}
    .stButton > button:hover {{
        background: {COLORES["primario_oscuro"]};
        transform: translateY(-2px);
    }}
    
    .metric-card {{
        background: {COLORES["fondo_tarjetas"]};
        border-radius: 15px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid {COLORES["borde"]};
    }}
    .metric-value {{
        font-size: 2rem;
        font-weight: bold;
        color: {COLORES["primario"]} !important;
    }}
    
    .producto-card {{
        background: {COLORES["fondo_tarjetas"]};
        border-radius: 10px;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid {COLORES["primario"]};
    }}
    
    .sin-stock {{
        background: #fee2e2;
        border-left-color: {COLORES["peligro"]};
    }}
    
    .stock-bajo {{
        background: #fff3e0;
        border-left-color: {COLORES["advertencia"]};
    }}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 💼 QTC Pro")
    st.markdown("---")
    if "cotizaciones" in st.session_state:
        st.metric("📄 Cotizaciones", st.session_state.get("cotizaciones", 0))
        st.metric("📦 Productos", st.session_state.get("total_prods", 0))
    st.markdown("---")
    st.markdown("### 🎯 Reglas")
    st.caption("• Xiaomi → Stock: apri004 + yessica")
    st.caption("• Otras marcas → Stock: apri1")
    st.caption("• SKU con * → Buscar en promociones")

# --- LOGIN ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown(f"""
        <div style="background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <h1 style="text-align: center; color: {COLORES['primario']};">💚 QTC Smart Sales</h1>
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
    """Convierte texto con formato de moneda a número float"""
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
    """Detecta y limpia las cabeceras de un DataFrame"""
    for i in range(min(20, len(df))):
        fila = [str(x).upper() for x in df.iloc[i].values]
        if any(h in item for h in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO'] for item in fila):
            df.columns = [str(c).strip() for c in df.iloc[i]]
            return df.iloc[i+1:].reset_index(drop=True)
    return df

def cargar_excel_completo(archivo):
    """Carga TODAS las hojas de un Excel y las devuelve como diccionario"""
    try:
        xls = pd.ExcelFile(archivo)
        hojas_data = {}
        
        for hoja in xls.sheet_names:
            df = pd.read_excel(archivo, sheet_name=hoja)
            df = limpiar_cabeceras(df)
            
            # Detectar columnas automáticamente
            col_sku = None
            col_desc = None
            columnas_precio = []
            
            for c in df.columns:
                c_str = str(c).upper()
                if any(p in c_str for p in ['SKU', 'COD', 'SAP', 'NUMERO']):
                    if col_sku is None:
                        col_sku = c
                if any(p in c_str for p in ['DESC', 'NOMBRE', 'PRODUCTO']):
                    if col_desc is None:
                        col_desc = c
                if any(p in c_str for p in ['PRECIO', 'CAJA', 'VIP', 'MAYOR', 'IR', 'BOX', 'SUGERIDO']):
                    columnas_precio.append(c)
            
            # Fallback si no se detectaron
            if col_sku is None and len(df.columns) > 0:
                col_sku = df.columns[0]
            if col_desc is None and len(df.columns) > 1:
                col_desc = df.columns[1]
            if not columnas_precio and len(df.columns) > 2:
                columnas_precio = [df.columns[2]]
            
            hojas_data[hoja] = {
                'df': df,
                'col_sku': col_sku,
                'col_desc': col_desc,
                'columnas_precio': columnas_precio
            }
        
        return {
            'nombre': archivo.name,
            'hojas': hojas_data,
            'total_hojas': len(hojas_data)
        }
    except Exception as e:
        st.error(f"Error en {archivo.name}: {str(e)}")
        return None

def cargar_stock(archivo):
    """Carga archivo de stock con todas sus hojas"""
    try:
        xls = pd.ExcelFile(archivo)
        dfs_stock = []
        
        for hoja in xls.sheet_names:
            df = pd.read_excel(archivo, sheet_name=hoja)
            df = limpiar_cabeceras(df)
            
            # Detectar columnas
            col_sku = None
            col_cant = None
            
            for c in df.columns:
                c_str = str(c).upper()
                if any(p in c_str for p in ['SKU', 'COD', 'SAP', 'NUMERO']):
                    if col_sku is None:
                        col_sku = c
                if any(p in c_str for p in ['DISP', 'STOCK', 'CANT', 'SALDO']):
                    if col_cant is None:
                        col_cant = c
            
            if col_sku is None and len(df.columns) > 0:
                col_sku = df.columns[0]
            if col_cant is None and len(df.columns) > 1:
                col_cant = df.columns[1]
            
            df['_origen_hoja'] = hoja
            dfs_stock.append(df)
        
        if dfs_stock:
            df_unificado = pd.concat(dfs_stock, ignore_index=True)
            return {
                'nombre': archivo.name,
                'df': df_unificado,
                'col_sku': col_sku,
                'col_cant': col_cant
            }
        return None
    except Exception as e:
        st.error(f"Error cargando stock {archivo.name}: {str(e)}")
        return None

def buscar_producto(catalogos, sku_buscar, es_promo=False):
    """Busca un SKU en todos los catálogos"""
    resultados = []
    
    for catalogo in catalogos:
        for hoja_nombre, hoja_data in catalogo['hojas'].items():
            # Si es promo y la hoja no es de promociones, saltar? (lo manejamos después)
            df = hoja_data['df']
            col_sku = hoja_data['col_sku']
            col_desc = hoja_data['col_desc']
            
            # Búsqueda exacta o parcial
            mask = df[col_sku].astype(str).str.contains(sku_buscar, case=False, na=False)
            
            for idx, row in df[mask].iterrows():
                resultados.append({
                    'archivo': catalogo['nombre'],
                    'hoja': hoja_nombre,
                    'sku': str(row[col_sku]),
                    'descripcion': str(row[col_desc]),
                    'col_precios': hoja_data['columnas_precio'],
                    'row': row
                })
    
    return resultados

def obtener_precio(row, columnas_precio, col_seleccionada):
    """Obtiene el precio de la columna seleccionada"""
    if col_seleccionada in columnas_precio and col_seleccionada in row.index:
        return corregir_numero(row[col_seleccionada])
    return 0.0

def obtener_stock_xiaomi(sku, stocks):
    """Obtiene stock sumando apri004 + yessica para productos Xiaomi"""
    stock_total = 0
    origenes = []
    
    for stock in stocks:
        if 'apri004' in stock['nombre'].lower() or 'yessica' in stock['nombre'].lower():
            mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku, case=False, na=False)
            if not stock['df'][mask].empty:
                cantidad = corregir_numero(stock['df'][mask].iloc[0][stock['col_cant']])
                stock_total += int(cantidad)
                origenes.append(f"{stock['nombre']}: {int(cantidad)}")
    
    return stock_total, origenes

def obtener_stock_general(sku, stocks):
    """Obtiene stock de apri1 para productos no Xiaomi"""
    stock_total = 0
    origenes = []
    
    for stock in stocks:
        if 'apri1' in stock['nombre'].lower():
            mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku, case=False, na=False)
            if not stock['df'][mask].empty:
                cantidad = corregir_numero(stock['df'][mask].iloc[0][stock['col_cant']])
                stock_total += int(cantidad)
                origenes.append(f"{stock['nombre']}: {int(cantidad)}")
    
    return stock_total, origenes

def generar_excel_cotizacion(items, cliente, ruc):
    """Genera Excel con el formato original de cotización"""
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    pd.DataFrame(items).to_excel(writer, sheet_name='Cotizacion', index=False, startrow=5)
    
    workbook = writer.book
    ws = writer.sheets['Cotizacion']
    
    # Formatos
    fmt_header = workbook.add_format({
        'bg_color': '#F79646', 
        'bold': True, 
        'border': 1, 
        'align': 'center',
        'font_color': 'white',
        'font_size': 11
    })
    
    fmt_money = workbook.add_format({
        'num_format': '"S/." #,##0.00',
        'border': 1,
        'align': 'right'
    })
    
    fmt_border = workbook.add_format({'border': 1})
    fmt_bold = workbook.add_format({'bold': True, 'font_size': 11})
    
    # Configurar columnas
    ws.set_column('A:A', 20)
    ws.set_column('B:B', 75)
    ws.set_column('C:C', 12)
    ws.set_column('D:D', 18)
    ws.set_column('E:E', 18)
    
    # Encabezados
    ws.write('A1', 'FECHA:', fmt_bold)
    ws.write('B1', datetime.now().strftime("%d/%m/%Y"))
    ws.write('A2', 'CLIENTE:', fmt_bold)
    ws.write('B2', cliente.upper())
    ws.write('A3', 'RUC:', fmt_bold)
    ws.write('B3', ruc)
    
    # Datos bancarios
    ws.merge_range('F1:H1', 'DATOS BANCARIOS', fmt_header)
    ws.write('F2', 'BBVA SOLES:', workbook.add_format({'font_color': 'red', 'bold': True, 'border': 1}))
    ws.write('G2', '0011-0616-0100012617', fmt_border)
    ws.write('H2', 'CCI: 011-616-0100012617-11', fmt_border)
    
    # Tabla
    headers = ['Código SAP', 'Descripción', 'Cantidad', 'Precio Unit.', 'Total']
    for i, header in enumerate(headers):
        ws.write(5, i, header, fmt_header)
    
    for row_idx, item in enumerate(items):
        ws.write_row(row_idx + 6, 0, [
            item['sku'], item['desc'], item['cant'], item['p_u'], item['total']
        ], fmt_border)
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
st.markdown("### Sistema Inteligente de Cotización con Múltiples Catálogos")
st.markdown("---")

# Inicializar session state
if 'resultados_procesados' not in st.session_state:
    st.session_state.resultados_procesados = None

tab_cotizacion, tab_busqueda, tab_config = st.tabs([
    "📦 Cotización", "🔍 Buscar Productos", "⚙️ Configuración"
])

# ============================================
# TAB CONFIGURACIÓN
# ============================================
with tab_config:
    st.markdown("### 📂 Carga de Archivos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📚 Catálogos de Precios")
        archivos_catalogos = st.file_uploader(
            "Sube uno o más catálogos (Excel)",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            key="catalogos"
        )
    
    with col2:
        st.markdown("#### 📦 Reportes de Stock")
        st.caption("• apri1.xlsx → Stock general (Innos, Ugreen, etc.)")
        st.caption("• apri004.xlsx + yessica.xlsx → Stock Xiaomi")
        
        archivos_stock = st.file_uploader(
            "Sube tus archivos de stock",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            key="stocks"
        )
    
    # Cargar catálogos
    if archivos_catalogos:
        with st.spinner("Cargando catálogos..."):
            catalogos_cargados = []
            for archivo in archivos_catalogos:
                resultado = cargar_excel_completo(archivo)
                if resultado:
                    catalogos_cargados.append(resultado)
                    st.success(f"✅ {archivo.name}: {resultado['total_hojas']} hojas")
            st.session_state.catalogos = catalogos_cargados
    
    # Cargar stocks
    if archivos_stock:
        with st.spinner("Cargando stocks..."):
            stocks_cargados = []
            for archivo in archivos_stock:
                resultado = cargar_stock(archivo)
                if resultado:
                    stocks_cargados.append(resultado)
                    st.success(f"✅ {archivo.name}: {len(resultado['df'])} productos")
            st.session_state.stocks = stocks_cargados
    
    # Mostrar resumen
    if st.session_state.get('catalogos'):
        st.markdown("---")
        st.markdown("#### ✅ Catálogos Cargados")
        for cat in st.session_state.catalogos:
            st.markdown(f"**{cat['nombre']}**")
            for hoja in cat['hojas'].keys():
                st.caption(f"  └─ {hoja}")

# ============================================
# TAB COTIZACIÓN
# ============================================
with tab_cotizacion:
    if not st.session_state.get('catalogos'):
        st.warning("⚠️ Primero carga los catálogos en la pestaña 'Configuración'")
    else:
        # Selección del tipo de precio
        st.markdown("### 💰 Configuración de Precios")
        
        # Recolectar todas las columnas de precio de todos los catálogos
        todas_columnas_precio = set()
        for cat in st.session_state.catalogos:
            for hoja_data in cat['hojas'].values():
                for col in hoja_data['columnas_precio']:
                    todas_columnas_precio.add(col)
        
        # Ordenar por prioridad
        orden_prioridad = ['CAJA', 'VIP', 'BOX', 'MAYOR', 'P.VIP', 'P.BOX', 'P.IR', 'SUGERIDO', 'PRECIO']
        columnas_ordenadas = []
        for p in orden_prioridad:
            for col in todas_columnas_precio:
                if p in str(col).upper():
                    columnas_ordenadas.append(col)
                    break
        for col in todas_columnas_precio:
            if col not in columnas_ordenadas:
                columnas_ordenadas.append(col)
        
        col_precio_seleccionada = st.selectbox(
            "Selecciona el tipo de precio para TODA la cotización:",
            columnas_ordenadas,
            help="Todos los productos usarán esta misma columna de precio"
        )
        
        st.markdown("---")
        st.markdown("### 📝 Ingresa los productos")
        
        # Área para SKUs con soporte para promociones (*)
        st.caption("💡 Usa * al inicio del SKU para buscar en promociones (ej: *CN123456)")
        
        if 'skus_transferidos' in st.session_state:
            texto_defecto = "\n".join([f"{sku}:{cant}" for sku, cant in st.session_state.skus_transferidos.items()])
            del st.session_state.skus_transferidos
        else:
            texto_defecto = ""
        
        texto_skus = st.text_area(
            "SKU:CANTIDAD (uno por línea)",
            height=150,
            value=texto_defecto,
            placeholder="Ejemplo:\nCN0900009WH8:5\n*CN0900509NA8:2\nCN0300010NA8:10"
        )
        
        # Procesar SKUs
        pedidos = []
        if texto_skus:
            for linea in texto_skus.split('\n'):
                linea = linea.strip()
                if not linea:
                    continue
                
                es_promo = linea.startswith('*')
                if es_promo:
                    linea = linea[1:]
                
                if ':' in linea:
                    sku, cant = linea.split(':')
                    try:
                        cantidad = int(cant.strip())
                        if cantidad > 0:
                            pedidos.append({
                                'sku': sku.strip().upper(),
                                'cantidad': cantidad,
                                'es_promo': es_promo
                            })
                    except:
                        pass
                elif linea:
                    pedidos.append({
                        'sku': linea.strip().upper(),
                        'cantidad': 1,
                        'es_promo': False
                    })
        
        if st.button("🚀 PROCESAR COTIZACIÓN", use_container_width=True, type="primary") and pedidos:
            with st.spinner("Buscando productos en todos los catálogos..."):
                resultados = []
                productos_no_encontrados = []
                
                for pedido in pedidos:
                    sku = pedido['sku']
                    cantidad_solicitada = pedido['cantidad']
                    es_promo = pedido['es_promo']
                    
                    # Buscar en catálogos
                    coincidencias = buscar_producto(st.session_state.catalogos, sku, es_promo)
                    
                    if not coincidencias:
                        productos_no_encontrados.append({
                            'SKU': sku,
                            'Cantidad': cantidad_solicitada,
                            'Motivo': 'No encontrado en ningún catálogo'
                        })
                        continue
                    
                    # Manejar múltiples coincidencias
                    producto_elegido = None
                    if len(coincidencias) > 1:
                        # Verificar si las descripciones son iguales
                        descripciones = set([c['descripcion'][:50] for c in coincidencias])
                        if len(descripciones) == 1:
                            # Misma descripción, tomar el primero
                            producto_elegido = coincidencias[0]
                        else:
                            # Descripciones diferentes, mostrar opciones
                            st.warning(f"⚠️ SKU {sku} encontrado en múltiples ubicaciones con diferentes descripciones:")
                            for i, c in enumerate(coincidencias):
                                st.markdown(f"{i+1}. `{c['archivo']}` → {c['hoja']}: {c['descripcion'][:60]}")
                            # Tomar el primero por defecto (el usuario puede ajustar)
                            producto_elegido = coincidencias[0]
                    else:
                        producto_elegido = coincidencias[0]
                    
                    # Obtener precio
                    precio = obtener_precio(
                        producto_elegido['row'],
                        producto_elegido['col_precios'],
                        col_precio_seleccionada
                    )
                    
                    # Determinar si es Xiaomi (por nombre del archivo o descripción)
                    es_xiaomi = 'xiaomi' in producto_elegido['archivo'].lower() or 'xiaomi' in producto_elegido['descripcion'].lower()
                    
                    # Obtener stock según reglas
                    if es_xiaomi:
                        stock, origen_stock = obtener_stock_xiaomi(sku, st.session_state.get('stocks', []))
                    else:
                        stock, origen_stock = obtener_stock_general(sku, st.session_state.get('stocks', []))
                    
                    # Determinar estado
                    if precio == 0:
                        estado = "⚠️ Sin precio"
                        color_estado = "orange"
                    elif stock >= cantidad_solicitada:
                        estado = "✅ OK"
                        color_estado = "green"
                    elif stock > 0 and stock < cantidad_solicitada:
                        estado = f"⚠️ Stock insuficiente (solo {stock})"
                        color_estado = "orange"
                    else:
                        estado = "❌ Sin stock"
                        color_estado = "red"
                    
                    resultados.append({
                        'id': sku,
                        'SKU': sku,
                        'Descripción': producto_elegido['descripcion'][:80],
                        'Archivo': producto_elegido['archivo'],
                        'Hoja': producto_elegido['hoja'],
                        'Precio': precio,
                        'Solicitado': cantidad_solicitada,
                        'Stock': stock,
                        'Origen_Stock': ', '.join(origen_stock) if origen_stock else 'Sin stock',
                        'Total': precio * cantidad_solicitada,
                        'Estado': estado,
                        'Color_Estado': color_estado,
                        'Es_Xiaomi': es_xiaomi,
                        'Es_Promo': es_promo
                    })
                
                st.session_state.resultados = resultados
                st.session_state.no_encontrados = productos_no_encontrados
        
        # Mostrar resultados
        if st.session_state.get('resultados'):
            st.markdown("---")
            st.markdown("### 📊 Resultados - Edita cantidades")
            
            resultados_editados = []
            
            # Mostrar tabla editable
            for i, item in enumerate(st.session_state.resultados):
                with st.container():
                    col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 3, 1.2, 1, 1.2, 1.2, 1.5])
                    
                    col1.markdown(f"**{item['SKU']}**")
                    col2.markdown(item['Descripción'])
                    col3.markdown(f"S/. {item['Precio']:,.2f}" if item['Precio'] > 0 else "Sin precio")
                    
                    nueva_cant = col4.number_input(
                        "Cant",
                        min_value=0,
                        max_value=999,
                        value=int(item['Solicitado']),
                        key=f"edit_{item['id']}_{i}",
                        label_visibility="collapsed"
                    )
                    
                    stock_text = f"{item['Stock']}"
                    if item['Origen_Stock'] and item['Origen_Stock'] != 'Sin stock':
                        stock_text += f"\n*{item['Origen_Stock'][:25]}*"
                    col5.markdown(stock_text)
                    
                    nuevo_total = item['Precio'] * nueva_cant
                    col6.markdown(f"S/. {nuevo_total:,.2f}")
                    
                    col7.markdown(f"<span style='color:{item['Color_Estado']}'>{item['Estado']}</span>", unsafe_allow_html=True)
                    
                    # Guardar editado
                    item_editado = item.copy()
                    item_editado['Solicitado'] = nueva_cant
                    item_editado['Total'] = nuevo_total
                    resultados_editados.append(item_editado)
                    
                    st.divider()
            
            # Productos no encontrados
            if st.session_state.get('no_encontrados'):
                st.markdown("### ⚠️ Productos no encontrados")
                for item in st.session_state.no_encontrados:
                    st.warning(f"❌ {item['SKU']} - {item['Motivo']}")
            
            # Resumen
            items_validos = [r for r in resultados_editados if r['Solicitado'] > 0 and r['Stock'] >= r['Solicitado'] and r['Precio'] > 0]
            total_cotizacion = sum(r['Total'] for r in items_validos)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("📦 Productos válidos", len(items_validos))
            col2.metric("💰 Total Cotización", f"S/. {total_cotizacion:,.2f}")
            col3.metric("⚠️ Excluidos/Sin stock", len([r for r in resultados_editados if r['Solicitado'] == 0 or r['Stock'] < r['Solicitado'] or r['Precio'] == 0]))
            
            # Generar cotización
            if items_validos:
                st.markdown("---")
                st.markdown("### 📥 Generar Cotización")
                
                col_cli1, col_cli2 = st.columns(2)
                with col_cli1:
                    cliente = st.text_input("🏢 Cliente", "CLIENTE NUEVO")
                with col_cli2:
                    ruc_cliente = st.text_input("📋 RUC/DNI", "-")
                
                if st.button("📥 GENERAR COTIZACIÓN", use_container_width=True, type="primary"):
                    items_excel = [{
                        'sku': r['SKU'],
                        'desc': r['Descripción'],
                        'cant': r['Solicitado'],
                        'p_u': r['Precio'],
                        'total': r['Total']
                    } for r in items_validos]
                    
                    excel_data = generar_excel_cotizacion(items_excel, cliente, ruc_cliente)
                    
                    st.download_button(
                        label="💾 DESCARGAR EXCEL",
                        data=excel_data,
                        file_name=f"Cotizacion_{cliente}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    
                    st.session_state.cotizaciones = st.session_state.get("cotizaciones", 0) + 1
                    st.session_state.total_prods = len(items_validos)
                    st.balloons()
                    st.success("✅ Cotización generada correctamente!")

# ============================================
# TAB BÚSQUEDA
# ============================================
with tab_busqueda:
    st.markdown("### 🔍 Buscar productos en catálogos")
    
    if not st.session_state.get('catalogos'):
        st.warning("⚠️ Primero carga los catálogos en 'Configuración'")
    else:
        busqueda = st.text_input("Buscar por SKU o descripción:", placeholder="Ej: CN0900009WH8, cargador, cable...")
        
        if busqueda:
            resultados_busqueda = []
            for catalogo in st.session_state.catalogos:
                for hoja_nombre, hoja_data in catalogo['hojas'].items():
                    df = hoja_data['df']
                    col_sku = hoja_data['col_sku']
                    col_desc = hoja_data['col_desc']
                    
                    mask_sku = df[col_sku].astype(str).str.contains(busqueda, case=False, na=False)
                    mask_desc = df[col_desc].astype(str).str.contains(busqueda, case=False, na=False)
                    
                    for idx, row in df[mask_sku | mask_desc].iterrows():
                        resultados_busqueda.append({
                            'SKU': str(row[col_sku]),
                            'Descripción': str(row[col_desc])[:80],
                            'Archivo': catalogo['nombre'],
                            'Hoja': hoja_nombre
                        })
            
            if resultados_busqueda:
                st.success(f"✅ {len(resultados_busqueda)} resultados encontrados")
                df_busqueda = pd.DataFrame(resultados_busqueda)
                st.dataframe(df_busqueda, use_container_width=True)
                
                if st.button("📋 Transferir primeros 20 SKU a Cotización"):
                    skus_dict = {r['SKU']: 1 for r in resultados_busqueda[:20]}
                    st.session_state.skus_transferidos = skus_dict
                    st.success("✅ Transferido! Ve a la pestaña Cotización")
                    st.info("💡 Puedes modificar las cantidades allí")
            else:
                st.warning("No se encontraron resultados")

st.markdown("---")
st.markdown("*💚 QTC Smart Sales Pro - Sistema Profesional de Cotización*")
