import streamlit as st
import pandas as pd
import re, io, os
from datetime import datetime
from PIL import Image
import numpy as np

# --- CONFIGURACIÓN DE LA PÁGINA ---
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
        layout="wide"
    )

# --- ESTILO PROFESIONAL MODERNO CON TEXTOS LEGIBLES ---
st.markdown("""
    <style>
    /* Variables de color corporativo */
    :root {
        --primary: #F79646;
        --primary-dark: #e67e22;
        --secondary: #2C3E50;
        --success: #27ae60;
        --danger: #e74c3c;
        --warning: #f39c12;
        --info: #3498db;
        --light: #f8f9fa;
        --dark: #2c3e50;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
        background: #f5f7fa;
    }
    
    /* Headers - texto oscuro para contraste */
    h1, h2, h3, h4, h5, h6 {
        color: #1a252f !important;
        font-weight: 600 !important;
    }
    
    /* Texto general */
    p, span, div, label, .stMarkdown {
        color: #2c3e50 !important;
    }
    
    /* Sidebar mejorado con texto blanco */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a252f 0%, #2C3E50 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    /* Cards mejoradas */
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #F79646 !important;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666 !important;
        margin-top: 0.5rem;
    }
    
    /* Alertas personalizadas */
    .custom-alert-success {
        background: #d4edda;
        color: #155724 !important;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid var(--success);
        margin: 1rem 0;
    }
    
    .custom-alert-warning {
        background: #fff3cd;
        color: #856404 !important;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid var(--warning);
        margin: 1rem 0;
    }
    
    /* Tabs personalizados */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: white;
        padding: 0.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        color: #2c3e50 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #F79646 0%, #e67e22 100%);
        color: white !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: #F79646;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
        font-weight: 600;
        color: #2c3e50 !important;
    }
    
    /* Botones */
    .stButton > button {
        background: linear-gradient(135deg, #F79646 0%, #e67e22 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    /* Input labels */
    .stTextInput label, .stNumberInput label, .stSelectbox label {
        color: #2c3e50 !important;
        font-weight: 500 !important;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR CON LOGO ---
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h2 style="color: #F79646;">💼 QTC Pro</h2>
            <p style="color: white !important;">Sistema Inteligente de Ventas</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 📊 Panel de Control")
    
    # Métricas en sidebar
    if "stats" in st.session_state:
        st.metric("📦 Productos", st.session_state.get("total_prods", 0))
        st.metric("📄 Cotizaciones", st.session_state.get("cotizaciones", 0))
        st.metric("🎯 SKU Detectados", st.session_state.get("skus_detectados", 0))

# --- SISTEMA DE LOGIN ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1);">
            <div style="text-align: center;">
                <h1 style="color: #F79646;">💼 QTC Smart Sales</h1>
                <p style="color: #666;">Sistema Corporativo de Ventas</p>
            </div>
        """, unsafe_allow_html=True)
        
        user = st.text_input("👤 Usuario", placeholder="Ingrese su usuario")
        pw = st.text_input("🔒 Contraseña", type="password", placeholder="Ingrese su contraseña")
        
        if st.button("🔐 Ingresar", use_container_width=True):
            if user == "admin" and pw == "qtc2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")
        
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- FUNCIONES DE PROCESAMIENTO ---
def corregir_numero(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "0", "0.0"]: 
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

def generar_excel_web(items, cliente, ruc):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    pd.DataFrame(items).to_excel(writer, sheet_name='Cotizacion', index=False, startrow=5)
    workbook, ws = writer.book, writer.sheets['Cotizacion']
    fmt_h = workbook.add_format({'bg_color': '#F79646', 'bold': True, 'border': 1, 'align': 'center', 'font_color': 'white'})
    fmt_m = workbook.add_format({'num_format': '"S/." #,##0.00', 'border': 1})
    fmt_b = workbook.add_format({'border': 1})
    
    ws.set_column('A:A', 20)
    ws.set_column('B:B', 75)
    ws.set_column('C:E', 15)
    
    ws.write('A1', 'FECHA:', workbook.add_format({'bold': True, 'font_size': 11}))
    ws.write('B1', datetime.now().strftime("%d/%m/%Y"))
    ws.write('A2', 'CLIENTE:', workbook.add_format({'bold': True, 'font_size': 11}))
    ws.write('B2', cliente.upper())
    ws.write('A3', 'RUC:', workbook.add_format({'bold': True, 'font_size': 11}))
    ws.write('B3', ruc)
    
    ws.merge_range('F1:H1', 'DATOS BANCARIOS', fmt_h)
    ws.write('F2', 'BBVA SOLES:', workbook.add_format({'font_color': 'red', 'bold': True, 'border': 1}))
    ws.write('G2', '0011-0616-0100012617', fmt_b)
    
    for i, col in enumerate(['Código SAP', 'Descripción', 'Cantidad', 'Precio Unit.', 'Total']):
        ws.write(5, i, col, fmt_h)
    
    for r, item in enumerate(items):
        ws.write_row(r + 6, 0, [item['sku'], item['desc'], item['cant'], item['p_u'], item['total']], fmt_b)
        ws.write(r + 6, 3, item['p_u'], fmt_m)
        ws.write(r + 6, 4, item['total'], fmt_m)
    
    total_row = len(items) + 6
    ws.write(total_row, 3, 'TOTAL S/.', fmt_h)
    ws.write(total_row, 4, sum(i['total'] for i in items), fmt_m)
    writer.close()
    return output.getvalue()

# --- FUNCIONES AVANZADAS PARA EXTRAER SKU DE IMÁGENES ---
def extract_text_from_image(image):
    """Extrae texto de imagen usando pytesseract (requiere instalación)"""
    try:
        import pytesseract
        import cv2
        
        # Convertir PIL a array numpy
        img_array = np.array(image)
        
        # Preprocesamiento para mejorar OCR
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Aplicar threshold adaptativo
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # Aumentar resolución
        h, w = thresh.shape
        thresh = cv2.resize(thresh, (w*2, h*2), interpolation=cv2.INTER_CUBIC)
        
        # OCR en español
        custom_config = r'--oem 3 --psm 6 -l spa+eng'
        text = pytesseract.image_to_string(thresh, config=custom_config)
        
        return text
    
    except ImportError:
        st.warning("⚠️ Tesseract no instalado. Usando modo básico...")
        return ""
    except Exception as e:
        st.error(f"Error en OCR: {str(e)}")
        return ""

def extract_skus_from_catalog_image(image):
    """Extrae SKU y cantidades de imágenes de catálogo"""
    try:
        # Extraer todo el texto de la imagen
        text = extract_text_from_image(image)
        
        if not text:
            return []
        
        # Patrones comunes de SKU (alfanumérico de 4-15 caracteres)
        sku_pattern = r'\b[A-Z0-9]{4,15}\b'
        
        # Patrón de cantidades
        qty_pattern = r'\b\d+\b'
        
        # Buscar SKUs en el texto
        skus_found = re.findall(sku_pattern, text)
        
        # Buscar cantidades cercanas a SKUs
        results = []
        lines = text.split('\n')
        
        for line in lines:
            # Buscar SKU en la línea
            skus_in_line = re.findall(sku_pattern, line)
            
            if skus_in_line:
                # Buscar números que podrían ser cantidades
                quantities = re.findall(qty_pattern, line)
                
                for sku in skus_in_line:
                    # Si hay cantidad en la misma línea, usarla
                    if quantities:
                        try:
                            qty = int(quantities[0])
                            results.append({'sku': sku, 'cantidad': qty})
                        except:
                            results.append({'sku': sku, 'cantidad': 1})
                    else:
                        results.append({'sku': sku, 'cantidad': 1})
        
        # Eliminar duplicados sumando cantidades
        unique_results = {}
        for item in results:
            if item['sku'] in unique_results:
                unique_results[item['sku']] += item['cantidad']
            else:
                unique_results[item['sku']] = item['cantidad']
        
        return [{'sku': k, 'cantidad': v} for k, v in unique_results.items()]
    
    except Exception as e:
        st.error(f"Error extrayendo SKU: {str(e)}")
        return []

def extract_table_from_image(image):
    """Intenta extraer tablas de imágenes (catalogo con columnas)"""
    try:
        import cv2
        import pandas as pd
        
        # Convertir a array numpy
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Detectar bordes para identificar tabla
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Detectar líneas horizontales y verticales
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        
        horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
        
        # Si detectamos estructura de tabla, usar OCR más agresivo
        if np.sum(horizontal_lines) > 1000 and np.sum(vertical_lines) > 1000:
            st.info("📊 Se detectó estructura de tabla en la imagen")
            text = extract_text_from_image(image)
            
            # Intentar parsear como tabla
            lines = text.split('\n')
            data = []
            
            for line in lines:
                # Separar por espacios o tabs
                parts = re.split(r'\s{2,}|\t', line.strip())
                if len(parts) >= 2:
                    # Buscar SKU y cantidad
                    for part in parts:
                        sku_match = re.search(r'\b[A-Z0-9]{4,}\b', part)
                        qty_match = re.search(r'\b\d+\b', part)
                        
                        if sku_match:
                            sku = sku_match.group()
                            qty = int(qty_match.group()) if qty_match else 1
                            data.append({'sku': sku, 'cantidad': qty})
            
            return data
        
        return []
    
    except Exception as e:
        return []

# --- INTERFAZ PRINCIPAL ---
st.markdown("""
<div style="background: linear-gradient(135deg, #F79646 0%, #e67e22 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0;">💼 QTC Smart Sales Pro</h1>
    <p style="color: white; margin-top: 0.5rem; opacity: 0.95;">Sistema Inteligente de Ventas con Reconocimiento de Imágenes</p>
</div>
""", unsafe_allow_html=True)

# Tabs principales
tab1, tab2, tab3 = st.tabs(["📦 Gestión de Pedidos", "🤖 Captura Inteligente de SKU", "📊 Dashboard"])

with tab1:
    st.sidebar.header("📂 Configuración de Archivos")
    
    f_p = st.sidebar.file_uploader("1. Catálogo de Precios", type=['xlsx'])
    f_s = st.sidebar.file_uploader("2. Reporte de Stock", type=['xlsx'])
    f_ped = st.sidebar.file_uploader("3. Excel de Pedido del Cliente", type=['xlsx'])
    
    if f_p and f_s:
        with st.spinner("Cargando datos..."):
            df_p_raw = pd.read_excel(f_p)
            xls_s = pd.ExcelFile(f_s)
            h_s = st.sidebar.selectbox("Selecciona hoja de Stock:", xls_s.sheet_names)
            df_s_raw = pd.read_excel(f_s, sheet_name=h_s)
        
        def limpiar_cabeceras(df):
            for i in range(min(15, len(df))):
                fila = [str(x).upper() for x in df.iloc[i].values]
                if any(h in item for h in ['SKU', 'SAP', 'ARTICULO', 'NUMERO', 'COD SAP'] for item in fila):
                    df.columns = [str(c).strip() for c in df.iloc[i]]
                    return df.iloc[i+1:].reset_index(drop=True).fillna(0)
            return df.fillna(0)
        
        df_p = limpiar_cabeceras(df_p_raw)
        df_s = limpiar_cabeceras(df_s_raw)
        
        # Selector de precio
        palabras_clave_precio = ['MAYOR', 'CAJA', 'VIP', 'IR', 'BOX', 'SUGERIDO', 'PRECIO', 'P.', 'UNIT']
        precios_opc = [c for c in df_p.columns if any(p in str(c).upper() for p in palabras_clave_precio)]
        
        if not precios_opc: 
            precios_opc = df_p.columns.tolist()
        
        col1, col2 = st.columns([2, 1])
        with col1:
            col_p_sel = st.selectbox("🎯 Selecciona el Precio a aplicar:", options=precios_opc)
        with col2:
            st.markdown("#### ⚙️")
            st.caption("Precios disponibles según catálogo")
        
        pedido_dict = {}
        
        # Verificar si hay SKUs transferidos desde tab2
        if 'skus_transferidos' in st.session_state and st.session_state.skus_transferidos:
            pedido_dict = st.session_state.skus_transferidos
            st.success(f"✅ {len(pedido_dict)} SKUs cargados desde reconocimiento de imagen")
            # Limpiar para no reutilizar
            del st.session_state.skus_transferidos
        
        elif f_ped:
            st.info("🔍 Analizando pedido en Excel...")
            df_ped_raw = pd.read_excel(f_ped)
            df_ped = limpiar_cabeceras(df_ped_raw)
            c_sku_ped = next((c for c in df_ped.columns if any(x in str(c).upper() for x in ['SKU', 'COD SAP', 'CODIGO', 'SAP', 'NO'])), df_ped.columns[0])
            c_cant_ped = next((c for c in df_ped.columns if any(x in str(c).upper() for x in ['PEDIDO', 'CANTIDAD', 'CANT', 'SOLICITADO'])), None)
            
            if c_cant_ped:
                for _, fila_p in df_ped.iterrows():
                    val_cant = fila_p[c_cant_ped]
                    if pd.notna(val_cant) and (isinstance(val_cant, (int, float)) or str(val_cant).replace('.','').isdigit()):
                        cant_p = int(float(val_cant))
                        if cant_p > 0:
                            sku_p = str(fila_p[c_sku_ped]).strip().upper()
                            if sku_p and sku_p != '0' and sku_p != '0.0' and sku_p != 'NAN':
                                pedido_dict[sku_p] = pedido_dict.get(sku_p, 0) + cant_p
                st.success(f"✅ Se detectaron {len(pedido_dict)} productos solicitados.")
            else:
                st.error("No se encontró la columna de cantidad en el pedido.")
        
        else:
            col1, col2 = st.columns([3, 1])
            with col1:
                txt_area = st.text_area("⌨️ O pega aquí SKU:CANTIDAD (un SKU por línea)", height=150, 
                                        placeholder="Ejemplo:\nABC123:5\nXYZ789:2\nPROD456:10")
            with col2:
                st.markdown("#### 📝")
                st.caption("Formato: SKU:CANTIDAD\nSeparado por líneas")
            
            if txt_area:
                for line in txt_area.split('\n'):
                    line = line.strip()
                    if ':' in line:
                        parts = line.split(':')
                        sku_l = parts[0].strip().upper()
                        try:
                            cant_l = int(parts[1].strip())
                            pedido_dict[sku_l] = pedido_dict.get(sku_l, 0) + cant_l
                        except:
                            pedido_dict[sku_l] = pedido_dict.get(sku_l, 0) + 1
                    elif line:
                        pedido_dict[line.strip().upper()] = pedido_dict.get(line.strip().upper(), 0) + 1
        
        if st.button("🚀 PROCESAR DISPONIBILIDAD", use_container_width=True) and pedido_dict:
            with st.spinner("Procesando información..."):
                c_sku_p = next((c for c in df_p.columns if any(x in str(c).upper() for x in ['SKU', 'SAP', 'COD SAP'])), df_p.columns[0])
                c_desc_p = next((c for c in df_p.columns if any(x in str(c).upper() for x in ['DESCRIPCION', 'GOODS', 'NOMBRE'])), df_p.columns[1] if len(df_p.columns) > 1 else df_p.columns[0])
                c_sku_s = next((c for c in df_s.columns if any(x in str(c).upper() for x in ['NUMERO', 'SKU', 'ARTICULO'])), df_s.columns[0])
                c_dsp = next((c for c in df_s.columns if 'DISPONIBLE' in str(c).upper()), df_s.columns[-1])
                
                resultados = []
                progress_bar = st.progress(0)
                
                for idx, (cod_f, cant_f) in enumerate(pedido_dict.items()):
                    progress_bar.progress((idx + 1) / len(pedido_dict))
                    mask = df_p[c_sku_p].astype(str).str.contains(re.escape(cod_f), case=False, na=False)
                    variantes = df_p[mask]
                    
                    for _, fila in variantes.iterrows():
                        info = fila.to_dict()
                        info['PEDIDO'] = cant_f
                        sku_real = str(info[c_sku_p]).strip()
                        m_stk = df_s[df_s[c_sku_s].astype(str).str.strip() == sku_real]
                        info['Disp'] = int(corregir_numero(m_stk[c_dsp].iloc[0] if not m_stk.empty else 0))
                        info['P_UNIT'] = corregir_numero(info[col_p_sel])
                        info['ALERTA'] = "✅ OK" if info['Disp'] >= cant_f else "⚠️ SIN STOCK"
                        resultados.append(info)
                
                progress_bar.empty()
            
            if resultados:
                df_res = pd.DataFrame(resultados).drop_duplicates()
                
                # Mostrar resumen
                total_prods = len(df_res)
                stock_ok = len(df_res[df_res.ALERTA == "✅ OK"])
                stock_fail = len(df_res[df_res.ALERTA == "⚠️ SIN STOCK"])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{total_prods}</div>
                        <div class="metric-label">📦 Productos Consultados</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value" style="color: #27ae60;">{stock_ok}</div>
                        <div class="metric-label">✅ Con Stock Suficiente</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value" style="color: #e74c3c;">{stock_fail}</div>
                        <div class="metric-label">⚠️ Sin Stock Suficiente</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.subheader("📊 Resultados de Cruce")
                
                def color_alerta(row):
                    return ['background-color: #ff6b6b; color: white; font-weight: bold' if row.ALERTA == "⚠️ SIN STOCK" 
                            else 'background-color: #51cf66; color: white' if row.ALERTA == "✅ OK" 
                            else '' for _ in row]
                
                st.dataframe(
                    df_res[[c_sku_p, c_desc_p, 'P_UNIT', 'PEDIDO', 'Disp', 'ALERTA']]
                    .style
                    .apply(color_alerta, axis=1)
                    .format({'P_UNIT': 'S/. {:.2f}'}),
                    use_container_width=True
                )
                
                with st.expander("📥 Generar Cotización Final", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        n_cli = st.text_input("🏢 Nombre del Cliente", value="CLIENTE NUEVO")
                    with col2:
                        r_cli = st.text_input("📋 RUC/DNI", value="-")
                    
                    items_ok = df_res[df_res.ALERTA == "✅ OK"]
                    
                    if not items_ok.empty:
                        total_cotizacion = (items_ok['PEDIDO'].astype(float) * items_ok['P_UNIT'].astype(float)).sum()
                        st.markdown(f"""
                        <div class="custom-alert-success">
                            <strong>💰 Total de Cotización:</strong> S/. {total_cotizacion:,.2f}<br>
                            <small>✅ Productos disponibles: {len(items_ok)}</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        final_list = [{
                            'sku': r[c_sku_p], 
                            'desc': r[c_desc_p], 
                            'cant': r['PEDIDO'], 
                            'p_u': r['P_UNIT'], 
                            'total': r['PEDIDO'] * r['P_UNIT']
                        } for _, r in items_ok.iterrows()]
                        
                        excel_data = generar_excel_web(final_list, n_cli, r_cli)
                        
                        st.download_button(
                            label="📥 Descargar Cotización en Excel",
                            data=excel_data,
                            file_name=f"Cotizacion_{n_cli}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                        
                        # Actualizar estadísticas
                        st.session_state.cotizaciones = st.session_state.get("cotizaciones", 0) + 1
                        st.session_state.total_prods = total_prods
                        
                        st.balloons()
                    else:
                        st.warning("⚠️ No hay productos con stock suficiente para cotizar")

with tab2:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem;">
        <h2 style="color: white; margin: 0;">🤖 Captura Inteligente de SKU</h2>
        <p style="color: white; margin-top: 0.5rem;">Sube una imagen de catálogo y el sistema extraerá automáticamente los SKU y cantidades</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_image = st.file_uploader(
            "📸 Subir imagen del catálogo",
            type=['jpg', 'jpeg', 'png', 'bmp', 'webp'],
            help="Sube foto del catálogo, lista de productos o captura de pantalla"
        )
        
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, caption="📷 Imagen cargada", use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Configuración de Extracción")
        
        metodo = st.radio(
            "Método de reconocimiento:",
            ["🔍 SKU y Cantidades", "📊 Tabla estructurada", "🤖 Automático"],
            help="SKU y Cantidades: busca patrones de SKU con números cercanos\nTabla: para imágenes con formato de tabla\nAutomático: combina ambos métodos"
        )
        
        if st.button("🔎 Extraer SKU de la imagen", use_container_width=True) and uploaded_image:
            with st.spinner("🔄 Procesando imagen con IA..."):
                extracted_data = []
                
                if metodo in ["🔍 SKU y Cantidades", "🤖 Automático"]:
                    with st.spinner("🔍 Buscando SKU y cantidades..."):
                        skus_data = extract_skus_from_catalog_image(image)
                        extracted_data.extend(skus_data)
                        st.info(f"📝 Método SKU encontró {len(skus_data)} productos")
                
                if metodo in ["📊 Tabla estructurada", "🤖 Automático"]:
                    with st.spinner("📊 Analizando estructura de tabla..."):
                        table_data = extract_table_from_image(image)
                        extracted_data.extend(table_data)
                        st.info(f"📊 Método Tabla encontró {len(table_data)} productos")
                
                if extracted_data:
                    # Eliminar duplicados y sumar cantidades
                    unique_data = {}
                    for item in extracted_data:
                        if item['sku'] in unique_data:
                            unique_data[item['sku']] += item['cantidad']
                        else:
                            unique_data[item['sku']] = item['cantidad']
                    
                    # Convertir a lista para mostrar
                    final_data = [{'SKU': k, 'Cantidad': v} for k, v in unique_data.items()]
                    df_extracted = pd.DataFrame(final_data)
                    
                    st.success(f"✅ Se extrajeron {len(final_data)} SKUs únicos")
                    
                    # Mostrar resultados
                    st.markdown("### 📋 SKU Detectados")
                    st.dataframe(df_extracted, use_container_width=True)
                    
                    # Opción para editar cantidades
                    st.markdown("### ✏️ Ajustar cantidades (opcional)")
                    edited_data = []
                    for idx, row in df_extracted.iterrows():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.code(row['SKU'])
                        with col2:
                            new_qty = st.number_input(f"Cantidad", value=int(row['Cantidad']), min_value=0, key=f"edit_{row['SKU']}", label_visibility="collapsed")
                        with col3:
                            if st.button(f"🗑️ Eliminar", key=f"del_{row['SKU']}"):
                                new_qty = 0
                        
                        if new_qty > 0:
                            edited_data.append({'sku': row['SKU'], 'cantidad': new_qty})
                    
                    # Botón para usar estos SKUs
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📋 Transferir a Pedido", use_container_width=True):
                            # Guardar en session state para usar en tab1
                            skus_dict = {item['sku']: item['cantidad'] for item in edited_data}
                            st.session_state.skus_transferidos = skus_dict
                            st.session_state.skus_detectados = len(skus_dict)
                            st.success(f"✅ {len(skus_dict)} SKUs transferidos a la pestaña de Pedidos")
                            st.info("👉 Cambia a la pestaña '📦 Gestión de Pedidos' y haz clic en 'PROCESAR DISPONIBILIDAD'")
                            st.balloons()
                    
                    with col2:
                        if st.button("📥 Descargar CSV", use_container_width=True):
                            csv = df_extracted.to_csv(index=False)
                            st.download_button(
                                label="📥 Descargar",
                                data=csv,
                                file_name="skus_detectados.csv",
                                mime="text/csv"
                            )
                else:
                    st.warning("⚠️ No se detectaron SKUs en la imagen. Intenta:")
                    st.markdown("""
                    - 📸 Tomar una foto más clara y con buena iluminación
                    - 📄 Asegurar que los SKU y números sean visibles
                    - ✍️ Usar entrada manual en la pestaña de Pedidos
                    """)

with tab3:
    st.markdown("## 📊 Dashboard de Ventas")
    
    # Estadísticas en cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.get("cotizaciones", 0)}</div>
            <div class="metric-label">📄 Cotizaciones Generadas</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.get("total_prods", 0)}</div>
            <div class="metric-label">📦 Productos Procesados</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.get("skus_detectados", 0)}</div>
            <div class="metric-label">🎯 SKU Detectados por IA</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📈 Rendimiento del Sistema")
    
    # Datos de ejemplo para gráfico
    chart_data = pd.DataFrame({
        'Cotizaciones': [st.session_state.get("cotizaciones", 0)],
        'Productos': [st.session_state.get("total_prods", 0)],
        'SKU IA': [st.session_state.get("skus_detectados", 0)]
    })
    st.bar_chart(chart_data)
    
    st.markdown("---")
    st.markdown("### 🎯 Tips para mejor reconocimiento de SKU")
    st.markdown("""
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px;">
        <h4>📸 Para mejores resultados:</h4>
        <ul>
            <li>✅ Usa imágenes con buena iluminación y contraste</li>
            <li>✅ Enfoca bien los SKU y números</li>
            <li>✅ Evita reflejos y sombras en la imagen</li>
            <li>✅ Para tablas, asegura que las líneas sean visibles</li>
            <li>✅ Prefiere imágenes escaneadas sobre fotos con ángulo</li>
        </ul>
        <h4>💡 Alternativas:</h4>
        <ul>
            <li>📝 Si la imagen no es clara, usa entrada manual de SKU</li>
            <li>📊 Para muchos productos, usa archivo Excel directamente</li>
            <li>🔍 Revisa los SKU detectados y ajusta cantidades antes de transferir</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem;">
    <p style="color: #666;">💼 QTC Smart Sales Pro © 2025 - Sistema Corporativo de Ventas con IA</p>
    <p style="color: #999; font-size: 0.8rem;">Versión 2.0 - Captura Inteligente de SKU desde Imágenes</p>
</div>
""", unsafe_allow_html=True)
