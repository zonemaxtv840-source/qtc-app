import streamlit as st
import pandas as pd
import re, io, os
import numpy as np
from PIL import Image
import google.generativeai as genai

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="QTC Smart Sales Pro", layout="wide")

# --- VERIFICACIÓN DE LLAVE ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Probamos una configuración de seguridad más relajada para que no bloquee los códigos
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("❌ LA API KEY NO ESTÁ CARGADA EN SECRETS. Revisa el paso anterior.")
    st.stop()

# --- ESTILO ---
st.markdown("""
    <style>
    .stButton>button { background-color: #F79646; color: white; border-radius: 8px; font-weight: bold; width: 100%; }
    .stDownloadButton>button { background-color: #28a745; color: white; border-radius: 8px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN (Simplificado para pruebas) ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Acceso QTC")
    user = st.text_input("Usuario")
    pw = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if user == "admin" and pw == "qtc2026": 
            st.session_state.auth = True
            st.rerun()
        else: st.error("❌ Error")
    st.stop()

# --- MOTOR DE VISIÓN IA (EXTRACCIÓN PURA) ---
def extraer_codigos_ia(imagen_pil):
    prompt = """
    Analiza la imagen y extrae todos los códigos SKU/SAP que veas (ejemplos: CN0900033NA8, RN..., WH...).
    Devuelve la respuesta en formato SKU:CANTIDAD separados por comas.
    Si no hay cantidad, usa 1. 
    Respuesta ejemplo: CN0900033NA8:1, CN0900043NA8:1
    NO escribas nada más, solo los códigos.
    """
    try:
        # Enviamos la imagen a Gemini
        response = model.generate_content([prompt, imagen_pil])
        return response.text.strip()
    except Exception as e:
        return f"ERROR_API: {str(e)}"

# --- INTERFAZ ---
st.title("💼 QTC Smart Sales")
st.sidebar.header("📂 Carga de Datos")

f_p = st.sidebar.file_uploader("1. Catálogo de Precios", type=['xlsx'])
f_s = st.sidebar.file_uploader("2. Reporte de Stock", type=['xlsx'])

if f_p and f_s:
    # Carga rápida
    df_p = pd.read_excel(f_p)
    df_s = pd.read_excel(f_s)
    
    # Limpieza de columnas (detectamos SKU en ambos)
    def auto_clean(df):
        for i in range(min(10, len(df))):
            row_vals = [str(x).upper() for x in df.iloc[i].values]
            if any(h in val for h in ['SKU', 'SAP', 'ARTICULO', 'COD SAP'] for val in row_vals):
                df.columns = [str(c).strip() for c in df.iloc[i]]
                return df.iloc[i+1:].reset_index(drop=True)
        return df

    df_p = auto_clean(df_p)
    df_s = auto_clean(df_s)

    c_sku_p = next((c for c in df_p.columns if any(x in str(c).upper() for x in ['SKU', 'SAP', 'COD SAP'])), df_p.columns[0])
    c_desc_p = next((c for c in df_p.columns if any(x in str(c).upper() for x in ['DESCRIPCION', 'GOODS', 'NOMBRE'])), df_p.columns[1])
    c_sku_s = next((c for c in df_s.columns if any(x in str(c).upper() for x in ['NUMERO', 'SKU', 'ARTICULO'])), df_s.columns[0])
    c_dsp = next((c for c in df_s.columns if 'DISPONIBLE' in str(c).upper()), df_s.columns[-1])
    
    precios_opc = [c for c in df_p.columns if any(p in str(c).upper() for p in ['VIP', 'P.', 'BOX', 'MAYOR', 'IR'])]
    col_p_sel = st.selectbox("🎯 Precio:", precios_opc)

    st.divider()
    img_file = st.file_uploader("📸 Sube la foto del pedido", type=['jpg', 'png', 'jpeg'])
    
    if "pedido_final" not in st.session_state: st.session_state.pedido_final = {}

    if img_file:
        img_pil = Image.open(img_file)
        st.image(img_pil, width=400)
        
        if st.button("🔍 ESCANEAR CON IA PRO"):
            with st.spinner("IA Pensando..."):
                respuesta_raw = extraer_codigos_ia(img_pil)
                
                # MOSTRAR QUÉ DIJO LA IA (Para depurar)
                st.info(f"🤖 Respuesta de la IA: {respuesta_raw}")
                
                if "ERROR_API" in respuesta_raw:
                    st.error(f"Hubo un problema con la llave de Google: {respuesta_raw}")
                else:
                    temp_ped = {}
                    # Limpiamos posibles caracteres de markdown que a veces pone Gemini
                    clean_text = respuesta_raw.replace('```', '').replace('csv', '').strip()
                    for it in clean_text.split(','):
                        if ':' in it:
                            sku, cant = it.split(':')
                            temp_ped[sku.strip().upper()] = int(re.sub(r'\D', '', cant)) if cant.strip() else 1
                        else:
                            temp_ped[it.strip().upper()] = 1
                    st.session_state.pedido_final = temp_ped
                    st.success("✅ Pedido cargado. Dale al botón de abajo para procesar stock.")

    if st.button("🚀 PROCESAR DISPONIBILIDAD") and st.session_state.pedido_final:
        res = []
        for sku_ped, cant_ped in st.session_state.pedido_final.items():
            mask = df_p[c_sku_p].astype(str).str.contains(sku_ped, case=False, na=False)
            variantes = df_p[mask]
            for _, fila in variantes.iterrows():
                info = fila.to_dict()
                info['PEDIDO'] = cant_ped
                sku_real = str(info[c_sku_p]).strip()
                m_stk = df_s[df_s[c_sku_s].astype(str).str.strip() == sku_real]
                
                # Fix decimales/miles
                def clean_n(v):
                    try: return int(float(str(v).replace('S/', '').replace(',', '').strip()))
                    except: return 0

                info['Disp'] = clean_n(m_stk[c_dsp].iloc[0] if not m_stk.empty else 0)
                info['P_UNIT'] = clean_n(fila[col_p_sel])
                info['ALERTA'] = "OK" if info['Disp'] >= cant_ped else "SIN STOCK"
                res.append(info)

        if res:
            df_res = pd.DataFrame(res).drop_duplicates()
            st.subheader("📊 Balance de Stock")
            def color_a(row): return ['background-color: #FF3333; color: black; font-weight: bold' if row.ALERTA == "SIN STOCK" else '' for _ in row]
            st.dataframe(df_res[[c_sku_p, c_desc_p, 'P_UNIT', 'PEDIDO', 'Disp', 'ALERTA']].style.apply(color_a, axis=1))
