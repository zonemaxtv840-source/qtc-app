import streamlit as st
import pandas as pd
import re, io, os
import numpy as np
from PIL import Image
import google.generativeai as genai

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="QTC Smart Sales Pro", layout="wide")

# --- CONEXIÓN IA (PROTECCIÓN TOTAL) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Intentamos cargar el modelo con un bloque de seguridad
    try:
        # Forzamos al sistema a no usar 'v1beta' si da error
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"⚠️ Error al inicializar IA: {e}")
else:
    st.error("❌ API KEY no encontrada. Agrégala en Settings > Secrets de Streamlit.")
    st.stop()

# --- ESTILO CORPORATIVO ---
st.markdown("""
    <style>
    .stButton>button { background-color: #F79646; color: white; border-radius: 8px; font-weight: bold; width: 100%; }
    .stDownloadButton>button { background-color: #28a745; color: white; border-radius: 8px; width: 100%; }
    [data-testid="stSidebar"] { background-color: #1C2833; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Acceso Corporativo QTC")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if u == "admin" and p == "qtc2026": 
            st.session_state.auth = True
            st.rerun()
        else: st.error("❌ Credenciales incorrectas")
    st.stop()

# --- MOTOR DE VISIÓN IA ---
def extraer_codigos_ia(imagen_pil):
    prompt = """
    Eres un extractor de datos de alta precisión. 
    Analiza la imagen y busca códigos de producto (SKUs). 
    Formato de salida: SKU:CANTIDAD, separado por comas.
    Ejemplo: CN0900033NA8:1, RN0800070NA8:5
    Si no hay cantidad visible, usa 1. Solo devuelve los códigos, nada de texto extra.
    """
    try:
        # Bloque de generación directo
        response = model.generate_content([prompt, imagen_pil])
        if response and response.text:
            return response.text.strip()
        else:
            return "ERROR: La IA no devolvió texto."
    except Exception as e:
        return f"ERROR_TECNICO: {str(e)}"

# --- INTERFAZ ---
st.title("💼 QTC Smart Sales")
st.sidebar.header("📂 Carga de Bases de Datos")

f_p = st.sidebar.file_uploader("1. Catálogo de Precios (Excel)", type=['xlsx'])
f_s = st.sidebar.file_uploader("2. Reporte de Stock (Excel)", type=['xlsx'])

if f_p and f_s:
    df_p_raw = pd.read_excel(f_p)
    df_s_raw = pd.read_excel(f_s)

    def auto_limpieza(df):
        for i in range(min(15, len(df))):
            linea = [str(x).upper() for x in df.iloc[i].values]
            if any(h in val for h in ['SKU', 'SAP', 'COD SAP', 'ARTICULO'] for val in linea):
                df.columns = [str(c).strip() for c in df.iloc[i]]
                return df.iloc[i+1:].reset_index(drop=True).fillna(0)
        return df.fillna(0)

    df_p = auto_limpieza(df_p_raw); df_s = auto_limpieza(df_s_raw)

    c_sku_p = next((c for c in df_p.columns if any(x in str(c).upper() for x in ['SKU', 'SAP', 'COD SAP'])), df_p.columns[0])
    c_desc_p = next((c for c in df_p.columns if any(x in str(c).upper() for x in ['DESCRIPCION', 'GOODS', 'NOMBRE'])), df_p.columns[1])
    c_sku_s = next((c for c in df_s.columns if any(x in str(c).upper() for x in ['NUMERO', 'SKU', 'ARTICULO'])), df_s.columns[0])
    c_dsp = next((c for c in df_s.columns if 'DISPONIBLE' in str(c).upper()), df_s.columns[-1])
    
    precios = [c for c in df_p.columns if any(p in str(c).upper() for p in ['VIP', 'P.', 'BOX', 'MAYOR', 'IR'])]
    col_p_sel = st.selectbox("🎯 Nivel de Precio a aplicar:", precios)

    st.divider()
    img_file = st.file_uploader("📸 Sube la foto del pedido del cliente", type=['jpg', 'png', 'jpeg'])
    
    if "pedido_ia" not in st.session_state: st.session_state.pedido_ia = {}

    if img_file:
        img_pil = Image.open(img_file)
        st.image(img_pil, width=350, caption="Imagen cargada")
        if st.button("🔍 ESCANEAR CON IA"):
            with st.spinner("IA analizando con precisión..."):
                res_raw = extraer_codigos_ia(img_pil)
                if "ERROR" in res_raw:
                    st.error(f"Detalle técnico: {res_raw}")
                else:
                    st.info(f"🤖 IA detectó: {res_raw}")
                    temp = {}
                    # Limpieza agresiva de caracteres extraños
                    clean = res_raw.replace('`', '').replace('csv', '').replace('SKU:', '').strip()
                    for item in clean.split(','):
                        if ':' in item:
                            s, c = item.split(':')
                            # Extraer solo números de la cantidad
                            c_num = int(re.sub(r'\D', '', c)) if re.sub(r'\D', '', c) else 1
                            temp[s.strip().upper()] = c_num
                        else:
                            temp[item.strip().upper()] = 1
                    st.session_state.pedido_ia = temp

    if st.button("🚀 PROCESAR DISPONIBILIDAD") and st.session_state.pedido_ia:
        res_final = []
        for sku_ped, cant_ped in st.session_state.pedido_ia.items():
            # Búsqueda flexible
            mask = df_p[c_sku_p].astype(str).str.contains(re.escape(sku_ped), case=False, na=False)
            match = df_p[mask]
            
            if match.empty:
                st.warning(f"⚠️ El código {sku_ped} no existe en este catálogo.")
                continue

            for _, fila in match.iterrows():
                info = fila.to_dict()
                info['PEDIDO'] = cant_ped
                sku_real = str(info[c_sku_p]).strip()
                stk_row = df_s[df_s[c_sku_s].astype(str).str.strip() == sku_real]
                
                def n_clean(v):
                    try: 
                        val = str(v).replace('S/', '').replace(',', '').strip()
                        return int(float(val))
                    except: return 0

                info['Disp'] = n_clean(stk_row[c_dsp].iloc[0] if not stk_row.empty else 0)
                info['P_UNIT'] = n_clean(fila[col_p_sel])
                info['ALERTA'] = "OK" if info['Disp'] >= cant_ped else "SIN STOCK"
                res_final.append(info)

        if res_final:
            df_final = pd.DataFrame(res_final).drop_duplicates()
            st.subheader("📊 Balance de Disponibilidad Actual")
            def estilo_rojo(row):
                return ['background-color: #FF3333; color: black; font-weight: bold' if row.ALERTA == "SIN STOCK" else '' for _ in row]
            st.dataframe(df_final[[c_sku_p, c_desc_p, 'P_UNIT', 'PEDIDO', 'Disp', 'ALERTA']].style.apply(estilo_rojo, axis=1).format({'P_UNIT': 'S/. {:.2f}'}))
