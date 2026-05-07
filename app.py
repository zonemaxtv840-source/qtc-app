            # ============================================
            # AJUSTE DE CANTIDADES - TABLA EDITABLE
            # ============================================
            st.markdown("---")
            st.markdown("### ✏️ Ajustar cantidades")
            
            # Preparar datos
            df_ajuste = pd.DataFrame([{
                'SKU': item['SKU'],
                'Descripción': item['Descripción'][:50],
                'Precio': item['Precio'],
                'Stock': item['Stock'],
                'A Cotizar': item['A Cotizar'],
            } for item in st.session_state.resultados])
            
            # Editor editable
            edited_df = st.data_editor(
                df_ajuste,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SKU": st.column_config.TextColumn("SKU", width="small", disabled=True),
                    "Descripción": st.column_config.TextColumn("Descripción", width="large", disabled=True),
                    "Precio": st.column_config.NumberColumn("Precio (S/.)", width="small", disabled=True),
                    "Stock": st.column_config.NumberColumn("Stock", width="small", disabled=True),
                    "A Cotizar": st.column_config.NumberColumn("A Cotizar", width="small", min_value=0, max_value=9999, step=1),
                },
                num_rows="fixed"
            )
            
            # Actualizar
            for i, item in enumerate(st.session_state.resultados):
                item['A Cotizar'] = edited_df.iloc[i]['A Cotizar']
                item['Total'] = item['Precio'] * item['A Cotizar']
            
            # Resumen
            items_validos = [r for r in st.session_state.resultados if r['A Cotizar'] > 0 and r['Precio'] > 0]
            total_general = sum(r['Total'] for r in items_validos)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("✅ A cotizar", len(items_validos))
            col2.metric("💰 Total", f"S/. {total_general:,.2f}")
            col3.metric("⚠️ Excluidos", len(st.session_state.resultados) - len(items_validos))
            
            # ============================================
            # REPORTE DE PRODUCTOS SIN PRECIO
            # ============================================
            sin_precio = [r for r in st.session_state.resultados if r['Estado'] == "⚠️ Sin precio" and r['Stock'] > 0]
            
            if sin_precio:
                st.markdown("---")
                
                for sp in sin_precio:
                    st.markdown(f"""
                    <div style="background: #FFF8E1; border-left: 4px solid #FFC107; padding: 0.8rem; margin: 0.5rem 0; border-radius: 8px;">
                        <b>📦 {sp['SKU']}</b><br>
                        {sp['Descripción']}<br>
                        <span style="color: #E65100;">🚫 Motivo: Sin precio registrado en el catálogo</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                if st.session_state.resultados:
                    st.success("✅ Todos los productos tienen precio registrado")
            
            # ============================================
            # GENERAR COTIZACIÓN
            # ============================================
            if items_validos:
                st.markdown("---")
                st.markdown("### 📥 Generar Cotización")
                
                cliente = st.text_input("🏢 Cliente", "CLIENTE NUEVO")
                ruc_cliente = st.text_input("📋 RUC/DNI", "-")
                
                if st.button("📥 GENERAR EXCEL", use_container_width=True, type="primary"):
                    items_excel = [{'sku': r['SKU'], 'desc': r['Descripción'], 'cant': r['A Cotizar'], 'p_u': r['Precio'], 'total': r['Total']} for r in items_validos]
                    excel = generar_excel(items_excel, cliente, ruc_cliente)
                    st.download_button("💾 DESCARGAR", data=excel, file_name=f"Cotizacion_{cliente}.xlsx", use_container_width=True)
                    st.session_state.cotizaciones += 1
                    st.session_state.total_prods = len(items_validos)
                    st.balloons()
                    st.success("✅ Cotización generada")
