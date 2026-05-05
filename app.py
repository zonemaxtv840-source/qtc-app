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

# --- INTERFAZ PREMIUM (CSS) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #1C2833 0%, #2C3E50 100%);
        color: white;
    }

    .login-container {
        background: rgba(255, 255, 255, 0.98);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.5);
        max-width: 450px;
        margin: auto;
    }

    .login-title {
        color: #1C2833;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 700;
        margin-bottom: 25px;
        text-align: center;
    }

    /* Estilo de los inputs */
    .stTextInput input {
        border-radius: 10px !important;
        border: 1px solid #ddd !important;
        padding: 10px !important;
    }

    /* Botón QTC Premium */
    .stButton>button {
        background: linear-gradient(90deg, #F79646 0%, #E67E22 100%) !important;
        color: white !important;
        border: none !important;
        padding: 12px !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(247, 150, 70, 0.4) !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111b21 !important;
    }
    
    .footer {
        position: fixed;
        bottom: 10px;
        width: 100%;
        text-align: center;
        font-size: 11px;
        color: rgba(255,255,255,0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. SISTEMA DE LOGIN ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.write("<br><br><br>", unsafe_allow_html=True)
    _, central_col, _ = st.columns([1, 2, 1])
    
    with central_col:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        try:
            st.image("logo.png", width=200)
        except:
            st.markdown("<h1 style='text-align:center; color:#F79646;'>QTC</h1>", unsafe_allow_html=True)
        
        # FIX DE SINTAXIS AQUÍ (Usando comillas simples para la clase)
        st.markdown("<h2 class='login-title'>Control de Acceso</h2>", unsafe_allow_html=True)
        
        user = st.text_input("Usuario Corporativo", placeholder="Nombre de usuario")
        pw = st.text_input("Contraseña", type="password", placeholder="••••••••")
        
        st.write("<br>", unsafe_allow_html=True)
        
        if st.button("INGRESAR AL PANEL"):
            if user == "admin" and pw == "qtc2026": 
                st.session_state.auth = True
                st.success("Acceso exitoso")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="footer">© 2026 Grupo QTC - Business Intelligence Unit</div>', unsafe_allow_html=True)
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
    fmt_h = workbook.add_format({'bg_color': '#F79646', 'bold': True, 'align': 'center', 'font_color': 'white', 'border': 1})
    fmt_m = workbook.add_format({'num_format': '"S/." #,##0.00', 'border': 1})
    fmt_b = workbook.add_format({'border': 1})
    ws.set_column('A:A', 15); ws.set_column('B:B', 65); ws.set_column('C:E', 12)
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

# --- 3. PANEL DE OPERACIONES ---
with st.sidebar:
    try: st.image("logo.png", use_container_width=True)
    except: st.title("💎 QTC PRO")
    st.divider()
    st.header("📂 Gestión de Datos")
    f_p = st.file_uploader("1. Lista de Precios", type=['xlsx'])
    f_s = st.file_uploader("2. Reporte de Almacén", type=['xlsx'])
    f_ped = st.file_uploader("3. Excel de Pedido (Opcional)", type=['xlsx'])
    st.write("<br><br>", unsafe_allow_html=True)
    if st.button("Cerrar Sesión"):
        st.session_state.auth = False
        st.rerun()

st.title("📊 Inteligencia de Ventas QTC")

if f_p and f_s:
    df_p_raw = pd.read_excel(f_p)
    xls_s = pd.ExcelFile(f_s)
    h_s = st.sidebar.selectbox("Punto de Venta (Hoja):", xls_s.sheet_names)
    df_s_raw = pd.read_excel(f_s, sheet_name=h_s)

    def limpiar_cabeceras(df):
        for i in range(min(15, len(df))):
            fila = [str(x).upper() for x in df.iloc[i].values]
            if any(h in item for h in ['SKU', 'SAP', 'ARTICULO', 'COD SAP'] for item in fila):
                df.columns = [str(c).strip() for c in df.iloc[i]]
                return df.iloc[i+1:].reset_index(drop=True).fillna(0)
        return df.fillna(0)

    df_p = limpiar_cabeceras(df_p_raw); df_s = limpiar_cabeceras(df_s_raw)

    precios_opc = [c for c in df_p.columns if any(p in str(c).upper() for p in ['MAYOR', 'CAJA', 'VIP', 'IR', 'BOX', 'SUGERIDO', 'PRECIO'])]
    col_p_sel = st.selectbox("🎯 Estrategia de Precio:", options=precios_opc if precios_opc else df_p.columns)

    st.divider()
    pedido_dict = {}
    
    if f_ped:
        df_ped_raw = pd.read_excel(f_ped)
        df_ped = limpiar_cabeceras(df_ped_raw)
        c_sku_ped = next((c for c in df_ped.columns if any(x in str(c).upper() for x in ['SKU', 'COD SAP', 'CODIGO', 'SAP', 'NO'])), df_ped.columns)
        c_cant_ped = next((c for c in df_ped.columns if any(x in str(c).upper() for x in ['PEDIDO', 'CANTIDAD', 'CANT'])), None)
        
        if c_cant_ped:
            for _, fila_p in df_ped.iterrows():
                val_cant = fila_p[c_cant_ped]
                if pd.notna(val_cant) and (isinstance(val_cant, (int, float)) or str(val_cant).replace('.','').isdigit()):
                    cant_p = int(float(val_cant))
                    if cant_p > 0:
                        sku_p = str(fila_p[c_sku_ped]).strip().upper()
                        if sku_p not in ['0', '0.0', 'NAN']: pedido_dict[sku_p] = cant_p
            st.success(f"📦 Pedido cargado: {len(pedido_dict)} SKUs")

    txt_area = st.text_area("⌨️ Entrada rápida (SKU:CANTIDAD, ...)", placeholder="ej. CN9404211NA8:5, RN0800070NA8:1")
    if txt_area:
        for it in txt_area.split(','):
            if ':' in it:
                parts = it.split(':')
                pedido_dict[parts[0].strip().upper()] = int(re.sub(r'\D', '', parts[1])) if parts[1].strip().isdigit() else 1
            else:
                pedido_dict[it.strip().upper()] = 1

    if st.button("🚀 ANALIZAR DISPONIBILIDAD") and pedido_dict:
        c_sku_p = next((c for c in df_p.columns if any(x in str(c).upper() for x in ['SKU', 'SAP', 'COD SAP'])), df_p.columns)
        c_desc_p = next((c for c in df_p.columns if any(x in str(c).upper() for x in ['DESCRIPCION', 'GOODS', 'NOMBRE'])), df_p.columns)
        c_sku_s = next((c for c in df_s.columns if any(x in str(c).upper() for x in ['NUMERO', 'SKU', 'ARTICULO'])), df_s.columns)
        c_dsp = next((c for c in df_s.columns if 'DISPONIBLE' in str(c).upper()), df_s.columns[-1])

        resultados = []
        for sku_ped, cant_ped in pedido_dict.items():
            mask = df_p[c_sku_p].astype(str).str.contains(re.escape(sku_ped), case=False, na=False)
            variantes = df_p[mask]
            for _, fila in variantes.iterrows():
                info = fila.to_dict(); info['PEDIDO'] = cant_ped; sku_real = str(info[c_sku_p]).strip()
                m_stk = df_s[df_s[c_sku_s].astype(str).str.strip() == sku_real]
                info['Disp'] = int(corregir_numero(m_stk[c_dsp].iloc[0] if not m_stk.empty else 0))
                info['P_UNIT'] = corregir_numero(info[col_p_sel])
                info['ALERTA'] = "OK" if info['Disp'] >= cant_ped else "SIN STOCK"
                resultados.append(info)

        if resultados:
            df_res = pd.DataFrame(resultados).drop_duplicates()
            def style_row(row): return ['background-color: #FF3333; color: black; font-weight: bold' if row.ALERTA == "SIN STOCK" else 'color: #1C2833' for _ in row]
            st.subheader("📋 Balance de Disponibilidad")
            st.dataframe(df_res[[c_sku_p, c_desc_p, 'P_UNIT', 'PEDIDO', 'Disp', 'ALERTA']].style.apply(style_row, axis=1).format({'P_UNIT': 'S/. {:.2f}'}))
            
            with st.expander("📥 Generar Cotización"):
                c1, c2 = st.columns(2)
                n_cli = c1.text_input("Razon Social / Cliente", value="CLIENTE NUEVO")
                r_cli = c2.text_input("RUC / DNI", value="-")
                items_ok = df_res[df_res.ALERTA == "OK"]
                if not items_ok.empty:
                    final_list = [{'sku': r[c_sku_p], 'desc': r[c_desc_p], 'cant': r['PEDIDO'], 'p_u': r['P_UNIT'], 'total': r['PEDIDO']*r['P_UNIT']} for _, r in items_ok.iterrows()]
                    st.download_button("📥 DESCARGAR COTIZACIÓN EXCEL", generar_excel_web(final_list, n_cli, r_cli), f"Coti_QTC_{n_cli}.xlsx")
