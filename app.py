import streamlit as st
import pandas as pd
import re, io, os
from datetime import datetime
from PIL import Image

# --- CONFIGURACIÓN DE LA PÁGINA (LOGO EN LA PESTAÑA) ---
# Intentamos cargar el logo para la pestaña
try:
    img_logo = Image.open("logo.png")
    st.set_page_config(page_title="QTC Smart Sales", page_icon=img_logo, layout="wide")
except:
    st.set_page_config(page_title="QTC Smart Sales", page_icon="💼", layout="wide")

# --- ESTILO VISUAL CORPORATIVO ---
st.markdown("""
    <style>
    .stButton>button { background-color: #F79646; color: white; border-radius: 8px; height: 3em; width: 100%; font-weight: bold; }
    .stDownloadButton>button { background-color: #28a745; color: white; border-radius: 8px; width: 100%; }
    [data-testid="stSidebar"] { background-color: #1C2833; color: white; }
    .stDataFrame { border: 1px solid #F79646; border-radius: 5px; }
    /* Ajuste para el logo en la barra lateral */
    [data-testid="stSidebarNav"] { padding-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO EN LA BARRA LATERAL ---
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.write("💼 **QTC Pro**")
    st.divider()

# --- 1. SISTEMA DE LOGIN ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso Corporativo QTC")
    col_log1, col_log2 = st.columns(2)
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

# --- 2. FUNCIONES LÓGICAS ---
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
    fmt_h = workbook.add_format({'bg_color': '#F79646', 'bold': True, 'border': 1, 'align': 'center'})
    fmt_m = workbook.add_format({'num_format': '"S/." #,##0.00', 'border': 1})
    fmt_b = workbook.add_format({'border': 1})
    ws.set_column('A:A', 20); ws.set_column('B:B', 75); ws.set_column('C:E', 15)
    ws.write('A1', 'FECHA:', workbook.add_format({'bold': True})); ws.write('B1', datetime.now().strftime("%d/%m/%Y"))
    ws.write('A2', 'CLIENTE:', workbook.add_format({'bold': True})); ws.write('B2', cliente.upper()); ws.write('A3', 'RUC:', workbook.add_format({'bold': True})); ws.write('B3', ruc)
    ws.merge_range('F1:H1', 'CUENTAS QUE TAL COMPRA', fmt_h)
    ws.write('F2', 'BBVA SOLES:', workbook.add_format({'font_color': 'red', 'bold': True, 'border': 1})); ws.write('G2', '0011-0616-0100012617', fmt_b)
    for i, col in enumerate(['Código Sap', 'Descripción', 'Cantidad', 'Precio Unit.', 'Total']):
        ws.write(5, i, col, fmt_h)
    for r, item in enumerate(items):
        ws.write_row(r + 6, 0, [item['sku'], item['desc'], item['cant'], item['p_u'], item['total']], fmt_b)
        ws.write(r + 6, 3, item['p_u'], fmt_m); ws.write(r + 6, 4, item['total'], fmt_m)
    ws.write(len(items)+6, 3, 'TOTAL S/.', fmt_h); ws.write(len(items)+6, 4, sum(i['total'] for i in items), fmt_m)
    writer.close()
    return output.getvalue()

# --- 3. INTERFAZ PRINCIPAL ---
st.title("💼 QTC Smart Sales - Filtro de Pedidos")
st.sidebar.header("📂 Carga de Archivos")

f_p = st.sidebar.file_uploader("1. Catálogo de Precios", type=['xlsx'])
f_s = st.sidebar.file_uploader("2. Reporte de Stock", type=['xlsx'])
f_ped = st.sidebar.file_uploader("3. Excel de Pedido del Cliente", type=['xlsx'])

if f_p and f_s:
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

    # --- MOTOR DE DETECCIÓN DE PRECIOS MEJORADO ---
    # Buscamos cualquier columna que contenga palabras relacionadas a precios
    palabras_clave_precio = ['MAYOR', 'CAJA', 'VIP', 'IR', 'BOX', 'SUGERIDO', 'PRECIO', 'P.', 'UNIT']
    precios_opc = [c for c in df_p.columns if any(p in str(c).upper() for p in palabras_clave_precio)]
    
    # Si no encuentra nada con las claves, muestra todas las columnas para no bloquearte
    if not precios_opc: precios_opc = df_p.columns.tolist()
    
    col_p_sel = st.selectbox("🎯 Selecciona el Precio a aplicar:", options=precios_opc)

    st.divider()
    pedido_dict = {}
    
    if f_ped:
        st.info("🔍 Analizando pedido en Excel...")
        df_ped_raw = pd.read_excel(f_ped)
        df_ped = limpiar_cabeceras(df_ped_raw)
        c_sku_ped = next((c for c in df_ped.columns if any(x in str(c).upper() for x in ['SKU', 'COD SAP', 'CODIGO', 'SAP', 'NO'])), df_ped.columns)
        c_cant_ped = next((c for c in df_ped.columns if any(x in str(c).upper() for x in ['PEDIDO', 'CANTIDAD', 'CANT', 'SOLICITADO'])), None)
        
        if c_cant_ped:
            for _, fila_p in df_ped.iterrows():
                val_cant = fila_p[c_cant_ped]
                if pd.notna(val_cant) and (isinstance(val_cant, (int, float)) or str(val_cant).replace('.','').isdigit()):
                    cant_p = int(float(val_cant))
                    if cant_p > 0:
                        sku_p = str(fila_p[c_sku_ped]).strip().upper()
                        if sku_p and sku_p != '0' and sku_p != '0.0':
                            pedido_dict[sku_p] = cant_p
            st.success(f"✅ Se detectaron {len(pedido_dict)} productos solicitados.")
        else:
            st.error("No se encontró la columna de cantidad en el pedido.")
    else:
        txt_area = st.text_area("⌨️ O pega aquí SKU:CANTIDAD (separados por coma)")
        if txt_area:
            for it in txt_area.split(','):
                if ':' in it:
                    parts = it.split(':')
                    sku_l = parts[0].strip().upper()
                    cant_l = int(parts[1].strip()) if parts[1].strip().isdigit() else 1
                    pedido_dict[sku_l] = cant_l
                else:
                    pedido_dict[it.strip().upper()] = 1

    if st.button("🚀 PROCESAR DISPONIBILIDAD") and pedido_dict:
        c_sku_p = next((c for c in df_p.columns if any(x in str(c).upper() for x in ['SKU', 'SAP', 'COD SAP'])), df_p.columns)
        c_desc_p = next((c for c in df_p.columns if any(x in str(c).upper() for x in ['DESCRIPCION', 'GOODS', 'NOMBRE'])), df_p.columns)
        c_sku_s = next((c for c in df_s.columns if any(x in str(c).upper() for x in ['NUMERO', 'SKU', 'ARTICULO'])), df_s.columns)
        c_dsp = next((c for c in df_s.columns if 'DISPONIBLE' in str(c).upper()), df_s.columns[-1])

        resultados = []
        for cod_f, cant_f in pedido_dict.items():
            mask = df_p[c_sku_p].astype(str).str.contains(re.escape(cod_f), case=False, na=False)
            variantes = df_p[mask]
            for _, fila in variantes.iterrows():
                info = fila.to_dict()
                info['PEDIDO'] = cant_f
                sku_real = str(info[c_sku_p]).strip()
                m_stk = df_s[df_s[c_sku_s].astype(str).str.strip() == sku_real]
                info['Disp'] = int(corregir_numero(m_stk[c_dsp].iloc[0] if not m_stk.empty else 0))
                info['P_UNIT'] = corregir_numero(info[col_p_sel])
                info['ALERTA'] = "OK" if info['Disp'] >= cant_f else "SIN STOCK"
                resultados.append(info)

        if resultados:
            df_res = pd.DataFrame(resultados).drop_duplicates()
            def color_alerta(row):
                return ['background-color: #FF3333; color: black; font-weight: bold' if row.ALERTA == "SIN STOCK" else '' for _ in row]
            st.subheader("📊 Resultados de Cruce")
            st.dataframe(df_res[[c_sku_p, c_desc_p, 'P_UNIT', 'PEDIDO', 'Disp', 'ALERTA']].style.apply(color_alerta, axis=1).format({'P_UNIT': 'S/. {:.2f}'}))
            with st.expander("📥 Generar Cotización Final"):
                n_cli = st.text_input("Cliente", value="CLIENTE NUEVO")
                r_cli = st.text_input("RUC/DNI", value="-")
                items_ok = df_res[df_res.ALERTA == "OK"]
                if not items_ok.empty:
                    final_list = [{'sku': r[c_sku_p], 'desc': r[c_desc_p], 'cant': r['PEDIDO'], 'p_u': r['P_UNIT'], 'total': r['PEDIDO']*r['P_UNIT']} for _, r in items_ok.iterrows()]
                    st.download_button(label="📥 Descargar Excel", data=generar_excel_web(final_list, n_cli, r_cli), file_name=f"Coti_{n_cli}.xlsx")


