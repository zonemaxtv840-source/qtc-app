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
    [data-testid="stSidebar"] { background-color: #1C2833; color: white; }
    .stDataFrame { border: 1px solid #F79646; border-radius: 5px; }
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
            if user == "admin" and pw == "qtc2026": 
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")
    st.stop()

# --- 2. FUNCIONES LÓGICAS (IGUALES A TU V16) ---
def corregir_numero(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "0", "0.0"]: return 0.0
    s = str(valor).upper().replace('S/', '').replace('$', '').replace(' ', '').strip()
    # Si tiene coma Y punto -> Quitar coma (miles)
    if ',' in s and '.' in s: s = s.replace(',', '')
    # Si solo tiene coma y 2 decimales -> Cambiar coma por punto
    elif ',' in s:
        partes = s.split(',')
        if len(partes[-1]) <= 2: s = s.replace(',', '.')
        else: s = s.replace(',', '')
    s = re.sub(r'[^\d.]', '', s)
    try: return float(s)
    except: return 0.0

def corregir_errores_ocr(texto):
    t = str(texto).upper()
    t = t.replace('CNO', 'CN0').replace('CNE', 'CN9').replace('CNS', 'CN9')
    t = t.replace('NAB', 'NA8').replace('NAS', 'NA8').replace('S00', '900').replace('O', '0')
    return t

def tratar_imagen_ocr(img_pil):
    img = cv2.cvtColor(np.array(img_pil.convert('RGB')), cv2.COLOR_RGB2BGR)
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    final = cv2.resize(gris, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    _, final = cv2.threshold(final, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return final

def generar_excel_web(items, cliente, ruc):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    pd.DataFrame(items).to_excel(writer, sheet_name='Cotizacion', index=False, startrow=5)
    workbook, ws = writer.book, writer.sheets['Cotizacion']
    
    # Formatos de la plantilla original
    fmt_h = workbook.add_format({'bg_color': '#F79646', 'bold': True, 'border': 1, 'align': 'center'})
    fmt_m = workbook.add_format({'num_format': '"S/." #,##0.00', 'border': 1})
    fmt_b = workbook.add_format({'border': 1})
    
    ws.set_column('A:A', 20); ws.set_column('B:B', 75); ws.set_column('C:E', 15)
    
    # Encabezados de cliente
    ws.write('A1', 'FECHA:', workbook.add_format({'bold': True})); ws.write('B1', datetime.now().strftime("%d/%m/%Y"))
    ws.write('A2', 'CLIENTE:', workbook.add_format({'bold': True})); ws.write('B2', cliente.upper()); ws.write('A3', 'RUC:', workbook.add_format({'bold': True})); ws.write('B3', ruc)
    
    # Cuentas bancarias
    ws.merge_range('F1:H1', 'CUENTAS QUE TAL COMPRA', fmt_h)
    ws.write('F2', 'BBVA SOLES:', workbook.add_format({'font_color': 'red', 'bold': True, 'border': 1})); ws.write('G2', '0011-0616-0100012617', fmt_b)
    
    # Títulos de tabla
    for i, col in enumerate(['Código Sap', 'Descripción', 'Cantidad', 'Precio Unit.', 'Total']):
        ws.write(5, i, col, fmt_h)
        
    # Datos y Totales
    for r, item in enumerate(items):
        ws.write_row(r + 6, 0, [item['sku'], item['desc'], item['cant'], item['p_u'], item['total']], fmt_b)
        ws.write(r + 6, 3, item['p_u'], fmt_m); ws.write(r + 6, 4, item['total'], fmt_m)
        
    ws.write(len(items)+6, 3, 'TOTAL S/.', fmt_h)
    ws.write(len(items)+6, 4, sum(i['total'] for i in items), fmt_m)
    
    writer.close()
    return output.getvalue()

# --- 3. INTERFAZ PRINCIPAL ---
st.title("💼 QTC Smart Sales - Consola de Operaciones")
st.sidebar.header("📂 Carga de Bases de Datos")

f_p = st.sidebar.file_uploader("1. Catálogo de Precios (Excel)", type=['xlsx'])
f_s = st.sidebar.file_uploader("2. Reporte de Stock (Excel)", type=['xlsx'])

if f_p and f_s:
    df_p_raw = pd.read_excel(f_p)
    xls_s = pd.ExcelFile(f_s)
    h_s = st.sidebar.selectbox("Selecciona hoja de Stock:", xls_s.sheet_names)
    df_s_raw = pd.read_excel(f_s, sheet_name=h_s)

    # Limpieza automática igual a tu función cargar_archivo_robusto
    def limpiar_cabeceras(df):
        for i in range(min(15, len(df))):
            fila = [str(x).upper() for x in df.iloc[i].values]
            if any(h in item for h in ['SKU', 'SAP', 'ARTICULO', 'NUMERO'] for item in fila):
                df.columns = [str(c).strip() for c in df.iloc[i]]
                return df.iloc[i+1:].reset_index(drop=True).fillna(0)
        return df.fillna(0)

    df_p = limpiar_cabeceras(df_p_raw)
    df_s = limpiar_cabeceras(df_s_raw)

    # Detección de columnas blindada
    def get_col(df, terms):
        match = [c for c in df.columns if any(t in str(c).upper() for t in terms)]
        return match[0] if match else df.columns[0]

    c_sku_p = get_col(df_p, ['SKU', 'SAP', 'CODIGO SAP'])
    c_desc_p = get_col(df_p, ['DESCRIPCION', 'GOODS', 'NOMBRE PRODUCTO'])
    c_sku_s = get_col(df_s, ['NUMERO', 'SKU', 'ARTICULO'])
    c_stk = next((c for c in df_s.columns if 'STOCK' in str(c).upper() or 'EN STOCK' in str(c).upper()), df_s.columns[-1])
    c_dsp = next((c for c in df_s.columns if 'DISPONIBLE' in str(c).upper()), df_s.columns[-1])
    
    precios_opc = [c for c in df_p.columns if any(p in str(c).upper() for p in ['VIP', 'P.', 'BOX', 'MAYOR', 'IR'])]
    col_p_sel = st.selectbox("🎯 Precio a aplicar:", precios_opc)

    st.divider()
    
    # MODO DE ENTRADA
    modo = st.radio("Método de pedido:", ["⌨️ Manual", "📸 Imagen"])
    pedido_dict = {}

    if modo == "⌨️ Manual":
        txt_area = st.text_area("Pega SKU:CANTIDAD (separados por coma)")
        if txt_area:
            for it in txt_area.split(','):
                if ':' in it:
                    parts = it.split(':')
                    sku_l = parts[0].strip().upper()
                    cant_l = int(parts[1].strip()) if parts[1].strip().isdigit() else 1
                    pedido_dict[sku_l] = cant_l
                else:
                    pedido_dict[it.strip().upper()] = 1
    else:
        up_img = st.file_uploader("Sube foto del pedido", type=['jpg', 'png', 'jpeg'])
        if up_img:
            img_pil = Image.open(up_img)
            st.image(img_pil, caption="Imagen cargada", width=300)
            img_proc = tratar_imagen_ocr(img_pil)
            texto_ocr = pytesseract.image_to_string(img_proc, config='--psm 6')
            for l in texto_ocr.split('\n'):
                l_corr = corregir_errores_ocr(l)
                match = re.search(r'CN[0-9A-Z]{5,15}', l_corr)
                if match:
                    cod = match.group()
                    nums = re.findall(r'\b\d{1,3}\b', l)
                    pedido_dict[cod] = int(nums[-1]) if nums else 1

    if st.button("🚀 PROCESAR DISPONIBILIDAD") and pedido_dict:
        resultados = []
        faltantes = []
        
        for cod_f, cant_f in pedido_dict.items():
            mask = df_p[c_sku_p].astype(str).str.contains(re.escape(cod_f), case=False, na=False)
            variantes = df_p[mask]
            
            if variantes.empty:
                faltantes.append(f"{cod_f} (No en catálogo)")
                continue

            for _, fila in variantes.iterrows():
                info = fila.to_dict()
                info['PEDIDO'] = cant_f
                sku_real = str(info[c_sku_p]).strip()
                m_stk = df_s[df_s[c_sku_s].astype(str).str.strip() == sku_real]
                
                info['Disp'] = int(corregir_numero(m_stk[c_dsp].values[0] if not m_stk.empty else 0))
                info['P_UNIT'] = corregir_numero(info[col_p_sel])
                info['ALERTA'] = "OK" if info['Disp'] >= cant_f else "SIN STOCK"
                resultados.append(info)

        if resultados or faltantes:
            if faltantes:
                st.error(f"⚠️ **Atención:** {', '.join(faltantes)}")
            
            if resultados:
                df_res = pd.DataFrame(resultados).drop_duplicates()
                
                def color_alerta(row):
                    return ['background-color: #FF3333; color: black; font-weight: bold' if row.ALERTA == "SIN STOCK" else '' for _ in row]
                
                st.subheader("📊 Balance de Stock Real")
                st.dataframe(df_res[[c_sku_p, c_desc_p, 'P_UNIT', 'PEDIDO', 'Disp', 'ALERTA']].style.apply(color_alerta, axis=1).format({'P_UNIT': 'S/. {:.2f}'}))

                with st.expander("📥 Generar Cotización Excel"):
                    c1, c2 = st.columns(2)
                    n_cli = c1.text_input("Cliente", value="CLIENTE NUEVO")
                    r_cli = c2.text_input("RUC/DNI", value="-")
                    
                    items_ok = df_res[df_res.ALERTA == "OK"]
                    if not items_ok.empty:
                        final_list = [{'sku': r[c_sku_p], 'desc': r[c_desc_p], 'cant': r['PEDIDO'], 'p_u': r['P_UNIT'], 'total': r['PEDIDO']*r['P_UNIT']} for _, r in items_ok.iterrows()]
                        excel_data = generar_excel_web(final_list, n_cli, r_cli)
                        st.download_button(label="📥 Descargar Cotización Excel", data=excel_data, file_name=f"Coti_{n_cli}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    else:
                        st.warning("No hay productos con stock suficiente para el Excel.")

