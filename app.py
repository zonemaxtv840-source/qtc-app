import streamlit as st
import pandas as pd
import re, io, cv2, os
import numpy as np
from PIL import Image
import pytesseract
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="QTC PRO - Consola de Ventas", layout="wide")

# --- ESTILO VISUAL CORPORATIVO ---
st.markdown("""
    <style>
    .stButton>button { background-color: #F79646; color: white; border-radius: 8px; height: 3em; width: 100%; font-weight: bold; }
    .stDownloadButton>button { background-color: #28a745; color: white; border-radius: 8px; width: 100%; }
    [data-testid="stMetricValue"] { font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. SISTEMA DE LOGIN ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso Corporativo QTC")
    col_log1, col_log2 = st.columns([1,1])
    with col_log1:
        user = st.text_input("Usuario")
        pw = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if user == "admin" and pw == "qtc2026": # Puedes cambiar esto después
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")
    st.stop()

# --- 2. FUNCIONES DE LIMPIEZA ---
def corregir_numero(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "0", "0.0"]: return 0.0
    s = str(valor).upper().replace('S/', '').replace('$', '').replace(' ', '').strip()
    if ',' in s and '.' in s: s = s.replace(',', '')
    elif ',' in s:
        partes = s.split(',')
        if len(partes[-1]) <= 2: s = s.replace(',', '.')
        else: s = s.replace(',', '')
    s = re.sub(r'[^\d.]', '', s)
    try: return float(s)
    except: return 0.0

def generar_excel_web(items, cliente, ruc):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    pd.DataFrame(items).to_excel(writer, sheet_name='Cotizacion', index=False, startrow=5)
    workbook, ws = writer.book, writer.sheets['Cotizacion']
    fmt_h = workbook.add_format({'bg_color': '#1C2833', 'bold': True, 'font_color': 'white', 'border': 1, 'align': 'center'})
    fmt_m = workbook.add_format({'num_format': '"S/." #,##0.00', 'border': 1})
    fmt_b = workbook.add_format({'border': 1})
    ws.set_column('A:A', 15); ws.set_column('B:B', 60); ws.set_column('C:E', 12)
    for i, col in enumerate(['Código Sap', 'Descripción', 'Cantidad', 'Precio Unit.', 'Total']):
        ws.write(5, i, col, fmt_h)
    writer.close()
    return output.getvalue()

# --- 3. INTERFAZ PRINCIPAL ---
st.title("📊 QTC Smart Sales - Consola de Operaciones")
st.sidebar.header("📂 Carga de Archivos")

f_p = st.sidebar.file_uploader("1. Catálogo de Precios (Excel)", type=['xlsx'])
f_s = st.sidebar.file_uploader("2. Reporte de Stock (Excel)", type=['xlsx'])

if f_p and f_s:
    df_p_raw = pd.read_excel(f_p)
    xls_s = pd.ExcelFile(f_s)
    h_s = st.sidebar.selectbox("Selecciona hoja de Stock:", xls_s.sheet_names)
    df_s_raw = pd.read_excel(f_s, sheet_name=h_s)

    # Limpieza de encabezados automática
    def limpiar_cabeceras(df):
        for i in range(min(10, len(df))):
            if any(h in [str(x).upper() for x in df.iloc[i].values] for h in ['SKU', 'SAP', 'ARTICULO', 'COD SAP']):
                df.columns = [str(c).strip() for c in df.iloc[i]]
                return df.iloc[i+1:].reset_index(drop=True).fillna(0)
        return df.fillna(0)

    df_p = limpiar_cabeceras(df_p_raw)
    df_s = limpiar_cabeceras(df_s_raw)

    # Detectar Columnas
    c_sku_p = next((c for c in df_p.columns if any(x in str(c).upper() for x in ['SKU', 'SAP', 'COD SAP'])), df_p.columns[0])
    c_desc_p = next((c for c in df_p.columns if any(x in str(c).upper() for x in ['DESCRIPCION', 'GOODS', 'NOMBRE'])), df_p.columns[1])
    c_sku_s = next((c for c in df_s.columns if any(x in str(c).upper() for x in ['NUMERO', 'SKU', 'ARTICULO'])), df_s.columns[0])
    c_dsp = next((c for c in df_s.columns if 'DISPONIBLE' in str(c).upper()), df_s.columns[-1])
    
    precios_opc = [c for c in df_p.columns if any(p in str(c).upper() for p in ['VIP', 'P.', 'BOX', 'MAYOR', 'IR'])]
    col_p_sel = st.selectbox("🎯 Nivel de Precio a aplicar:", precios_opc)

    # ENTRADA DE PEDIDO
    st.divider()
    tipo_entrada = st.radio("Método de pedido:", ["⌨️ Manual (Texto)", "📸 Imagen (IA)"])
    pedido_final = {}

    if tipo_entrada == "⌨️ Manual (Texto)":
        txt_area = st.text_area("Pega SKU:CANTIDAD (ej: CN1271072NA8:4, CN0900374NA8:6)")
        if txt_area:
            for it in txt_area.split(','):
                if ':' in it:
                    parts = it.split(':')
                    pedido_final[parts[0].strip().upper()] = int(parts[1]) if parts[1].strip().isdigit() else 1
                else: pedido_final[it.strip().upper()] = 1
    else:
        st.info("Función de Imagen en desarrollo para web. Usa Modo Manual por ahora.")

    if st.button("🚀 PROCESAR DISPONIBILIDAD"):
        res = []
        for sku_ped, cant_ped in pedido_final.items():
            mask = df_p[c_sku_p].astype(str).str.contains(sku_ped, case=False, na=False)
            variantes = df_p[mask]
            for _, fila in variantes.iterrows():
                info = fila.to_dict()
                info['PEDIDO'] = cant_ped
                sku_real = str(info[c_sku_p]).strip()
                m_stk = df_s[df_s[c_sku_s].astype(str).str.strip() == sku_real]
                info['Disp'] = int(corregir_numero(m_stk[c_dsp].iloc[0] if not m_stk.empty else 0))
                info['P_UNIT'] = corregir_numero(info[col_p_sel])
                info['ALERTA'] = "OK" if info['Disp'] >= cant_ped else "SIN STOCK"
                res.append(info)

        if res:
            df_res = pd.DataFrame(res).drop_duplicates()
            st.subheader("📊 Balance de Stock Real")
            
            def color_alerta(row):
                return ['background-color: #FF3333; color: black; font-weight: bold' if row.ALERTA == "SIN STOCK" else '' for _ in row]
            
            st.dataframe(df_res[[c_sku_p, c_desc_p, 'P_UNIT', 'PEDIDO', 'Disp', 'ALERTA']].style.apply(color_alerta, axis=1).format({'P_UNIT': 'S/. {:.2f}'}))

            # Formulario de Excel
            with st.expander("📥 Generar Archivo de Cotización"):
                c1, c2 = st.columns(2)
                nombre_cli = c1.text_input("Nombre del Cliente", value="CLIENTE NUEVO")
                ruc_cli = c2.text_input("RUC / DNI", value="-")
                
                items_ok = df_res[df_res.ALERTA == "OK"]
                if not items_ok.empty:
                    final_list = [{'sku': r[c_sku_p], 'desc': r[c_desc_p], 'cant': r['PEDIDO'], 'p_u': r['P_UNIT'], 'total': r['PEDIDO']*r['P_UNIT']} for _, r in items_ok.iterrows()]
                    excel_data = generar_excel_web(final_list, nombre_cli, ruc_cli)
                    st.download_button(label="📥 Descargar Cotización Excel", data=excel_data, file_name=f"Cotizacion_{nombre_cli}.xlsx")
                else:
                    st.warning("No hay productos con stock para generar el Excel.")


