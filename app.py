import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Cotizador QTC", layout="wide")

st.title("📊 Cotizador QTC - Modo General")

# Login simple
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    user = st.text_input("Usuario")
    pw = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if user == "admin" and pw == "qtc2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
    st.stop()

# Sidebar para cargar archivos
with st.sidebar:
    st.header("📂 Cargar archivos")
    
    archivo_precios = st.file_uploader("Catálogo de precios", type=['xlsx', 'xls', 'csv'])
    archivo_stock = st.file_uploader("Stock", type=['xlsx', 'xls', 'csv'])

# Leer archivos
df_precios = None
df_stock = None

if archivo_precios:
    if archivo_precios.name.endswith('.csv'):
        df_precios = pd.read_csv(archivo_precios, encoding='latin-1')
    else:
        df_precios = pd.read_excel(archivo_precios)
    st.success(f"✅ Precios: {len(df_precios)} productos")

if archivo_stock:
    if archivo_stock.name.endswith('.csv'):
        df_stock = pd.read_csv(archivo_stock, encoding='latin-1')
    else:
        df_stock = pd.read_excel(archivo_stock)
    st.success(f"✅ Stock: {len(df_stock)} registros")

# Input de productos
st.subheader("📝 Ingresa SKU y cantidad")
texto = st.text_area("Formato: SKU:CANTIDAD (uno por línea)", height=150)

# Procesar
if st.button("Procesar") and texto and df_precios is not None:
    pedidos = []
    for linea in texto.split('\n'):
        if ':' in linea:
            sku, cant = linea.split(':')
            pedidos.append({'sku': sku.strip().upper(), 'cantidad': int(cant.strip())})
    
    resultados = []
    for p in pedidos:
        sku = p['sku']
        # Buscar precio
        producto = df_precios[df_precios.astype(str).apply(lambda x: x.str.contains(sku, case=False).any(), axis=1)]
        
        if not producto.empty:
            # Intentar encontrar columna de precio
            cols_precio = [c for c in producto.columns if 'PRECIO' in c.upper() or 'MAYOR' in c.upper() or 'PVP' in c.upper()]
            if cols_precio:
                precio = pd.to_numeric(producto.iloc[0][cols_precio[0]], errors='coerce')
            else:
                precio = 0
            
            # Buscar stock
            stock = 0
            if df_stock is not None:
                stock_producto = df_stock[df_stock.astype(str).apply(lambda x: x.str.contains(sku, case=False).any(), axis=1)]
                if not stock_producto.empty:
                    cols_stock = [c for c in stock_producto.columns if 'STOCK' in c.upper() or 'CANT' in c.upper()]
                    if cols_stock:
                        stock = pd.to_numeric(stock_producto.iloc[0][cols_stock[0]], errors='coerce')
            
            cotizar = min(p['cantidad'], stock) if stock > 0 else 0
            total = precio * cotizar
            
            resultados.append({
                'SKU': sku,
                'Precio': precio,
                'Pedido': p['cantidad'],
                'Stock': stock,
                'A Cotizar': cotizar,
                'Total': total
            })
        else:
            resultados.append({'SKU': sku, 'Precio': 0, 'Pedido': p['cantidad'], 'Stock': 0, 'A Cotizar': 0, 'Total': 0})
    
    # Mostrar resultados
    st.dataframe(pd.DataFrame(resultados))
    
    total_final = sum(r['Total'] for r in resultados)
    st.metric("💰 Total", f"S/. {total_final:,.2f}")
    
    # Generar Excel
    if st.button("Generar Excel"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            pd.DataFrame(resultados).to_excel(writer, index=False)
        st.download_button("Descargar", data=output.getvalue(), file_name="cotizacion.xlsx")
        
