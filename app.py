# ============================================
# TAB BUSCAR PRODUCTOS (CORREGIDO)
# ============================================
with tab_buscar:
    st.markdown("### 🔍 Buscar Productos")
    st.markdown("💡 **Busca por SKU o descripción** - Separa términos con comas o espacios para búsqueda múltiple")
    
    if not st.session_state.catalogos:
        st.warning("🌿 Primero carga catálogos en la pestaña 'Cotización'")
    else:
        # Selector de precio para mostrar
        todas_columnas = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio']:
                todas_columnas.add(col)
        
        col_precio_consulta = st.selectbox(
            "💰 Mostrar precios en columna:",
            options=["(No mostrar precio)"] + sorted(list(todas_columnas)),
            key="precio_busqueda"
        )
        
        # Campo de búsqueda unificado
        busqueda = st.text_input(
            "🔎 Buscar productos:", 
            placeholder="Escribe SKU o descripción... Ej: cable, cargador, CN0900009WH8"
        )
        
        if busqueda and len(busqueda) >= 2:
            with st.spinner("🔍 Buscando productos y consultando stock..."):
                precio_seleccionado = None if col_precio_consulta == "(No mostrar precio)" else col_precio_consulta
                
                # Búsqueda en catálogos
                resultados_dict = {}
                
                # Separar términos (soporta búsqueda múltiple)
                if ',' in busqueda:
                    terminos = [t.strip() for t in busqueda.split(',')]
                else:
                    terminos = [t.strip() for t in busqueda.split() if len(t.strip()) >= 2]
                
                for cat in st.session_state.catalogos:
                    df = cat['df']
                    for term in terminos:
                        mask_sku = df[cat['col_sku']].astype(str).str.contains(term, case=False, na=False, regex=False)
                        mask_desc = df[cat['col_desc']].astype(str).str.contains(term, case=False, na=False, regex=False)
                        
                        for idx, row in df[mask_sku | mask_desc].iterrows():
                            sku = str(row[cat['col_sku']])
                            
                            if sku not in resultados_dict:
                                # Precio
                                precio = None
                                if precio_seleccionado and precio_seleccionado != "(No mostrar precio)":
                                    if precio_seleccionado in df.columns:
                                        precio = corregir_numero(row[precio_seleccionado])
                                    else:
                                        precio = 0
                                
                                # Stock - BUSCAR EN TODOS LOS STOCKS
                                stock_total = 0
                                stocks_detalle = []
                                
                                if st.session_state.stocks:
                                    for stock in st.session_state.stocks:
                                        try:
                                            mask_stock = stock['df'][stock['col_sku']].astype(str).str.contains(sku, case=False, na=False, regex=False)
                                            if not stock['df'][mask_stock].empty:
                                                row_stock = stock['df'][mask_stock].iloc[0]
                                                cantidad = int(corregir_numero(row_stock[stock['col_stock']])) if stock['col_stock'] else 0
                                                stocks_detalle.append({
                                                    'origen': stock['nombre'],
                                                    'stock': cantidad
                                                })
                                                stock_total += cantidad
                                        except:
                                            pass
                                
                                resultados_dict[sku] = {
                                    'SKU': sku,
                                    'Descripción': str(row[cat['col_desc']])[:100],
                                    'Catálogo': cat['nombre'],
                                    'Precio': precio,
                                    'Stock_Total': stock_total,
                                    'Stocks_Detalle': stocks_detalle
                                }
                
                resultados = list(resultados_dict.values())
            
            if resultados:
                st.success(f"✅ {len(resultados)} resultados encontrados")
                
                for res in resultados:
                    # Determinar clase de stock
                    if res['Stock_Total'] <= 0:
                        stock_icon = "🔴"
                        stock_text = "Sin stock"
                        stock_bg = "#FFCDD2"
                    elif res['Stock_Total'] < 10:
                        stock_icon = "🟠"
                        stock_text = f"Stock bajo: {res['Stock_Total']} uds"
                        stock_bg = "#FFF3E0"
                    else:
                        stock_icon = "🟢"
                        stock_text = f"Stock disponible: {res['Stock_Total']} uds"
                        stock_bg = "#C8E6C9"
                    
                    # Construir detalles de stock por hoja
                    stock_detalle_html = ""
                    for s in res['Stocks_Detalle']:
                        if s['stock'] > 0:
                            stock_detalle_html += f'<span style="background:#E8F5E9; padding:2px 8px; border-radius:12px; font-size:0.7rem; margin-right:5px;">📁 {s["origen"][:35]}: {s["stock"]} uds</span> '
                    
                    # Precio
                    precio_html = f'<span style="font-size:1rem; font-weight:bold; color:#66BB6A;">S/. {res["Precio"]:,.2f}</span>' if res['Precio'] else '<span style="color:#FF8F00;">⚠️ Sin precio</span>'
                    
                    st.markdown(f"""
                    <div style="background: white; border-radius: 12px; padding: 1rem; margin: 0.5rem 0; border-left: 4px solid #66BB6A; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <span style="font-size:1rem; font-weight: bold; font-family: monospace; color: #2E7D32;">📦 {res['SKU']}</span><br>
                                <span style="font-size:0.85rem; color: #555;">{res['Descripción']}</span>
                            </div>
                            <div>
                                {precio_html}
                            </div>
                        </div>
                        <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #eee;">
                            <span style="background:{stock_bg}; padding:4px 12px; border-radius:20px; font-size:0.75rem; font-weight:600;">
                                {stock_icon} {stock_text}
                            </span>
                            <div style="margin-top: 6px;">
                                {stock_detalle_html}
                            </div>
                            <span style="font-size:0.7rem; color:#888;">📁 Catálogo: {res['Catálogo'][:50]}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Botón para agregar
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**➕ Agregar a cotización**")
                    with col2:
                        cantidad = st.number_input(
                            "Cant",
                            min_value=0,
                            max_value=999,
                            value=0,
                            key=f"add_{res['SKU']}",
                            label_visibility="collapsed"
                        )
                        if cantidad > 0:
                            st.session_state.productos_seleccionados[res['SKU']] = st.session_state.productos_seleccionados.get(res['SKU'], 0) + cantidad
                    st.divider()
            else:
                st.warning("No se encontraron productos. Intenta con otros términos.")
        
        # Mostrar productos seleccionados
        if st.session_state.productos_seleccionados:
            st.markdown("---")
            st.markdown(f"### ✅ Productos seleccionados ({len(st.session_state.productos_seleccionados)})")
            
            # Mostrar tabla de seleccionados con resumen de stock
            seleccionados_lista = []
            for sku, cant in st.session_state.productos_seleccionados.items():
                # Obtener stock
                stock_total = 0
                for stock in st.session_state.stocks:
                    try:
                        mask_stock = stock['df'][stock['col_sku']].astype(str).str.contains(sku, case=False, na=False, regex=False)
                        if not stock['df'][mask_stock].empty:
                            row_stock = stock['df'][mask_stock].iloc[0]
                            cantidad = int(corregir_numero(row_stock[stock['col_stock']])) if stock['col_stock'] else 0
                            stock_total += cantidad
                    except:
                        pass
                
                seleccionados_lista.append({
                    'SKU': sku,
                    'Cantidad a cotizar': cant,
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
                if st.button("📋 TRANSFERIR A COTIZACIÓN", use_container_width=True, type="primary"):
                    st.session_state.skus_transferidos = st.session_state.productos_seleccionados.copy()
                    st.session_state.productos_seleccionados = {}
                    st.success(f"✅ {len(st.session_state.skus_transferidos)} productos transferidos!")
                    st.info("👉 Ve a la pestaña 'Cotización' y haz clic en PROCESAR")
