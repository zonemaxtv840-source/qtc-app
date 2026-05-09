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
# CONSTANTES Y CONFIGURACIÓN
# ============================================

class ModoCotizacion:
    XIAOMI = "XIAOMI"
    GENERAL = "GENERAL"

STOCK_HOJA_MAP = {
    ModoCotizacion.XIAOMI: ["APRI.004", "YESSICA"],
    ModoCotizacion.GENERAL: ["APRI.001"]
}

TIPOS_CATALOGO = {
    "XIAOMI_DRIVE": {
        "patrones": ["xiaomi", "drive", "mi", "redmi"],
        "columnas": {
            "sku": ["SKU"],
            "descripcion": ["NOMBRE PRODUCTO", "PRODUCTO"],
            "precios": {
                "P. IR": ["Mayorista", "MAYORISTA"],
                "P. BOX": ["Caja", "CAJA", "BOX"],
                "P. VIP": ["Vip", "VIP"]
            }
        }
    },
    "XIAOMI_POWERBE": {
        "patrones": ["powerbe", "powerbeats", "beats"],
        "columnas": {
            "sku": ["COD SAP", "SKU", "CODIGO"],
            "descripcion": ["NOMBRE PRODUCTO", "PRODUCTO", "DESCRIPCION"],
            "precios": {
                "P. IR": ["P. IR", "IR", "MAYORISTA"],
                "P. BOX": ["P. BOX", "BOX", "CAJA"],
                "P. VIP": ["P. VIP", "VIP"]
            }
        }
    },
    "GENERAL": {
        "patrones": [],
        "columnas": {
            "sku": ["SKU", "COD", "SAP", "NUMERO", "ARTICULO", "COD SAP", "CODIGO"],
            "descripcion": ["DESC", "DESCRIPCION", "NOMBRE", "GOODS DESCRIPTION", "NOMBRE PRODUCTO", "PRODUCTO"],
            "precios": {
                "P. IR": ["P. IR", "IR", "MAYORISTA", "MAYOR"],
                "P. BOX": ["P. BOX", "BOX", "CAJA"],
                "P. VIP": ["P. VIP", "VIP"]
            }
        }
    }
}

# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

def corregir_numero(valor) -> float:
    if pd.isna(valor) or str(valor).strip() in ["", "0", "0.0", "-"]:
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

def limpiar_cabeceras(df: pd.DataFrame) -> pd.DataFrame:
    for i in range(min(20, len(df))):
        fila = [str(x).upper() for x in df.iloc[i].values]
        if any(h in item for h in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO', 'COD SAP', 'GOODS', 'DESC'] for item in fila):
            df.columns = [str(c).strip() for c in df.iloc[i]]
            return df.iloc[i+1:].reset_index(drop=True)
    return df

def cargar_archivo_datos(uploaded_file) -> Optional[pd.DataFrame]:
    nombre = uploaded_file.name.lower()
    try:
        if nombre.endswith('.csv'):
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(uploaded_file, encoding='latin-1')
        else:
            df = pd.read_excel(uploaded_file)
        return limpiar_cabeceras(df)
    except Exception as e:
        st.error(f"Error cargando {uploaded_file.name}: {str(e)[:100]}")
        return None

def detectar_columna_inteligente(df: pd.DataFrame, posibles: List[str], columna_fallback: str = None) -> str:
    df_cols = [str(c).strip() for c in df.columns]
    df_cols_upper = [c.upper() for c in df_cols]
    for posible in posibles:
        posible_upper = posible.upper()
        for idx, col_upper in enumerate(df_cols_upper):
            if posible_upper == col_upper or posible_upper in col_upper:
                return df_cols[idx]
    if columna_fallback and columna_fallback in df.columns:
        return columna_fallback
    return df.columns[0]

# ============================================
# FUNCIONES DE CARGA
# ============================================

def cargar_catalogo(archivo) -> Optional[Dict]:
    df = cargar_archivo_datos(archivo)
    if df is None:
        return None
    
    col_sku = detectar_columna_inteligente(df, ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO', 'COD SAP', 'CODIGO'])
    col_desc = detectar_columna_inteligente(df, ['DESC', 'DESCRIPCION', 'NOMBRE', 'GOODS DESCRIPTION', 'NOMBRE PRODUCTO', 'PRODUCTO'])
    
    columnas_precio = {}
    for col in df.columns:
        col_upper = str(col).upper()
        if 'P. BOX' in col_upper or 'BOX' in col_upper or 'CAJA' in col_upper:
            columnas_precio['P. BOX'] = col
        elif 'P. IR' in col_upper or 'MAYORISTA' in col_upper or 'MAYOR' in col_upper:
            columnas_precio['P. IR'] = col
        elif 'P. VIP' in col_upper or 'VIP' in col_upper:
            columnas_precio['P. VIP'] = col
        elif 'PRECIO' in col_upper:
            columnas_precio['PRECIO'] = col
    
    with st.sidebar.expander(f"📋 {archivo.name[:30]}...", expanded=False):
        st.caption(f"🔑 SKU: `{col_sku}`")
        st.caption(f"📝 Desc: `{col_desc}`")
        if columnas_precio:
            st.caption(f"💰 Precios: `{', '.join(columnas_precio.keys())}`")
    
    return {
        'nombre': archivo.name,
        'df': df,
        'col_sku': col_sku,
        'col_desc': col_desc,
        'columnas_precio': columnas_precio
    }

def cargar_stocks(archivos, modo: str) -> List[Dict]:
    stocks_cargados = []
    for archivo in archivos:
        try:
            xls = pd.ExcelFile(archivo)
            for hoja in xls.sheet_names:
                hoja_upper = hoja.upper()
                patrones = STOCK_HOJA_MAP.get(modo, [])
                if not any(patron in hoja_upper for patron in patrones):
                    continue
                
                df = pd.read_excel(archivo, sheet_name=hoja)
                df = limpiar_cabeceras(df)
                
                col_sku = detectar_columna_inteligente(df, ['SKU', 'COD', 'NUMERO', 'NÚMERO DE ARTÍCULO', 'ARTICULO'])
                col_stock = detectar_columna_inteligente(df, ['STOCK', 'DISPONIBLE', 'CANTIDAD', 'CANT'])
                
                # Detectar columnas adicionales para GENERAL
                col_en_stock = detectar_columna_inteligente(df, ['EN STOCK', 'STOCK'])
                col_comprometido = detectar_columna_inteligente(df, ['COMPROMETIDO', 'RESERVADO'])
                col_solicitado = detectar_columna_inteligente(df, ['SOLICITADO', 'SOLICITADA'])
                col_disponible = detectar_columna_inteligente(df, ['DISPONIBLE', 'LIBRE'])
                
                stocks_cargados.append({
                    'nombre': f"{archivo.name} [{hoja}]",
                    'df': df,
                    'col_sku': col_sku,
                    'col_stock': col_stock,
                    'col_en_stock': col_en_stock,
                    'col_comprometido': col_comprometido,
                    'col_solicitado': col_solicitado,
                    'col_disponible': col_disponible,
                    'hoja': hoja,
                    'modo': modo
                })
                st.success(f"✅ {archivo.name} → Hoja: {hoja}")
        except Exception as e:
            st.error(f"Error en {archivo.name}: {str(e)[:100]}")
    return stocks_cargados

# ============================================
# FUNCIONES DE BÚSQUEDA
# ============================================

def buscar_precio(catalogos: List[Dict], sku: str, col_precio_seleccionada: str) -> Dict:
    sku_limpio = sku.strip().upper()
    for cat in catalogos:
        df = cat['df']
        mask_sku = df[cat['col_sku']].astype(str).str.strip().str.upper() == sku_limpio
        if not df[mask_sku].empty:
            row = df[mask_sku].iloc[0]
            col_precio = cat['columnas_precio'].get(col_precio_seleccionada)
            precio = corregir_numero(row[col_precio]) if col_precio and col_precio in df.columns else 0.0
            return {
                'encontrado': True,
                'precio': precio,
                'descripcion': str(row[cat['col_desc']]) if pd.notna(row[cat['col_desc']]) else ""
            }
        
        mask_desc = df[cat['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
        if not df[mask_desc].empty:
            row = df[mask_desc].iloc[0]
            col_precio = cat['columnas_precio'].get(col_precio_seleccionada)
            precio = corregir_numero(row[col_precio]) if col_precio and col_precio in df.columns else 0.0
            return {
                'encontrado': True,
                'precio': precio,
                'descripcion': str(row[cat['col_desc']]) if pd.notna(row[cat['col_desc']]) else ""
            }
    return {'encontrado': False, 'precio': 0.0, 'descripcion': ""}

def buscar_stock(stocks: List[Dict], sku: str, modo: str):
    """Busca stock - MODO GENERAL usa DISPONIBLE, MODO XIAOMI suma APRI.004 + YESSICA"""
    sku_limpio = sku.strip().upper()
    stock_total = 0
    stock_apri004 = 0
    stock_yessica = 0
    detalles_completos = {}
    
    for stock in stocks:
        hoja = stock['hoja'].upper()
        mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
        if not mask.any():
            continue
        
        row = stock['df'][mask].iloc[0]
        
        # MODO GENERAL: usa DISPONIBLE
        if modo == ModoCotizacion.GENERAL and 'APRI.001' in hoja:
            disponible = int(corregir_numero(row[stock['col_disponible']])) if stock.get('col_disponible') else 0
            en_stock = int(corregir_numero(row[stock['col_en_stock']])) if stock.get('col_en_stock') else 0
            comprometido = int(corregir_numero(row[stock['col_comprometido']])) if stock.get('col_comprometido') else 0
            solicitado = int(corregir_numero(row[stock['col_solicitado']])) if stock.get('col_solicitado') else 0
            
            stock_total = disponible  # ✅ USA DISPONIBLE
            detalles_completos = {
                'En Stock': en_stock,
                'Comprometido': comprometido,
                'Solicitado': solicitado,
                'Disponible': disponible
            }
            return stock_total, {}, 0, 0, detalles_completos
        
        # MODO XIAOMI: suma APRI.004 + YESSICA
        elif modo == ModoCotizacion.XIAOMI:
            cantidad = int(corregir_numero(row[stock['col_stock']]))
            if 'APRI.004' in hoja:
                stock_apri004 = cantidad
            elif 'YESSICA' in hoja:
                stock_yessica = cantidad
    
    if modo == ModoCotizacion.XIAOMI:
        stock_total = stock_apri004 + stock_yessica
    
    return stock_total, {}, stock_apri004, stock_yessica, detalles_completos

def obtener_descripcion_fallback(stocks: List[Dict], sku: str) -> str:
    sku_limpio = sku.strip().upper()
    for stock in stocks:
        df = stock['df']
        mask = df[stock['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
        if not df[mask].empty:
            row = df[mask].iloc[0]
            for col in df.columns:
                if any(p in str(col).upper() for p in ['DESC', 'NOMBRE', 'GOODS', 'PRODUCTO']):
                    desc = str(row[col])
                    if desc and desc != 'nan':
                        return desc[:100]
            return f"SKU: {sku}"
    return f"SKU: {sku}"

# ============================================
# PROCESAR PEDIDOS
# ============================================

def procesar_pedidos(pedidos: List[Dict], catalogos: List[Dict], stocks: List[Dict], 
                     col_precio: str, modo: str) -> Tuple[List[Dict], List[str]]:
    resultados = []
    advertencias = []
    
    for pedido in pedidos:
        sku = pedido['sku']
        cant_solicitada = pedido['cantidad']
        
        precio_info = buscar_precio(catalogos, sku, col_precio)
        stock_total, _, stock_apri004, stock_yessica, stock_detalles = buscar_stock(stocks, sku, modo)
        
        descripcion = precio_info['descripcion']
        if not descripcion:
            descripcion = obtener_descripcion_fallback(stocks, sku)
        
        precio = precio_info['precio']
        sin_precio = not precio_info['encontrado'] or precio == 0
        sin_stock = stock_total == 0
        
        if sin_precio and sin_stock:
            estado = "❌ Sin precio y sin stock"
            badge_estado = "badge-danger"
            a_cotizar = 0
            total = 0
            advertencias.append(f"❌ **{sku}**: Sin precio y sin stock")
        elif sin_precio:
            estado = "⚠️ Sin precio"
            badge_estado = "badge-warning"
            a_cotizar = 0
            total = 0
            advertencias.append(f"⚠️ **{sku}**: Sin precio en catálogo")
        elif sin_stock:
            estado = "❌ Sin stock"
            badge_estado = "badge-danger"
            a_cotizar = 0
            total = 0
            advertencias.append(f"❌ **{sku}**: Sin stock disponible")
        elif cant_solicitada > stock_total:
            a_cotizar = stock_total
            total = precio * a_cotizar
            estado = f"⚠️ Stock insuficiente ({stock_total}/{cant_solicitada})"
            badge_estado = "badge-warning"
            advertencias.append(f"⚠️ **{sku}**: Stock insuficiente")
        else:
            a_cotizar = cant_solicitada
            total = precio * a_cotizar
            estado = "✅ OK"
            badge_estado = "badge-ok"
        
        # Badges
        if modo == ModoCotizacion.XIAOMI:
            if stock_apri004 > 0 and stock_yessica > 0:
                badge_origen = f'<span class="origin-badge origin-both">🟣 APRI.004: {stock_apri004} | 🔵 YESSICA: {stock_yessica}</span>'
            elif stock_apri004 > 0:
                badge_origen = f'<span class="origin-badge origin-apri004">🟣 APRI.004: {stock_apri004}</span>'
            elif stock_yessica > 0:
                badge_origen = f'<span class="origin-badge origin-yessica">🔵 YESSICA: {stock_yessica}</span>'
            else:
                badge_origen = '<span class="badge-danger">❌ Sin stock</span>'
            detalle_html = ""
        else:
            badge_origen = f'<span class="origin-badge origin-both">🟢 Stock: {stock_total}</span>' if stock_total > 0 else '<span class="badge-danger">❌ Sin stock</span>'
            detalle_html = ""
            if stock_detalles:
                detalle_html = f"""
                <div style="font-size: 0.7rem; margin-top: 5px; color: #666;">
                    📊 Detalle: 📦 En Stock: {stock_detalles.get('En Stock', 0)} | 
                    🔒 Comprometido: {stock_detalles.get('Comprometido', 0)} | 
                    ✅ Solicitado: {stock_detalles.get('Solicitado', 0)} | 
                    🟢 Disponible: {stock_detalles.get('Disponible', 0)}
                </div>
                """
        
        resultados.append({
            'SKU': sku,
            'Descripción': descripcion[:80],
            'Precio': precio,
            'Pedido': cant_solicitada,
            'Stock': stock_total,
            'Origen': badge_origen,
            'Detalle_HTML': detalle_html,
            'A Cotizar': a_cotizar,
            'Total': total,
            'Estado': estado,
            'Badge_Estado': badge_estado
        })
    
    return resultados, advertencias

# ============================================
# GENERAR EXCEL
# ============================================

def generar_excel(items: List[Dict], cliente: str, ruc: str) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pd.DataFrame(items).to_excel(writer, sheet_name='Cotizacion', index=False, startrow=5)
        
        workbook = writer.book
        ws = writer.sheets['Cotizacion']
        
        fmt_header = workbook.add_format({'bg_color': '#F79646', 'bold': True, 'border': 1, 'align': 'center', 'font_color': 'white'})
        fmt_money = workbook.add_format({'num_format': '"S/." #,##0.00', 'border': 1, 'align': 'right'})
        fmt_border = workbook.add_format({'border': 1})
        fmt_bold = workbook.add_format({'bold': True})
        
        ws.set_column('A:A', 20)
        ws.set_column('B:B', 75)
        ws.set_column('C:C', 12)
        ws.set_column('D:D', 18)
        ws.set_column('E:E', 18)
        
        ws.write('A1', 'FECHA:', fmt_bold)
        ws.write('B1', datetime.now().strftime("%d/%m/%Y"))
        ws.write('A2', 'CLIENTE:', fmt_bold)
        ws.write('B2', cliente.upper())
        ws.write('A3', 'RUC:', fmt_bold)
        ws.write('B3', ruc)
        
        ws.merge_range('F1:H1', 'DATOS BANCARIOS', fmt_header)
        ws.write('F2', 'BBVA SOLES:', workbook.add_format({'font_color': 'red', 'bold': True, 'border': 1}))
        ws.write('G2', '0011-0616-0100012617', fmt_border)
        
        headers = ['Código SAP', 'Descripción', 'Cantidad', 'Precio Unit.', 'Total']
        for i, header in enumerate(headers):
            ws.write(5, i, header, fmt_header)
        
        for row_idx, item in enumerate(items):
            ws.write_row(row_idx + 6, 0, [item['sku'], item['desc'], item['cant'], item['p_u'], item['total']], fmt_border)
            ws.write(row_idx + 6, 3, item['p_u'], fmt_money)
            ws.write(row_idx + 6, 4, item['total'], fmt_money)
        
        total_row = len(items) + 6
        ws.write(total_row, 3, 'TOTAL S/.', fmt_header)
        ws.write(total_row, 4, sum(item['total'] for item in items), fmt_money)
    
    return output.getvalue()

# ============================================
# UTILIDADES UI
# ============================================

def obtener_clase_stock(stock: int) -> str:
    if stock == 0:
        return "stock-rojo"
    elif stock <= 5:
        return "stock-amarillo"
    return "stock-verde"

def obtener_icono_stock(stock: int) -> str:
    if stock == 0:
        return "❌"
    elif stock <= 5:
        return "⚠️"
    return "✅"

def obtener_mensaje_stock(stock: int) -> str:
    if stock == 0:
        return "Sin stock disponible"
    elif stock <= 5:
        return f"¡Stock bajo! Solo quedan {stock} unidades"
    return "Stock suficiente"

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================

try:
    img_logo = Image.open("logo.png")
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon=img_logo, layout="wide")
except:
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon="💼", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #E8F5E9 50%, #C8E6C9 100%) !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0D3B0F 50%, #1B5E20 100%) !important; }
[data-testid="stSidebar"] * { color: #FFFFFF !important; }
.stButton > button { background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%) !important; color: white !important; border-radius: 12px; font-weight: 600; border: none; }
.badge-ok { background-color: #C8E6C9; color: #1B5E20; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
.badge-warning { background-color: #FFF3E0; color: #E65100; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
.badge-danger { background-color: #FFCDD2; color: #C62828; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
.origin-badge { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; margin-right: 5px; }
.origin-apri004 { background-color: #E1BEE7; color: #4A148C; }
.origin-yessica { background-color: #BBDEFB; color: #0D47A1; }
.origin-both { background-color: #C8E6C9; color: #1B5E20; }
.stock-verde { color: #2E7D32; font-weight: bold; background-color: #C8E6C9; padding: 2px 8px; border-radius: 20px; display: inline-block; }
.stock-amarillo { color: #E65100; font-weight: bold; background-color: #FFE0B2; padding: 2px 8px; border-radius: 20px; display: inline-block; }
.stock-rojo { color: #C62828; font-weight: bold; background-color: #FFCDD2; padding: 2px 8px; border-radius: 20px; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# ============================================
# INICIALIZACIÓN DE SESIÓN
# ============================================

for key in ["auth", "tipo_cotizacion", "catalogos", "stocks", "resultados", "cotizaciones", "total_prods", "productos_seleccionados"]:
    if key not in st.session_state:
        if key == "auth":
            st.session_state.auth = False
        elif key == "tipo_cotizacion":
            st.session_state.tipo_cotizacion = None
        elif key in ["catalogos", "stocks", "productos_seleccionados"]:
            st.session_state[key] = []
        elif key == "resultados":
            st.session_state.resultados = None
        else:
            st.session_state[key] = 0

# ============================================
# LOGIN
# ============================================

if not st.session_state.auth:
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #FFF8E1 0%, #FFE0B2 50%, #FFCC80 100%) !important; }
    .login-card { background: #FFFDF5; border-radius: 28px; padding: 2.5rem; box-shadow: 0 25px 50px rgba(0,0,0,0.15); text-align: center; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:
        st.markdown('<div class="login-card"><h1 style="color:#E65100;">QTC Smart Sales</h1><p style="color:#F57C00;">Sistema Profesional de Cotización</p>', unsafe_allow_html=True)
        user = st.text_input("👤 USUARIO", placeholder="Ingresa tu usuario", key="login_user")
        pw = st.text_input("🔒 CONTRASEÑA", type="password", placeholder="Ingresa tu contraseña", key="login_pass")
        if st.button("🚀 INGRESAR", use_container_width=True):
            if user == "admin" and pw == "qtc2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.stop()

# ============================================
# HEADER
# ============================================

try:
    col_logo, col_title, col_user = st.columns([1, 4, 2])
    with col_logo:
        st.image("logo.png", width="60px")
    with col_title:
        st.title("QTC Smart Sales Pro")
    with col_user:
        st.markdown(f"""
        <div style="text-align: right; background: white; padding: 8px 15px; border-radius: 30px;">
            <span style="font-weight: 600;">👤 admin</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚪 Cerrar Sesión", key="logout"):
            st.session_state.auth = False
            st.rerun()
except:
    st.title("QTC Smart Sales Pro")

st.markdown("---")

if st.session_state.tipo_cotizacion is None:
    st.markdown("### 🎯 ¿Qué vas a cotizar hoy?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔋 XIAOMI", use_container_width=True):
            st.session_state.tipo_cotizacion = ModoCotizacion.XIAOMI
            st.rerun()
    with col2:
        if st.button("💼 GENERAL", use_container_width=True):
            st.session_state.tipo_cotizacion = ModoCotizacion.GENERAL
            st.rerun()
    st.stop()

if st.session_state.tipo_cotizacion == ModoCotizacion.XIAOMI:
    st.success("🔋 **Modo XIAOMI** - Stock en APRI.004 + YESSICA")
else:
    st.info("💼 **Modo GENERAL** - Stock usa columna DISPONIBLE")

st.markdown("---")

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("### 🎯 Modo Actual")
    st.markdown(f"**{st.session_state.tipo_cotizacion}**")
    
    st.markdown("---")
    st.markdown("### 📂 Archivos")
    
    st.markdown("**📚 Catálogos**")
    archivos_catalogos = st.file_uploader("Excel o CSV", type=['xlsx', 'xls', 'csv'], accept_multiple_files=True, key="cat_upload")
    if archivos_catalogos:
        st.session_state.catalogos = []
        for archivo in archivos_catalogos:
            resultado = cargar_catalogo(archivo)
            if resultado:
                st.session_state.catalogos.append(resultado)
                st.success(f"✅ {resultado['nombre'][:50]}")
    
    st.markdown("**📦 Stocks**")
    archivos_stock = st.file_uploader("Excel", type=['xlsx', 'xls'], accept_multiple_files=True, key="stock_upload")
    if archivos_stock:
        st.session_state.stocks = cargar_stocks(archivos_stock, st.session_state.tipo_cotizacion)

# ============================================
# TABS
# ============================================

tab_cotizacion, tab_buscar, tab_dashboard = st.tabs(["📦 Cotización", "🔍 Buscar", "📊 Dashboard"])

# TAB COTIZACIÓN
with tab_cotizacion:
    if not st.session_state.catalogos:
        st.warning("🌿 Carga catálogos en el panel izquierdo")
    else:
        opciones_precio = set()
        for cat in st.session_state.catalogos:
            opciones_precio.update(cat['columnas_precio'].keys())
        
        if not opciones_precio:
            st.error("⚠️ No se detectaron precios")
            col_precio = None
        else:
            col_precio = st.selectbox("💰 Columna de precio:", sorted(list(opciones_precio)))
        
        st.markdown("---")
        st.markdown("### 📝 Ingresa productos")
        st.caption("Formato: SKU:CANTIDAD (uno por línea)")
        
        if 'skus_transferidos' in st.session_state:
            texto_defecto = "\n".join([f"{sku}:{cant}" for sku, cant in st.session_state.skus_transferidos.items()])
            del st.session_state.skus_transferidos
        else:
            texto_defecto = ""
        
        texto_skus = st.text_area("", height=150, value=texto_defecto, placeholder="Ejemplo:\nRN0200046BK8:5")
        
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
                            pass
                elif line:
                    sku = line.strip().upper()
                    pedidos_dict[sku] = pedidos_dict.get(sku, 0) + 1
        
        pedidos = [{'sku': sku, 'cantidad': cant} for sku, cant in pedidos_dict.items()]
        
        if st.button("🚀 PROCESAR", use_container_width=True, type="primary") and pedidos:
            if not col_precio:
                st.error("❌ Selecciona precio")
            else:
                with st.spinner("🔍 Procesando..."):
                    resultados, advertencias = procesar_pedidos(pedidos, st.session_state.catalogos, st.session_state.stocks, col_precio, st.session_state.tipo_cotizacion)
                    for adv in advertencias:
                        if "⚠️" in adv:
                            st.warning(adv)
                        else:
                            st.error(adv)
                    st.session_state.resultados = resultados
        
        if st.session_state.resultados:
            st.markdown("---")
            st.markdown("### 📊 Resultados")
            
            html = '<div style="overflow-x: auto;"><table style="width:100%; border-collapse: collapse; background: white; border-radius: 12px;">'
            html += '<thead><tr style="background: #1B5E20; color: white;">'
            html += '<th style="padding: 10px;">SKU</th><th style="padding: 10px;">Descripción</th><th style="padding: 10px;">Precio</th>'
            html += '<th style="padding: 10px;">Pedido</th><th style="padding: 10px;">Stock</th><th style="padding: 10px;">Origen</th>'
            html += '<th style="padding: 10px;">A Cotizar</th><th style="padding: 10px;">Total</th><th style="padding: 10px;">Estado</th></tr></thead><tbody>'
            
            for item in st.session_state.resultados:
                precio_str = f"S/. {item['Precio']:,.2f}" if item['Precio'] > 0 else "Sin precio"
                total_str = f"S/. {item['Total']:,.2f}"
                stock_clase = obtener_clase_stock(item['Stock'])
                stock_icono = obtener_icono_stock(item['Stock'])
                
                html += f'<tr style="border-bottom: 1px solid #E8F5E9;">'
                html += f'<td style="padding: 10px;">{item["SKU"]}</td>'
                html += f'<td style="padding: 10px;">{item["Descripción"][:60]}</td>'
                html += f'<td style="padding: 10px; text-align: center;">{precio_str}</td>'
                html += f'<td style="padding: 10px; text-align: center;">{item["Pedido"]}</td>'
                html += f'<td style="padding: 10px; text-align: center;"><span class="{stock_clase}">{stock_icono} {item["Stock"]}</span></td>'
                html += f'<td style="padding: 10px;">{item["Origen"]}{item.get("Detalle_HTML", "")}</td>'
                html += f'<td style="padding: 10px; text-align: center;"><strong>{item["A Cotizar"]}</strong></td>'
                html += f'<td style="padding: 10px; text-align: center;"><strong>{total_str}</strong></td>'
                html += f'<td style="padding: 10px; text-align: center;"><span class="{item["Badge_Estado"]}">{item["Estado"]}</span></td>'
                html += '</tr>'
            
            html += '</tbody></table></div>'
            st.markdown(html, unsafe_allow_html=True)
            
            # Tabla editable
            st.markdown("---")
            st.markdown("### ✏️ Ajustar cantidades")
            
            df_ajuste = pd.DataFrame(st.session_state.resultados)[['SKU', 'Descripción', 'Precio', 'Stock', 'A Cotizar']].copy()
            df_ajuste['Precio'] = df_ajuste['Precio'].apply(lambda x: f"S/. {x:,.2f}" if x > 0 else "Sin precio")
            
            edited_df = st.data_editor(df_ajuste, column_config={
                "SKU": st.column_config.TextColumn("SKU", disabled=True),
                "Descripción": st.column_config.TextColumn("Descripción", disabled=True),
                "Precio": st.column_config.TextColumn("Precio", disabled=True),
                "Stock": st.column_config.NumberColumn("Stock", disabled=True),
                "A Cotizar": st.column_config.NumberColumn("A Cotizar", min_value=0, step=1),
            }, use_container_width=True, hide_index=True)
            
            for idx, row in edited_df.iterrows():
                if idx < len(st.session_state.resultados):
                    nueva_cant = row['A Cotizar']
                    stock_disp = st.session_state.resultados[idx]['Stock']
                    if nueva_cant > stock_disp and stock_disp > 0:
                        nueva_cant = stock_disp
                    st.session_state.resultados[idx]['A Cotizar'] = nueva_cant
                    if st.session_state.resultados[idx]['Precio'] > 0:
                        st.session_state.resultados[idx]['Total'] = st.session_state.resultados[idx]['Precio'] * nueva_cant
            
            items_validos = [r for r in st.session_state.resultados if r['A Cotizar'] > 0 and r['Precio'] > 0]
            total_general = sum(r['Total'] for r in items_validos)
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("✅ A cotizar", len(items_validos))
            col_m2.metric("💰 Total", f"S/. {total_general:,.2f}")
            
            if items_validos:
                st.markdown("---")
                cliente = st.text_input("🏢 Cliente", "CLIENTE NUEVO")
                ruc_cliente = st.text_input("📋 RUC/DNI", "-")
                
                if st.button("📥 GENERAR EXCEL", use_container_width=True, type="primary"):
                    items_excel = [{'sku': r['SKU'], 'desc': r['Descripción'], 'cant': r['A Cotizar'], 'p_u': r['Precio'], 'total': r['Total']} for r in items_validos]
                    excel = generar_excel(items_excel, cliente, ruc_cliente)
                    st.download_button("💾 DESCARGAR", data=excel, file_name=f"Cotizacion_{cliente}.xlsx", use_container_width=True)
                    st.session_state.cotizaciones += 1
                    st.balloons()

# TAB BUSCAR
with tab_buscar:
    st.markdown("### 🔍 Buscar Productos")
    if not st.session_state.catalogos:
        st.warning("🌿 Primero carga catálogos")
    else:
        busqueda = st.text_input("🔎 Buscar:", placeholder="SKU o descripción")
        if busqueda and len(busqueda) >= 2:
            with st.spinner("🔍 Buscando..."):
                resultados_busqueda = []
                skus_vistos = set()
                for cat in st.session_state.catalogos:
                    df = cat['df']
                    mask = df[cat['col_sku']].astype(str).str.contains(busqueda, case=False, na=False)
                    mask |= df[cat['col_desc']].astype(str).str.contains(busqueda, case=False, na=False)
                    for _, row in df[mask].iterrows():
                        sku = str(row[cat['col_sku']])
                        if sku in skus_vistos:
                            continue
                        skus_vistos.add(sku)
                        stock_total, _, _, _, _ = buscar_stock(st.session_state.stocks, sku, st.session_state.tipo_cotizacion)
                        resultados_busqueda.append({
                            'SKU': sku,
                            'Descripción': str(row[cat['col_desc']])[:100],
                            'Stock': stock_total
                        })
                
                for res in resultados_busqueda:
                    st.markdown(f"""
                    <div style="background: white; border-radius: 12px; padding: 1rem; margin: 0.5rem 0;">
                        <strong>📦 {res['SKU']}</strong><br>
                        <span style="font-size:0.85rem;">{res['Descripción']}</span><br>
                        <span>📊 Stock: {res['Stock']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        cantidad = st.number_input("Cant", min_value=0, value=0, key=f"add_{res['SKU']}", label_visibility="collapsed")
                        if cantidad > 0:
                            st.session_state.productos_seleccionados[res['SKU']] = st.session_state.productos_seleccionados.get(res['SKU'], 0) + cantidad
                    st.divider()
        
        if st.session_state.productos_seleccionados:
            if st.button("📋 TRANSFERIR A COTIZACIÓN", use_container_width=True, type="primary"):
                st.session_state.skus_transferidos = st.session_state.productos_seleccionados.copy()
                st.session_state.productos_seleccionados = {}
                st.success("✅ Transferido! Ve a Cotización y presiona PROCESAR")

# TAB DASHBOARD
with tab_dashboard:
    st.markdown("### 📊 Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("📄 Cotizaciones", st.session_state.cotizaciones)
    col2.metric("🌿 Productos", st.session_state.total_prods)
    col3.metric("📚 Catálogos", len(st.session_state.catalogos))

st.markdown("---")
st.markdown("*💚 QTC Smart Sales Pro*")
