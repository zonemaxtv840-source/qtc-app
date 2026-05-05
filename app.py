import streamlit as st
import pandas as pd
import re, io, os, time
from datetime import datetime
from PIL import Image

# --- CONFIGURACIÓN DE PÁGINA ---
try:
    img_logo = Image.open("logo.png")
    st.set_page_config(page_title="QTC Smart Sales", page_icon=img_logo, layout="wide")
except:
    st.set_page_config(page_title="QTC Smart Sales", page_icon="💼", layout="wide")

# --- CSS RADICAL (ELIMINA BARRAS Y FIJA CONTRASTE) ---
st.markdown("""
    <style>
    /* Eliminar cabecera y espacio superior de Streamlit */
    [data-testid="stHeader"] {display: none !important;}
    .block-container {padding-top: 0rem !important; padding-bottom: 0rem !important;}
    
    /* Fondo general de la App */
    .stApp { background-color: #f0f2f6; }

    /* Caja de Login Premium */
    .login-card {
        background-color: white;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
        border-top: 6px solid #F79646;
        text-align: center;
        color: #1C2833 !important; /* Letra oscura siempre visible */
    }

    /* Forzar color de etiquetas de texto */
    .stTextInput label { color: #1C2833 !important; font-weight: bold !important; }
    
    /* Botón QTC */
    .stButton>button {
        background-color: #F79646 !important;
        color: white !important;
        border-radius: 10px !important;
        height: 3.5em !important;
        width: 100% !important;
        font-weight: bold !important;
        border: none !important;
        font-size: 16px !important;
    }

    /* Sidebar oscuro */
    [data-testid="stSidebar"] { background-color: #1C2833 !important; }
    [data-testid="stSidebar"] * { color: white !important; }

    /* Footer */
    .footer-text {
        text-align: center;
        color: #999;
        font-size: 12px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. SISTEMA DE LOGIN ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    # Centrado absoluto sin barras blancas
    st.write("<br><br><br>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 1.2, 1])
    
    with col_mid:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        try:
            st.image("logo.png", width=220)
        except:
            st.markdown("<h1 style='color:#F79646;'>QTC PRO</h1>", unsafe_allow_html=True)
        
        st.markdown("<h2 style='color:#1C2833; margin-top:0;'>Acceso al Sistema</h2>", unsafe_allow_html=True)
        
        user = st.text_input("Usuario")
        pw = st.text_input("Contraseña", type="password")
        
        st.write("<br>", unsafe_allow_html=True)
        
        if st.button("INICIAR SESIÓN"):
            if user == "admin" and pw == "qtc2026": 
                st.session_state.auth = True
                st.success("Acceso concedido")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<p class="footer-text">© 2026 Que Tal Compra - Business Intelligence</p>', unsafe_allow_html=True)
    st.stop()

# --- 2. FUNCIONES DE PROCESAMIENTO ---
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

# --- 3. PANEL PRINCIPAL ---
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
        c_sku_ped = next((c for c in df_ped.columns if any(x in str(c).upper() for x in ['SKU', 'COD SAP', 'CODIGO', 'SAP'])), df_ped.columns[0])
        c_cant_ped = next((c for c in df_ped.columns if any(x in str(c).upper() for x in ['PEDIDO', 'CANTIDAD', 'CANT'])), None)
        if c_cant_ped:
            for _, fila in df_ped.iterrows():
                if pd.notna(fila[c_cant_ped]) and corregir_numero(fila[c_cant_ped]) > 0:
                    pedido_dict[str(fila[c_sku_ped]).strip().upper()] = int(corregir_numero(fila[c_cant_ped]))
            st.success(f"✅ {len(pedido_dict)} SKUs detectados en el Excel.")

    txt = st.text_area("⌨️ Entrada rápida (SKU:CANTIDAD, ...)")
    if txt:
        for it in txt.split(','):
            if ':' in it:
                p = it.split(':'); pedido_dict[p[0].strip().upper()] = int(re.sub(r'\D', '', p[1])) if p[1].strip() else 1
            else: pedido_dict[it.strip().upper()] = 1

    if st.button("🚀 ANALIZAR STOCK"):
        # FIX ERROR 'DATAFRAME' OBJECT: Forzar selección de columna única
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
                # Cruce con stock usando localizador seguro
                m_stk = df_s[df_s[c_sku_s].astype(str).str.strip() == sku_real]
                info['Disp'] = int(corregir_numero(m_stk[c_dsp].iloc[0] if not m_stk.empty else 0))
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
