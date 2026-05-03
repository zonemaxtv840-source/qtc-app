import streamlit as st
import pandas as pd
import re, io, os
from PIL import Image
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="QTC Smart Sales Pro", layout="wide")

# --- AI CONNECTION (FORCE GEMINI 1.5 FLASH) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Force the Flash 1.5 model, which is the current standard
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"❌ Error connecting to the AI brain: {e}")
        st.stop()
else:
    st.error("❌ No API KEY in Secrets.")
    st.stop()

# --- CORPORATE STYLE ---
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
    st.title("🔐 QTC Corporate Access")
    u = st.text_input("User")
    p = st.text_input("Password", type="password")
    if st.button("Enter"):
        if u == "admin" and p == "qtc2026": 
            st.session_state.auth = True
            st.rerun()
        else: st.error("Access denied")
    st.stop()

# --- AI VISION ENGINE ---
def extraer_codigos_ia(imagen_pil):
    prompt = """
    Analyze this order image. 
    Extract all SKU codes (e.g.: CN..., RN..., LP..., 12345...).
    Format: SKU:QUANTITY, separated by commas.
    If there is no quantity, put 1.
    Example: CN0900033NA8:1, RN0800070NA8:3
    Do NOT write anything else, only the codes on a single line.
    """
    try:
        # Gemini 1.5 Flash accepts the image directly
        response = model.generate_content([prompt, imagen_pil])
        if response.text:
            return response.text.strip()
        return "ERROR: The AI did not detect text."
    except Exception as e:
        return f"TECHNICAL_ERROR: {str(e)}"

# --- INTERFACE ---
st.title("💼 QTC Smart Sales")
st.sidebar.header("📂 Data Upload")

f_p = st.sidebar.file_uploader("1. Price List", type=['xlsx'])
f_s = st.sidebar.file_uploader("2. Stock Report", type=['xlsx'])

if f_p and f_s:
    df_p_raw = pd.read_excel(f_p)
    df_s_raw = pd.read_excel(f_s)

    def limpiar(df):
        for i in range(min(15, len(df))):
            row = [str(x).upper() for x in df.iloc[i].values]
            if any(h in v for h in ['SKU', 'SAP', 'ARTICULO', 'COD SAP'] for v in row):
                df.columns = [str(c).strip() for c in df.iloc[i]]
                return df.iloc[i+1:].reset_index(drop=True).fillna(0)
        return df.fillna(0)

    df_p = limpiar(df_p_raw); df_s = limpiar(df_s_raw)

    c_sku_p = next((c for c in df_p.columns if any(x in str(c).upper() for x in ['SKU', 'SAP', 'COD SAP'])), df_p.columns)
    c_desc_p = next((c for c in df_p.columns if any(x in str(c).upper() for x in ['DESCRIPTION', 'GOODS', 'NAME'])), df_p.columns)
    c_sku_s = next((c for c in df_s.columns if any(x in str(c).upper() for x in ['NUMBER', 'SKU', 'ARTICULO'])), df_s.columns)
    c_dsp = next((c for c in df_s.columns if 'AVAILABLE' in str(c).upper()), df_s.columns[-1])
    
    precios = [c for c in df_p.columns if any(p in str(c).upper() for p in ['VIP', 'P.', 'BOX', 'MAYOR', 'IR'])]
    col_p_sel = st.selectbox("🎯 Price:", precios)

    st.divider()
    img_file = st.file_uploader("📸 Upload the order photo", type=['jpg', 'png', 'jpeg'])
    
    if "pedido_ia" not in st.session_state: st.session_state.pedido_ia = {}

    if img_file:
        img_pil = Image.open(img_file)
        st.image(img_pil, width=350)
        if st.button("🔍 SCAN WITH AI"):
            with st.spinner("AI analyzing image with precision..."):
                res_raw = extraer_codigos_ia(img_pil)
                if "ERROR" in res_raw:
                    st.error(res_raw)
                else:
                    st.info(f"🤖 Detected: {res_raw}")
                    temp = {}
                    clean = res_raw.replace('`', '').replace('csv', '').strip()
                    for item in clean.split(','):
                        if ':' in item:
                            s, c = item.split(':')
                            c_num = int(re.sub(r'\D', '', c)) if re.sub(r'\D', '', c) else 1
                            temp[s.strip().upper()] = c_num
                        else:
                            temp[item.strip().upper()] = 1
                    st.session_state.pedido_ia = temp

    if st.button("🚀 PROCESS AVAILABILITY") and st.session_state.pedido_ia:
        final_data = []
        for sku_ped, cant_ped in st.session_state.pedido_ia.items():
            mask = df_p[c_sku_p].astype(str).str.contains(re.escape(sku_ped), case=False, na=False)
            match = df_p[mask]
            
            if match.empty:
                st.warning(f"Not found {sku_ped}")
                continue

            for _, fila in match.iterrows():
                info = fila.to_dict()
                info['ORDERED'] = cant_ped
                sku_real = str(info[c_sku_p]).strip()
                stk_row = df_s[df_s[c_sku_s].astype(str).str.strip() == sku_real]
                
                def n_clean(v):
                    try: return int(float(str(v).replace('S/', '').replace(',', '').strip()))
                    except: return 0

                info['Disp'] = n_clean(stk_row[c_dsp].iloc if not stk_row.empty else 0)
                info['P_UNIT'] = n_clean(fila[col_p_sel])
                info['ALERT'] = "OK" if info['Disp'] >= cant_ped else "OUT OF STOCK"
                final_data.append(info)

        if final_data:
            df_final = pd.DataFrame(final_data).drop_duplicates()
            st.subheader("📊 Stock Balance")
            def color_red(row): return ['background-color: #FF3333; color: black; font-weight: bold' if row.ALERT == "OUT OF STOCK" else '' for _ in row]
            st.dataframe(df_final[[c_sku_p, c_desc_p, 'P_UNIT', 'ORDERED', 'Disp', 'ALERT']].style.apply(color_red, axis=1).format({'P_UNIT': 'S/. {:.2f}'}))
