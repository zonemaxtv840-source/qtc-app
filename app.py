# Dentro del TAB 1, reemplaza el bloque de procesamiento (desde "if st.button" hasta el final del TAB 1)

if st.button("🚀 PROCESAR COTIZACIÓN", use_container_width=True, type="primary") and pedidos:
    with st.spinner("Procesando..."):
        resultados = []
        for pedido in pedidos:
            sku_original = pedido['sku']
            cant_solicitada = pedido['cantidad']
            
            # Limpiar SKU para búsqueda (eliminar espacios, caracteres extraños)
            sku_limpio = sku_original.strip().upper()
            
            # Buscar en catálogos de precios - búsqueda más flexible
            producto = None
            for catalogo in st.session_state.catalogos:
                df = catalogo['df']
                col_sku = catalogo['col_sku']
                col_desc = catalogo['col_desc']
                
                # Intentar coincidencia exacta primero
                mask_exacta = df[col_sku].astype(str).str.strip().str.upper() == sku_limpio
                if not df[mask_exacta].empty:
                    row = df[mask_exacta].iloc[0]
                    producto = {
                        'encontrado': True,
                        'catalogo': catalogo['nombre'],
                        'sku': str(row[col_sku]),
                        'descripcion': str(row[col_desc]),
                        'row': row,
                        'columnas_precio': catalogo['columnas_precio']
                    }
                    break
                
                # Si no, buscar coincidencia parcial (para casos donde el SKU tiene sufijos)
                mask_parcial = df[col_sku].astype(str).str.contains(sku_limpio, case=False, na=False, regex=False)
                if not df[mask_parcial].empty:
                    row = df[mask_parcial].iloc[0]
                    producto = {
                        'encontrado': True,
                        'catalogo': catalogo['nombre'],
                        'sku': str(row[col_sku]),
                        'descripcion': str(row[col_desc]),
                        'row': row,
                        'columnas_precio': catalogo['columnas_precio']
                    }
                    break
            
            # Buscar en stock
            stock_disponible = 0
            origen_stock = "Sin stock"
            for stock in st.session_state.stocks:
                mask_stock = stock['df'][stock['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False, regex=False)
                if not stock['df'][mask_stock].empty:
                    row_stock = stock['df'][mask_stock].iloc[0]
                    stock_disponible = int(corregir_numero(row_stock[stock['col_stock']])) if stock['col_stock'] else 0
                    origen_stock = stock['nombre']
                    break
            
            # Determinar estado
            if producto and stock_disponible > 0:
                # Tiene precio y stock
                precio = obtener_precio(producto['row'], producto['columnas_precio'], col_precio)
                estado = "✅ OK"
                color_estado = "green"
                descripcion = producto['descripcion'][:80]
                origen_precio = producto['catalogo']
                precio_valido = precio
                motivo_exclusion = None
                a_cotizar = min(cant_solicitada, stock_disponible)
                total = precio * a_cotizar
                
            elif producto and stock_disponible == 0:
                # Tiene precio pero NO tiene stock
                precio = obtener_precio(producto['row'], producto['columnas_precio'], col_precio)
                estado = "⚠️ Sin stock (tiene precio)"
                color_estado = "orange"
                descripcion = producto['descripcion'][:80]
                origen_precio = producto['catalogo']
                precio_valido = precio
                motivo_exclusion = "Sin stock disponible"
                a_cotizar = 0
                total = 0
                
            elif not producto and stock_disponible > 0:
                # NO tiene precio pero SÍ tiene stock
                estado = "⚠️ NO ESTÁ EN LISTA DE PRECIOS"
                color_estado = "orange"
                descripcion = f"Producto con stock ({stock_disponible} uds) pero sin precio en catálogo"
                precio_valido = 0
                origen_precio = "❌ No encontrado"
                motivo_exclusion = "No está en lista de precios"
                a_cotizar = 0
                total = 0
                
            else:
                # No tiene precio ni stock
                estado = "❌ No encontrado"
                color_estado = "red"
                descripcion = "Producto no existe en catálogos ni stock"
                precio_valido = 0
                origen_precio = "❌ No encontrado"
                stock_disponible = 0
                motivo_exclusion = "No encontrado en catálogo ni stock"
                a_cotizar = 0
                total = 0
            
            resultados.append({
                'id': sku_original,
                'SKU': sku_original,
                'Descripción': descripcion,
                'Precio': precio_valido,
                'Solicitado': cant_solicitada,
                'Stock_Disponible': stock_disponible,
                'A_Cotizar': a_cotizar,
                'Total': total,
                'Estado': estado,
                'Color_Estado': color_estado,
                'Origen_Precio': origen_precio if producto else "❌ Sin precio",
                'Origen_Stock': origen_stock,
                'Motivo_Exclusion': motivo_exclusion
            })
        
        st.session_state.resultados = resultados
