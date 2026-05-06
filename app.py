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

# ============================================
# 🎨 COLORES VERDE FRESH
# ============================================
COLORES = {
    "fondo_principal": "#f0fdf4",        # Verde muy claro (fondo)
    "fondo_tarjetas": "#ffffff",         # Blanco
    "texto_principal": "#1a3c34",        # Verde oscuro para texto
    "color_primario": "#27ae60",         # Verde fresh principal
    "color_primario_oscuro": "#219a52",  # Verde más oscuro
    "color_hover": "#2ecc71",            # Verde más brillante para hover
    "sidebar_fondo1": "#0d2818",         # Verde muy oscuro
    "sidebar_fondo2": "#1a4a2e",         # Verde oscuro
    "sidebar_texto": "#ffffff",          # Blanco
    "exito": "#27ae60",
    "error": "#e74c3c",
    "advertencia": "#f39c12",
    "texto_tab_inactivo": "#555555",     # Gris oscuro para tabs inactivos
    "texto_tab_activo": "#ffffff",       # Blanco para tab activo
}
# ============================================

# --- ESTILOS CON COLORES VERDE FRESH ---
st.markdown(f"""
    <style>
    /* Fondo general */
    .stApp {{
        background-color: {COLORES["fondo_principal"]};
    }}
    
    .main .block-container {{
        background-color: {COLORES["fondo_principal"]};
        color: {COLORES["texto_principal"]} !important;
    }}
    
    /* Headers y texto */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORES["texto_principal"]} !important;
        font-weight: 600 !important;
    }}
    
    p, span, div, label, .stMarkdown {{
        color: {COLORES["texto_principal"]} !important;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORES["sidebar_fondo1"]} 0%, {COLORES["sidebar_fondo2"]} 100%);
    }}
    
    [data-testid="stSidebar"] * {{
        color: {COLORES["sidebar_texto"]} !important;
    }}
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {{
        color: {COLORES["sidebar_texto"]} !important;
    }}
    
    /* Tabs - MEJORADO PARA LEGIBILIDAD */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {COLORES["fondo_tarjetas"]};
        border-radius: 12px;
        padding: 0.5rem;
        gap: 0.5rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        color: {COLORES["texto_tab_inactivo"]} !important;
        background-color: #f5f5f5;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: {COLORES["color_primario"]};
        color: white !important;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {COLORES["color_primario"]} 0%, {COLORES["color_primario_oscuro"]} 100%);
        color: {COLORES["texto_tab_activo"]} !important;
        box-shadow: 0 2px 8px rgba(39,174,96,0.3);
    }}
    
    /* Botones - VERDE CON TEXTO BLANCO */
    .stButton > button {{
        background: linear-gradient(135deg, {COLORES["color_primario"]} 0%, {COLORES["color_primario_oscuro"]} 100%);
        color: white !important;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1rem;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        background: linear-gradient(135deg, {COLORES["color_hover"]} 0%, {COLORES["color_primario"]} 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(39,174,96,0.4);
        color: white !important;
    }}
    
    /* Botón de descarga */
    .stDownloadButton > button {{
        background: linear-gradient(135deg, {COLORES["color_primario"]} 0%, {COLORES["color_primario_oscuro"]} 100%);
        color: white !important;
    }}
    
    /* Inputs */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {{
        background-color: {COLORES["fondo_tarjetas"]};
        color: {COLORES["texto_principal"]} !important;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 0.5rem;
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {COLORES["color_primario"]};
        box-shadow: 0 0 0 2px rgba(39,174,96,0.1);
    }}
    
    /* Selectbox */
    .stSelectbox > div > div {{
        background-color: {COLORES["fondo_tarjetas"]};
        color: {COLORES["texto_principal"]} !important;
        border-radius: 8px;
    }}
    
    /* Dataframe */
    .stDataFrame {{
        background-color: {COLORES["fondo_tarjetas"]};
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background-color: {COLORES["fondo_tarjetas"]};
        color: {COLORES["texto_principal"]} !important;
        border-radius: 10px;
        font-weight: 600;
        border: 1px solid #e0e0e0;
    }}
    
    /* Metric cards */
    .metric-card {{
        background: {COLORES["fondo_tarjetas"]};
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid rgba(39,174,96,0.2);
    }}
    
    .metric-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(39,174,96,0.15);
        border-color: {COLORES["color_primario"]};
    }}
    
    .metric-value {{
        font-size: 2.2rem;
        font-weight: bold;
        color: {COLORES["color_primario"]} !important;
    }}
    
    .metric-label {{
        font-size: 0.9rem;
        color: {COLORES["texto_principal"]} !important;
        margin-top: 0.5rem;
    }}
    
    /* Alertas */
    .stAlert {{
        border-radius: 10px;
        border-left: 4px solid {COLORES["color_primario"]};
    }}
    
    /* Código */
    code {{
        background-color: #e8f5e9;
        color: {COLORES["color_primario_oscuro"]} !important;
        padding: 2px 6px;
        border-radius: 5px;
        font-weight: 500;
    }}
    
    /* Expander content */
    .streamlit-expanderContent {{
        background-color: {COLORES["fondo_tarjetas"]};
        border-radius: 0 0 10px 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <h2 style="color: {COLORES["color_primario"]};">💼 QTC Pro</h2>
            <p style="color: white !important;">Sistema Verde Fresh</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 📊 Panel")
    
    if "stats" in st.session_state:
        st.metric("🌿 Productos", st.session_state.get("total_prods", 0))
        st.metric("📄 Cotizaciones", st.session_state.get("cotizaciones", 0))

# --- LOGIN ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown(f"""
            <div style="background: {COLORES["fondo_tarjetas"]}; padding: 2rem; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
                <h1 style="text-align: center; color: {COLORES["color_primario"]};">💚 QTC Smart Sales</h1>
                <p style="text-align: center; color: #666;">Sistema Verde Fresh</p>
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

# --- FUNCIONES (igual que antes) ---
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
    fmt_h = workbook.add_format({'bg_color': COLORES["color_primario"], 'bold': True, 'border': 1, 'align': 'center', 'font_color': 'white'})
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

def extract_skus_with_gemini(image, api_key):
    """Usar Gemini API para reconocimiento - Versión Segura"""
    if not api_key:
        return None
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Usar el modelo correcto
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        response = model.generate_content([
            "Extrae todos los códigos SKU y sus cantidades de esta imagen de catálogo. "
            "Devuelve SOLO un array JSON válido en este formato: [{\"sku\": \"CODIGO\", \"cantidad\": NUMERO}]. "
            "Si no hay cantidad, asume 1. Si ves una tabla, extrae todos los SKU y cantidades.",
            image
        ])
        
        text = response.text
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            import json
            data = json.loads(json_match.group())
            return data
        
        return []
    except Exception as e:
        st.error(f"Error con Gemini: {str(e)}")
        return None

# --- INTERFAZ PRINCIPAL ---
st.title("💚 QTC Smart Sales Pro - Verde Fresh")
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
        
        palabras_precio = ['MAYOR', 'CAJA', 'VIP', 'PRECIO', 'UNIT']
        precios_opc = [c for c in df_p.columns if any(p in str(c).upper() for p in palabras_precio)]
        if not precios_opc: 
            precios_opc = df_p.columns.tolist()
        
        col_p_sel = st.selectbox("🎯 Precio a aplicar:", precios_opc)
        
        pedido_dict = {}
        
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
        
        if st.button("🚀 PROCESAR DISPONIBILIDAD", use_container_width=True) and pedido_dict:
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
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Productos", len(df_res))
                    col2.metric("Con Stock", len(df_res[df_res.ALERTA == "✅ OK"]))
                    col3.metric("Sin Stock", len(df_res[df_res.ALERTA == "⚠️ SIN STOCK"]))
                    
                    st.dataframe(df_res[[c_sku_p, c_desc_p, 'P_UNIT', 'PEDIDO', 'Disp', 'ALERTA']])
                    
                    with st.expander("📥 Generar Cotización"):
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
                                file_name=f"Cotizacion_{n_cli}_{datetime.now().strftime('%Y%m%d')}.xlsx")
                            st.session_state.cotizaciones = st.session_state.get("cotizaciones", 0) + 1
                            st.session_state.total_prods = len(df_res)
                            st.balloons()

with tab2:
    st.markdown("### 🤖 Captura Inteligente de SKU")
    st.info("💚 Usa Gemini AI para extraer SKU automáticamente desde imágenes")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_image = st.file_uploader("📸 Subir imagen del catálogo", type=['jpg', 'jpeg', 'png'])
        
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, caption="Imagen cargada", use_container_width=True)
    
    with col2:
        st.markdown("#### 🔧 Configuración de Gemini")
        
        # ⚠️ IMPORTANTE: Usa st.secrets para producción
        # Por ahora, permitimos entrada manual pero con advertencia
        st.warning("⚠️ **Seguridad:** No compartas tu API Key. En producción, usa st.secrets")
        
        api_key = st.text_input("Google Gemini API Key", type="password", 
                               help="Obtén tu API Key en https://makersuite.google.com/app/apikey")
        
        if st.button("🌿 Extraer SKU con Gemini", use_container_width=True) and uploaded_image:
            if not api_key:
                st.warning("⚠️ Ingresa tu API Key de Gemini")
            else:
                with st.spinner("🤖 Analizando imagen..."):
                    extracted_data = extract_skus_with_gemini(image, api_key)
                    
                    if extracted_data and len(extracted_data) > 0:
                        df_skus = pd.DataFrame(extracted_data)
                        st.success(f"✅ Extraídos {len(df_skus)} SKUs")
                        st.dataframe(df_skus, use_container_width=True)
                        
                        if st.button("📋 Transferir a Pedido", use_container_width=True):
                            skus_dict = {row['sku']: row['cantidad'] for _, row in df_skus.iterrows()}
                            st.session_state.skus_transferidos = skus_dict
                            st.session_state.skus_detectados = len(skus_dict)
                            st.success(f"✅ {len(skus_dict)} SKUs transferidos")
                            st.info("👉 Ve a 'Gestión de Pedidos' y procesa")
                    else:
                        st.warning("⚠️ No se detectaron SKUs. Prueba entrada manual.")
        
        st.markdown("---")
        st.markdown("#### ✏️ Entrada Manual")
        num_items = st.number_input("Número de productos", min_value=1, max_value=10, value=3)
        
        manual_data = []
        for i in range(int(num_items)):
            col_a, col_b = st.columns(2)
            with col_a:
                sku = st.text_input(f"SKU {i+1}", key=f"manual_sku_{i}")
            with col_b:
                cant = st.number_input(f"Cantidad {i+1}", min_value=1, value=1, key=f"manual_cant_{i}")
            if sku:
                manual_data.append({'sku': sku.upper(), 'cantidad': cant})
        
        if manual_data and st.button("📋 Transferir Manual", use_container_width=True):
            skus_dict = {item['sku']: item['cantidad'] for item in manual_data}
            st.session_state.skus_transferidos = skus_dict
            st.success(f"✅ {len(skus_dict)} SKUs transferidos")

with tab3:
    st.markdown("### 📊 Dashboard Verde Fresh")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.get("cotizaciones", 0)}</div>
            <div class="metric-label">📄 Cotizaciones</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.get("total_prods", 0)}</div>
            <div class="metric-label">🌿 Productos</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.get("skus_detectados", 0)}</div>
            <div class="metric-label">🤖 SKU IA</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🔐 Seguridad API Key")
    st.info("""
    **Para producción en Streamlit Cloud:**
    
    1. Crea un archivo `.streamlit/secrets.toml`:
    ```toml
    GEMINI_API_KEY = "tu_nueva_api_key_aqui"
