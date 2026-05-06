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
    
    .hoja-info {{
        font-size: 0.7rem;
        color: {COLORES["texto_secundario"]};
        margin-left: 5px;
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
    s = re.sub(r'[^\d.,]', '', str(valor).replace('S/', '').replace('$', ''))
    s = s.replace(',', '.') if '.' not in s else s.replace(',', '')
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

def cargar_todas_las_hojas(archivo):
    """Carga TODAS las hojas de un archivo Excel y las une en un solo DataFrame"""
    try:
        xls = pd.ExcelFile(archivo)
        todas_las_hojas = []
        
        for hoja in xls.sheet_names:
            df = pd.read_excel(archivo, sheet_name=hoja)
            df = limpiar_cabeceras(df)
            
            # Identificar columnas automáticamente
            col_sku = None
            col_desc = None
            
            # Buscar columna de SKU
            for c in df.columns:
                c_str = str(c).upper()
                if any(palabra in c_str for palabra in ['SKU', 'COD', 'NUMERO', 'ARTICULO', 'PRODUCTO']):
                    if not col_sku or len(c_str) < len(str(col_sku)):  # Preferir la más corta
                        col_sku = c
            
            # Buscar columna de descripción
            for c in df.columns:
                c_str = str(c).upper()
                if any(palabra in c_str for palabra in ['DESC', 'NOMBRE', 'PRODUCTO', 'ITEM']):
                    if not col_desc or len(c_str) < len(str(col_desc)):
                        col_desc = c
            
            # Si no se encontraron, usar las primeras columnas
            if col_sku is None and len(df.columns) > 0:
                col_sku = df.columns[0]
            if col_desc is None and len(df.columns) > 1:
                col_desc = df.columns[1]
            
            if col_sku and col_desc:
                # Agregar columnas de origen
                df['_origen_archivo'] = archivo.name
                df['_origen_hoja'] = hoja
                df['_origen_sku_col'] = col_sku
                df['_origen_desc_col'] = col_desc
                
                todas_las_hojas.append(df)
        
        if todas_las_hojas:
            # Unir todas las hojas
            df_completo = pd.concat(todas_las_hojas, ignore_index=True)
            
            # Renombrar columnas para consistencia
            # Crear un mapeo de columnas
            return {
                'nombre': archivo.name,
                'df': df_completo,
                'hojas': xls.sheet_names,
                'total_filas': len(df_completo),
                'col_sku': '_sku_unificado',  # Lo crearemos después
                'col_desc': '_desc_unificado'
            }
        
        return None
        
    except Exception as e:
        st.error(f"Error cargando {archivo.name}: {str(e)}")
        return None

def unificar_dataframe(df_completo):
    """Unifica las columnas SKU y Descripción de diferentes hojas"""
    # Crear columnas unificadas
    sku_values = []
    desc_values = []
    
    for idx, row in df_completo.iterrows():
        # Obtener SKU de la columna correspondiente
        col_sku = row.get('_origen_sku_col')
        if col_sku and col_sku in df_completo.columns:
            sku = str(row[col_sku]) if pd.notna(row[col_sku]) else ""
        else:
            sku = ""
        
        # Obtener descripción
        col_desc = row.get('_origen_desc_col')
        if col_desc and col_desc in df_completo.columns:
            desc = str(row[col_desc]) if pd.notna(row[col_desc]) else ""
        else:
            desc = ""
        
        sku_values.append(sku)
        desc_values.append(desc)
    
    df_completo['_sku_unificado'] = sku_values
    df_completo['_desc_unificado'] = desc_values
    
    return df_completo

def buscar_en_todos_catalogos(catalogos, termino, tipo='sku'):
    """Busca en todos los catálogos (todas las hojas ya combinadas)"""
    resultados = []
    
    for catalogo in catalogos:
        df = catalogo['df']
        
        if tipo == 'sku':
            mask = df['_sku_unificado'].astype(str).str.contains(termino, case=False, na=False)
        else:
            mask = df['_desc_unificado'].astype(str).str.contains(termino, case=False, na=False)
        
        for idx, row in df[mask].iterrows():
            resultados.append({
                'archivo': catalogo['nombre'],
                'hoja': row.get('_origen_hoja', 'N/A'),
                'sku': row['_sku_unificado'],
                'descripcion': row['_desc_unificado'][:100],
                'datos_completos': row.to_dict()
            })
    
    return resultados

def generar_excel(items, cliente, ruc):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df = pd.DataFrame(items)
    df.to_excel(writer, sheet_name='Cotizacion', index=False)
    writer.close()
    return output.getvalue()

def extraer_skus_gemini(image):
    try:
        import google.generativeai as genai
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key:
            return []
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([
            "Extrae todos los códigos SKU y sus cantidades de esta imagen. "
            "Devuelve SOLO un array JSON: [{\"sku\": \"CODIGO\", \"cantidad\": NUMERO}]",
            image
        ])
        texto = response.text
        match = re.search(r'\[.*\]', texto, re.DOTALL)
        if match:
            import json
            return json.loads(match.group())
        return []
    except:
        return []

# --- INTERFAZ PRINCIPAL ---
st.title("💚 QTC Smart Sales Pro")
st.markdown("### 🔍 Busca automáticamente en TODAS las hojas de tus Excel")
st.markdown("---")

tab_pedidos, tab_busqueda, tab_imagen, tab_dashboard = st.tabs([
    "📦 Gestión de Pedidos", 
    "🔍 Búsqueda Inteligente", 
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
    st.sidebar.caption("✨ El sistema buscará en TODAS las hojas automáticamente")
    
    archivos_catalogos = st.sidebar.file_uploader(
        "Sube uno o más archivos Excel",
        type=['xlsx', 'xls'],
        accept_multiple_files=True,
        key="catalogos_multi"
    )
    
    if archivos_catalogos:
        catalogos_cargados = []
        
        with st.spinner("Cargando y procesando todas las hojas..."):
            for archivo in archivos_catalogos:
                resultado = cargar_todas_las_hojas(archivo)
                if resultado:
                    # Unificar el DataFrame
                    df_unificado = unificar_dataframe(resultado['df'])
                    resultado['df'] = df_unificado
                    catalogos_cargados.append(resultado)
                    
                    st.sidebar.success(f"✅ {archivo.name}: {len(resultado['hojas'])} hojas, {resultado['total_filas']} productos")
        
        st.session_state.catalogos = catalogos_cargados
        
        # Subir stock
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📦 Reporte de Stock")
        archivo_stock = st.sidebar.file_uploader("Stock (Excel)", type=['xlsx', 'xls'], key="stock_file")
        
        if archivo_stock:
            try:
                # También cargar todas las hojas del stock
                xls_stock = pd.ExcelFile(archivo_stock)
                dfs_stock = []
                
                for hoja in xls_stock.sheet_names:
                    df = pd.read_excel(archivo_stock, sheet_name=hoja)
                    df = limpiar_cabeceras(df)
                    df['_origen_hoja'] = hoja
                    dfs_stock.append(df)
                
                df_stock_unificado = pd.concat(dfs_stock, ignore_index=True)
                
                # Identificar columnas
                col_sku = next((c for c in df_stock_unificado.columns if 'SKU' in str(c).upper() or 'COD' in str(c).upper()), df_stock_unificado.columns[0])
                col_cant = next((c for c in df_stock_unificado.columns if 'DISP' in str(c).upper() or 'STOCK' in str(c).upper()), df_stock_unificado.columns[-1])
                
                st.session_state.df_stock = df_stock_unificado
                st.session_state.col_stock_sku = col_sku
                st.session_state.col_stock_cant = col_cant
                
                st.sidebar.success(f"✅ Stock: {len(df_stock_unificado)} productos en {len(xls_stock.sheet_names)} hojas")
                
            except Exception as e:
                st.sidebar.error(f"Error: {str(e)}")
    
    # Mostrar interfaz si hay catálogos
    if st.session_state.get('catalogos'):
        st.success(f"✅ {len(st.session_state.catalogos)} catálogo(s) procesados correctamente")
        
        # Mostrar resumen
        with st.expander("📋 Ver detalle de catálogos cargados"):
            for cat in st.session_state.catalogos:
                st.markdown(f"**📗 {cat['nombre']}**")
                st.markdown(f"- Hojas: {', '.join(cat['hojas'])}")
                st.markdown(f"- Total productos: {cat['total_filas']}")
                st.markdown("---")
        
        # Área de SKUs
        st.subheader("📝 Ingresa los SKU y cantidades")
        
        if 'skus_transferidos' in st.session_state:
            texto_defecto = "\n".join([f"{sku}:{cant}" for sku, cant in st.session_state.skus_transferidos.items()])
            del st.session_state.skus_transferidos
        else:
            texto_defecto = ""
        
        # Opción de pegar lista
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
        
        # Configuración de precio
        st.subheader("💰 Precios")
        
        # Recopilar todas las columnas de precio de todos los catálogos
        todas_columnas_precio = set()
        for cat in st.session_state.catalogos:
            for col in cat['df'].columns:
                if 'PRECIO' in str(col).upper() or 'MAYOR' in str(col).upper() or 'UNIT' in str(col).upper():
                    todas_columnas_precio.add(col)
        
        if todas_columnas_precio:
            col_precio = st.selectbox("Selecciona la columna de precio:", list(todas_columnas_precio))
        else:
            col_precio = None
            st.warning("No se detectaron columnas de precio. Usando 0.")
        
        if st.button("🚀 PROCESAR DISPONIBILIDAD", use_container_width=True) and pedidos:
            with st.spinner("Buscando en TODAS las hojas de TODOS los catálogos..."):
                resultados = []
                
                for sku, cant_solic in pedidos.items():
                    encontrado = False
                    
                    for catalogo in st.session_state.catalogos:
                        df = catalogo['df']
                        
                        # Buscar en el DataFrame unificado
                        mask = df['_sku_unificado'].astype(str).str.contains(sku, case=False, na=False)
                        productos = df[mask]
                        
                        if not productos.empty:
                            encontrado = True
                            prod = productos.iloc[0]
                            
                            # Obtener precio
                            precio = 0
                            if col_precio and col_precio in df.columns:
                                precio = corregir_numero(prod[col_precio])
                            
                            # Buscar stock
                            stock = 0
                            if st.session_state.get('df_stock') is not None:
                                mask_stock = st.session_state.df_stock[st.session_state.col_stock_sku].astype(str).str.contains(sku, case=False, na=False)
                                if not st.session_state.df_stock[mask_stock].empty:
                                    stock = int(corregir_numero(st.session_state.df_stock[mask_stock].iloc[0][st.session_state.col_stock_cant]))
                            
                            resultados.append({
                                'SKU': sku,
                                'Archivo': catalogo['nombre'],
                                'Hoja': prod.get('_origen_hoja', 'N/A'),
                                'Descripción': prod['_desc_unificado'][:60],
                                'Precio': precio,
                                'Solicitado': cant_solic,
                                'Stock': stock,
                                'Total': precio * cant_solic,
                                'Estado': '✅ OK' if stock >= cant_solic else '⚠️ Sin Stock'
                            })
                            break
                    
                    if not encontrado:
                        resultados.append({
                            'SKU': sku,
                            'Archivo': '❌ No encontrado',
                            'Hoja': '-',
                            'Descripción': 'Producto no encontrado en ningún catálogo',
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
                    col1.metric("💰 Total", f"S/. {total_ok:,.2f}")
                    col2.metric("✅ OK", productos_ok)
                    col3.metric("❌ No encontrados", len(resultados) - productos_ok)
                    
                    with st.expander("📥 Generar Cotización", expanded=True):
                        cliente = st.text_input("Cliente", "CLIENTE NUEVO")
                        items_ok = [r for r in resultados if r['Estado'] == '✅ OK']
                        if items_ok and st.button("📥 Descargar Excel"):
                            excel = generar_excel(items_ok, cliente, "-")
                            st.download_button("💾 Guardar", excel, f"cotizacion_{cliente}.xlsx")
                            st.session_state.cotizaciones = st.session_state.get("cotizaciones", 0) + 1
                            st.session_state.total_prods = len(items_ok)
                            st.balloons()
    else:
        st.info("📂 Sube tus catálogos en la barra lateral izquierda")
        st.markdown("""
        ### 💡 Tips:
        - Puedes subir varios archivos Excel
        - El sistema buscará en **TODAS las hojas** automáticamente
        - Si un producto está en varias hojas, se mostrará la primera coincidencia
        - También puedes subir el reporte de stock (también busca en todas sus hojas)
        """)

# ============================================
# TAB 2: BÚSQUEDA INTELIGENTE
# ============================================
with tab_busqueda:
    st.markdown("### 🔍 Búsqueda en TODAS las hojas de TODOS los catálogos")
    
    if st.session_state.get('catalogos'):
        tipo_busqueda = st.radio("Buscar por:", ["📝 Descripción", "🔢 SKU"], horizontal=True)
        termino = st.text_input("Escribe tu búsqueda:", placeholder="Ej: LAPTOP, USB, HDMI, ABC123...")
        
        if termino:
            tipo = 'desc' if tipo_busqueda == "📝 Descripción" else 'sku'
            with st.spinner(f"Buscando '{termino}' en todas las hojas..."):
                resultados = buscar_en_todos_catalogos(st.session_state.catalogos, termino, tipo)
            
            if resultados:
                st.success(f"✅ Encontrados {len(resultados)} productos en {len(set(r['archivo'] for r in resultados))} archivos")
                
                # Agrupar por archivo
                for archivo in set(r['archivo'] for r in resultados):
                    st.markdown(f"#### 📗 {archivo}")
                    resultados_archivo = [r for r in resultados if r['archivo'] == archivo]
                    
                    for res in resultados_archivo:
                        col1, col2, col3 = st.columns([2, 5, 1])
                        with col1:
                            st.markdown(f"**📦 {res['sku']}**")
                            st.caption(f"Hoja: {res['hoja']}")
                        with col2:
                            st.markdown(res['descripcion'])
                        with col3:
                            if st.button("➕ Agregar", key=f"add_{res['sku']}_{res['hoja']}"):
                                if 'temp_seleccion' not in st.session_state:
                                    st.session_state.temp_seleccion = {}
                                st.session_state.temp_seleccion[res['sku']] = st.session_state.temp_seleccion.get(res['sku'], 0) + 1
                                st.success(f"Agregado: {res['sku']}")
                        st.divider()
                
                # Transferir seleccionados
                if st.session_state.get('temp_seleccion'):
                    if st.button("📋 Transferir seleccionados a Pedidos"):
                        st.session_state.skus_transferidos = st.session_state.temp_seleccion
                        st.session_state.temp_seleccion = {}
                        st.success("Transferido! Ve a Gestión de Pedidos")
            else:
                st.warning(f"No se encontraron productos con '{termino}'")
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
            with st.spinner("Procesando imagen..."):
                datos = extraer_skus_gemini(img)
                if datos:
                    st.success(f"✅ {len(datos)} SKUs detectados")
                    df_detectados = pd.DataFrame(datos)
                    st.dataframe(df_detectados, use_container_width=True)
                    
                    if st.button("📋 Transferir todos a Pedidos"):
                        skus_dict = {item['sku']: item['cantidad'] for item in datos}
                        st.session_state.skus_transferidos = skus_dict
                        st.success("Transferido!")
                else:
                    st.warning("No se detectaron SKUs en la imagen")
    
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
    st.markdown("### 📚 Resumen de Catálogos")
    if st.session_state.get('catalogos'):
        for cat in st.session_state.catalogos:
            st.markdown(f"""
            **📗 {cat['nombre']}**
            - Hojas: {', '.join(cat['hojas'])}
            - Productos: {cat['total_filas']:,}
            """)
    else:
        st.info("Aún no hay catálogos cargados")

st.markdown("---")
st.markdown("*💚 QTC Smart Sales - Búsqueda Automática en TODAS las hojas*")
