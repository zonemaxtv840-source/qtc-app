import streamlit as st
import pandas as pd
import re, io, os
import numpy as np
from PIL import Image
import google.generativeai as genai

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="QTC Smart Sales Pro", layout="wide")

# --- CONEXIÓN IA REFORZADA ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Configuramos el modelo para que sea más permisivo con la lectura de datos
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        generation_config={
            "temperature": 0.1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 1000,
        }
    )
else:
    st.error("❌ No se encontró la API KEY en Secrets.")
    st.stop()

# --- ESTILO ---
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
    st.title("🔐 Acceso QTC")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if u == "admin" and p == "qtc2026": 
            st.session_state.auth = True
            st.rerun()
        else: st.error("❌ Datos incorrectos")
    st.stop()

# --- MOTOR DE VISIÓN IA ---
def extraer_codigos_ia(imagen_pil):
    prompt = """
    Lee esta imagen. Extrae los códigos de producto y su cantidad.
    Formato: SKU:CANTIDAD, separado por comas.
    Ejemplo: CN0900033NA8:1, RN0800070NA8:2
    Si no ves cantidad, asume 1. No escribas nada más que los códigos.
    """
    try:
        # En la versión nueva de la librería, enviamos la imagen directamente
        response = model.generate_content([prompt, imagen_pil])
        return response.text.strip()
    except Exception as e:
        return f"ERROR_TECNICO: {str(e)}"

# --- INTERFAZ PRINCIPAL ---
st.title("💼 QTC Smart Sales")
st.sidebar.header("📂 Carga de Datos")

f_p = st.sidebar.file_uploader("1. Catálogo de Precios", type=['xlsx'])
f_s = st.sidebar.file_uploader("2. Reporte de Stock", type=['xlsx'])

if f_p and f_s:
    df_p_raw = pd.read_excel(f_p)
    df_s_raw = pd.read_excel(f_s)

    def limpiar(df):
        for i in range(min(15, len(df))):
            row_v = [str(x).upper() for x in df.iloc[i].values]
            if any(h in val for h in ['SKU', 'SAP', 'COD SAP', 'ARTICULO'] for val in row_v):
                df.columns = [str(c).strip() for c in df.iloc[i]]
                return df.iloc[i+1:].reset_index(drop=True).fillna(0)
        return df.fillna(0)

    df_p = limpiar(df_p_raw); df_s = limpiar(df_s_raw)

    c_sku_p = next((c for c in df_p.columns if any(x in str(c).upper() for x in ['SKU', 'SAP', 'COD SAP'])), df_p.columns[0])
    c_desc_p = next((c for c in df_p.columns if any(x in str(c).upper() for x in ['DESCRIPCION', 'GOODS', 'NOMBRE'])), df_p.columns[1])
    c_sku_s = next((c for c in df_s.columns if any(x in str(c).upper() for x in ['NUMERO', 'SKU', 'ARTICULO'])), df_s.columns[0])
    c_dsp = next((c for c in df_s.columns if 'DISPONIBLE' in str(c).upper()), df_s.columns[-1])
    
    precios = [c for c in df_p.columns if any(p in str(c).upper() for p in ['VIP', 'P.', 'BOX', 'MAYOR', 'IR'])]
    col_p_sel = st.selectbox("🎯 Nivel de Precio:", precios)

    st.divider()
    img_file = st.file_uploader("📸 Sube la foto del pedido", type=['jpg', 'png', 'jpeg'])
    
    if "pedido_ia" not in st.session_state: st.session_state.pedido_ia = {}

    if img_file:
        img_pil = Image.open(img_file)
        st.image(img_pil, width=400)
        if st.button("🔍 ESCANEAR CON IA"):
            with st.spinner("IA analizando imagen..."):
                res_raw = extraer_codigos_ia(img_pil)
                if "ERROR_TECNICO" in res_raw:
                    st.error(f"Hubo un detalle: {res_raw}")
                else:
                    st.info(f"🤖 IA detectó: {res_raw}")
                    temp = {}
                    # Limpiar el texto que a veces la IA manda con ``` o espacios
                    clean_res = res_raw.replace('`', '').replace('SKU:', '').strip()
                    for it in clean_res.split(','):
                        if ':' in it:
                            s, c = it.split(':')
                            # Solo números para la cantidad
                            c_num = int(re.sub(r'\D', '', c)) if re.sub(r'\D', '', c) else 1
                            temp[s.strip().upper()] = c_num
                        else:
                            temp[it.strip().upper()] = 1
                    st.session_state.pedido_ia = temp

    if st.button("🚀 PROCESAR DISPONIBILIDAD") and st.session_state.pedido_ia:
        final_list = []
        for sku_ped, cant_ped in st.session_state.pedido_ia.items():
            mask = df_p[c_sku_p].astype(str).str.contains(re.escape(sku_ped), case=False, na=False)
            match = df_p[mask]
            
            if match.empty:
                st.warning(f"⚠️ No se encontró el código {sku_ped} en el catálogo.")
                continue

            for _, fila in match.iterrows():
                info = fila.to_dict()
                info['PEDIDO'] = cant_ped
                sku_real = str(info[c_sku_p]).strip()
                stk_row = df_s[df_s[c_sku_s].astype(str).str.strip() == sku_real]
                
                def n_clean(v):
                    try: return int(float(str(v).replace('S/', '').replace(',', '').strip()))
                    except: return 0

                info['Disp'] = n_clean(stk_row[c_dsp].iloc[0] if not stk_row.empty else 0)
                info['P_UNIT'] = n_clean(fila[col_p_sel])
                info['ALERTA'] = "OK" if info['Disp'] >= cant_ped else "SIN STOCK"
                final_list.append(info)

        if final_list:
            df_final = pd.DataFrame(final_list).drop_duplicates()
            st.subheader("📊 Balance de Stock Real")
            def color_r(row): return ['background-color: #FF3333; color: black; font-weight: bold' if row.ALERTA == "SIN STOCK" else '' for _ in row]
            st.dataframe(df_final[[c_sku_p, c_desc_p, 'P_UNIT', 'PEDIDO', 'Disp', 'ALERTA']].style.apply(color_r, axis=1).format({'P_UNIT': 'S/. {:.2f}'}))
