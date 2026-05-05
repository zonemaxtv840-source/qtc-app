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

# --- ESTILO LIMPIO (SIN BARRAS FANTASMA) ---
st.markdown("""
    <style>
    /* Eliminar espacios vacíos de Streamlit al inicio */
    .block-container { padding-top: 2rem !important; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    
    /* Fondo general */
    .stApp { background-color: #f4f7f6; }

    /* Caja de Login */
    .login-box {
        background-color: white;
        padding: 35px;
        border-radius: 15px;
        box-shadow: 0px 8px 25px rgba(0,0,0,0.1);
        border-top: 5px solid #F79646; /* Toque naranja corporativo */
    }
    
    /* Botón Corporativo */
    .stButton>button {
        background-color: #F79646 !important;
        color: white !important;
        border-radius: 8px !important;
        height: 3.2em !important;
        width: 100% !important;
        font-weight: bold !important;
        border: none !important;
    }
    
    /* Personalización de Sidebar */
    [data-testid="stSidebar"] { background-color: #1C2833; color: white; }
    
    /* Tablas */
    .stDataFrame { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. SISTEMA DE LOGIN (VERSIÓN MEJORADA) ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    # Creamos columnas para centrar el cuadro
    _, col_central, _ = st.columns([1, 1.5, 1])
    
    with col_central:
        # Usamos un contenedor nativo para evitar la barra blanca superior
        with st.container():
            st.markdown('<div class="login-box">', unsafe_allow_html=True)
            
            # Logo centrado
            try:
                st.image("logo.png", width=200)
            except:
                st.title("💼 QTC PRO")
            
            st.markdown("<h2 style='text-align: center; color: #1C2833;'>Control de Acceso</h2>", unsafe_allow_html=True)
            
            user = st.text_input("Usuario Corporativo", placeholder="Ingrese su usuario")
            pw = st.text_input("Contraseña", type="password", placeholder="••••••••")
            
            st.write("") # Espacio
            
            if st.button("ACCEDER AL PANEL"):
                if user == "admin" and pw == "qtc2026": 
                    st.session_state.auth = True
                    st.success("✅ Acceso correcto")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Credenciales inválidas")
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray; font-size: 11px; margin-top: 15px;'>© 2026 Que Tal Compra - Intelligence Unit</p>", unsafe_allow_html=True)
    st.stop()

# --- 2. FUNCIONES LÓGICAS (V16 ESTABLE) ---
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
    ws.set_column('A:A', 20); ws.set_column('B:B', 75); ws.set_column('C:E', 15)
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
    except: st.title("💼 QTC Pro")
    st.divider()
    st.header("📂 Carga de Datos")
    f_p = st.file_uploader("1. Catálogo de Precios", type=['xlsx'])
    f_s = st.file_uploader("2. Reporte de Stock", type=['xlsx'])
    f_ped = st.file_uploader("3. Excel de Pedido (Opcional)", type=['xlsx'])
    st.write("<br><br><br>", unsafe_allow_html=True)
    if st.button("Cerrar Sesión"):
        st.session_state.auth = False
        st.rerun()

st.title("📊 Consola de Operaciones QTC")

if f_p and f_s:
    df_p_raw = pd.read_excel(f_p)
    xls_s = pd.ExcelFile(f_s)
    h_s = st.sidebar.selectbox("Hoja de Stock:", xls_s.sheet_names)
    df_s_raw = pd.read_excel(f_s, sheet_name=h_s)

    def limpiar_cabeceras(df):
        for i in range(min(15, len(df))):
            fila = [str(x).upper() for x in df.iloc[i].values]
            if any(h in item for h in ['SKU', 'SAP', 'ARTICULO', 'NUMERO', 'COD SAP'] for item in fila):
                df.columns = [str(c).strip() for c in df.iloc[i]]
                return df.iloc[i+1:].reset_index(drop=True).fillna(0)
        return df.fillna(0)

    df_p = limpiar_cabeceras(df_p_raw); df_s = limpiar_cabeceras(df_s_raw)

    precios_opc = [c for c in df_p.columns if any(p in str(c).upper() for p in ['MAYOR', 'CAJA', 'VIP', 'IR', 'BOX', 'SUGERIDO', 'PRECIO'])]
    col_p_sel = st.selectbox("🎯 Selecciona Nivel de Precio:", options=precios_opc if precios_opc else df_p.columns)

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
            st.success(f"✅ Pedido detectado: {len(pedido_dict)} SKUs")

    txt_area = st.text_area("⌨️ Entrada manual (SKU:CANTIDAD, ...)")
    if txt_area:
        for it in txt_area.split(','):
            if ':' in it:
                parts = it.split(':')
                pedido_dict[parts.strip().upper()] = int(re.sub(r'\D', '', parts)) if parts.strip().isdigit() else 1
            else:
                pedido_dict[it.strip().upper()] = 1

    if st.button("🚀 PROCESAR DISPONIBILIDAD") and pedido_dict:
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
                info['Disp'] = int(corregir_numero(m_stk[c_dsp].iloc if not m_stk.empty else 0))
                info['P_UNIT'] = corregir_numero(info[col_p_sel])
                info['ALERTA'] = "OK" if info['Disp'] >= cant_ped else "SIN STOCK"
                resultados.append(info)

        if resultados:
            df_res = pd.DataFrame(resultados).drop_duplicates()
            def color_a(row): return ['background-color: #FF3333; color: black; font-weight: bold' if row.ALERTA == "SIN STOCK" else '' for _ in row]
            st.subheader("📋 Balance de Disponibilidad Real")
            st.dataframe(df_res[[c_sku_p, c_desc_p, 'P_UNIT', 'PEDIDO', 'Disp', 'ALERTA']].style.apply(color_a, axis=1).format({'P_UNIT': 'S/. {:.2f}'}))
            
            with st.expander("📥 Generar Cotización"):
                c1, c2 = st.columns(2)
                n_cli = c1.text_input("Cliente", value="CLIENTE NUEVO")
                r_cli = c2.text_input("RUC/DNI", value="-")
                items_ok = df_res[df_res.ALERTA == "OK"]
                if not items_ok.empty:
                    final_list = [{'sku': r[c_sku_p], 'desc': r[c_desc_p], 'cant': r['PEDIDO'], 'p_u': r['P_UNIT'], 'total': r['PEDIDO']*r['P_UNIT']} for _, r in items_ok.iterrows()]
                    st.download_button("📥 Descargar Excel Naranja", generar_excel_web(final_list, n_cli, r_cli), f"Cotizacion_{n_cli}.xlsx")
