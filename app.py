# ============================================
# TAB BUSCAR PRODUCTOS (CON BÚSQUEDA EXACTA)
# ============================================
with tab_buscar:
    st.markdown("### 🔍 Buscar Productos")
    
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
        
        # Selector de tipo de búsqueda
        tipo_busqueda = st.radio(
            "🎯 Tipo de búsqueda:",
            ["🔍 Exacta (palabras completas)", "📝 Parcial (contiene)"],
            horizontal=True,
            help="Exacta: busca la frase completa. Parcial: busca productos que contengan las palabras"
        )
        
        busqueda = st.text_input(
            "🔎 Buscar productos:", 
            placeholder="Ej: buds 6 play, cable, CN0900009WH8"
        )
        
        if busqueda and len(busqueda) >= 2:
            with st.spinner("🔍 Buscando productos..."):
                precio_seleccionado = None if col_precio_consulta == "(No mostrar precio)" else col_precio_consulta
                es_busqueda_exacta = "Exacta" in tipo_busqueda
                
                resultados_dict = {}
                
                # Preparar términos según el tipo de búsqueda
                if es_busqueda_exacta:
                    # Búsqueda exacta: usar la frase completa
                    terminos_busqueda = [busqueda.strip().upper()]
                else:
                    # Búsqueda parcial: separar por espacios
                    if ',' in busqueda:
                        terminos_busqueda = [t.strip().upper() for t in busqueda.split(',') if len(t.strip()) >= 2]
                    else:
                        terminos_busqueda = [t.strip().upper() for t in busqueda.split() if len(t.strip()) >= 2]
                    if not terminos_busqueda:
                        terminos_busqueda = [busqueda.upper()]
                
                for cat in st.session_state.catalogos:
                    df = cat['df']
                    col_sku = cat['col_sku']
                    col_desc = cat['col_desc']
                    
                    for term in terminos_busqueda:
                        if es_busqueda_exacta:
                            # Búsqueda exacta: coincidencia total en SKU o descripción
                            mask_sku = df[col_sku].astype(str).str.upper() == term
                            mask_desc = df[col_desc].astype(str).str.upper().str.contains(term, case=False, na=False, regex=False)
                            # Para descripción en búsqueda exacta, buscamos la frase completa
                            mask_desc = df[col_desc].astype(str).str.upper().str.contains(term, case=False, na=False, regex=False)
                        else:
                            # Búsqueda parcial: contiene la palabra
                            mask_sku = df[col_sku].astype(str).str.contains(term, case=False, na=False, regex=False)
                            mask_desc = df[col_desc].astype(str).str.contains(term, case=False, na=False, regex=False)
                        
                        for idx, row in df[mask_sku | mask_desc].iterrows():
                            sku = str(row[col_sku]).strip().upper()
                            
                            if sku in resultados_dict:
                                continue
                            
                            # Precio
                            precio = None
                            if precio_seleccionado and precio_seleccionado != "(No mostrar precio)":
                                if precio_seleccionado in df.columns:
                                    precio = corregir_numero(row[precio_seleccionado])
                                else:
                                    precio = 0
                            
                            # Stock
                            stock_total = 0
                            stocks_detalle = {}
                            
                            if st.session_state.stocks:
                                for stock in st.session_state.stocks:
                                    try:
                                        mask_stock = stock['df'][stock['col_sku']].astype(str).str.contains(sku, case=False, na=False, regex=False)
                                        if not stock['df'][mask_stock].empty:
                                            row_stock = stock['df'][mask_stock].iloc[0]
                                            cantidad = int(corregir_numero(row_stock[stock['col_stock']])) if stock['col_stock'] else 0
                                            stock_key = stock['nombre']
                                            stocks_detalle[stock_key] = stocks_detalle.get(stock_key, 0) + cantidad
                                            stock_total += cantidad
                                    except:
                                        pass
                            
                            resultados_dict[sku] = {
                                'SKU': sku,
                                'Descripción': str(row[col_desc])[:100],
                                'Catálogo': cat['nombre'],
                                'Precio': precio,
                                'Stock_Total': stock_total,
                                'Stocks_Detalle': stocks_detalle
                            }
                
                resultados = list(resultados_dict.values())
            
            if resultados:
                st.success(f"✅ {len(resultados)} resultados encontrados")
                
                for res in resultados:
                    # Stock status
                    if res['Stock_Total'] <= 0:
                        stock_icon = "🔴"
                        stock_text = "Sin stock"
                        stock_bg = "#FFCDD2"
                        stock_color = "#C62828"
                    elif res['Stock_Total'] < 10:
                        stock_icon = "🟠"
                        stock_text = f"Stock bajo: {res['Stock_Total']} uds"
                        stock_bg = "#FFF3E0"
                        stock_color = "#E65100"
                    else:
                        stock_icon = "🟢"
                        stock_text = f"Stock disponible: {res['Stock_Total']} uds"
                        stock_bg = "#C8E6C9"
                        stock_color = "#1B5E20"
                    
                    # Stock detalle
                    stock_detalle_html = ""
                    for origen, cantidad in res['Stocks_Detalle'].items():
                        if cantidad > 0:
                            nombre_corto = origen.split('[')[0].strip() if '[' in origen else origen
                            stock_detalle_html += f'<div style="margin: 2px 0;"><span style="background:#E8F5E9; padding:2px 8px; border-radius:12px; font-size:0.7rem;">📁 {nombre_corto}: {cantidad} uds</span></div>'
                    
                    # Precio
                    if res['Precio'] and res['Precio'] > 0:
                        precio_html = f'<span style="font-size:1.1rem; font-weight:bold; color:#66BB6A;">S/. {res["Precio"]:,.2f}</span>'
                    else:
                        precio_html = '<span style="color:#FF8F00;">⚠️ Sin precio en catálogo</span>'
                    
                    catalogo_origen = res['Catálogo'].split('[')[0].strip() if '[' in res['Catálogo'] else res['Catálogo']
                    
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
                        <div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid #eee;">
                            <div style="margin-bottom: 6px;">
                                <span style="background:{stock_bg}; padding:4px 12px; border-radius:20px; font-size:0.75rem; font-weight:600; color:{stock_color};">
                                    {stock_icon} {stock_text}
                                </span>
                            </div>
                            <div style="margin-top: 6px; font-size:0.75rem;">
                                {stock_detalle_html if stock_detalle_html else '<span style="color:#888;">No hay stock registrado</span>'}
                            </div>
                            <div style="margin-top: 6px; font-size:0.7rem; color:#888;">
                                📋 Catálogo: {catalogo_origen}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Botón para agregar
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"**➕ Agregar a la cotización**")
                    with col2:
                        cantidad = st.number_input(
                            "Cantidad",
                            min_value=0,
                            max_value=999,
                            value=0,
                            key=f"add_{res['SKU']}",
                            label_visibility="collapsed"
                        )
                    with col3:
                        if cantidad > 0:
                            if st.button("✓ Agregar", key=f"btn_{res['SKU']}"):
                                st.session_state.productos_seleccionados[res['SKU']] = st.session_state.productos_seleccionados.get(res['SKU'], 0) + cantidad
                                st.success(f"✅ {cantidad} x {res['SKU']} agregado")
                                st.rerun()
                    st.divider()
            else:
                st.warning("No se encontraron productos. Intenta con otros términos.")
        
        # Productos seleccionados
        if st.session_state.productos_seleccionados:
            st.markdown("---")
            st.markdown(f"### ✅ Productos seleccionados ({len(st.session_state.productos_seleccionados)})")
            
            seleccionados_lista = []
            for sku, cant in st.session_state.productos_seleccionados.items():
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
                    'Cantidad': cant,
                    'Stock': stock_total,
                    'Estado': '⚠️ Stock insuficiente' if cant > stock_total and stock_total > 0 else ('❌ Sin stock' if stock_total == 0 else '✅ OK')
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
