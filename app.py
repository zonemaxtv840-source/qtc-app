import streamlit as st
import pandas as pd
import re, io, os
from datetime import datetime
from PIL import Image
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# --- CONFIGURACIÓN ---
try:
    img_logo = Image.open("logo.png")
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon=img_logo, layout="wide")
except:
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon="💼", layout="wide")

# ============================================
# 🎨 COLORES
# ============================================
COLORES = {
    "fondo_principal": "#F8F9FA",
    "fondo_tarjetas": "#FFFFFF",
    "fondo_sidebar": "#1a472a",
    "texto_principal": "#2C3E50",
    "texto_secundario": "#6C757D",
    "texto_blanco": "#FFFFFF",
    "primario": "#27AE60",
    "primario_oscuro": "#1E8449",
    "borde": "#DEE2E6",
    "sombra": "rgba(0,0,0,0.1)",
}

# --- ESTILOS CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLORES["fondo_principal"]}; }}
    .main .block-container {{ color: {COLORES["texto_principal"]} !important; }}
    h1, h2, h3, p, div, label {{ color: {COLORES["texto_principal"]} !important; }}
    
    [data-testid="stSidebar"] {{
        background: {COLORES["fondo_sidebar"]};
    }}
    [data-testid="stSidebar"] * {{
        color: {COLORES["texto_blanco"]} !important;
    }}
    
    .stButton > button {{
        background: {COLORES["primario"]};
        color: white !important;
        border-radius: 8px;
        font-weight: 600;
    }}
    
    .metric-card {{
        background: {COLORES["fondo_tarjetas"]};
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 8px {COLORES["sombra"]};
    }}
    .metric-value {{
        font-size: 2rem;
        font-weight: bold;
        color: {COLORES["primario"]} !important;
    }}
    
    .precio-card {{
        background: {COLORES["fondo_tarjetas"]};
        border: 1px solid {COLORES["borde"]};
        border-radius: 10px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        cursor: pointer;
    }}
    .precio-card:hover {{
        border-color: {COLORES["primario"]};
        box-shadow: 0 2px 8px {COLORES["sombra"]};
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

# --- LOGIN ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown(f"""
        <div style="background: white; padding: 2rem; border-radius: 20px;">
            <h1 style="text-align: center; color: {COLORES['primario']};">💚 QTC Smart Sales</h1>
        </div>
        """, unsafe_allow_html=True)
        user = st.text_input("Usuario")
        pw = st.text_input("Contraseña", type="password")
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
    if pd.isna(valor) or str(valor).strip() in ["", "0"]:
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
    for i in range(min(15, len(df))):
        fila = [str(x).upper() for x in df.iloc[i].values]
        if any(h in item for h in ['SKU', 'SAP', 'CODIGO', 'ARTICULO', 'COD'] for item in fila):
            df.columns = [str(c).strip() for c in df.iloc[i]]
            return df.iloc[i+1:].reset_index(drop=True)
    return df

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
    
    # Configurar ancho de columnas
    ws.set_column('A:A', 20)   # SKU
    ws.set_column('B:B', 75)   # Descripción
    ws.set_column('C:C', 12)   # Cantidad
    ws.set_column('D:D', 18)   # Precio Unit.
    ws.set_column('E:E', 18)   # Total
    
    # Escribir encabezados y datos del cliente
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
    
    # Encabezados de la tabla
    headers = ['Código SAP', 'Descripción', 'Cantidad', 'Precio Unit.', 'Total']
    for i, header in enumerate(headers):
        ws.write(5, i, header, fmt_header)
    
    # Escribir datos
    for row_idx, item in enumerate(items):
        ws.write_row(row_idx + 6, 0, [
            item['sku'], 
            item['desc'], 
            item['cant'], 
            item['p_u'], 
            item['total']
        ], fmt_border)
        ws.write(row_idx + 6, 3, item['p_u'], fmt_money)
        ws.write(row_idx + 6, 4, item['total'], fmt_money)
    
    # Total
    total_row = len(items) + 6
    ws.write(total_row, 3, 'TOTAL S/.', fmt_header)
    ws.write(total_row, 4, sum(item['total'] for item in items), fmt_money)
    
    writer.close()
    return output.getvalue()

def cargar_todas_las_hojas(archivo):
    """Carga TODAS las hojas de un archivo Excel y las une"""
    try:
        xls = pd.ExcelFile(archivo)
        todas_las_hojas = []
        
        for hoja in xls.sheet_names:
            df = pd.read_excel(archivo, sheet_name=hoja)
            df = limpiar_cabeceras(df)
            
            # Identificar columnas
            col_sku = None
            col_desc = None
            
            for c in df.columns:
                c_str = str(c).upper()
                if any(p in c_str for p in ['SKU', 'COD', 'NUMERO', 'ARTICULO']):
                    if not col_sku or len(c_str) < len(str(col_sku)):
                        col_sku = c
                if any(p in c_str for p in ['DESC', 'NOMBRE', 'PRODUCTO']):
                    if not col_desc or len(c_str) < len(str(col_desc)):
                        col_desc = c
            
            if col_sku is None and len(df.columns) > 0:
                col_sku = df.columns[0]
            if col_desc is None and len(df.columns) > 1:
                col_desc = df.columns[1]
            
            # Identificar columnas de precio
            cols_precio = [c for c in df.columns if any(p in str(c).upper() for p in ['PRECIO', 'MAYOR', 'UNIT', 'VENTA'])]
            
            if col_sku and col_desc:
                df['_origen_archivo'] = archivo.name
                df['_origen_hoja'] = hoja
                df['_origen_sku_col'] = col_sku
                df['_origen_desc_col'] = col_desc
                df['_columnas_precio'] = str(cols_precio)  # Guardar columnas de precio
                
                todas_las_hojas.append(df)
        
        if todas_las_hojas:
            df_completo = pd.concat(todas_las_hojas, ignore_index=True)
            
            # Unificar SKU y descripción
            sku_values = []
            desc_values = []
            
            for idx, row in df_completo.iterrows():
                col_sku = row.get('_origen_sku_col')
                sku = str(row[col_sku]) if col_sku and col_sku in df_completo.columns else ""
                sku_values.append(sku)
                
                col_desc = row.get('_origen_desc_col')
                desc = str(row[col_desc]) if col_desc and col_desc in df_completo.columns else ""
                desc_values.append(desc)
            
            df_completo['_sku_unificado'] = sku_values
            df_completo['_desc_unificado'] = desc_values
            
            return {
                'nombre': archivo.name,
                'df': df_completo,
                'hojas': xls.sheet_names,
                'total_filas': len(df_completo)
            }
        return None
    except Exception as e:
        st.error(f"Error en {archivo.name}: {str(e)}")
        return None

def obtener_columnas_precio(catalogos):
    """Obtiene todas las columnas de precio disponibles en los catálogos"""
    columnas_precio = {}
    
    for catalogo in catalogos:
        df = catalogo['df']
        columnas = []
        
        for col in df.columns:
            col_str = str(col).upper()
            if any(p in col_str for p in ['PRECIO', 'MAYOR', 'UNIT', 'VENTA', 'PRECIO1', 'PRECIO2']):
                columnas.append(col)
        
        if columnas:
            columnas_precio[catalogo['nombre']] = columnas
    
    return columnas_precio

def buscar_sku_en_catalogos(catalogos, sku, col_precio_seleccionada=None):
    """Busca un SKU en todos los catálogos y devuelve información con precio"""
    for catalogo in catalogos:
        df = catalogo['df']
        mask = df['_sku_unificado'].astype(str).str.contains(sku, case=False, na=False)
        productos = df[mask]
        
        if not productos.empty:
            prod = productos.iloc[0]
            
            # Determinar precio
            precio = 0
            if col_precio_seleccionada and col_precio_seleccionada in df.columns:
                precio = corregir_numero(prod[col_precio_seleccionada])
            else:
                # Buscar automáticamente la primera columna de precio
                for col in df.columns:
                    if any(p in str(col).upper() for p in ['PRECIO', 'MAYOR', 'UNIT']):
                        precio = corregir_numero(prod[col])
                        break
            
            return {
                'encontrado': True,
                'archivo': catalogo['nombre'],
                'hoja': prod.get('_origen_hoja', 'N/A'),
                'sku': str(prod['_sku_unificado']),
                'descripcion': str(prod['_desc_unificado']),
                'precio': precio,
                'datos': prod.to_dict()
            }
    
    return {'encontrado': False}

# --- INTERFAZ PRINCIPAL ---
st.title("💚 QTC Smart Sales Pro")
st.markdown("### 🔍 Busca automáticamente en TODAS las hojas de tus Excel")
st.markdown("---")

tab_pedidos, tab_busqueda, tab_imagen, tab_dashboard = st.tabs([
    "📦 Gestión de Pedidos", 
    "🔍 Búsqueda Múltiple", 
    "🤖 SKU por Imagen", 
    "📊 Dashboard"
])

# ============================================
# TAB 1: GESTIÓN DE PEDIDOS
# ============================================
with tab_pedidos:
    st.sidebar.header("📂 Carga de Archivos")
    
    # Subir múltiples catálogos
    st.sidebar.markdown("### 📚 Catálogos (Excel)")
    st.sidebar.caption("✨ El sistema buscará en TODAS las hojas")
    
    archivos_catalogos = st.sidebar.file_uploader(
        "Sube uno o más archivos Excel",
        type=['xlsx', 'xls'],
        accept_multiple_files=True,
        key="catalogos_multi"
    )
    
    if archivos_catalogos:
        catalogos_cargados = []
        
        with st.spinner("Cargando todas las hojas..."):
            for archivo in archivos_catalogos:
                resultado = cargar_todas_las_hojas(archivo)
                if resultado:
                    catalogos_cargados.append(resultado)
                    st.sidebar.success(f"✅ {archivo.name}: {len(resultado['hojas'])} hojas, {resultado['total_filas']} productos")
        
        st.session_state.catalogos = catalogos_cargados
        
        # Selección de columnas de precio
        if catalogos_cargados:
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 💰 Configuración de Precios")
            
            columnas_precio = obtener_columnas_precio(catalogos_cargados)
            
            # Selector global de precio
            opciones_precio = []
            for archivo, cols in columnas_precio.items():
                for col in cols:
                    opciones_precio.append(f"{archivo} → {col}")
            
            if opciones_precio:
                seleccion_precio = st.sidebar.selectbox(
                    "Selecciona qué columna de precio usar:",
                    opciones_precio,
                    help="Puedes cambiar esta selección en cualquier momento"
                )
                st.session_state.col_precio_seleccionada = seleccion_precio.split(" → ")[-1]
            else:
                st.sidebar.warning("No se detectaron columnas de precio")
                st.session_state.col_precio_seleccionada = None
        
        # Subir stock
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📦 Reporte de Stock")
        archivo_stock = st.sidebar.file_uploader("Stock (Excel)", type=['xlsx', 'xls'], key="stock_file")
        
        if archivo_stock:
            try:
                xls_stock = pd.ExcelFile(archivo_stock)
                dfs_stock = []
                
                for hoja in xls_stock.sheet_names:
                    df = pd.read_excel(archivo_stock, sheet_name=hoja)
                    df = limpiar_cabeceras(df)
                    df['_origen_hoja'] = hoja
                    dfs_stock.append(df)
                
                df_stock_unificado = pd.concat(dfs_stock, ignore_index=True)
                
                col_sku = next((c for c in df_stock_unificado.columns if 'SKU' in str(c).upper() or 'COD' in str(c).upper()), df_stock_unificado.columns[0])
                col_cant = next((c for c in df_stock_unificado.columns if 'DISP' in str(c).upper() or 'STOCK' in str(c).upper()), df_stock_unificado.columns[-1])
                
                st.session_state.df_stock = df_stock_unificado
                st.session_state.col_stock_sku = col_sku
                st.session_state.col_stock_cant = col_cant
                
                st.sidebar.success(f"✅ Stock: {len(df_stock_unificado)} productos en {len(xls_stock.sheet_names)} hojas")
            except Exception as e:
                st.sidebar.error(f"Error: {str(e)}")
    
    # Mostrar interfaz principal
    if st.session_state.get('catalogos'):
        st.success(f"✅ {len(st.session_state.catalogos)} catálogo(s) procesados correctamente")
        
        # Mostrar resumen
        with st.expander("📋 Ver detalle de catálogos cargados"):
            for cat in st.session_state.catalogos:
                st.markdown(f"**📗 {cat['nombre']}**")
                st.markdown(f"- Hojas: {', '.join(cat['hojas'])}")
                st.markdown(f"- Productos: {cat['total_filas']:,}")
                st.markdown("---")
        
        # Mostrar precio seleccionado
        if st.session_state.get('col_precio_seleccionada'):
            st.info(f"💰 Precio seleccionado: **{st.session_state.col_precio_seleccionada}**")
        
        # Área de SKUs
        st.subheader("📝 Ingresa los SKU y cantidades")
        
        if 'skus_transferidos' in st.session_state:
            texto_defecto = "\n".join([f"{sku}:{cant}" for sku, cant in st.session_state.skus_transferidos.items()])
            del st.session_state.skus_transferidos
        else:
            texto_defecto = ""
        
        texto_skus = st.text_area(
            "Formato: SKU:CANTIDAD (uno por línea)", 
            height=150,
            value=texto_defecto,
            placeholder="Ejemplo:\nABC123:5\nXYZ789:2\nPROD456:10"
        )
        
        pedidos = {}
        if texto_skus:
            for linea in texto_skus.split('\n'):
                linea = linea.strip()
                if ':' in linea:
                    sku, cant = linea.split(':')
                    pedidos[sku.strip().upper()] = int(cant.strip())
                elif linea:
                    pedidos[linea.strip().upper()] = 1
        
        if st.button("🚀 PROCESAR DISPONIBILIDAD", use_container_width=True) and pedidos:
            with st.spinner("Buscando en TODAS las hojas..."):
                resultados = []
                
                for sku, cant_solic in pedidos.items():
                    busqueda = buscar_sku_en_catalogos(
                        st.session_state.catalogos, 
                        sku, 
                        st.session_state.get('col_precio_seleccionada')
                    )
                    
                    if busqueda['encontrado']:
                        # Buscar stock
                        stock = 0
                        if st.session_state.get('df_stock') is not None:
                            mask_stock = st.session_state.df_stock[st.session_state.col_stock_sku].astype(str).str.contains(sku, case=False, na=False)
                            if not st.session_state.df_stock[mask_stock].empty:
                                stock = int(corregir_numero(st.session_state.df_stock[mask_stock].iloc[0][st.session_state.col_stock_cant]))
                        
                        resultados.append({
                            'SKU': sku,
                            'Archivo': busqueda['archivo'],
                            'Hoja': busqueda['hoja'],
                            'Descripción': busqueda['descripcion'][:80],
                            'Precio': busqueda['precio'],
                            'Solicitado': cant_solic,
                            'Stock': stock,
                            'Total': busqueda['precio'] * cant_solic,
                            'Estado': '✅ OK' if stock >= cant_solic else '⚠️ Sin Stock'
                        })
                    else:
                        resultados.append({
                            'SKU': sku,
                            'Archivo': '❌ No encontrado',
                            'Hoja': '-',
                            'Descripción': 'Producto no encontrado',
                            'Precio': 0,
                            'Solicitado': cant_solic,
                            'Stock': 0,
                            'Total': 0,
                            'Estado': '❌ No existe'
                        })
                
                if resultados:
                    df_res = pd.DataFrame(resultados)
                    st.dataframe(df_res, use_container_width=True)
                    
                    total_ok = sum(r['Total'] for r in resultados if r['Estado'] == '✅ OK')
                    productos_ok = len([r for r in resultados if r['Estado'] == '✅ OK'])
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("💰 Total Cotización", f"S/. {total_ok:,.2f}")
                    col2.metric("✅ Con Stock", productos_ok)
                    col3.metric("❌ Sin Stock/Novencontrado", len(resultados) - productos_ok)
                    
                    with st.expander("📥 Generar Cotización", expanded=True):
                        col_cli1, col_cli2 = st.columns(2)
                        with col_cli1:
                            cliente = st.text_input("🏢 Cliente", "CLIENTE NUEVO")
                        with col_cli2:
                            ruc = st.text_input("📋 RUC/DNI", "-")
                        
                        items_ok = [r for r in resultados if r['Estado'] == '✅ OK']
                        
                        if items_ok:
                            # Formato para la cotización original
                            items_cotizacion = [{
                                'sku': r['SKU'],
                                'desc': r['Descripción'],
                                'cant': r['Solicitado'],
                                'p_u': r['Precio'],
                                'total': r['Total']
                            } for r in items_ok]
                            
                            st.markdown(f"""
                            <div style="background: #d4edda; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                                <strong>📄 Resumen de Cotización:</strong><br>
                                Cliente: {cliente}<br>
                                Productos: {len(items_ok)}<br>
                                Total: S/. {total_ok:,.2f}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button("📥 Descargar Cotización en Excel", use_container_width=True):
                                excel_data = generar_excel_cotizacion(items_cotizacion, cliente, ruc)
                                st.download_button(
                                    label="💾 Guardar archivo",
                                    data=excel_data,
                                    file_name=f"Cotizacion_{cliente}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                                st.session_state.cotizaciones = st.session_state.get("cotizaciones", 0) + 1
                                st.session_state.total_prods = len(items_ok)
                                st.balloons()
                        else:
                            st.warning("No hay productos con stock disponible para cotizar")
    else:
        st.info("📂 Sube tus catálogos en la barra lateral izquierda")

# ============================================
# TAB 2: BÚSQUEDA MÚLTIPLE
# ============================================
with tab_busqueda:
    st.markdown("### 🔍 Búsqueda en TODOS los catálogos")
    
    if st.session_state.get('catalogos'):
        tipo_busqueda = st.radio("Buscar por:", ["📝 Descripción", "🔢 SKU"], horizontal=True)
        termino = st.text_input("Escribe tu búsqueda:", placeholder="Ej: LAPTOP, USB, HDMI...")
        
        if termino:
            tipo = 'desc' if tipo_busqueda == "📝 Descripción" else 'sku'
            resultados = []
            
            for catalogo in st.session_state.catalogos:
                df = catalogo['df']
                
                if tipo == 'sku':
                    mask = df['_sku_unificado'].astype(str).str.contains(termino, case=False, na=False)
                else:
                    mask = df['_desc_unificado'].astype(str).str.contains(termino, case=False, na=False)
                
                for idx, row in df[mask].iterrows():
                    # Obtener precio
                    precio = 0
                    col_precio = st.session_state.get('col_precio_seleccionada')
                    if col_precio and col_precio in df.columns:
                        precio = corregir_numero(row[col_precio])
                    
                    resultados.append({
                        'Archivo': catalogo['nombre'],
                        'Hoja': row.get('_origen_hoja', 'N/A'),
                        'SKU': row['_sku_unificado'],
                        'Descripción': row['_desc_unificado'][:80],
                        'Precio': precio
                    })
            
            if resultados:
                st.success(f"✅ {len(resultados)} resultados encontrados")
                df_busq = pd.DataFrame(resultados)
                st.dataframe(df_busq, use_container_width=True)
            else:
                st.warning("No se encontraron resultados")
    else:
        st.warning("Primero carga catálogos en 'Gestión de Pedidos'")

# ============================================
# TAB 3: SKU POR IMAGEN
# ============================================
with tab_imagen:
    st.markdown("### 🤖 Captura de SKU por Imagen")
    
    imagen = st.file_uploader("Subir imagen", type=['jpg', 'png', 'jpeg'])
    
    if imagen:
        img = Image.open(imagen)
        st.image(img, width=250)
        
        if st.button("🔍 Extraer SKU con IA"):
            with st.spinner("Procesando..."):
                try:
                    import google.generativeai as genai
                    api_key = st.secrets.get("GEMINI_API_KEY", "")
                    
                    if not api_key:
                        st.warning("⚠️ API Key no configurada")
                    else:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content([
                            "Extrae todos los códigos SKU y sus cantidades. Devuelve SOLO JSON: [{\"sku\": \"CODIGO\", \"cantidad\": NUMERO}]",
                            img
                        ])
                        
                        texto = response.text
                        match = re.search(r'\[.*\]', texto, re.DOTALL)
                        if match:
                            import json
                            datos = json.loads(match.group())
                            st.success(f"✅ {len(datos)} SKUs detectados")
                            df_detectados = pd.DataFrame(datos)
                            st.dataframe(df_detectados, use_container_width=True)
                            
                            if st.button("📋 Transferir a Pedidos"):
                                skus_dict = {item['sku']: item['cantidad'] for item in datos}
                                st.session_state.skus_transferidos = skus_dict
                                st.success("Transferido! Ve a Gestión de Pedidos")
                        else:
                            st.warning("No se detectaron SKUs")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    st.markdown("### ✏️ Entrada Manual")
    num = st.number_input("Cantidad de productos", min_value=1, max_value=10, value=3)
    
    skus_manual = {}
    for i in range(int(num)):
        col1, col2 = st.columns(2)
        with col1:
            sku = st.text_input(f"SKU {i+1}", key=f"manual_{i}")
        with col2:
            cant = st.number_input("Cantidad", min_value=1, value=1, key=f"manual_cant_{i}")
        if sku:
            skus_manual[sku.upper()] = cant
    
    if skus_manual and st.button("📋 Transferir Manual"):
        st.session_state.skus_transferidos = skus_manual
        st.success(f"✅ {len(skus_manual)} SKUs transferidos")

# ============================================
# TAB 4: DASHBOARD
# ============================================
with tab_dashboard:
    st.markdown("### 📊 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.get("cotizaciones", 0)}</div>
            <div class="metric-label">Cotizaciones</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        total_hojas = sum(len(cat.get('hojas', [])) for cat in st.session_state.get('catalogos', []))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(st.session_state.get('catalogos', []))}</div>
            <div class="metric-label">Archivos</div>
            <div class="metric-label" style="font-size:0.7rem;">({total_hojas} hojas)</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        total_productos = sum(cat.get('total_filas', 0) for cat in st.session_state.get('catalogos', []))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_productos:,}</div>
            <div class="metric-label">Productos Indexados</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 💰 Columna de Precio Seleccionada")
    if st.session_state.get('col_precio_seleccionada'):
        st.success(f"**{st.session_state.col_precio_seleccionada}**")
    else:
        st.info("No se ha seleccionado ninguna columna de precio aún")

st.markdown("---")
st.markdown("*💚 QTC Smart Sales - Búsqueda Automática en TODAS las hojas con selección de precio*")
