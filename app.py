# app.py - Cotizador Inteligente QTC v6.0
# Conecta a SharePoint para precios | Lee stock local | Búsqueda inteligente

import streamlit as st
import pandas as pd
import re
from io import BytesIO
from datetime import datetime
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential
import getpass

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title="QTC Cotizador Inteligente", page_icon="🧠", layout="wide")

# SharePoint
SHAREPOINT_SITE = "https://quetalcompra-my.sharepoint.com/personal/cristhian_leon_quetalcompra_com"
SHAREPOINT_DOCS = "/personal/cristhian_leon_quetalcompra_com/Documents"
SHAREPOINT_FILE = "Catalogo General/UGREEN-BASEUS-TRANSFORMERS_PRECIOS (General).xlsx"

# Mapeo de modos
MODO_STOCK = {
    "UGREEN": {"precio_hoja": "Ugreen", "stock_hojas": ["APRI.001"]},
    "UGREEN_PROMO": {"precio_hoja": "Ugreen_Promos", "stock_hojas": ["APRI.001"]},
    "BENFEI": {"precio_hoja": "Benfei", "stock_hojas": ["APRI.001"]},
    "BASEUS": {"precio_hoja": "Baseus", "stock_hojas": ["APRI.001"]},
    "TRANSFORMERS": {"precio_hoja": "Transformers", "stock_hojas": ["APRI.001"]},
    "MAONO": {"precio_hoja": "Maono", "stock_hojas": ["APRI.001"]},
    "INNOS": {"precio_hoja": "Innos", "stock_hojas": ["APRI.001"]},
    "XIAOMI": {"precio_hoja": "Xiaomi", "stock_hojas": ["APRI.004"]},
    "YESSICA": {"precio_hoja": "Xiaomi", "stock_hojas": ["YESSICA", "APRI.004"]},
    "SOFIA": {"precio_hoja": "Xiaomi", "stock_hojas": ["SOFIA", "APRI.004"]},
    "DJI": {"precio_hoja": None, "stock_hojas": ["DJI SEPARADO"]},  # DJI solo stock
}

# Columnas del catálogo
COL_SKU = "SKU"
COL_MODEL = "MODEL MARK"
COL_NO = "NO."
COL_DESC = "GOODS DESCRITPION"
COL_PRECIOS = {
    "IR": "Mayor",
    "BOX": "Caja",
    "VIP": "Vip"
}

# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def conectar_sharepoint(usuario, password):
    """Conecta a SharePoint con credenciales"""
    try:
        ctx = ClientContext(SHAREPOINT_SITE).with_credentials(UserCredential(usuario, password))
        web = ctx.web
        ctx.load(web)
        ctx.execute_query()
        return ctx
    except Exception as e:
        st.error(f"❌ Error de conexión a SharePoint: {e}")
        return None

@st.cache_data(ttl=3600)
def descargar_precios(ctx):
    """Descarga el archivo de precios desde SharePoint"""
    try:
        ruta_completa = f"{SHAREPOINT_DOCS}/{SHAREPOINT_FILE}"
        archivo = ctx.web.get_file_by_server_relative_path(ruta_completa)
        ctx.load(archivo)
        ctx.execute_query()
        
        contenido = archivo.read().value
        df_precios = pd.read_excel(BytesIO(contenido), sheet_name=None)
        return df_precios
    except Exception as e:
        st.error(f"❌ Error descargando precios: {e}")
        return None

@st.cache_data
def cargar_stock(archivo_excel):
    """Carga el archivo de stock local y unifica por SKU"""
    try:
        dfs = pd.read_excel(archivo_excel, sheet_name=None)
        stock_unificado = {}
        
        for hoja, df in dfs.items():
            # Detectar columna de SKU
            col_sku = None
            for col in df.columns:
                if any(p in str(col).upper() for p in ['NUMERO', 'ARTICULO', 'SKU', 'ID']):
                    col_sku = col
                    break
            
            # Detectar columna de cantidad/stock
            col_cant = None
            if hoja in ['APRI.001', 'APRI.004']:
                for col in df.columns:
                    if 'DISPONIBLE' in str(col).upper():
                        col_cant = col
                        break
            else:  # YESSICA, SOFIA, etc.
                for col in df.columns:
                    if 'CANTIDAD' in str(col).upper() or 'CANT' in str(col).upper():
                        col_cant = col
                        break
            
            if col_sku and col_cant:
                for _, row in df.iterrows():
                    sku = str(row[col_sku]).strip().upper()
                    sku = normalizar_sku(sku)
                    try:
                        cantidad = int(row[col_cant]) if pd.notna(row[col_cant]) else 0
                    except:
                        cantidad = 0
                    
                    if sku and sku != 'NAN':
                        if sku not in stock_unificado:
                            stock_unificado[sku] = {}
                        stock_unificado[sku][hoja] = cantidad
        
        return stock_unificado, dfs
    except Exception as e:
        st.error(f"❌ Error cargando stock: {e}")
        return {}, {}

def normalizar_sku(sku):
    """Normaliza SKU: CN1271619N → CN1271619NA8"""
    if pd.isna(sku):
        return ""
    sku = str(sku).strip().upper()
    if sku.endswith('N') and not sku.endswith('NA8'):
        sku = sku + 'A8'
    return sku

def buscar_producto(entrada, df_precios_hoja, stock_unificado):
    """Busca producto por SKU, MODEL MARK, NO. o descripción"""
    entrada_limpia = entrada.strip().upper()
    
    # Búsqueda exacta
    for col in [COL_SKU, COL_MODEL, COL_NO, COL_DESC]:
        if col in df_precios_hoja.columns:
            mask = df_precios_hoja[col].astype(str).str.upper() == entrada_limpia
            if mask.any():
                return df_precios_hoja[mask].iloc[0].to_dict()
    
    # Búsqueda parcial
    for col in [COL_SKU, COL_MODEL, COL_NO, COL_DESC]:
        if col in df_precios_hoja.columns:
            mask = df_precios_hoja[col].astype(str).str.upper().str.contains(entrada_limpia, na=False)
            if mask.any():
                return df_precios_hoja[mask].iloc[0].to_dict()
    
    return None

# ═══════════════════════════════════════════════════════════════════════════════
# INTERFAZ PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

st.title("🧠 QTC Cotizador Inteligente")
st.caption("Conecta a SharePoint · Lee stock local · Búsqueda por SKU, modelo o código")

# ── Autenticación SharePoint ──
with st.sidebar:
    st.markdown("### 🔐 SharePoint")
    usuario_sharepoint = st.text_input("Usuario corporativo", placeholder="cristhian.leon@quetalcompra.com")
    password_sharepoint = st.text_input("Contraseña", type="password")
    
    if st.button("📡 Conectar a SharePoint") and usuario_sharepoint and password_sharepoint:
        with st.spinner("Conectando..."):
            ctx = conectar_sharepoint(usuario_sharepoint, password_sharepoint)
            if ctx:
                st.session_state['ctx'] = ctx
                st.success("✅ Conectado")
    
    # ── Modo de cotización ──
    st.markdown("---")
    st.markdown("### 📌 Configuración")
    
    modo = st.selectbox("Modo de cotización", list(MODO_STOCK.keys()))
    precio_nivel = st.selectbox("Nivel de precio", ["VIP", "BOX", "IR"])
    
    # ── Carga de stock local ──
    st.markdown("---")
    st.markdown("### 📦 Stock (local)")
    stock_file = st.file_uploader("Cargar STOCKKKK.xlsx", type=["xlsx"])
    
    if stock_file:
        with st.spinner("Cargando stock..."):
            stock_unificado, stock_dfs = cargar_stock(stock_file)
            st.session_state['stock_unificado'] = stock_unificado
            st.session_state['stock_dfs'] = stock_dfs
            st.success(f"✅ Stock cargado: {len(stock_unificado)} SKUs únicos")

# ── Cargar precios desde SharePoint si hay conexión ──
if 'ctx' in st.session_state and 'df_precios' not in st.session_state:
    with st.spinner("Cargando precios desde SharePoint..."):
        df_precios = descargar_precios(st.session_state['ctx'])
        if df_precios:
            st.session_state['df_precios'] = df_precios
            st.success("✅ Catálogo de precios cargado")

# ── BÚSQUEDA DE PRODUCTOS ──
if 'df_precios' in st.session_state and 'stock_unificado' in st.session_state:
    
    st.markdown("---")
    st.markdown("### 🔍 Buscar producto")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        busqueda = st.text_input("", placeholder="Ej: CN9405860NA8 | PB532 | 20956A | HiTune S3", label_visibility="collapsed")
    with col2:
        buscar_btn = st.button("🔍 Buscar", use_container_width=True)
    
    # Obtener la hoja de precios según el modo
    precio_hoja_nombre = MODO_STOCK[modo]["precio_hoja"]
    if precio_hoja_nombre and precio_hoja_nombre in st.session_state['df_precios']:
        df_precios_hoja = st.session_state['df_precios'][precio_hoja_nombre]
    else:
        df_precios_hoja = None
    
    if buscar_btn and busqueda:
        if df_precios_hoja is not None:
            producto = buscar_producto(busqueda, df_precios_hoja, st.session_state['stock_unificado'])
            
            if producto:
                sku = normalizar_sku(producto.get(COL_SKU, ''))
                descripcion = producto.get(COL_DESC, 'Sin descripción')
                model_mark = producto.get(COL_MODEL, '')
                no_code = producto.get(COL_NO, '')
                
                # Precios
                col_precio = COL_PRECIOS[precio_nivel]
                precio = producto.get(col_precio, 0)
                if pd.isna(precio):
                    precio = 0
                else:
                    precio = float(precio)
                
                # Stock
                stock_info = st.session_state['stock_unificado'].get(sku, {})
                
                # Mostrar resultados
                st.markdown("---")
                st.markdown(f"### 📦 {sku}")
                st.markdown(f"**Descripción:** {descripcion}")
                st.markdown(f"**MODEL MARK:** {model_mark} | **NO.:** {no_code}")
                st.markdown(f"**💰 Precio {precio_nivel}:** S/ {precio:,.2f}")
                
                # Stock separado por hoja
                st.markdown("**📊 Stock disponible:**")
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                with col_s1:
                    st.metric("APRI.001", stock_info.get("APRI.001", 0))
                with col_s2:
                    st.metric("APRI.004", stock_info.get("APRI.004", 0))
                with col_s3:
                    st.metric("YESSICA", stock_info.get("YESSICA", 0))
                with col_s4:
                    st.metric("SOFIA", stock_info.get("SOFIA", 0))
                
                # Botón agregar a cotización
                if st.button("➕ Agregar a cotización", key=f"add_{sku}"):
                    if 'carrito' not in st.session_state:
                        st.session_state['carrito'] = []
                    
                    st.session_state['carrito'].append({
                        'sku': sku,
                        'descripcion': descripcion[:60],
                        'model_mark': model_mark,
                        'precio': precio,
                        'cantidad': 1,
                        'stock_apri001': stock_info.get("APRI.001", 0),
                        'stock_apri004': stock_info.get("APRI.004", 0),
                        'stock_yessica': stock_info.get("YESSICA", 0),
                        'stock_sofia': stock_info.get("SOFIA", 0)
                    })
                    st.success(f"✅ {sku} agregado")
                    st.rerun()
            else:
                st.warning(f"❌ No se encontró: {busqueda}")
        else:
            st.warning(f"No hay hoja de precios para el modo {modo}")
    
    # ── COTIZACIÓN ──
    st.markdown("---")
    st.markdown("### 🛒 Cotización actual")
    
    if 'carrito' in st.session_state and st.session_state['carrito']:
        carrito_df = pd.DataFrame(st.session_state['carrito'])
        
        # Mostrar tabla editable
        edited_df = st.data_editor(
            carrito_df[['sku', 'descripcion', 'model_mark', 'precio', 'cantidad']],
            column_config={
                "sku": "SKU",
                "descripcion": "Descripción",
                "model_mark": "Modelo",
                "precio": st.column_config.NumberColumn("Precio", format="S/ %.2f"),
                "cantidad": st.column_config.NumberColumn("Cantidad", step=1, min_value=1)
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Actualizar cantidades
        for i, row in edited_df.iterrows():
            if i < len(st.session_state['carrito']):
                st.session_state['carrito'][i]['cantidad'] = row['cantidad']
        
        # Total
        total = sum(item['precio'] * item['cantidad'] for item in st.session_state['carrito'])
        st.markdown(f"### 💰 TOTAL: S/ {total:,.2f}")
        
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            if st.button("📥 Exportar a Excel", use_container_width=True):
                export_df = pd.DataFrame(st.session_state['carrito'])
                export_df['subtotal'] = export_df['precio'] * export_df['cantidad']
                
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    export_df.to_excel(writer, sheet_name='Cotizacion', index=False)
                
                st.download_button(
                    "💾 Descargar Excel",
                    data=output.getvalue(),
                    file_name=f"cotizacion_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        with col_exp2:
            if st.button("🧹 Limpiar carrito", use_container_width=True):
                st.session_state['carrito'] = []
                st.rerun()
    else:
        st.info("No hay productos en la cotización. Busca y agrega productos.")

else:
    if 'ctx' not in st.session_state:
        st.info("🔐 Conéctate a SharePoint en el panel lateral para cargar precios")
    elif 'stock_unificado' not in st.session_state:
        st.info("📦 Carga el archivo de stock en el panel lateral")

# ═══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.caption(f"QTC Cotizador Inteligente v6.0 | Modo: {modo} | Precio: {precio_nivel}")
