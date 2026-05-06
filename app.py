import streamlit as st
import pandas as pd
import re, io, os
from datetime import datetime
from PIL import Image
import numpy as np
from io import BytesIO
import base64

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

# --- ESTILO PROFESIONAL MODERNO ---
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
        --light: #ecf0f1;
        --dark: #2c3e50;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--secondary);
        font-weight: 600 !important;
    }
    
    /* Botones principales */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%);
    }
    
    /* Botón de descarga */
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--success) 0%, #219a52 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Sidebar mejorado */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a252f 0%, #2C3E50 100%);
        padding: 2rem 1rem;
    }
    
    [data-testid="stSidebar"] * {
        color: white;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    /* Cards */
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
        font-size: 2rem;
        font-weight: bold;
        color: var(--primary);
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: var(--dark);
        margin-top: 0.5rem;
    }
    
    /* Alertas personalizadas */
    .custom-alert-success {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid var(--success);
        margin: 1rem 0;
    }
    
    .custom-alert-warning {
        background: #fff3cd;
        color: #856404;
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
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    /* Dataframe */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: var(--primary);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
        font-weight: 600;
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
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 📊 Panel de Control")
    
    # Métricas en sidebar
    if "stats" in st.session_state:
        st.metric("Productos Procesados", st.session_state.get("total_prods", 0))
        st.metric("Cotizaciones Generadas", st.session_state.get("cotizaciones", 0))

# --- SISTEMA DE LOGIN MEJORADO ---
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
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔐 Ingresar", use_container_width=True):
                if user == "admin" and pw == "qtc2026":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
        with col_btn2:
            st.markdown("[¿Olvidó su contraseña?](#)")
        
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

# --- FUNCIONES DE RECONOCIMIENTO DE SKU POR IMAGEN ---
def initialize_ocr():
    """Inicializa el sistema OCR para reconocimiento de texto en imágenes"""
    try:
        import easyocr
        return easyocr.Reader(['es', 'en'])
    except ImportError:
        st.warning("⚠️ EasyOCR no está instalado. Ejecuta: pip install easyocr")
        return None

def preprocess_image(image):
    """Preprocesa la imagen para mejorar OCR"""
    from PIL import ImageEnhance, ImageFilter
    
    # Convertir a escala de grises
    gray = image.convert('L')
    
    # Aumentar contraste
    enhancer = ImageEnhance.Contrast(gray)
    enhanced = enhancer.enhance(2)
    
    # Aplicar sharpen
    sharpened = enhanced.filter(ImageFilter.SHARPEN)
    
    return sharpened

def extract_skus_from_image(image, reader):
    """Extrae SKUs de una imagen usando OCR"""
    try:
        # Preprocesar imagen
        processed_image = preprocess_image(image)
        
        # Guardar imagen temporal
        temp_path = "temp_ocr.jpg"
        processed_image.save(temp_path, quality=95)
        
        # Realizar OCR
        result = reader.readtext(temp_path, detail=0, paragraph=False)
        
        # Eliminar archivo temporal
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # Procesar resultados
        skus = []
        for text in result:
            # Limpiar y normalizar texto
            cleaned = re.sub(r'[^A-Z0-9]', '', text.upper().strip())
            if len(cleaned) >= 4 and not cleaned.isdigit():  # SKU típicamente alfanumérico
                skus.append(cleaned)
        
        return list(set(skus))  # Eliminar duplicados
    
    except Exception as e:
        st.error(f"Error en OCR: {str(e)}")
        return []

def extract_barcodes_from_image(image):
    """Extrae códigos de barras de la imagen"""
    try:
        from pyzbar import pyzbar
        
        # Convertir a RGB si es necesario
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Detectar códigos de barras
        barcodes = pyzbar.decode(image)
        
        skus = []
        for barcode in barcodes:
            code = barcode.data.decode('utf-8')
            # Limpiar código
            cleaned = re.sub(r'[^A-Z0-9]', '', code.upper())
            if len(cleaned) >= 4:
                skus.append(cleaned)
        
        return list(set(skus))
    
    except ImportError:
        st.info("📦 Para escanear códigos de barras, instala: pip install pyzbar pillow")
        return []
    except Exception as e:
        st.error(f"Error leyendo código de barras: {str(e)}")
        return []

# --- INTERFAZ PRINCIPAL ---
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0;">💼 QTC Smart Sales Pro</h1>
    <p style="color: white; margin-top: 0.5rem; opacity: 0.9;">Sistema Inteligente de Ventas con IA</p>
</div>
""", unsafe_allow_html=True)

# Tabs principales
tab1, tab2, tab3 = st.tabs(["📦 Gestión de Pedidos", "🤖 SKU por Imagen", "📊 Dashboard"])

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
        
        # Selector de precio mejorado
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
        
        if f_ped:
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
                                pedido_dict[sku_p] = cant_p
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
                            pedido_dict[sku_l] = cant_l
                        except:
                            pedido_dict[sku_l] = 1
                    elif line:
                        pedido_dict[line.strip().upper()] = 1
        
        if st.button("🚀 PROCESAR DISPONIBILIDAD", use_container_width=True) and pedido_dict:
            with st.spinner("Procesando..."):
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
                        <div class="metric-label">Productos Consultados</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value" style="color: #27ae60;">{stock_ok}</div>
                        <div class="metric-label">Con Stock Suficiente</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value" style="color: #e74c3c;">{stock_fail}</div>
                        <div class="metric-label">Sin Stock Suficiente</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.subheader("📊 Resultados de Cruce")
                
                # Dataframe con estilo
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
                        total_cotizacion = items_ok['PEDIDO'].astype(float) * items_ok['P_UNIT'].astype(float)
                        st.markdown(f"""
                        <div class="custom-alert-success">
                            <strong>💵 Total de Cotización:</strong> S/. {total_cotizacion.sum():,.2f}<br>
                            <small>Productos disponibles: {len(items_ok)}</small>
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
        <h2 style="color: white; margin: 0;">🤖 Reconocimiento Inteligente de SKU</h2>
        <p style="color: white; margin-top: 0.5rem;">Carga una imagen de productos y la IA detectará automáticamente los códigos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar OCR
    if 'ocr_reader' not in st.session_state:
        with st.spinner("🔄 Inicializando sistema de reconocimiento..."):
            st.session_state.ocr_reader = initialize_ocr()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_image = st.file_uploader(
            "📸 Cargar imagen del producto/etiqueta",
            type=['jpg', 'jpeg', 'png', 'bmp', 'webp'],
            help="Formatos soportados: JPG, PNG, BMP, WEBP"
        )
        
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, caption="Imagen cargada", use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Métodos de Reconocimiento")
        
        metodo = st.radio(
            "Selecciona el método:",
            ["🔍 OCR (Texto)", "📊 Código de Barras", "🤖 Ambos"],
            help="OCR reconoce texto impreso, Código de Barras escanea códigos"
        )
        
        if st.button("🔎 Analizar Imagen", use_container_width=True) and uploaded_image:
            with st.spinner("Procesando imagen con IA..."):
                skus_detectados = set()
                
                # Método OCR
                if metodo in ["🔍 OCR (Texto)", "🤖 Ambos"] and st.session_state.ocr_reader:
                    skus_ocr = extract_skus_from_image(image, st.session_state.ocr_reader)
                    skus_detectados.update(skus_ocr)
                    st.info(f"📝 OCR detectó {len(skus_ocr)} SKUs")
                
                # Método Código de Barras
                if metodo in ["📊 Código de Barras", "🤖 Ambos"]:
                    skus_barcode = extract_barcodes_from_image(image)
                    skus_detectados.update(skus_barcode)
                    st.info(f"📊 Código de barras detectó {len(skus_barcode)} SKUs")
                
                if skus_detectados:
                    st.success(f"✅ Se detectaron {len(skus_detectados)} SKUs únicos")
                    
                    # Mostrar SKUs detectados
                    st.markdown("### 🏷️ SKUs Detectados")
                    
                    # Opción para agregar cantidades
                    st.markdown("#### 📦 Asignar cantidades")
                    skus_con_cantidad = {}
                    
                    for sku in skus_detectados:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.code(sku)
                        with col2:
                            cantidad = st.number_input(f"Cantidad", min_value=1, value=1, key=f"qty_{sku}", label_visibility="collapsed")
                            skus_con_cantidad[sku] = cantidad
                    
                    # Botón para usar estos SKUs
                    if st.button("📋 Usar estos SKUs en el pedido", use_container_width=True):
                        # Transferir a la pestaña de pedidos
                        pedido_text = "\n".join([f"{sku}:{cant}" for sku, cant in skus_con_cantidad.items()])
                        st.session_state.pedido_texto = pedido_text
                        st.success("✅ SKUs transferidos a la pestaña de Pedidos")
                        st.info("Cambia a la pestaña 📦 Gestión de Pedidos para continuar")
                        
                        # Guardar en session state para usar en tab1
                        if 'pedido_dict_temp' not in st.session_state:
                            st.session_state.pedido_dict_temp = skus_con_cantidad
                else:
                    st.warning("⚠️ No se detectaron SKUs en la imagen. Intenta con una imagen más clara o utiliza otro método.")

with tab3:
    st.markdown("## 📊 Dashboard de Ventas")
    
    # Aquí puedes agregar gráficos y estadísticas
    if 'cotizaciones' in st.session_state:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Cotizaciones Generadas", st.session_state.get("cotizaciones", 0), delta="+2")
        with col2:
            st.metric("Productos Procesados", st.session_state.get("total_prods", 0))
        with col3:
            st.metric("SKU Reconocidos", st.session_state.get("skus_detectados", 0))
        
        # Gráfico de ejemplo
        st.markdown("### 📈 Actividad Reciente")
        chart_data = pd.DataFrame({
            'Cotizaciones': [st.session_state.get("cotizaciones", 0)],
            'Productos': [st.session_state.get("total_prods", 0)]
        })
        st.bar_chart(chart_data)
    else:
        st.info("ℹ️ Las estadísticas se actualizarán a medida que uses el sistema")
    
    st.markdown("---")
    st.markdown("### 🎯 Tips de Uso")
    st.markdown("""
    - ✅ **OCR**: Mejor para etiquetas impresas con buena iluminación
    - ✅ **Código de Barras**: Ideal para productos con código de barras estándar
    - ✅ **Pega manual**: Puedes copiar SKUs desde cualquier fuente
    - ✅ **Excel**: Soporta múltiples formatos de archivo
    """)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>💼 QTC Smart Sales Pro © 2025 - Sistema Corporativo de Ventas con IA</p>
    <p style="font-size: 0.8rem;">Versión 2.0 - Reconocimiento Inteligente de SKU</p>
</div>
""", unsafe_allow_html=True)

