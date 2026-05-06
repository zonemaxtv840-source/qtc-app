import streamlit as st
import pandas as pd
import re, io, os
from datetime import datetime
from PIL import Image
import numpy as np

# --- CONFIGURACIÓN ---
try:
    img_logo = Image.open("logo.png")
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon=img_logo, layout="wide")
except:
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon="💼", layout="wide")

# --- COLORES VERDE FRESH ---
COLORES = {
    "fondo": "#f0fdf4",
    "tarjeta": "#ffffff", 
    "texto": "#1a3c34",
    "verde": "#27ae60",
    "verde_oscuro": "#219a52",
    "verde_hover": "#2ecc71",
}

# --- ESTILOS ---
st.markdown(f"""
    <style>
    .stApp, .main .block-container {{
        background-color: {COLORES["fondo"]};
        color: {COLORES["texto"]} !important;
    }}
    .stButton > button {{
        background: linear-gradient(135deg, {COLORES["verde"]}, {COLORES["verde_oscuro"]});
        color: white !important;
        border-radius: 10px;
        font-weight: 600;
    }}
    .metric-card {{
        background: {COLORES["tarjeta"]};
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    .metric-value {{
        font-size: 2rem;
        font-weight: bold;
        color: {COLORES["verde"]} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 💼 QTC Pro")
    st.divider()
    if "stats" in st.session_state:
        st.metric("📦 Productos", st.session_state.get("total_prods", 0))
        st.metric("📄 Cotizaciones", st.session_state.get("cotizaciones", 0))

# --- LOGIN ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown(f"""
        <div style="background: white; padding: 2rem; border-radius: 20px;">
            <h1 style="color: {COLORES['verde']}; text-align: center;">💚 QTC Smart Sales</h1>
        </div>
        """, unsafe_allow_html=True)
        user = st.text_input("Usuario")
        pw = st.text_input("Contraseña", type="password")
        if st.button("Ingresar", use_container_width=True):
            if user == "admin" and pw == "qtc2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")
    st.stop()

# --- FUNCIONES ---
def corregir_numero(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "0"]:
        return 0.0
    s = re.sub(r'[^\d.,]', '', str(valor).replace('S/', '').replace('$', ''))
    s = s.replace(',', '.') if '.' not in s else s.replace(',', '')
    try:
        return float(s)
    except:
        return 0.0

def generar_excel(items, cliente, ruc):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    pd.DataFrame(items).to_excel(writer, sheet_name='Cotizacion', index=False)
    workbook = writer.book
    ws = writer.sheets['Cotizacion']
    header_fmt = workbook.add_format({'bg_color': COLORES['verde'], 'bold': True, 'font_color': 'white'})
    for i, col in enumerate(['SKU', 'Descripcion', 'Cantidad', 'Precio', 'Total']):
        ws.write(0, i, col, header_fmt)
    writer.close()
    return output.getvalue()

# --- INTERFAZ ---
st.title("💚 QTC Smart Sales Pro")
tab1, tab2, tab3 = st.tabs(["📦 Pedidos", "🤖 SKU por Imagen", "📊 Dashboard"])

with tab1:
    st.sidebar.header("Archivos")
    f_precios = st.sidebar.file_uploader("Catálogo Precios", type=['xlsx'])
    f_stock = st.sidebar.file_uploader("Reporte Stock", type=['xlsx'])
    
    if f_precios and f_stock:
        df_precios = pd.read_excel(f_precios)
        df_stock = pd.read_excel(f_stock)
        
        # Buscar columnas
        col_sku = next((c for c in df_precios.columns if 'SKU' in str(c).upper()), df_precios.columns[0])
        col_desc = next((c for c in df_precios.columns if 'DESC' in str(c).upper()), df_precios.columns[1])
        col_precio = st.selectbox("Columna de Precio", df_precios.columns)
        
        # Ingreso manual
        texto = st.text_area("SKU:CANTIDAD (uno por línea)", height=150)
        pedidos = {}
        
        if texto:
            for linea in texto.split('\n'):
                if ':' in linea:
                    sku, cant = linea.split(':')
                    pedidos[sku.strip().upper()] = int(cant.strip())
                elif linea.strip():
                    pedidos[linea.strip().upper()] = 1
        
        if st.button("Procesar") and pedidos:
            resultados = []
            for sku, cant in pedidos.items():
                producto = df_precios[df_precios[col_sku].astype(str).str.contains(sku, case=False, na=False)]
                if not producto.empty:
                    precio = corregir_numero(producto.iloc[0][col_precio])
                    resultados.append({
                        'SKU': sku,
                        'Descripcion': producto.iloc[0][col_desc],
                        'Precio': precio,
                        'Cantidad': cant,
                        'Total': precio * cant
                    })
            
            if resultados:
                df_res = pd.DataFrame(resultados)
                st.dataframe(df_res)
                
                total = df_res['Total'].sum()
                st.metric("Total Cotización", f"S/. {total:,.2f}")
                
                cliente = st.text_input("Cliente", "CLIENTE NUEVO")
                if st.button("Descargar Excel"):
                    excel = generar_excel(resultados, cliente, "999999")
                    st.download_button("📥 Descargar", excel, f"cotizacion_{cliente}.xlsx")

with tab2:
    st.markdown("### 🤖 Extraer SKU desde Imagen")
    st.info("💡 Sube una foto del catálogo y el sistema extraerá los SKU")
    
    imagen = st.file_uploader("Subir imagen", type=['jpg', 'png', 'jpeg'])
    
    if imagen:
        img = Image.open(imagen)
        st.image(img, width=300)
        
        # Entrada manual alternativa
        st.markdown("---")
        st.markdown("### ✏️ Ingreso Manual")
        num = st.number_input("Cantidad de productos", min_value=1, max_value=10, value=3)
        
        skus_manual = {}
        for i in range(int(num)):
            col1, col2 = st.columns(2)
            with col1:
                sku = st.text_input(f"SKU {i+1}", key=f"sku_{i}")
            with col2:
                cant = st.number_input(f"Cantidad {i+1}", min_value=1, value=1, key=f"cant_{i}")
            if sku:
                skus_manual[sku.upper()] = cant
        
        if skus_manual and st.button("Transferir a Pedidos"):
            # Guardar en session state
            st.session_state.pedidos = skus_manual
            st.success(f"✅ {len(skus_manual)} SKUs transferidos")
            st.info("👉 Ve a la pestaña 'Pedidos' y pega los SKU manualmente")

with tab3:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.get("cotizaciones", 0)}</div>
            <div class="metric-label">Cotizaciones</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.get("total_prods", 0)}</div>
            <div class="metric-label">Productos</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("*💚 QTC Smart Sales - Sistema Seguro*")
