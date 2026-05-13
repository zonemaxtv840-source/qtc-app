import streamlit as st
import pandas as pd
import re
import io
from datetime import datetime
from PIL import Image
import warnings
from typing import List, Dict, Optional, Tuple

warnings.filterwarnings('ignore')

# ============================================
# FUNCIONES DE LIMPIEZA (DE TU SCRIPT V16)
# ============================================

def corregir_numero(valor):
    """Misma función que funciona en tu script V16"""
    if pd.isna(valor) or valor == "" or str(valor).strip() == "0":
        return 0.0
    s = str(valor).upper().replace('S/', '').replace('$', '').replace(' ', '').strip()
    if ',' in s and '.' in s:
        s = s.replace(',', '')
    elif ',' in s:
        partes = s.split(',')
        if len(partes[-1]) <= 2:
            s = s.replace(',', '.')
        else:
            s = s.replace(',', '')
    s = re.sub(r'[^\d.]', '', s)
    try:
        return float(s)
    except:
        return 0.0

def detectar_columna(df, terminos_busqueda, fallback=0):
    """Detecta columna por términos de búsqueda - IGUAL que tu script"""
    for col in df.columns:
        col_upper = str(col).upper()
        for termino in terminos_busqueda:
            if termino.upper() in col_upper:
                return col
    return df.columns[fallback] if isinstance(fallback, int) else fallback

# ============================================
# CARGA DE ARCHIVOS
# ============================================

def cargar_archivo(uploaded_file) -> Optional[pd.DataFrame]:
    """Carga archivo Excel o CSV y limpia cabeceras"""
    if uploaded_file is None:
        return None
    
    nombre = uploaded_file.name.lower()
    try:
        if nombre.endswith('.csv'):
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except:
                df = pd.read_csv(uploaded_file, encoding='latin-1')
        else:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        # Limpiar cabeceras (buscar fila con SKU)
        for i in range(min(15, len(df))):
            fila_texto = [str(x).upper() for x in df.iloc[i].values]
            if any(h in item for h in ['SKU', 'MODEL', 'ARTICULO', 'NUMERO', 'SAP', 'CODIGO'] for item in fila_texto):
                df.columns = [str(c).strip() for c in df.iloc[i]]
                df = df.iloc[i+1:].reset_index(drop=True)
                break
        
        df.columns = [str(c).strip() for c in df.columns]
        return df.fillna(0)
    except Exception as e:
        st.error(f"Error cargando {uploaded_file.name}: {str(e)[:100]}")
        return None

# ============================================
# MOTOR DE BÚSQUEDA (IGUAL A TU SCRIPT)
# ============================================

def buscar_productos(df_precios, df_stock, skus_buscar, col_precio_seleccionada, modo_xiaomi=True):
    """
    Motor de búsqueda IDÉNTICO a tu script V16 pero adaptado a Streamlit
    """
    # Detectar columnas
    col_sku_p = detectar_columna(df_precios, ['SKU', 'SAP', 'CODIGO SAP', 'CODIGO', 'NUMERO'], 0)
    col_desc_p = detectar_columna(df_precios, ['DESCRIPCION', 'GOODS', 'NOMBRE PRODUCTO', 'DESC'], 1)
    col_sku_s = detectar_columna(df_stock, ['NUMERO', 'SKU', 'ARTICULO', 'CODIGO'], 0)
    
    # Detectar columnas de stock
    col_stock = None
    col_apartado = None
    col_disponible = None
    
    for col in df_stock.columns:
        col_upper = str(col).upper()
        if 'STOCK' in col_upper or 'EN STOCK' in col_upper:
            if col_stock is None:
                col_stock = col
        if 'APARTADO' in col_upper or 'COMPROMETIDO' in col_upper:
            col_apartado = col
        if 'DISPONIBLE' in col_upper:
            col_disponible = col
    
    # Si no encuentra columna de stock, usa la primera columna numérica
    if col_stock is None:
        for col in df_stock.columns:
            if df_stock[col].dtype in ['int64', 'float64']:
                col_stock = col
                break
    
    # Para modo XIAOMI, buscar también en APRI.001 si no hay stock
    mostrar_nota_apri001 = False
    
    resultados = []
    advertencias = []
    
    for sku, cantidad in skus_buscar.items():
        sku_limpio = str(sku).strip().upper()
        
        # Buscar en catálogo (búsqueda flexible como en tu script)
        mask = df_precios[col_sku_p].astype(str).str.contains(re.escape(sku_limpio), case=False, na=False)
        variantes = df_precios[mask]
        
        if variantes.empty:
            advertencias.append(f"❌ **{sku}**: No encontrado en catálogo")
            resultados.append({
                'SKU': sku,
                'Descripción': 'NO ENCONTRADO',
                'Precio': 0,
                'Pedido': cantidad,
                'Stock': 0,
                'Stock_Detalle': {},
                'A Cotizar': 0,
                'Total': 0,
                'Estado': '❌ No encontrado',
                'Sin_Precio': True,
                'Sin_Stock': True
            })
            continue
        
        # Procesar cada variante encontrada
        for _, fila in variantes.iterrows():
            sku_real = str(fila[col_sku_p]).strip().upper()
            descripcion = str(fila[col_desc_p])[:100] if col_desc_p in fila else sku_real
            
            # Obtener precio
            precio = corregir_numero(fila.get(col_precio_seleccionada, 0))
            
            # Buscar stock
            mask_stock = df_stock[col_sku_s].astype(str).str.strip() == sku_real
            stock_info = {}
            
            if mask_stock.any():
                row_stock = df_stock[mask_stock].iloc[0]
                
                # Stock total
                if col_stock:
                    stock_info['Almacen'] = int(corregir_numero(row_stock.get(col_stock, 0)))
                else:
                    stock_info['Almacen'] = 0
                
                # Apartado/Comprometido
                if col_apartado:
                    stock_info['Apartado'] = int(corregir_numero(row_stock.get(col_apartado, 0)))
                else:
                    stock_info['Apartado'] = 0
                
                # Disponible real
                if col_disponible:
                    stock_info['Disponible'] = int(corregir_numero(row_stock.get(col_disponible, 0)))
                else:
                    # Calcular disponible = Almacen - Apartado
                    stock_info['Disponible'] = max(0, stock_info['Almacen'] - stock_info['Apartado'])
            else:
                stock_info = {'Almacen': 0, 'Apartado': 0, 'Disponible': 0}
                
                # Para modo XIAOMI, verificar si hay nota de APRI.001 (esto se hace después)
                if modo_xiaomi and 'APRI.001' in str(df_stock):
                    mostrar_nota_apri001 = True
            
            stock_disponible = stock_info['Disponible']
            sin_precio = precio == 0
            sin_stock = stock_disponible == 0
            
            # Determinar estado y cantidad a cotizar
            if sin_precio and sin_stock:
                estado = "❌ Sin precio y sin stock"
                a_cotizar = 0
                total = 0
                advertencias.append(f"❌ **{sku_real}**: Sin precio y sin stock")
            elif sin_precio:
                estado = "⚠️ Sin precio - Puedes cotizar a 0"
                a_cotizar = cantidad if cantidad > 0 else 0
                total = 0
                advertencias.append(f"⚠️ **{sku_real}**: Sin precio en catálogo")
            elif sin_stock:
                estado = "❌ Sin stock disponible"
                a_cotizar = 0
                total = 0
                advertencias.append(f"❌ **{sku_real}**: Sin stock disponible (Disponible: 0)")
            elif cantidad > stock_disponible:
                a_cotizar = stock_disponible
                total = precio * a_cotizar
                estado = f"⚠️ Stock insuficiente (solo {stock_disponible})"
                advertencias.append(f"⚠️ **{sku_real}**: Stock insuficiente. Pedido: {cantidad} | Disponible: {stock_disponible}")
            else:
                a_cotizar = cantidad
                total = precio * a_cotizar
                estado = "✅ OK"
            
            resultados.append({
                'SKU': sku_real,
                'Descripción': descripcion,
                'Precio': precio,
                'Pedido': cantidad,
                'Stock': stock_disponible,
                'Stock_Almacen': stock_info['Almacen'],
                'Stock_Apartado': stock_info['Apartado'],
                'A Cotizar': a_cotizar,
                'Total': total,
                'Estado': estado,
                'Sin_Precio': sin_precio,
                'Sin_Stock': sin_stock
            })
            break  # Solo tomar la primera variante encontrada
    
    return resultados, advertencias, mostrar_nota_apri001

# ============================================
# GENERAR EXCEL
# ============================================

def generar_excel(items: List[Dict], cliente: str, ruc: str) -> bytes:
    """Genera Excel profesional"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_excel = pd.DataFrame([{
            'sku': item['SKU'],
            'desc': item['Descripción'],
            'cant': item['A Cotizar'],
            'p_u': item['Precio'],
            'total': item['Total']
        } for item in items if item['A Cotizar'] > 0])
        
        df_excel.to_excel(writer, sheet_name='Cotizacion', index=False, startrow=5)
        
        workbook = writer.book
        ws = writer.sheets['Cotizacion']
        
        # Formatos
        fmt_header = workbook.add_format({'bg_color': '#F79646', 'bold': True, 'border': 1, 'align': 'center'})
        fmt_money = workbook.add_format({'num_format': '"S/." #,##0.00', 'border': 1, 'align': 'right'})
        fmt_border = workbook.add_format({'border': 1})
        fmt_bold = workbook.add_format({'bold': True})
        
        # Columnas
        ws.set_column('A:A', 20)
        ws.set_column('B:B', 75)
        ws.set_column('C:C', 12)
        ws.set_column('D:D', 15)
        ws.set_column('E:E', 15)
        
        # Encabezados
        ws.write('A1', 'FECHA:', fmt_bold)
        ws.write('B1', datetime.now().strftime("%d/%m/%Y"))
        ws.write('A2', 'CLIENTE:', fmt_bold)
        ws.write('B2', cliente.upper())
        ws.write('A3', 'RUC:', fmt_bold)
        ws.write('B3', ruc)
        
        ws.merge_range('F1:H1', 'DATOS BANCARIOS', fmt_header)
        ws.write('F2', 'BBVA SOLES:', workbook.add_format({'font_color': 'red', 'bold': True, 'border': 1}))
        ws.write('G2', '0011-0616-0100012617', fmt_border)
        
        # Tabla
        headers = ['Código SAP', 'Descripción', 'Cantidad', 'Precio Unit.', 'Total']
        for i, header in enumerate(headers):
            ws.write(5, i, header, fmt_header)
        
        for row_idx, item in enumerate(df_excel.to_dict('records')):
            ws.write_row(row_idx + 6, 0, [item['sku'], item['desc'], item['cant'], item['p_u'], item['total']], fmt_border)
            ws.write(row_idx + 6, 3, item['p_u'], fmt_money)
            ws.write(row_idx + 6, 4, item['total'], fmt_money)
        
        total_row = len(df_excel) + 6
        ws.write(total_row, 3, 'TOTAL S/.', fmt_header)
        ws.write(total_row, 4, sum(item['total'] for item in df_excel.to_dict('records')), fmt_money)
    
    return output.getvalue()

# ============================================
# CONFIGURACIÓN STREAMLIT
# ============================================

st.set_page_config(page_title="QTC Smart Sales Pro", page_icon="💼", layout="wide")

# CSS para mejor visualización
st.markdown("""
<style>
.badge-ok { background-color: #C8E6C9; color: #1B5E20; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
.badge-warning { background-color: #FFF3E0; color: #E65100; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
.badge-danger { background-color: #FFCDD2; color: #C62828; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
.nota-apri001 { background-color: #FFF9C4; color: #F57F17; padding: 8px 15px; border-radius: 10px; border-left: 4px solid #F57F17; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'catalogo_df' not in st.session_state:
    st.session_state.catalogo_df = None
if 'stock_df' not in st.session_state:
    st.session_state.stock_df = None
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 'skus_pedido' not in st.session_state:
    st.session_state.skus_pedido = {}

# ============================================
# SIDEBAR - CARGA DE ARCHIVOS
# ============================================

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    st.title("QTC Smart Sales")
    
    st.markdown("---")
    st.markdown("### 📂 1. Catálogo de Precios")
    archivo_catalogo = st.file_uploader("Excel o CSV", type=['xlsx', 'xls', 'csv'], key="catalogo")
    if archivo_catalogo:
        df = cargar_archivo(archivo_catalogo)
        if df is not None:
            st.session_state.catalogo_df = df
            st.success(f"✅ {archivo_catalogo.name}")
            st.caption(f"📊 {len(df)} productos | {len(df.columns)} columnas")
    
    st.markdown("---")
    st.markdown("### 📦 2. Reporte de Stock")
    archivo_stock = st.file_uploader("Excel", type=['xlsx', 'xls'], key="stock")
    if archivo_stock:
        df = cargar_archivo(archivo_stock)
        if df is not None:
            st.session_state.stock_df = df
            st.success(f"✅ {archivo_stock.name}")
            st.caption(f"📊 {len(df)} registros")
    
    st.markdown("---")
    st.markdown("### ⚙️ Configuración")
    modo_xiaomi = st.checkbox("🔋 Modo XIAOMI", value=True, help="Muestra nota si hay stock en APRI.001")
    
    if st.button("🔄 Limpiar todo", use_container_width=True):
        st.session_state.catalogo_df = None
        st.session_state.stock_df = None
        st.session_state.resultados = None
        st.session_state.skus_pedido = {}
        st.rerun()

# ============================================
# MAIN - PESTAÑAS
# ============================================

tab1, tab2, tab3 = st.tabs(["📝 Ingreso Manual", "🔍 Búsqueda por SKU", "📊 Cotización"])

# ========== TAB 1: INGRESO MANUAL (como tu script) ==========
with tab1:
    st.markdown("### 📝 Ingresa los productos manualmente")
    st.caption("Formato: `SKU:CANTIDAD` (uno por línea) o solo SKU (cantidad=1)")
    
    # Texto de ejemplo
    texto_ejemplo = """CN0900374NA8:6
CN9405859NA8:6
RN0200046BK8:2"""
    
    texto_skus = st.text_area(
        "Lista de productos",
        height=150,
        placeholder=texto_ejemplo,
        help="Ejemplo: CN0900374NA8:6  o  solo SKU (cantidad=1)"
    )
    
    # Procesar texto a diccionario
    pedidos_dict = {}
    if texto_skus:
        for line in texto_skus.split('\n'):
            line = line.strip()
            if not line:
                continue
            if ':' in line:
                parts = line.split(':')
                sku = parts[0].strip().upper()
                try:
                    cantidad = int(parts[1].strip())
                except:
                    cantidad = 1
            else:
                sku = line.upper()
                cantidad = 1
            
            if sku:
                pedidos_dict[sku] = pedidos_dict.get(sku, 0) + cantidad
    
    col_b1, col_b2 = st.columns([1, 4])
    with col_b1:
        if st.button("🚀 Buscar", type="primary", use_container_width=True):
            if st.session_state.catalogo_df is None:
                st.error("❌ Primero carga el catálogo de precios")
            elif st.session_state.stock_df is None:
                st.error("❌ Primero carga el reporte de stock")
            elif not pedidos_dict:
                st.warning("⚠️ Ingresa al menos un producto")
            else:
                with st.spinner("🔍 Procesando..."):
                    resultados, advertencias, nota_apri001 = buscar_productos(
                        st.session_state.catalogo_df,
                        st.session_state.stock_df,
                        pedidos_dict,
                        st.session_state.get('col_precio', list(st.session_state.catalogo_df.columns)[-1]),
                        modo_xiaomi
                    )
                    st.session_state.resultados = resultados
                    
                    if advertencias:
                        for adv in advertencias:
                            if "❌" in adv:
                                st.error(adv)
                            else:
                                st.warning(adv)
                    
                    if nota_apri001 and modo_xiaomi:
                        st.markdown('<div class="nota-apri001">📌 <strong>Nota:</strong> Algunos productos pueden tener stock en APRI.001 (stock general). Revisa la pestaña Búsqueda por SKU para ver alternativas.</div>', unsafe_allow_html=True)

# ========== TAB 2: BÚSQUEDA POR SKU (con alternativas) ==========
with tab2:
    st.markdown("### 🔍 Buscar producto por SKU")
    st.caption("Busca un SKU y te mostraremos todas las variantes disponibles")
    
    if st.session_state.catalogo_df is not None and st.session_state.stock_df is not None:
        # Selector de columna de precio
        columnas_precio = [c for c in st.session_state.catalogo_df.columns 
                          if any(p in str(c).upper() for p in ['PRECIO', 'P.', 'BOX', 'IR', 'VIP', 'CAJA', 'MAYOR'])]
        
        if columnas_precio:
            col_precio_seleccionada = st.selectbox(
                "💰 Selecciona columna de precio",
                columnas_precio,
                key="precio_selector"
            )
            st.session_state.col_precio = col_precio_seleccionada
        else:
            col_precio_seleccionada = st.session_state.catalogo_df.columns[-1]
            st.session_state.col_precio = col_precio_seleccionada
            st.info(f"Usando columna: {col_precio_seleccionada}")
        
        # Input de búsqueda
        sku_buscar = st.text_input("🔎 SKU a buscar:", placeholder="Ej: CN0900374NA8")
        
        if sku_buscar:
            with st.spinner("Buscando..."):
                # Buscar en catálogo todas las variantes que coincidan
                col_sku_p = detectar_columna(st.session_state.catalogo_df, ['SKU', 'SAP', 'CODIGO SAP', 'CODIGO'], 0)
                mask = st.session_state.catalogo_df[col_sku_p].astype(str).str.contains(re.escape(sku_buscar.upper()), case=False, na=False)
                variantes = st.session_state.catalogo_df[mask]
                
                if variantes.empty:
                    st.warning(f"❌ No se encontró '{sku_buscar}' en el catálogo")
                else:
                    st.success(f"✅ Se encontraron {len(variantes)} variantes")
                    
                    for _, fila in variantes.iterrows():
                        sku_real = str(fila[col_sku_p]).strip().upper()
                        
                        # Buscar stock
                        col_sku_s = detectar_columna(st.session_state.stock_df, ['NUMERO', 'SKU', 'ARTICULO', 'CODIGO'], 0)
                        mask_stock = st.session_state.stock_df[col_sku_s].astype(str).str.strip() == sku_real
                        
                        stock_disponible = 0
                        stock_almacen = 0
                        stock_apartado = 0
                        
                        if mask_stock.any():
                            row_stock = st.session_state.stock_df[mask_stock].iloc[0]
                            # Detectar columnas de stock
                            for col in st.session_state.stock_df.columns:
                                col_upper = str(col).upper()
                                if 'STOCK' in col_upper or 'EN STOCK' in col_upper:
                                    stock_almacen = int(corregir_numero(row_stock.get(col, 0)))
                                if 'APARTADO' in col_upper or 'COMPROMETIDO' in col_upper:
                                    stock_apartado = int(corregir_numero(row_stock.get(col, 0)))
                                if 'DISPONIBLE' in col_upper:
                                    stock_disponible = int(corregir_numero(row_stock.get(col, 0)))
                            
                            if stock_disponible == 0:
                                stock_disponible = max(0, stock_almacen - stock_apartado)
                        
                        # Precio
                        precio = corregir_numero(fila.get(col_precio_seleccionada, 0))
                        
                        # Mostrar tarjeta
                        with st.container():
                            col_a, col_b, col_c = st.columns([3, 1, 1])
                            with col_a:
                                st.markdown(f"""
                                **📦 {sku_real}**  
                                <span style="font-size:0.8rem;">{str(fila.get(detectar_columna(st.session_state.catalogo_df, ['DESCRIPCION', 'GOODS'], 1), '')[:80]}</span>
                                """, unsafe_allow_html=True)
                                st.caption(f"💰 Precio: S/. {precio:,.2f}" if precio > 0 else "💰 Sin precio")
                                
                                if stock_disponible > 0:
                                    st.success(f"✅ Stock disponible: {stock_disponible}")
                                else:
                                    st.error(f"❌ Sin stock")
                                    
                                    # Nota para modo XIAOMI
                                    if modo_xiaomi and 'APRI.001' in str(st.session_state.stock_df):
                                        st.info("📌 Producto puede tener stock en APRI.001 (stock general)")
                            
                            with col_b:
                                cantidad = st.number_input("Cantidad", min_value=0, max_value=stock_disponible if stock_disponible > 0 else 999, value=0, step=1, key=f"cant_{sku_real}", label_visibility="collapsed")
                            with col_c:
                                if st.button("➕ Agregar", key=f"add_{sku_real}"):
                                    if cantidad > 0:
                                        if stock_disponible > 0 or cantidad <= stock_disponible:
                                            st.session_state.skus_pedido[sku_real] = st.session_state.skus_pedido.get(sku_real, 0) + cantidad
                                            st.toast(f"✅ Agregado: {cantidad}x {sku_real}", icon="✅")
                                            st.rerun()
                                        else:
                                            st.warning(f"⚠️ Stock insuficiente para {sku_real}")
                            st.divider()
    
    # Mostrar carrito actual
    if st.session_state.skus_pedido:
        st.markdown("---")
        st.markdown("### 🛒 Productos seleccionados")
        
        df_carrito = pd.DataFrame([{'SKU': k, 'Cantidad': v} for k, v in st.session_state.skus_pedido.items()])
        st.dataframe(df_carrito, use_container_width=True, hide_index=True)
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("🗑️ Limpiar carrito", use_container_width=True):
                st.session_state.skus_pedido = {}
                st.rerun()
        with col_c2:
            if st.button("📋 Transferir a Cotización", use_container_width=True, type="primary"):
                # Transferir a la pestaña de ingreso manual
                texto_transferido = "\n".join([f"{sku}:{cant}" for sku, cant in st.session_state.skus_pedido.items()])
                st.session_state.texto_transferido = texto_transferido
                st.session_state.skus_pedido = {}
                st.success("✅ Transferido! Ve a la pestaña 'Ingreso Manual' y presiona Buscar")
                st.rerun()

# ========== TAB 3: COTIZACIÓN (RESULTADOS) ==========
with tab3:
    st.markdown("### 📊 Cotización")
    
    if st.session_state.resultados:
        # Mostrar tabla de resultados
        df_resultados = pd.DataFrame(st.session_state.resultados)[['SKU', 'Descripción', 'Precio', 'Pedido', 'Stock', 'A Cotizar', 'Total', 'Estado']]
        
        # Formatear precios
        df_resultados['Precio'] = df_resultados['Precio'].apply(lambda x: f"S/. {x:,.2f}" if x > 0 else "Sin precio")
        df_resultados['Total'] = df_resultados['Total'].apply(lambda x: f"S/. {x:,.2f}")
        
        st.dataframe(df_resultados, use_container_width=True, hide_index=True)
        
        # Tabla editable SOLO para cantidades (como en tu script)
        st.markdown("---")
        st.markdown("### ✏️ Ajustar cantidades")
        st.caption("Modifica las cantidades que deseas cotizar. Las cantidades se actualizan automáticamente.")
        
        # Crear inputs para cada producto
        items_validos = []
        for i, item in enumerate(st.session_state.resultados):
            # Solo mostrar productos con precio > 0 o que tengan stock
            if item['Precio'] > 0 or item['Stock'] > 0:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**📦 {item['SKU']}**  \n{item['Descripción'][:60]}...")
                    if item['Sin_Precio']:
                        st.warning("⚠️ Sin precio - Se cotizará a 0")
                    if item['Sin_Stock']:
                        st.error("❌ Sin stock")
                with col2:
                    nueva_cant = st.number_input(
                        "Cantidad",
                        min_value=0,
                        max_value=item['Stock'] if item['Stock'] > 0 else 999,
                        value=item['A Cotizar'],
                        step=1,
                        key=f"edit_{item['SKU']}_{i}",
                        label_visibility="collapsed"
                    )
                with col3:
                    if nueva_cant != item['A Cotizar']:
                        item['A Cotizar'] = nueva_cant
                        if item['Precio'] > 0:
                            item['Total'] = item['Precio'] * nueva_cant
                            item['Estado'] = "✅ OK" if nueva_cant > 0 else "⚠️ Sin stock"
                        else:
                            item['Total'] = 0
                            item['Estado'] = "⚠️ Sin precio" if nueva_cant > 0 else "❌ Sin stock"
                        st.rerun()
                
                if nueva_cant > 0 and item['Precio'] > 0:
                    items_validos.append(item)
                st.divider()
        
        # Totales
        if items_validos:
            total_general = sum(item['Total'] for item in items_validos)
            
            col_t1, col_t2, col_t3 = st.columns(3)
            col_t1.metric("✅ Productos a cotizar", len(items_validos))
            col_t2.metric("💰 Total", f"S/. {total_general:,.2f}")
            col_t3.metric("⚠️ Excluidos", len([i for i in st.session_state.resultados if i not in items_validos]))
            
            st.markdown("---")
            st.markdown("### 📥 Generar Cotización")
            
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                cliente = st.text_input("🏢 Cliente", "CLIENTE NUEVO")
            with col_c2:
                ruc = st.text_input("📋 RUC/DNI", "-")
            
            if st.button("📥 GENERAR EXCEL", type="primary", use_container_width=True):
                excel_data = generar_excel(items_validos, cliente, ruc)
                st.download_button(
                    "💾 DESCARGAR EXCEL",
                    data=excel_data,
                    file_name=f"Cotizacion_{cliente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                st.balloons()
                st.success("✅ Cotización generada")
    
    else:
        st.info("💡 No hay resultados. Ve a la pestaña 'Ingreso Manual' o 'Búsqueda por SKU' para agregar productos.")

# Footer
st.markdown("---")
st.markdown("*💚 QTC Smart Sales Pro - Sistema Profesional de Cotización*")
