
2. **Columnas requeridas**:
- Debe tener una columna con códigos SKU (puede llamarse: SKU, COD, CODIGO, SAP)
- Debe tener columnas de precio (P. IR, P. BOX, P. VIP o PRECIO)
- Opcional: columna de descripción

3. **Proceso de carga**:
1. Haz clic en "Sube tus catálogos" arriba
2. Selecciona tu archivo CSV
3. El sistema detectará automáticamente las columnas
4. Verás un mensaje de éxito

### 💡 Tips:
- Para archivos Excel, el sistema mostrará todas las hojas disponibles
- Puedes cargar múltiples archivos a la vez
- Los archivos CSV deben tener codificación UTF-8 o Latin-1
""")
else:
# Mostrar catálogos cargados
with st.expander("📋 Catálogos cargados"):
cols = st.columns(3)
for i, cat in enumerate(st.session_state.catalogos):
 with cols[i % 3]:
     st.caption(f"✅ {cat['nombre'][:30]}")

# Selección de columna de precio
opciones_precio = set()
for cat in st.session_state.catalogos:
for col in cat['columnas_precio'].keys():
 opciones_precio.add(col)

if opciones_precio:
col_precio = st.selectbox(
 "💰 **Selecciona la columna de precio**",
 sorted(list(opciones_precio)),
 help="Elige qué lista de precios usar"
)
else:
col_precio = None
st.error("⚠️ No se detectaron columnas de precio en los catálogos")

st.markdown("---")

# Ingreso de productos
st.markdown("### 📝 Ingresa los productos a cotizar")
st.caption("💡 **Formato:** `SKU:CANTIDAD` (uno por línea) - Los SKUs duplicados se suman automáticamente")

if 'skus_transferidos' in st.session_state:
texto_defecto = "\n".join([f"{sku}:{cant}" for sku, cant in st.session_state.skus_transferidos.items()])
del st.session_state.skus_transferidos
else:
texto_defecto = ""

texto_skus = st.text_area(
"Productos", 
height=150, 
value=texto_defecto,
placeholder="Ejemplos:\nRN0200046BK8:5\nCN0900009WH8:2\nRN0200046BK8:3  (este se sumará con el primero)",
key="input_productos"
)

# Procesar pedidos
pedidos_dict = {}
if texto_skus:
for line in texto_skus.split('\n'):
 line = line.strip()
 if ':' in line:
     parts = line.split(':')
     if len(parts) == 2:
         try:
             sku = parts[0].strip().upper()
             cantidad = int(parts[1].strip())
             if cantidad > 0:
                 pedidos_dict[sku] = pedidos_dict.get(sku, 0) + cantidad
         except:
             st.warning(f"⚠️ Formato incorrecto: {line}")
 elif line:
     sku = line.strip().upper()
     pedidos_dict[sku] = pedidos_dict.get(sku, 0) + 1

pedidos = [{'sku': sku, 'cantidad': cant} for sku, cant in pedidos_dict.items()]

# Botón procesar
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
if st.button("🚀 **PROCESAR COTIZACIÓN**", use_container_width=True, type="primary") and pedidos:
 if not col_precio:
     st.error("❌ Selecciona una columna de precio primero")
 else:
     with st.spinner("🔍 Procesando..."):
         resultados = []
         advertencias_stock = []
         
         for pedido in pedidos:
             sku = pedido['sku']
             cant = pedido['cantidad']
             
             precio_info = buscar_precio(st.session_state.catalogos, sku, col_precio)
             
             if not precio_info['descripcion'] or precio_info['descripcion'] == '':
                 precio_info['descripcion'] = buscar_descripcion_en_stock(st.session_state.stocks, sku)
             
             if st.session_state.tipo_cotizacion == "XIAOMI":
                 stock_total, stock_detalle, stock_apri004, stock_yessica = buscar_stock_xiaomi(st.session_state.stocks, sku)
             else:
                 stock_total, stock_detalle = buscar_stock_general(st.session_state.stocks, sku)
                 stock_apri004 = 0
                 stock_yessica = 0
             
             # Validaciones de stock
             if cant > stock_total and stock_total > 0:
                 advertencias_stock.append(f"⚠️ **{sku}**: Stock insuficiente. Solicitado: {cant} | Disponible: {stock_total}")
                 badge_estado = "badge-warning"
                 estado_texto = "⚠️ Stock parcial"
             elif cant > stock_total and stock_total == 0:
                 advertencias_stock.append(f"❌ **{sku}**: Sin stock disponible")
                 badge_estado = "badge-danger"
                 estado_texto = "❌ Sin stock"
             else:
                 badge_estado = "badge-ok"
                 estado_texto = "✅ OK"
             
             # Badges de origen
             if st.session_state.tipo_cotizacion == "XIAOMI":
                 if stock_apri004 > 0 and stock_yessica > 0:
                     badge_origen = f'<span class="origin-badge origin-both">🟣 APRI.004: {stock_apri004} | 🔵 YESSICA: {stock_yessica}</span>'
                 elif stock_apri004 > 0:
                     badge_origen = f'<span class="origin-badge origin-apri004">🟣 APRI.004: {stock_apri004}</span>'
                 elif stock_yessica > 0:
                     badge_origen = f'<span class="origin-badge origin-yessica">🔵 YESSICA: {stock_yessica}</span>'
                 else:
                     badge_origen = '<span class="badge-danger">❌ Sin stock</span>'
             else:
                 badge_origen = f'<span class="origin-badge origin-both">🟢 Stock: {stock_total}</span>' if stock_total > 0 else '<span class="badge-danger">❌ Sin stock</span>'
             
             # Calcular cotización
             if precio_info['encontrado'] and stock_total > 0:
                 a_cotizar = min(cant, stock_total)
                 total = precio_info['precio'] * a_cotizar
             else:
                 a_cotizar = 0
                 total = 0
                 if not precio_info['encontrado'] and stock_total > 0:
                     badge_estado = "badge-warning"
                     estado_texto = "⚠️ Sin precio"
             
             resultados.append({
                 'SKU': sku,
                 'Descripción': precio_info['descripcion'][:80] if precio_info['descripcion'] else f"SKU: {sku}",
                 'Precio': precio_info['precio'],
                 'Pedido': cant,
                 'Stock': stock_total,
                 'Stock_APRI004': stock_apri004,
                 'Stock_YESSICA': stock_yessica,
                 'Origen': badge_origen,
                 'A Cotizar': a_cotizar,
                 'Total': total,
                 'Estado': estado_texto,
                 'Badge_Estado': badge_estado
             })
         
         # Mostrar advertencias
         for adv in advertencias_stock:
             if "⚠️" in adv:
                 st.warning(adv)
             else:
                 st.error(adv)
         
         st.session_state.resultados = resultados

# Mostrar resultados
if st.session_state.resultados:
st.markdown("---")
st.markdown("## 📊 Resultados de la Cotización")

# Tabla de resultados
for item in st.session_state.resultados:
 with st.container():
     col1, col2, col3, col4, col5 = st.columns([2, 3, 1, 1, 1.5])
     
     precio_str = f"S/. {item['Precio']:,.2f}" if item['Precio'] > 0 else "Sin precio"
     total_str = f"S/. {item['Total']:,.2f}"
     stock_clase = obtener_clase_stock(item['Stock'])
     stock_icono = obtener_icono_stock(item['Stock'])
     
     with col1:
         st.markdown(f"**📦 {item['SKU']}**")
     with col2:
         st.markdown(item['Descripción'][:60])
     with col3:
         st.markdown(f"💰 {precio_str}")
     with col4:
         st.markdown(f"📊 Pedido: {item['Pedido']}")
     with col5:
         st.markdown(f"<span class='{stock_clase}'>{stock_icono} Stock: {item['Stock']}</span>", unsafe_allow_html=True)
     
     st.markdown(f"<div style='margin-left: 10px;'>{item['Origen']}</div>", unsafe_allow_html=True)
     st.markdown(f"<div style='margin-left: 10px;'><strong>✏️ A Cotizar: {item['A Cotizar']} | Total: {total_str}</strong></div>", unsafe_allow_html=True)
     st.markdown(f"<div style='margin-left: 10px;'><span class='{item['Badge_Estado']}'>{item['Estado']}</span></div>", unsafe_allow_html=True)
     st.divider()

# Tabla editable
st.markdown("### ✏️ Ajustar cantidades")
st.caption("💡 Modifica las cantidades directamente - Los totales se actualizarán automáticamente")

df_ajuste = pd.DataFrame(st.session_state.resultados)
df_editor = df_ajuste[['SKU', 'Descripción', 'Precio', 'Stock', 'A Cotizar']].copy()
df_editor['Precio'] = df_editor['Precio'].apply(lambda x: f"S/. {x:,.2f}" if x > 0 else "Sin precio")

edited_df = st.data_editor(
 df_editor,
 column_config={
     "SKU": st.column_config.TextColumn("SKU", disabled=True),
     "Descripción": st.column_config.TextColumn("Descripción", disabled=True, width="large"),
     "Precio": st.column_config.TextColumn("Precio", disabled=True),
     "Stock": st.column_config.NumberColumn("Stock", disabled=True),
     "A Cotizar": st.column_config.NumberColumn("A Cotizar", min_value=0, step=1, required=True),
 },
 use_container_width=True,
 hide_index=True,
 key="ajuste_editor"
)

# Actualizar resultados
for idx, row in edited_df.iterrows():
 if idx < len(st.session_state.resultados):
     nueva_cant = row['A Cotizar']
     stock_disponible = st.session_state.resultados[idx]['Stock']
     
     if nueva_cant > stock_disponible and stock_disponible > 0:
         nueva_cant = stock_disponible
         st.warning(f"⚠️ **{st.session_state.resultados[idx]['SKU']}**: Ajustado a stock disponible ({stock_disponible})")
     
     st.session_state.resultados[idx]['A Cotizar'] = nueva_cant
     if st.session_state.resultados[idx]['Precio'] > 0:
         st.session_state.resultados[idx]['Total'] = st.session_state.resultados[idx]['Precio'] * nueva_cant
         st.session_state.resultados[idx]['Estado'] = "✅ OK" if nueva_cant > 0 else "⚠️ Sin stock"
         st.session_state.resultados[idx]['Badge_Estado'] = "badge-ok" if nueva_cant > 0 else "badge-warning"
     else:
         st.session_state.resultados[idx]['Total'] = 0

# Resumen
items_validos = [r for r in st.session_state.resultados if r['A Cotizar'] > 0 and r['Precio'] > 0]
items_con_issues = [r for r in st.session_state.resultados if r['A Cotizar'] == 0 or r['Precio'] == 0]
total_general = sum(r['Total'] for r in items_validos)

# Métricas
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
 st.markdown(f"""
 <div class="metric-premium">
     <div class="label">✅ Productos a cotizar</div>
     <div class="value">{len(items_validos)}</div>
 </div>
 """, unsafe_allow_html=True)
with col_m2:
 st.markdown(f"""
 <div class="metric-premium">
     <div class="label">💰 Total</div>
     <div class="value">S/. {total_general:,.2f}</div>
 </div>
 """, unsafe_allow_html=True)
with col_m3:
 st.markdown(f"""
 <div class="metric-premium">
     <div class="label">⚠️ Excluidos</div>
     <div class="value">{len(items_con_issues)}</div>
 </div>
 """, unsafe_allow_html=True)

# Generar cotización
if items_validos:
 st.markdown("---")
 st.markdown("### 📥 Generar Cotización")
 
 col_cli1, col_cli2 = st.columns(2)
 with col_cli1:
     cliente = st.text_input("🏢 **Nombre del Cliente**", "CLIENTE NUEVO", key="cliente_nombre")
 with col_cli2:
     ruc_cliente = st.text_input("📋 **RUC/DNI**", "-", key="cliente_ruc")
 
 if st.button("📥 **GENERAR EXCEL**", use_container_width=True, type="primary"):
     items_excel = [{'sku': r['SKU'], 'desc': r['Descripción'], 'cant': r['A Cotizar'], 'p_u': r['Precio'], 'total': r['Total']} for r in items_validos]
     excel = generar_excel(items_excel, cliente, ruc_cliente)
     st.download_button(
         "💾 **DESCARGAR COTIZACIÓN**", 
         data=excel, 
         file_name=f"Cotizacion_{cliente}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", 
         use_container_width=True, 
         key="download_btn"
     )
     st.session_state.cotizaciones += 1
     st.session_state.total_prods = len(items_validos)
     st.balloons()
     st.success("✅ **¡Cotización generada exitosamente!**")

# ============================================
# TAB BUSCAR PRODUCTOS
# ============================================
with tab_buscar:
st.markdown("## 🔍 Buscador de Productos")
st.caption("💡 Busca por SKU o descripción - Encuentra precios y stock en tiempo real")

if not st.session_state.catalogos:
st.info("📢 Primero carga catálogos en la pestaña 'Cotización'")
else:
opciones_precio_buscar = set()
for cat in st.session_state.catalogos:
for col in cat['columnas_precio'].keys():
 opciones_precio_buscar.add(col)

col_precio_consulta = st.selectbox(
"💰 **Mostrar precios en columna:**",
options=["(No mostrar precio)"] + sorted(list(opciones_precio_buscar)),
key="precio_busqueda"
)

busqueda = st.text_input(
"🔎 **Buscar producto:**", 
placeholder="Ej: cable cargador o RN0200046BK8",
help="Puedes buscar por SKU, descripción o palabras clave"
)

if busqueda and len(busqueda) >= 2:
with st.spinner("🔍 Buscando..."):
 precio_seleccionado = None if col_precio_consulta == "(No mostrar precio)" else col_precio_consulta
 resultados = buscar_en_catalogos(
     st.session_state.catalogos, 
     busqueda, 
     st.session_state.stocks, 
     precio_seleccionado,
     st.session_state.tipo_cotizacion
 )

if resultados:
 st.success(f"✅ **{len(resultados)} productos encontrados**")
 
 for res in resultados:
     with st.container():
         st.markdown(f"""
         <div class="modern-card fade-in">
             <div style="display: flex; justify-content: space-between; align-items: start;">
                 <div>
                     <h4 style="margin: 0; color: #1B5E20;">📦 {res['SKU']}</h4>
                     <p style="margin: 5px 0; color: #666;">{res['Descripcion']}</p>
                     <p style="margin: 5px 0; font-weight: bold; color: #4CAF50;">
                         {f'S/. {res["Precio"]:,.2f}' if res["Precio"] else "💰 Sin precio"}
                     </p>
                 </div>
                 <div>
                     <span class="{obtener_clase_stock(res['Stock_Total'])}">
                         {obtener_icono_stock(res['Stock_Total'])} Stock: {res['Stock_Total']}
                     </span>
                 </div>
             </div>
         </div>
         """, unsafe_allow_html=True)
         
         col1, col2 = st.columns([3, 1])
         with col1:
             st.markdown("**➕ Agregar a cotización**")
         with col2:
             cantidad = st.number_input(
                 "Cantidad", 
                 min_value=0, 
                 max_value=999, 
                 value=0, 
                 key=f"add_{res['SKU']}", 
                 label_visibility="collapsed"
             )
             if cantidad > 0:
                 st.session_state.productos_seleccionados[res['SKU']] = \
                     st.session_state.productos_seleccionados.get(res['SKU'], 0) + cantidad
                 st.success(f"✅ {cantidad} unidad(es) agregadas")
         st.divider()
else:
 st.warning("😕 No se encontraron productos con ese término")

# Mostrar productos seleccionados
if st.session_state.productos_seleccionados:
st.markdown("---")
st.markdown(f"## ✅ Productos Seleccionados ({len(st.session_state.productos_seleccionados)})")

seleccionados_lista = []
for sku, cant in st.session_state.productos_seleccionados.items():
 if st.session_state.tipo_cotizacion == "XIAOMI":
     stock_total, _, _, _ = buscar_stock_xiaomi(st.session_state.stocks, sku)
 else:
     stock_total, _ = buscar_stock_general(st.session_state.stocks, sku)
 seleccionados_lista.append({'SKU': sku, 'Cantidad': cant, 'Stock disponible': stock_total})

st.dataframe(pd.DataFrame(seleccionados_lista), use_container_width=True)

col1, col2 = st.columns(2)
with col1:
 if st.button("🗑️ **Limpiar todo**", use_container_width=True):
     st.session_state.productos_seleccionados = {}
     st.rerun()
with col2:
 if st.button("📋 **TRANSFERIR A COTIZACIÓN**", use_container_width=True, type="primary"):
     st.session_state.skus_transferidos = st.session_state.productos_seleccionados.copy()
     st.session_state.productos_seleccionados = {}
     st.success(f"✅ **{len(st.session_state.skus_transferidos)} productos transferidos exitosamente!**")
     st.info("👉 Ve a la pestaña 'Cotización' y haz clic en PROCESAR")

# ============================================
# TAB DASHBOARD
# ============================================
with tab_dashboard:
st.markdown("## 📊 Dashboard de Control")

# Métricas principales
col1, col2, col3, col4 = st.columns(4)
with col1:
st.markdown(f"""
<div class="metric-premium">
<div class="label">📄 Cotizaciones</div>
<div class="value">{st.session_state.get('cotizaciones', 0)}</div>
</div>
""", unsafe_allow_html=True)
with col2:
st.markdown(f"""
<div class="metric-premium">
<div class="label">🌿 Productos</div>
<div class="value">{st.session_state.get('total_prods', 0)}</div>
</div>
""", unsafe_allow_html=True)
with col3:
st.markdown(f"""
<div class="metric-premium">
<div class="label">📚 Catálogos</div>
<div class="value">{len(st.session_state.get('catalogos', []))}</div>
</div>
""", unsafe_allow_html=True)
with col4:
st.markdown(f"""
<div class="metric-premium">
<div class="label">📦 Stocks</div>
<div class="value">{len(st.session_state.get('stocks', []))}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Detalle de catálogos
st.markdown("### 📋 Catálogos Cargados")
if st.session_state.get('catalogos'):
for cat in st.session_state.catalogos:
st.markdown(f"✅ **{cat['nombre']}**")
else:
st.info("No hay catálogos cargados")

st.markdown("---")

# Detalle de stocks
st.markdown("### 📋 Stocks Cargados")
if st.session_state.get('stocks'):
for stock in st.session_state.stocks:
st.markdown(f"📄 **{stock['nombre']}**")
else:
st.info("No hay stocks cargados")

st.markdown("---")

# Reglas actuales
st.markdown("### 🎯 Reglas de Negocio Activas")
if st.session_state.tipo_cotizacion == "XIAOMI":
st.success("""
**🔋 Modo XIAOMI Activo**
- 📦 Stock en **APRI.004**: Stock físico disponible
- 📋 Stock en **YESSICA**: Stock apartado (también disponible)
- ➕ **Stock Total** = APRI.004 + YESSICA
""")
else:
st.info("""
**💼 Modo GENERAL Activo**
- 📦 Stock en **APRI.001**: Stock general
- ✅ Un solo origen de stock
""")

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem;">
<p style="color: #666;">💚 <strong>QTC Smart Sales Pro</strong> - Sistema Profesional de Cotización</p>
<p style="color: #999; font-size: 0.8rem;">© 2024 - Todos los derechos reservados</p>
</div>
""", unsafe_allow_html=True)
