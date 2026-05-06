import streamlit as st
import pandas as pd
import re, io, os
from datetime import datetime
from PIL import Image, ImageEnhance, ImageFilter
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

# --- ESTILOS CORREGIDOS (FONDOS CLAROS, TEXTOS OSCUROS) ---
st.markdown("""
    <style>
    /* Fondo general claro */
    .stApp {
        background-color: #f5f7fa;
    }
    
    /* Todo el texto principal en oscuro */
    .main .block-container {
        background-color: #f5f7fa;
        color: #1a252f !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        color: #1a252f !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a252f 0%, #2C3E50 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: white;
        border-radius: 10px;
        padding: 0.5rem;
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #1a252f !important;
        background-color: #e9ecef;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #F79646 0%, #e67e22 100%);
        color: white !important;
    }
    
    /* Botones */
    .stButton > button {
        background: linear-gradient(135deg, #F79646 0%, #e67e22 100%);
        color: white !important;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    /* Inputs */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background-color: white;
        color: #1a252f !important;
        border: 1px solid #ddd;
        border-radius: 8px;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background-color: white;
        color: #1a252f !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        background-color: white;
        border-radius: 10px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: white;
        color: #1a252f !important;
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Info, Success, Warning boxes */
    .stAlert {
        background-color: white;
        border-radius: 10px;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #F79646 !important;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666 !important;
    }
    
    /* Código */
    code {
        background-color: #f0f0f0;
        color: #d63384 !important;
        padding: 2px 5px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
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
    st.markdown("### 📊 Panel")
    
    if "stats" in st.session_state:
        st.metric("📦 Productos", st.session_state.get("total_prods", 0))
        st.metric("📄 Cotizaciones", st.session_state.get("cotizaciones", 0))

# --- LOGIN ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown("""
            <div style="background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
                <h1 style="text-align: center; color: #F79646;">💼 QTC Smart Sales</h1>
                <p style="text-align: center; color: #666;">Sistema Corporativo de Ventas</p>
            </div>
            """, unsafe_allow_html=True)
            
            user = st.text_input("👤 Usuario")
            pw = st.text_input("🔒 Contraseña", type="password")
            
            if st.button("🔐 Ingresar", use_container_width=True):
                if user == "admin" and pw == "qtc2026":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
    st.stop()

# --- FUNCIONES ---
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
    
    ws.write('A1', 'FECHA:', workbook.add_format({'bold': True}))
    ws.write('B1', datetime.now().strftime("%d/%m/%Y"))
    ws.write('A2', 'CLIENTE:', workbook.add_format({'bold': True}))
    ws.write('B2', cliente.upper())
    ws.write('A3', 'RUC:', workbook.add_format({'bold': True}))
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

# --- RECONOCIMIENTO DE SKU SIN TESSERACT ---
def preprocess_image_basic(image):
    """Preprocesamiento básico de imagen"""
    # Convertir a escala de grises
    gray = image.convert('L')
    
    # Aumentar contraste
    enhancer = ImageEnhance.Contrast(gray)
    enhanced = enhancer.enhance(2.0)
    
    # Aumentar nitidez
    sharpener = ImageEnhance.Sharpness(enhanced)
    sharp = sharpener.enhance(2.0)
    
    # Invertir colores para mejor detección de texto oscuro sobre fondo claro
    inverted = Image.eval(sharp, lambda x: 255 - x)
    
    return inverted

def extract_skus_from_image_simple(image):
    """Extrae SKU de imagen SIN TESSERACT usando detección de patrones"""
    try:
        # Preprocesar
        processed = preprocess_image_basic(image)
        
        # Redimensionar para mejor procesamiento
        processed = processed.resize((processed.width * 2, processed.height * 2), Image.Resampling.LANCZOS)
        
        # Convertir a array numpy para procesamiento
        img_array = np.array(processed)
        
        # Binarizar (convertir a blanco y negro)
        threshold = np.mean(img_array)
        binary = (img_array < threshold).astype(np.uint8) * 255
        
        # Intentar extraer texto por regiones
        height, width = binary.shape
        
        # Detectar regiones con texto
        text_regions = []
        row_projection = np.sum(binary == 0, axis=1)
        
        # Encontrar filas con contenido
        threshold_rows = np.percentile(row_projection, 95)
        text_rows = np.where(row_projection > threshold_rows)[0]
        
        if len(text_rows) > 0:
            # Agrupar filas cercanas
            groups = []
            current_group = [text_rows[0]]
            
            for i in range(1, len(text_rows)):
                if text_rows[i] - text_rows[i-1] < 10:
                    current_group.append(text_rows[i])
                else:
                    groups.append(current_group)
                    current_group = [text_rows[i]]
            groups.append(current_group)
            
            # Extraer texto de cada grupo
            potential_skus = []
            
            for group in groups:
                if len(group) > 3:  # Altura mínima para una línea de texto
                    y_start = group[0] - 5
                    y_end = group[-1] + 5
                    y_start = max(0, y_start)
                    y_end = min(height, y_end)
                    
                    # Extraer región
                    region = binary[y_start:y_end, :]
                    
                    # Proyección vertical para detectar caracteres
                    col_projection = np.sum(region == 0, axis=0)
                    threshold_cols = np.percentile(col_projection, 90)
                    text_cols = np.where(col_projection > threshold_cols)[0]
                    
                    if len(text_cols) > 0:
                        # Agrupar columnas en palabras
                        word_groups = []
                        current_word = [text_cols[0]]
                        
                        for j in range(1, len(text_cols)):
                            if text_cols[j] - text_cols[j-1] < 15:
                                current_word.append(text_cols[j])
                            else:
                                if len(current_word) > 5:  # Longitud mínima de palabra
                                    word_groups.append(current_word)
                                current_word = [text_cols[j]]
                        
                        if len(current_word) > 5:
                            word_groups.append(current_word)
                        
                        # Extraer cada palabra como posible SKU
                        for word in word_groups:
                            x_start = max(0, word[0] - 5)
                            x_end = min(width, word[-1] + 5)
                            
                            word_region = binary[y_start:y_end, x_start:x_end]
                            
                            # Intentar reconocer caracteres por similitud de formas
                            word_text = recognize_characters_simple(word_region)
                            
                            if word_text and len(word_text) >= 4:
                                potential_skus.append(word_text)
            
            # Filtrar y limpiar SKUs
            skus_found = []
            for sku in potential_skus:
                # Limpiar SKU
                cleaned = re.sub(r'[^A-Z0-9]', '', sku.upper())
                if len(cleaned) >= 4 and len(cleaned) <= 20:
                    skus_found.append(cleaned)
            
            # Eliminar duplicados
            skus_found = list(set(skus_found))
            
            return skus_found
        
        return []
    
    except Exception as e:
        st.error(f"Error en procesamiento: {str(e)}")
        return []

def recognize_characters_simple(region):
    """Reconoce caracteres básicos por patrones (simulación simple)"""
    # Esta es una versión simplificada
    # Para producción real, recomendaríamos usar una API externa
    return None

def extract_skus_with_gemini(image, api_key=None):
    """Usar Gemini API para reconocimiento (recomendado)"""
    if not api_key:
        return None
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro-vision')
        
        response = model.generate_content([
            "Extrae todos los códigos SKU y sus cantidades de esta imagen. "
            "Devuelve solo en formato JSON: [{'sku': 'CODIGO', 'cantidad': NUMERO}]",
            image
        ])
        
        # Parsear respuesta
        import json
        text = response.text
        # Buscar JSON en la respuesta
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data
        
        return []
    except:
        return None

# --- INTERFAZ PRINCIPAL ---
st.title("💼 QTC Smart Sales Pro")
st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["📦 Gestión de Pedidos", "🤖 SKU por Imagen", "📊 Dashboard"])

with tab1:
    st.sidebar.header("📂 Archivos")
    
    f_p = st.sidebar.file_uploader("1. Catálogo de Precios", type=['xlsx'])
    f_s = st.sidebar.file_uploader("2. Reporte de Stock", type=['xlsx'])
    f_ped = st.sidebar.file_uploader("3. Excel Pedido", type=['xlsx'])
    
    if f_p and f_s:
        with st.spinner("Cargando..."):
            df_p_raw = pd.read_excel(f_p)
            xls_s = pd.ExcelFile(f_s)
            h_s = st.sidebar.selectbox("Hoja Stock:", xls_s.sheet_names)
            df_s_raw = pd.read_excel(f_s, sheet_name=h_s)
        
        def limpiar_cabeceras(df):
            for i in range(min(15, len(df))):
                fila = [str(x).upper() for x in df.iloc[i].values]
                if any(h in item for h in ['SKU', 'SAP', 'ARTICULO', 'COD'] for item in fila):
                    df.columns = [str(c).strip() for c in df.iloc[i]]
                    return df.iloc[i+1:].reset_index(drop=True).fillna(0)
            return df.fillna(0)
        
        df_p = limpiar_cabeceras(df_p_raw)
        df_s = limpiar_cabeceras(df_s_raw)
        
        # Precio
        palabras_precio = ['MAYOR', 'CAJA', 'VIP', 'PRECIO', 'UNIT']
        precios_opc = [c for c in df_p.columns if any(p in str(c).upper() for p in palabras_precio)]
        if not precios_opc: 
            precios_opc = df_p.columns.tolist()
        
        col_p_sel = st.selectbox("🎯 Precio a aplicar:", precios_opc)
        
        pedido_dict = {}
        
        # SKUs transferidos
        if 'skus_transferidos' in st.session_state and st.session_state.skus_transferidos:
            pedido_dict = st.session_state.skus_transferidos
            st.success(f"✅ {len(pedido_dict)} SKUs cargados desde imagen")
            del st.session_state.skus_transferidos
        
        elif f_ped:
            df_ped_raw = pd.read_excel(f_ped)
            df_ped = limpiar_cabeceras(df_ped_raw)
            c_sku_ped = next((c for c in df_ped.columns if any(x in str(c).upper() for x in ['SKU', 'COD'])), df_ped.columns[0])
            c_cant_ped = next((c for c in df_ped.columns if any(x in str(c).upper() for x in ['CANT'])), None)
            
            if c_cant_ped:
                for _, row in df_ped.iterrows():
                    val_cant = row[c_cant_ped]
                    if pd.notna(val_cant) and str(val_cant).replace('.','').isdigit():
                        cant = int(float(val_cant))
                        if cant > 0:
                            sku = str(row[c_sku_ped]).strip().upper()
                            if sku and sku not in ['0', 'NAN']:
                                pedido_dict[sku] = pedido_dict.get(sku, 0) + cant
                st.success(f"✅ {len(pedido_dict)} productos detectados")
        
        else:
            txt_area = st.text_area("📝 SKU:CANTIDAD (uno por línea)", height=150)
            if txt_area:
                for line in txt_area.split('\n'):
                    line = line.strip()
                    if ':' in line:
                        sku, cant = line.split(':')
                        pedido_dict[sku.strip().upper()] = int(cant.strip())
                    elif line:
                        pedido_dict[line.strip().upper()] = 1
        
        if st.button("🚀 PROCESAR", use_container_width=True) and pedido_dict:
            with st.spinner("Procesando..."):
                c_sku_p = next((c for c in df_p.columns if any(x in str(c).upper() for x in ['SKU', 'SAP'])), df_p.columns[0])
                c_desc_p = next((c for c in df_p.columns if any(x in str(c).upper() for x in ['DESCRIPCION'])), df_p.columns[1] if len(df_p.columns) > 1 else df_p.columns[0])
                c_sku_s = next((c for c in df_s.columns if any(x in str(c).upper() for x in ['NUMERO', 'SKU'])), df_s.columns[0])
                c_dsp = next((c for c in df_s.columns if 'DISPONIBLE' in str(c).upper()), df_s.columns[-1])
                
                resultados = []
                for cod_f, cant_f in pedido_dict.items():
                    mask = df_p[c_sku_p].astype(str).str.contains(cod_f, case=False, na=False)
                    for _, row in df_p[mask].iterrows():
                        info = row.to_dict()
                        info['PEDIDO'] = cant_f
                        sku_real = str(info[c_sku_p]).strip()
                        m_stk = df_s[df_s[c_sku_s].astype(str).str.strip() == sku_real]
                        info['Disp'] = int(corregir_numero(m_stk[c_dsp].iloc[0] if not m_stk.empty else 0))
                        info['P_UNIT'] = corregir_numero(info[col_p_sel])
                        info['ALERTA'] = "✅ OK" if info['Disp'] >= cant_f else "⚠️ SIN STOCK"
                        resultados.append(info)
                
                if resultados:
                    df_res = pd.DataFrame(resultados).drop_duplicates()
                    
                    # Métricas
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Productos", len(df_res))
                    col2.metric("Con Stock", len(df_res[df_res.ALERTA == "✅ OK"]))
                    col3.metric("Sin Stock", len(df_res[df_res.ALERTA == "⚠️ SIN STOCK"]))
                    
                    st.dataframe(df_res[[c_sku_p, c_desc_p, 'P_UNIT', 'PEDIDO', 'Disp', 'ALERTA']])
                    
                    with st.expander("📥 Cotización"):
                        n_cli = st.text_input("Cliente", "CLIENTE NUEVO")
                        r_cli = st.text_input("RUC", "-")
                        items_ok = df_res[df_res.ALERTA == "✅ OK"]
                        
                        if not items_ok.empty:
                            final_list = [{
                                'sku': r[c_sku_p], 'desc': r[c_desc_p], 
                                'cant': r['PEDIDO'], 'p_u': r['P_UNIT'], 
                                'total': r['PEDIDO'] * r['P_UNIT']
                            } for _, r in items_ok.iterrows()]
                            
                            st.download_button("📥 Descargar Excel", 
                                data=generar_excel_web(final_list, n_cli, r_cli),
                                file_name=f"Coti_{n_cli}.xlsx")
                            st.session_state.cotizaciones = st.session_state.get("cotizaciones", 0) + 1
                            st.balloons()

with tab2:
    st.markdown("### 🤖 Captura de SKU desde Imagen")
    st.info("💡 **Alternativas disponibles:**\n\n1. **Google Gemini API** (recomendado, más preciso)\n2. **Entrada manual** (si la imagen no es clara)\n3. **Subir Excel** con los SKU")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_image = st.file_uploader("📸 Subir imagen", type=['jpg', 'jpeg', 'png'])
        
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, caption="Imagen cargada", use_container_width=True)
    
    with col2:
        st.markdown("#### 🔧 Método de reconocimiento")
        
        metodo = st.radio("Selecciona:", [
            "📝 Entrada Manual", 
            "🤖 Google Gemini API"
        ])
        
        if metodo == "🤖 Google Gemini API":
            api_key = st.text_input("API Key de Gemini", type="password", 
                                   help="Obtén tu API Key en https://makersuite.google.com/app/apikey")
        
        if st.button("🔍 Extraer SKU", use_container_width=True) and uploaded_image:
            extracted_data = []
            
            if metodo == "🤖 Google Gemini API" and api_key:
                with st.spinner("Usando Gemini AI..."):
                    try:
                        import google.generativeai as genai
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        
                        response = model.generate_content([
                            "Analiza esta imagen de catálogo. Extrae TODOS los códigos SKU y sus cantidades. "
                            "Responde SOLO con un array JSON en este formato: [{'sku': 'CODIGO', 'cantidad': NUMERO}]",
                            image
                        ])
                        
                        # Extraer JSON de la respuesta
                        json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                        if json_match:
                            import json
                            extracted_data = json.loads(json_match.group())
                            st.success(f"✅ Gemini detectó {len(extracted_data)} productos")
                    except Exception as e:
                        st.error(f"Error con Gemini: {str(e)}")
                        st.info("💡 Prueba con entrada manual o verifica tu API Key")
            
            if metodo == "📝 Entrada Manual" or not extracted_data:
                st.info("📝 Usando entrada manual - puedes escribir los SKU directamente")
                
                # Mostrar campos para entrada manual
                st.markdown("#### ✏️ Ingresa SKU manualmente")
                num_items = st.number_input("Número de productos", min_value=1, max_value=20, value=3)
                
                manual_data = []
                for i in range(int(num_items)):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        sku = st.text_input(f"SKU {i+1}", key=f"sku_{i}")
                    with col_b:
                        cant = st.number_input(f"Cantidad {i+1}", min_value=1, value=1, key=f"cant_{i}")
                    if sku:
                        manual_data.append({'sku': sku.upper(), 'cantidad': cant})
                
                if manual_data:
                    extracted_data = manual_data
            
            if extracted_data:
                df_skus = pd.DataFrame(extracted_data)
                st.success(f"✅ {len(df_skus)} SKUs extraídos")
                st.dataframe(df_skus, use_container_width=True)
                
                if st.button("📋 Transferir a Pedido", use_container_width=True):
                    skus_dict = {row['sku']: row['cantidad'] for _, row in df_skus.iterrows()}
                    st.session_state.skus_transferidos = skus_dict
                    st.success(f"✅ {len(skus_dict)} SKUs transferidos a la pestaña de Pedidos")
                    st.info("👉 Ve a la pestaña 'Gestión de Pedidos' y haz clic en PROCESAR")
            else:
                st.warning("⚠️ No se detectaron SKUs. Puedes:")
                st.markdown("""
                - 📝 Usar entrada manual
                - 📄 Subir un archivo Excel con los SKU
                - 🔄 Configurar Gemini API para mejor reconocimiento
                """)

with tab3:
    st.markdown("### 📊 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Cotizaciones", st.session_state.get("cotizaciones", 0))
    col2.metric("Productos", st.session_state.get("total_prods", 0))
    col3.metric("SKU IA", st.session_state.get("skus_detectados", 0))
    
    st.markdown("### 📈 Actividad")
    chart_data = pd.DataFrame({
        'Valor': [st.session_state.get("cotizaciones", 0), 
                  st.session_state.get("total_prods", 0)],
        'Métrica': ['Cotizaciones', 'Productos']
    })
    st.bar_chart(chart_data.set_index('Métrica'))
    
    st.markdown("### 💡 Consejos")
    st.info("""
    **Para mejor reconocimiento de SKU:**
    1. Usa imágenes nítidas y bien iluminadas
    2. Configura Gemini API para IA avanzada
    3. Si la imagen no es clara, usa entrada manual
    4. También puedes subir Excel directamente
    """)

# Footer
st.markdown("---")
st.markdown("*💼 QTC Smart Sales Pro - Sistema de Ventas con IA*")
