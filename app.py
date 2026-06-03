# app.py - Cotizador Inteligente QTC v6.0 (SIN SHAREPOINT)

import streamlit as st
import pandas as pd
import re
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="QTC Cotizador Inteligente", page_icon="🧠", layout="wide")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

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
    "DJI": {"precio_hoja": None, "stock_hojas": ["DJI SEPARADO"]},
}

COL_SKU = "SKU"
COL_MODEL = "MODEL MARK"
COL_NO = "NO."
COL_DESC = "GOODS DESCRITPION"
COL_PRECIOS = {"IR": "Mayor", "BOX": "Caja", "VIP": "Vip"}

# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES
# ═══════════════════════════════════════════════════════════════════════════════

def normalizar_sku(sku):
    """CN1271619N → CN1271619NA8"""
    if pd.isna(sku):
        return ""
    sku = str(sku).strip().upper()
    if sku.endswith('N') and not sku.endswith('NA8'):
        sku = sku + 'A8'
    return sku

@st.cache_data
def cargar_precios(archivo):
    """Carga archivo de precios local (todas las hojas)"""
    try:
        dfs = pd.read_excel(archivo, sheet_name=None)
        return dfs
    except Exception as e:
        st.error(f"Error cargando precios: {e}")
        return None

@st.cache_data
def cargar_stock(archivo):
    """Carga archivo de stock local y unifica por SKU"""
    try:
        dfs = pd.read_excel(archivo, sheet_name=None)
        stock_unificado = {}
        
        for hoja, df in dfs.items():
            # Detectar columna SKU
            col_sku = None
            for col in df.columns:
                if any(p in str(col).upper() for p in ['NUMERO', 'ARTICULO', 'SKU', 'ID']):
                    col_sku = col
                    break
            
            # Detectar columna cantidad
            col_cant = None
            if hoja in ['APRI.001', 'APRI.004']:
                for col in df.columns:
                    if 'DISPONIBLE' in str(col).upper():
                        col_cant = col
                        break
            else:
                for col in df.columns:
                    if 'CANTIDAD' in str(col).upper() or 'CANT' in str(col).upper():
                        col_cant = col
                        break
            
            if col_sku and col_cant:
                for _, row in df.iterrows():
                    sku = normalizar_sku(row[col_sku])
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
        st.error(f"Error cargando stock: {e}")
        return {}, {}

def buscar_producto(entrada, df_precios_hoja):
    """Busca por SKU, MODEL MARK, NO. o descripción"""
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
# INTERFAZ
# ═══════════════════════════════════════════════════════════════════════════════

st.title("🧠 QTC Cotizador Inteligente")
st.caption("Carga tus archivos de precios y stock · Búsqueda por SKU, modelo o código")

with st.sidebar:
    st.markdown("### 📚 1. Cargar Precios")
    precios_file = st.file_uploader("Archivo de precios", type=["xlsx"], key="precios")
    
    st.markdown("### 📦 2. Cargar Stock")
    stock_file = st.file_uploader("Archivo de stock STOCKKKK.xlsx", type=["xlsx"], key="stock")
    
    st.markdown("---")
    st.markdown("### 📌 Configuración")
    
    modo = st.selectbox("Modo de cotización", list(MODO_STOCK.keys()))
    precio_nivel = st.selectbox("Nivel de precio", ["VIP", "BOX", "IR"])

# Cargar datos
if precios_file:
    df_precios = cargar_precios(precios_file)
    if df_precios:
        st.success(f"✅ Precios cargados: {len(df_precios)} hojas")
        st.session_state['df_precios'] = df_precios

if stock_file:
    stock_unificado, _ = cargar_stock(stock_file)
    if stock_unificado:
        st.session_state['stock_unificado'] = stock_unificado
        st.success(f"✅ Stock cargado: {len(stock_unificado)} SKUs únicos")

# Búsqueda
if 'df_precios' in st.session_state and 'stock_unificado' in st.session_state:
    
    precio_hoja_nombre = MODO_STOCK[modo]["precio_hoja"]
    
    if precio_hoja_nombre and precio_hoja_nombre in st.session_state['df_precios']:
        df_precios_hoja = st.session_state['df_precios'][precio_hoja_nombre]
        
        st.markdown("---")
        st.markdown("### 🔍 Buscar producto")
        
        busqueda = st.text_input("", placeholder="Ej: CN9405860NA8 | PB532 | 20956A | HiTune S3", label_visibility="collapsed")
        
        if busqueda:
            producto = buscar_producto(busqueda, df_precios_hoja)
            
            if producto:
                sku = normalizar_sku(producto.get(COL_SKU, ''))
                descripcion = producto.get(COL_DESC, 'Sin descripción')
                model_mark = producto.get(COL_MODEL, '')
                no_code = producto.get(COL_NO, '')
                
                col_precio = COL_PRECIOS[precio_nivel]
                precio = producto.get(col_precio, 0)
                if pd.isna(precio):
                    precio = 0
                else:
                    precio = float(precio)
                
                stock_info = st.session_state['stock_unificado'].get(sku, {})
                
                # Mostrar resultados
                st.markdown(f"""
                <div style="background:#f0f2f6; border-radius:10px; padding:15px; margin:10px 0;">
                    <h3>📦 {sku}</h3>
                    <p><strong>Descripción:</strong> {descripcion}</p>
                    <p><strong>MODEL MARK:</strong> {model_mark} | <strong>NO.:</strong> {no_code}</p>
                    <p><strong>💰 Precio {precio_nivel}:</strong> S/ {precio:,.2f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Stock por almacén
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("📦 APRI.001", stock_info.get("APRI.001", 0))
                col2.metric("📦 APRI.004", stock_info.get("APRI.004", 0))
                col3.metric("👩 YESSICA", stock_info.get("YESSICA", 0))
                col4.metric("👩 SOFIA", stock_info.get("SOFIA", 0))
                
                # Botón agregar
                if st.button("➕ Agregar a cotización"):
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
        st.warning(f"No hay hoja de precios para '{modo}'. Hoja esperada: {precio_hoja_nombre}")

# Carrito
st.markdown("---")
st.markdown("### 🛒 Cotización actual")

if 'carrito' in st.session_state and st.session_state['carrito']:
    carrito_df = pd.DataFrame(st.session_state['carrito'])
    
    edited_df = st.data_editor(
        carrito_df[['sku', 'descripcion', 'precio', 'cantidad']],
        column_config={
            "sku": "SKU",
            "descripcion": "Descripción",
            "precio": st.column_config.NumberColumn("Precio", format="S/ %.2f"),
            "cantidad": st.column_config.NumberColumn("Cantidad", step=1, min_value=1)
        },
        hide_index=True,
        use_container_width=True
    )
    
    for i, row in edited_df.iterrows():
        if i < len(st.session_state['carrito']):
            st.session_state['carrito'][i]['cantidad'] = row['cantidad']
    
    total = sum(item['precio'] * item['cantidad'] for item in st.session_state['carrito'])
    st.markdown(f"### 💰 TOTAL: S/ {total:,.2f}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Exportar a Excel"):
            export_df = pd.DataFrame(st.session_state['carrito'])
            export_df['subtotal'] = export_df['precio'] * export_df['cantidad']
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                export_df.to_excel(writer, sheet_name='Cotizacion', index=False)
            
            st.download_button(
                "💾 Descargar",
                data=output.getvalue(),
                file_name=f"cotizacion_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col2:
        if st.button("🧹 Limpiar todo"):
            st.session_state['carrito'] = []
            st.rerun()
else:
    st.info("No hay productos en la cotización. Busca y agrega.")
