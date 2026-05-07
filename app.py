# ============================================
# TAB 2: BUSCAR PRODUCTOS (CORREGIDO - NOMBRE COMPLETO)
# ============================================
with tab_buscar:
    st.markdown("### 🔍 Buscar Productos")
    st.caption("💡 Busca por SKU, nombre o descripcion - Separa terminos con espacios o comas")
    
    if not st.session_state.catalogos:
        st.warning("🌿 Primero carga catalogos en la pestaña Cotizacion")
    else:
        todas_columnas = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio']:
                todas_columnas.add(col)
        
        col_precio_consulta = st.selectbox("💰 Mostrar precios en columna:", options=["(No mostrar precio)"] + sorted(list(todas_columnas)), key="precio_busqueda")
        
        busqueda = st.text_input("🔎 Buscar:", placeholder="Ej: cable cargador RN0200046BK8")
        
        if busqueda and len(busqueda) >= 2:
            with st.spinner("🔍 Buscando..."):
                precio_seleccionado = None if col_precio_consulta == "(No mostrar precio)" else col_precio_consulta
                resultados = buscar_en_catalogos_multiple(st.session_state.catalogos, busqueda, st.session_state.stocks, precio_seleccionado)
            
            if resultados:
                st.success(f"✅ {len(resultados)} resultados encontrados")
                
                for res in resultados:
                    if res['Stock_Total'] <= 0:
                        stock_icon = "🔴 Sin stock"
                    elif res['Stock_Total'] < 10:
                        stock_icon = f"🟠 Stock bajo: {res['Stock_Total']}"
                    else:
                        stock_icon = f"🟢 Stock disponible: {res['Stock_Total']}"
                    
                    stock_detalle = ""
                    for s in res['Stocks_Detalle']:
                        if s['stock'] > 0:
                            stock_detalle += f'<span class="stock-badge">📁 {s["origen"][:30]}: {s["stock"]}</span> '
                    
                    st.markdown(f"""
                    <div class="search-result-card">
                        <div>
                            <span class="search-sku">📦 {res['SKU']}</span><br>
                            <span class="search-desc">{res['Descripcion']}</span>
                            <span class="search-price">{f'S/. {res["Precio"]:,.2f}' if res["Precio"] else "💰 Sin precio"}</span>
                        </div>
                        <div class="search-stock">
                            {stock_icon}<br>
                            {stock_detalle}
                            <div style="font-size:0.7rem; color:#888; margin-top:5px;">📁 Catalogo: {res['Catalogo']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown("**➕ Agregar a cotizacion**")
                    with col2:
                        cantidad = st.number_input("Cant", min_value=0, max_value=999, value=0, key=f"add_{res['SKU']}", label_visibility="collapsed")
                        if cantidad > 0:
                            st.session_state.productos_seleccionados[res['SKU']] = st.session_state.productos_seleccionados.get(res['SKU'], 0) + cantidad
                    st.divider()
            else:
                st.warning("No se encontraron productos")
        
        if st.session_state.productos_seleccionados:
            st.markdown("---")
            st.markdown(f"### ✅ Productos seleccionados ({len(st.session_state.productos_seleccionados)})")
            
            seleccionados_lista = []
            for sku, cant in st.session_state.productos_seleccionados.items():
                stock_total, _ = buscar_stock(st.session_state.stocks, sku)
                seleccionados_lista.append({
                    'SKU': sku,
                    'Cantidad': cant,
                    'Stock disponible': stock_total,
                    'Estado': '⚠️ Stock insuficiente' if cant > stock_total else '✅ OK'
                })
            
            st.dataframe(pd.DataFrame(seleccionados_lista), use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Limpiar todo", use_container_width=True):
                    st.session_state.productos_seleccionados = {}
                    st.rerun()
            with col2:
                if st.button("📋 TRANSFERIR A COTIZACION", use_container_width=True, type="primary"):
                    st.session_state.skus_transferidos = st.session_state.productos_seleccionados.copy()
                    st.session_state.productos_seleccionados = {}
                    st.success(f"✅ {len(st.session_state.skus_transferidos)} productos transferidos!")
                    st.info("👉 Ve a la pestaña Cotizacion y haz clic en PROCESAR")
