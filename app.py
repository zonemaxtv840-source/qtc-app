import streamlit as st
import pandas as pd
import re, io, cv2, os
import numpy as np
from PIL import Image
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="QTC Smart Sales", layout="wide")

# --- CONEXIÓN CON LA IA (GEMINI) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ Falta la configuración de GOOGLE_API_KEY en Secrets")

# --- ESTILO CORPORATIVO ---
st.markdown("""
    <style>
    .stButton>button { background-color: #F79646; color: white; border-radius: 8px; font-weight: bold; width: 100%; }
    .stDownloadButton>button { background-color: #28a745; color: white; border-radius: 8px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Acceso Corporativo QTC")
    user = st.text_input("Usuario")
    pw = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if user == "admin" and pw == "qtc2026": 
            st.session_state.auth = True
            st.rerun()
        else: st.error("❌ Credenciales incorrectas")
    st.stop()

# --- FUNCIONES DE LIMPIEZA ---
def corregir_numero(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "0", "0.0"]: return 0.0
    s = str(valor).upper().replace('S/', '').replace('$', '').replace(' ', '').replace(',', '').strip()
    try: return float(re.sub(r'[^\d.]', '', s))
    except: return 0.0

def generar_excel_web(items, cliente, ruc):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    pd.DataFrame(items).to_excel(writer, sheet_name='Cotizacion', index=False, startrow=5)
    workbook, ws = writer.book, writer.sheets['Cotizacion']
    fmt_h = workbook.add_format({'bg_color': '#1C2833', 'bold': True, 'font_color': 'white', 'border': 1, 'align': 'center'})
    ws.set_column('A:A', 15); ws.set_column('B:B', 60); ws.set_column('C:E', 12)
    for i, col in enumerate(['Código Sap', 'Descripción', 'Cantidad', 'Precio Unit.', 'Total']):
        ws.write(5, i, col, fmt_h)
    writer.close()
    return output.getvalue()

# --- MOTOR DE VISIÓN IA ---
def extraer_codigos_ia(imagen_pil):
    prompt = """
    Analiza esta imagen de un pedido. Extrae exclusivamente los códigos de producto (SKUs) y cantidades.
    Busca patrones de Xiaomi (RN..., CN...) y Ugreen (LP..., 12345...).
    Responde estrictamente en este formato: SKU:CANTIDAD, separado por comas.
    Ejemplo: RN0800070NA8:1, CN9407604NA8:3
    Si no ves cantidad, pon 1. No escribas nada de texto adicional.
    """
    try:
        response = model.generate_content([prompt, imagen_pil])
        return response.text.strip()
    except: return ""

# --- INTERFAZ PRINCIPAL ---
st.title("💼 QTC Smart Sales")
st.sidebar.header("📂 Carga de Datos")

f_p = st.sidebar.file_uploader("1. Catálogo de Precios", type=['xlsx'])
f_s = st.sidebar.file_uploader("2. Reporte de Stock", type=['xlsx'])

if f_p and f_s:
    df_p_raw = pd.read_excel(f_p)
    xls_s = pd.ExcelFile(f_s)
    h_s = st.sidebar.selectbox("Hoja de Stock:", xls_s.sheet_names)
    df_s_raw = pd.read_excel(f_s, sheet_name=h_s)

    # Limpieza automática
    def limpiar(df):
        for i in range(min(10, len(df))):
            if any(h in [str(x).upper() for x in df.iloc[i].values] for h in ['SKU', 'SAP', 'ARTICULO', 'COD SAP']):
                df.columns = [str(c).strip() for c in df.iloc[i]]
                return df.iloc[i+1:].reset_index(drop=True).fillna(0)
        return df.fillna(0)

    df_p = limpiar(df_p_raw); df_s = limpiar(df_s_raw)

    c_sku_p = next((c for c in df_p.columns if any(x in str(c).upper() for x in ['SKU', 'SAP', 'COD SAP'])), df_p.columns)
    c_desc_p = next((c for c in df_p.columns if any(x in str(c).upper() for x in ['DESCRIPCION', 'GOODS', 'NOMBRE'])), df_p.columns)
    c_sku_s = next((c for c in df_s.columns if any(x in str(c).upper() for x in ['NUMERO', 'SKU', 'ARTICULO'])), df_s.columns)
    c_dsp = next((c for c in df_s.columns if 'DISPONIBLE' in str(c).upper()), df_s.columns[-1])
    
    precios_opc = [c for c in df_p.columns if any(p in str(c).upper() for p in ['VIP', 'P.', 'BOX', 'MAYOR', 'IR'])]
    col_p_sel = st.selectbox("🎯 Precio a aplicar:", precios_opc)

    st.divider()
    modo = st.radio("Método de pedido:", ["⌨️ Manual", "📸 Imagen (IA Pro)"])
    pedido_ia = {}

    if modo == "⌨️ Manual":
        txt = st.text_area("Pega SKU:CANTIDAD")
        if txt:
            for it in txt.split(','):
                if ':' in it:
                    parts = it.split(':')
                    pedido_ia[parts[0].strip().upper()] = int(re.sub(r'\D', '', parts[1])) if parts[1].strip().isdigit() else 1
                else: pedido_ia[it.strip().upper()] = 1
    else:
        img_file = st.file_uploader("Sube foto del pedido", type=['jpg', 'png', 'jpeg'])
        if img_file:
            img_pil = Image.open(img_file)
            st.image(img_pil, width=300)
            if st.button("🔍 Escanear con IA"):
                with st.spinner("IA analizando con precisión quirúrgica..."):
                    texto_ia = extraer_codigos_ia(img_pil)
                    if texto_ia:
                        st.success(f"Detección: {texto_ia}")
                        for it in texto_ia.split(','):
                            if ':' in it:
                                p_parts = it.split(':')
                                pedido_ia[p_parts[0].strip().upper()] = int(re.sub(r'\D', '', p_parts[1])) if p_parts[1].strip() else 1
                            else: pedido_ia[it.strip().upper()] = 1

    if st.button("🚀 PROCESAR DISPONIBILIDAD") or (modo == "📸 Imagen (IA Pro)" and pedido_ia):
        res = []
        for sku_ped, cant_ped in pedido_ia.items():
            mask = df_p[c_sku_p].astype(str).str.contains(sku_ped, case=False, na=False)
            variantes = df_p[mask]
            for _, fila in variantes.iterrows():
                info = fila.to_dict(); info['PEDIDO'] = cant_ped; sku_real = str(info[c_sku_p]).strip()
                m_stk = df_s[df_s[c_sku_s].astype(str).str.strip() == sku_real]
                info['Disp'] = int(corregir_numero(m_stk[c_dsp].iloc if not m_stk.empty else 0))
                info['P_UNIT'] = corregir_numero(info[col_p_sel])
                info['ALERTA'] = "OK" if info['Disp'] >= cant_ped else "SIN STOCK"
                res.append(info)

        if res:
            df_res = pd.DataFrame(res).drop_duplicates()
            st.subheader("📊 Balance de Stock")
            def color_a(row): return ['background-color: #FF3333; color: black; font-weight: bold' if row.ALERTA == "SIN STOCK" else '' for _ in row]
            st.dataframe(df_res[[c_sku_p, c_desc_p, 'P_UNIT', 'PEDIDO', 'Disp', 'ALERTA']].style.apply(color_a, axis=1).format({'P_UNIT': 'S/. {:.2f}'}))

            with st.expander("📥 Generar Cotización"):
                c1, c2 = st.columns(2)
                n_cli = c1.text_input("Cliente", value="CLIENTE NUEVO")
                r_cli = c2.text_input("RUC/DNI", value="-")
                items_ok = df_res[df_res.ALERTA == "OK"]
                if not items_ok.empty:
                    f_list = [{'sku': r[c_sku_p], 'desc': r[c_desc_p], 'cant': r['PEDIDO'], 'p_u': r['P_UNIT'], 'total': r['PEDIDO']*r['P_UNIT']} for _, r in items_ok.iterrows()]
                    st.download_button("📥 Descargar Excel", generar_excel_web(f_list, n_cli, r_cli), f"Coti_{n_cli}.xlsx")

