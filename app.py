import streamlit as st
import pandas as pd
import re, io, os, time
from datetime import datetime
from PIL import Image

# --- 1. CONFIGURACIÓN E INTERFAZ (CSS DE ALTO CONTRASTE) ---
try:
    img_logo = Image.open("logo.png")
    st.set_page_config(page_title="QTC Smart Sales", page_icon=img_logo, layout="wide")
except:
    st.set_page_config(page_title="QTC Smart Sales", page_icon="💼", layout="wide")

st.markdown("""
    <style>
    /* ELIMINAR BARRAS Y ESPACIOS BLANCOS SUPERIORES */
    [data-testid="stHeader"] {display: none !important;}
    .block-container {padding-top: 0rem !important; padding-bottom: 0rem !important;}
    
    /* FONDO DE LA APP */
    .stApp { background-color: #f0f2f6; }

    /* TARJETA DE LOGIN */
    .login-card {
        background-color: white !important;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0px 10px 40px rgba(0,0,0,0.15);
        border-top: 8px solid #F79646;
        text-align: center;
        margin-top: 50px;
    }

    /* FORZAR COLOR DE LETRAS (AZUL OSCURO) */
    .login-card h1, .login-card h2, .login-card p, .stTextInput label {
        color: #1C2833 !important;
        font-family: 'Segoe UI', Tahoma, sans-serif;
    }
    
    /* INPUTS CON BORDE VISIBLE */
    .stTextInput input {
        color: #1C2833 !important;
        background-color: #fff !important;
        border: 2px solid #dcdde1 !important;
        border-radius: 10px !important;
    }

    /* BOTÓN QTC NARANJA */
    .stButton>button {
        background-color: #F79646 !important;
        color: white !important;
        border-radius: 12px !important;
        height: 3.5em !important;
        width: 100% !important;
        font-weight: bold !important;
        border: none !important;
        font-size: 16px !important;
        box-shadow: 0px 4px 10px rgba(247, 150, 70, 0.3);
    }
    .stButton>button:hover { background-color: #e67e22 !important; }

    /* SIDEBAR OSCURO */
    [data-testid="stSidebar"] { background-color: #1C2833 !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SISTEMA DE ACCESO ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    _, col_central, _ = st.columns([1, 1.2, 1])
    
    with col_central:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        try:
            st.image("logo.png", width=220)
        except:
            st.markdown("<h1 style='font-size: 50px; margin-bottom: 0;'>QTC</h1>", unsafe_allow_html=True)
        
        st.markdown("<h2 style='margin-top: 0;'>Panel de Operaciones</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 14px;'>Ingrese credenciales para continuar</p>", unsafe_allow_html=True)
        
        user = st.text_input("Usuario")
        pw = st.text_input("Contraseña", type="password")
        
        st.write("<br>", unsafe_allow_html=True)
        
        if st.button("ACCEDER AHORA"):
            if user == "admin" and pw == "qtc2026": 
                st.session_state.auth = True
                st.success("✅ Acceso correcto")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 3. LÓGICA DE DATOS (PROTECCIÓN CONTRA ERRORES) ---
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
    fmt_h = workbook.add_format({'bg_color': '#F79646', 'bold': True, 'align': 'center', 'font_color': 'white'})
    fmt_m = workbook.add_format({'num_format': '"S/." #,##0.00', 'border': 1})
    fmt_b = workbook.add_format({'border': 1})
    ws.set_column('A:A', 20); ws.set_column('B:B', 70); ws.set_column('C:E', 15)
    ws.write('A1', 'FECHA:', workbook.add_format({'bold': True})); ws.write('B1', datetime.now().strftime("%d/%m/%Y"))
    ws.write('A2', 'CLIENTE:', workbook.add_format({'bold': True})); ws.write('B2', cliente.upper()); ws.write('A3', 'RUC:', workbook.add_format({'bold': True})); ws.write('B3', ruc)
    for i, col in enumerate(['Código Sap', 'Descripción', 'Cantidad', 'Precio Unit.', 'Total']):
        ws.write(5, i, col, fmt_h)
    for r, item in enumerate(items):
        ws.write_row(r + 6, 0, [item['sku'], item['desc'], item['cant'], item['p_u'], item['total']], fmt_b)
        ws.write(r + 6, 3, item['p_u'], fmt_m); ws.write(r + 6, 4, item['total'], fmt_m)
    ws.write(len(items)+6, 3, 'TOTAL S/.', fmt_h); ws.write(len(items)+6, 4, sum(i['total'] for i in items), fmt_m)
    writer.close()
    return output.getvalue()

# --- 4. PANEL PRINCIPAL ---
with st.sidebar:
    try: st.image("logo.png", use_container_width=True)
    except: st.title("💎 QTC PRO")
    st.divider()
    st.header("📂 Carga de Datos")
    f_p = st.file_uploader("1. Catálogo de Precios", type=['xlsx'])
    f_s = st.file_uploader("2. Reporte de Stock", type=['xlsx'])
    f_ped = st.file_uploader("3. Excel de Pedido (Opcional)", type=['xlsx'])
    if st.button("Cerrar Sesión"):
        st.session_state.auth = False
        st.rerun()

st.title("📊 Panel de Inteligencia QTC")

if f_p and f_s:
    df_p_raw = pd.read_excel(f_p); xls_s = pd.ExcelFile(f_s)
    h_s = st.sidebar.selectbox("Seleccionar Hoja de Almacén:", xls_s.sheet_names)
    df_s_raw = pd.read_excel(f_s, sheet_name=h_s)

    def limpiar_df(df):
        for i in range(min(15, len(df))):
            linea = [str(x).upper() for x in df.iloc[i].values]
            if any(h in val for h in ['SKU', 'SAP', 'ARTICULO', 'NUMERO', 'COD SAP'] for val in linea):
                df.columns = [str(c).strip() for c in df.iloc[i]]
                return df.iloc[i+1:].reset_index(drop=True).fillna(0)
        return df.fillna(0)

    df_p = limpiar_df(df_p_raw); df_s = limpiar_df(df_s_raw)

    precios_opc = [c for c in df_p.columns if any(p in str(c).upper() for p in ['MAYOR', 'CAJA', 'VIP', 'IR', 'BOX', 'SUGERIDO'])]
    col_p_sel = st.selectbox("🎯 Estrategia de Precio:", options=precios_opc if precios_opc else df_p.columns)

    st.divider()
    pedido_dict = {}
    
    if f_ped:
        df_ped = limpiar_df(pd.read_excel(f_ped))
        c_sku_ped_list = [c for c in df_ped.columns if any(x in str(c).upper() for x in ['SKU', 'COD SAP', 'CODIGO', 'SAP'])]
        c_cant_ped_list = [c for c in df_ped.columns if any(x in str(c).upper() for x in ['PEDIDO', 'CANTIDAD', 'CANT'])]
        
        if c_sku_ped_list and c_cant_ped_list:
            c_s_p = c_sku_ped_list[0]; c_c_p = c_cant_ped_list[0]
            for _, fila in df_ped.iterrows():
                if pd.notna(fila[c_c_p]) and corregir_numero(fila[c_c_p]) > 0:
                    pedido_dict[str(fila[c_s_p]).strip().upper()] = int(corregir_numero(fila[c_c_p]))
            st.success(f"✅ {len(pedido_dict)} SKUs detectados.")

    txt = st.text_area("⌨️ Entrada rápida (SKU:CANTIDAD, ...)")
    if txt:
        for it in txt.split(','):
            if ':' in it:
                p = it.split(':'); pedido_dict[p[0].strip().upper()] = int(re.sub(r'\D', '', p[1])) if p[1].strip() else 1
            else: pedido_dict[it.strip().upper()] = 1

    if st.button("🚀 ANALIZAR STOCK"):
        # USAMOS [0] PARA EVITAR ERROR 'DATAFRAME' OBJECT HAS NO STR
        c_sku_p = [c for c in df_p.columns if any(x in str(c).upper() for x in ['SKU', 'SAP', 'COD SAP'])][0]
        c_desc_p = [c for c in df_p.columns if any(x in str(c).upper() for x in ['DESCRIPCION', 'GOODS', 'NOMBRE'])][0]
        c_sku_s = [c for c in df_s.columns if any(x in str(c).upper() for x in ['NUMERO', 'SKU', 'ARTICULO'])][0]
        c_dsp = [c for c in df_s.columns if 'DISPONIBLE' in str(c).upper()][0]

        resultados = []
        for sku_ped, cant_ped in pedido_dict.items():
            mask = df_p[c_sku_p].astype(str).str.contains(re.escape(sku_ped), case=False, na=False)
            variantes = df_p[mask]
            for _, fila in variantes.iterrows():
                info = fila.to_dict(); info['PEDIDO'] = cant_ped; sku_real = str(info[c_sku_p]).strip()
                m_stk = df_s[df_s[c_sku_s].astype(str).str.strip() == sku_real]
                if not m_stk.empty:
                    info['Disp'] = int(corregir_numero(m_stk[c_dsp].iloc[0]))
                else:
                    info['Disp'] = 0
                info['P_UNIT'] = corregir_numero(info[col_p_sel])
                info['ALERTA'] = "OK" if info['Disp'] >= cant_ped else "SIN STOCK"
                resultados.append(info)

        if resultados:
            df_res = pd.DataFrame(resultados).drop_duplicates()
            def style_r(row): return ['background-color: #FF3333; color: black; font-weight: bold' if row.ALERTA == "SIN STOCK" else 'color: #1C2833' for _ in row]
            st.dataframe(df_res[[c_sku_p, c_desc_p, 'P_UNIT', 'PEDIDO', 'Disp', 'ALERTA']].style.apply(style_r, axis=1).format({'P_UNIT': 'S/. {:.2f}'}))
            
            with st.expander("📥 Exportar a Excel"):
                n_cli = st.text_input("Cliente:", value="CLIENTE NUEVO")
                items_ok = df_res[df_res.ALERTA == "OK"]
                if not items_ok.empty:
                    f_list = [{'sku': r[c_sku_p], 'desc': r[c_desc_p], 'cant': r['PEDIDO'], 'p_u': r['P_UNIT'], 'total': r['PEDIDO']*r['P_UNIT']} for _, r in items_ok.iterrows()]
                    st.download_button("📥 DESCARGAR EXCEL", generar_excel_web(f_list, n_cli, "-"), f"Coti_{n_cli}.xlsx")
