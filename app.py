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

# Mapeo de nombres de columnas de precios
PRECIO_MAP = {
    "P. BOX": ["P.BOX", "BOX", "CAJA"],
    "P. IR": ["P.IR", "MAYORISTA", "MAYOR"],
    "P. VIP": ["P.VIP", "VIP"]
}

# Hojas de stock por modo
STOCK_HOJA_MAP = {
    ModoCotizacion.XIAOMI: ["APRI.004", "YESSICA"],
    ModoCotizacion.GENERAL: ["APRI.001"]
}

# Columnas de stock para modo GENERAL
STOCK_COLUMNS_GENERAL = {
    "total": ["En stock", "STOCK", "TOTAL", "INVENTARIO"],
    "comprometido": ["Comprometido", "COMPROMETIDO", "RESERVADO", "APARTADO"],
    "solicitado": ["Solicitado", "SOLICITADO", "PEDIDO"],
    "disponible": ["Disponible", "DISPONIBLE", "STOCK REAL", "REAL"]  # ✅ PRIORIDAD
}

# ============================================
# CONFIGURACIÓN DE PATRONES POR TIPO DE CATÁLOGO
# ============================================

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
            "sku": ["SKU", "COD", "SAP", "NUMERO", "ARTICULO", "COD SAP", "CODIGO", "Número de artículo"],
            "descripcion": ["DESC", "DESCRIPCION", "NOMBRE", "GOODS DESCRIPTION", "NOMBRE PRODUCTO", "PRODUCTO", "Descripción del artículo"],
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
    """Convierte cualquier formato de número a float."""
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
    """Detecta la fila de encabezados y la establece como columnas."""
    for i in range(min(20, len(df))):
        fila = [str(x).upper() for x in df.iloc[i].values]
        if any(h in item for h in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO', 'COD SAP', 'GOODS', 'DESC', 'NÚMERO DE ARTÍCULO'] for item in fila):
            df.columns = [str(c).strip() for c in df.iloc[i]]
            return df.iloc[i+1:].reset_index(drop=True)
    return df

def cargar_archivo_datos(uploaded_file) -> Optional[pd.DataFrame]:
    """Carga XLSX, XLS o CSV y devuelve DataFrame."""
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

def detectar_tipo_catalogo(nombre_archivo: str, df: pd.DataFrame) -> str:
    """Detecta automáticamente el tipo de catálogo."""
    nombre_lower = nombre_archivo.lower()
    columnas_str = " ".join([str(c).upper() for c in df.columns])
    
    for tipo, config in TIPOS_CATALOGO.items():
        if tipo == "GENERAL":
            continue
        for patron in config["patrones"]:
            if patron in nombre_lower:
                return tipo
    
    if "COD SAP" in columnas_str or ("P. IR" in columnas_str and "P. BOX" in columnas_str):
        return "XIAOMI_POWERBE"
    
    if ("Family" in columnas_str or "SKU" in columnas_str) and \
       "Mayorista" in columnas_str and "Caja" in columnas_str and "Vip" in columnas_str:
        return "XIAOMI_DRIVE"
    
    return "GENERAL"

def detectar_columna_inteligente(df: pd.DataFrame, posibles: List[str], columna_fallback: str = None) -> str:
    """Detecta la primera columna que coincida con los posibles nombres."""
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

def detectar_precio_inteligente(df: pd.DataFrame, tipo_precio: str, tipo_catalogo: str) -> Optional[str]:
    """Detecta columna de precio según el tipo de catálogo."""
    config = TIPOS_CATALOGO.get(tipo_catalogo, TIPOS_CATALOGO["GENERAL"])
    patrones_precio = config["columnas"]["precios"].get(tipo_precio, [])
    
    for col in df.columns:
        col_limpio = str(col).strip()
        col_upper = col_limpio.upper()
        for patron in patrones_precio:
            patron_upper = patron.upper()
            if patron_upper == col_upper or patron_upper in col_upper:
                return col_limpio
    return None

def cargar_catalogo(archivo) -> Optional[Dict]:
    """Carga un catálogo con detección inteligente."""
    df = cargar_archivo_datos(archivo)
    if df is None:
        return None
    
    tipo_catalogo = detectar_tipo_catalogo(archivo.name, df)
    config = TIPOS_CATALOGO.get(tipo_catalogo, TIPOS_CATALOGO["GENERAL"])
    cols_config = config["columnas"]
    
    col_sku = detectar_columna_inteligente(df, cols_config["sku"])
    col_desc = detectar_columna_inteligente(df, cols_config["descripcion"])
    
    columnas_precio = {}
    for tipo_precio in ["P. IR", "P. BOX", "P. VIP"]:
        col = detectar_precio_inteligente(df, tipo_precio, tipo_catalogo)
        if col:
            columnas_precio[tipo_precio] = col
    
    if not columnas_precio:
        for col in df.columns:
            if 'PRECIO' in str(col).upper():
                columnas_precio['PRECIO'] = col
                break
    
    with st.sidebar.expander(f"📋 {archivo.name[:30]}...", expanded=False):
        st.caption(f"🏷️ Tipo: **{tipo_catalogo.replace('_', ' ')}**")
        st.caption(f"🔑 SKU: `{col_sku}`")
        st.caption(f"📝 Desc: `{col_desc}`")
        if columnas_precio:
            st.caption(f"💰 Precios: `{', '.join(columnas_precio.keys())}`")
    
    return {
        'nombre': archivo.name,
        'tipo': tipo_catalogo,
        'df': df,
        'col_sku': col_sku,
        'col_desc': col_desc,
        'columnas_precio': columnas_precio
    }

def cargar_stocks(archivos, modo: str) -> List[Dict]:
    """Carga archivos de stock y filtra hojas según el modo.
       Para modo GENERAL, detecta columnas: En stock, Comprometido, Solicitado, Disponible
    """
    stocks_cargados = []
    for archivo in archivos:
        try:
            xls = pd.ExcelFile(archivo)
            hojas_a_cargar = []
            
            for hoja in xls.sheet_names:
                hoja_upper = hoja.upper()
                patrones_hoja = STOCK_HOJA_MAP.get(modo, [])
                if any(patron in hoja_upper for patron in patrones_hoja):
                    hojas_a_cargar.append(hoja)
            
            if not hojas_a_cargar and modo == ModoCotizacion.GENERAL:
                st.warning(f"⚠️ No se encontró hoja 'APRI.001' en {archivo.name}. Cargando primera hoja.")
                hojas_a_cargar = [xls.sheet_names[0]]
            
            for hoja in hojas_a_cargar:
                df = pd.read_excel(archivo, sheet_name=hoja)
                df = limpiar_cabeceras(df)
                
                col_sku = detectar_columna_inteligente(
                    df, 
                    ['SKU', 'COD', 'NUMERO', 'ARTICULO', 'NÚMERO DE ARTÍCULO', 'CODIGO', 'Número de artículo']
                )
                
                # ✅ NUEVO: Detección específica para modo GENERAL
                col_stock_total = None
                col_stock_comprometido = None
                col_stock_solicitado = None
                col_stock_disponible = None
                
                if modo == ModoCotizacion.GENERAL:
                    # Detectar columna "En stock" (Total)
                    col_stock_total = detectar_columna_inteligente(df, STOCK_COLUMNS_GENERAL["total"])
                    # Detectar columna "Comprometido"
                    col_stock_comprometido = detectar_columna_inteligente(df, STOCK_COLUMNS_GENERAL["comprometido"])
                    # Detectar columna "Solicitado"
                    col_stock_solicitado = detectar_columna_inteligente(df, STOCK_COLUMNS_GENERAL["solicitado"])
                    # ✅ Detectar columna "Disponible" (la más importante)
                    col_stock_disponible = detectar_columna_inteligente(df, STOCK_COLUMNS_GENERAL["disponible"])
                    
                    # Si no encuentra Disponible, usa la columna stock normal como fallback
                    if not col_stock_disponible:
                        col_stock_disponible = detectar_columna_inteligente(df, ['STOCK', 'DISPONIBLE', 'CANTIDAD', 'CANT'])
                        st.warning(f"⚠️ No se encontró columna 'Disponible' en {archivo.name} [{hoja}], usando stock general")
                else:
                    # Modo XIAOMI: detección normal
                    col_stock_disponible = detectar_columna_inteligente(
                        df, 
                        ['STOCK', 'DISPONIBLE', 'CANTIDAD', 'CANT', 'SALDO', 'UNIDADES']
                    )
                
                stocks_cargados.append({
                    'nombre': f"{archivo.name} [{hoja}]",
                    'df': df,
                    'col_sku': col_sku,
                    'col_stock_total': col_stock_total,
                    'col_stock_comprometido': col_stock_comprometido,
                    'col_stock_solicitado': col_stock_solicitado,
                    'col_stock_disponible': col_stock_disponible,  # ✅ Este es el stock REAL
                    'hoja': hoja,
                    'modo': modo
                })
                st.success(f"✅ {archivo.name} → Hoja: {hoja}")
                if modo == ModoCotizacion.GENERAL and col_stock_disponible:
                    st.caption(f"   📊 Stock real desde columna: `{col_stock_disponible}`")
        except Exception as e:
            st.error(f"Error en {archivo.name}: {str(e)[:100]}")
    
    return stocks_cargados

def buscar_precio(catalogos: List[Dict], sku: str, col_precio_seleccionada: str) -> Dict:
    """Busca precio en catálogos con búsqueda EXACTA."""
    sku_limpio = sku.strip().upper()
    for cat in catalogos:
        df = cat['df']
        # ✅ Búsqueda EXACTA (no contains)
        df_sku_limpio = df[cat['col_sku']].astype(str).str.strip().str.upper()
        mask = df_sku_limpio == sku_limpio
        
        if not df[mask].empty:
            row = df[mask].iloc[0]
            col_precio_real = cat['columnas_precio'].get(col_precio_seleccionada)
            if col_precio_real and col_precio_real in df.columns:
                precio = corregir_numero(row[col_precio_real])
            else:
                precio = 0.0
            return {
                'encontrado': True,
                'catalogo': cat['nombre'],
                'precio': precio,
                'descripcion': str(row[cat['col_desc']]) if pd.notna(row[cat['col_desc']]) else ""
            }
    return {'encontrado': False, 'precio': 0.0, 'descripcion': ""}

def buscar_stock(stocks: List[Dict], sku: str, modo: str) -> Tuple[int, Dict, int, int, Dict]:
    """Busca stock según el modo.
       Para modo GENERAL: usa la columna DISPONIBLE como stock real.
       Retorna: (stock_disponible, detalles_completos, stock_apri004, stock_yessica, stock_detalle_columnas)
    """
    sku_limpio = sku.strip().upper()
    stock_total_disponible = 0
    stock_apri004 = 0
    stock_yessica = 0
    detalles = {}
    stock_detalle_columnas = {}  # ✅ Para guardar breakdown de Total/Comprometido/Solicitado/Disponible
    
    for stock in stocks:
        hoja = stock['hoja'].upper()
        
        # ✅ Búsqueda EXACTA
        df_sku_limpio = stock['df'][stock['col_sku']].astype(str).str.strip().str.upper()
        mask = df_sku_limpio == sku_limpio
        
        if mask.any():
            # ✅ Suma TODAS las filas coincidentes
            for _, row in stock['df'][mask].iterrows():
                
                if modo == ModoCotizacion.XIAOMI:
                    cantidad = int(corregir_numero(row.get(stock.get('col_stock_disponible', ''), 0)))
                    if 'APRI.004' in hoja:
                        stock_apri004 += cantidad
                        detalles[f'APRI.004 ({stock["nombre"]})'] = detalles.get(f'APRI.004 ({stock["nombre"]})', 0) + cantidad
                    elif 'YESSICA' in hoja:
                        stock_yessica += cantidad
                        detalles[f'YESSICA ({stock["nombre"]})'] = detalles.get(f'YESSICA ({stock["nombre"]})', 0) + cantidad
                
                else:  # ✅ MODO GENERAL - Usa DISPONIBLE como stock real
                    if 'APRI.001' in hoja:
                        # Stock REAL desde columna Disponible
                        disponible = int(corregir_numero(row.get(stock.get('col_stock_disponible', ''), 0)))
                        stock_total_disponible += disponible
                        
                        # ✅ Capturar todas las columnas para badge detallado
                        total = int(corregir_numero(row.get(stock.get('col_stock_total', ''), 0)))
                        comprometido = int(corregir_numero(row.get(stock.get('col_stock_comprometido', ''), 0)))
                        solicitado = int(corregir_numero(row.get(stock.get('col_stock_solicitado', ''), 0)))
                        
                        # Guardar breakdown
                        origen_key = stock['nombre']
                        if origen_key not in stock_detalle_columnas:
                            stock_detalle_columnas[origen_key] = {
                                'total': 0,
                                'comprometido': 0,
                                'solicitado': 0,
                                'disponible': 0
                            }
                        stock_detalle_columnas[origen_key]['total'] += total
                        stock_detalle_columnas[origen_key]['comprometido'] += comprometido
                        stock_detalle_columnas[origen_key]['solicitado'] += solicitado
                        stock_detalle_columnas[origen_key]['disponible'] += disponible
                        
                        detalles[stock['nombre']] = detalles.get(stock['nombre'], 0) + disponible
    
    # Para modo XIAOMI, suma ambos orígenes
    if modo == ModoCotizacion.XIAOMI:
        stock_total_disponible = stock_apri004 + stock_yessica
    
    return stock_total_disponible, detalles, stock_apri004, stock_yessica, stock_detalle_columnas

def obtener_descripcion_fallback(stocks: List[Dict], sku: str) -> str:
    """Obtiene descripción de archivos de stock."""
    sku_limpio = sku.strip().upper()
    for stock in stocks:
        df = stock['df']
        df_sku_limpio = df[stock['col_sku']].astype(str).str.strip().str.upper()
        mask = df_sku_limpio == sku_limpio
        if not df[mask].empty:
            row = df[mask].iloc[0]
            for col in df.columns:
                if any(p in str(col).upper() for p in ['DESC', 'NOMBRE', 'GOODS', 'PRODUCTO', 'DESCRIPCIÓN']):
                    desc = str(row[col])
                    if desc and desc != 'nan':
                        return desc[:100]
            return f"SKU: {sku}"
    return f"SKU: {sku}"

def procesar_pedidos(pedidos: List[Dict], catalogos: List[Dict], stocks: List[Dict], 
                     col_precio: str, modo: str) -> Tuple[List[Dict], List[str]]:
    """Procesa el listado de pedidos."""
    resultados = []
    advertencias = []
    
    for pedido in pedidos:
        sku = pedido['sku']
        cant_solicitada = pedido['cantidad']
        
        precio_info = buscar_precio(catalogos, sku, col_precio)
        stock_total, stock_detalle, stock_apri004, stock_yessica, stock_columnas = buscar_stock(stocks, sku, modo)
        
        descripcion = precio_info['descripcion']
        if not descripcion or descripcion == '':
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
            estado = "❌ Sin stock disponible"
            badge_estado = "badge-danger"
            a_cotizar = 0
            total = 0
            advertencias.append(f"❌ **{sku}**: Sin stock disponible (columna DISPONIBLE = 0)")
        elif cant_solicitada > stock_total:
            a_cotizar = stock_total
            total = precio * a_cotizar
            estado = f"⚠️ Stock insuficiente ({stock_total}/{cant_solicitada})"
            badge_estado = "badge-warning"
            advertencias.append(f"⚠️ **{sku}**: Stock insuficiente. Solicitado: {cant_solicitada} | Disponible: {stock_total}")
        else:
            a_cotizar = cant_solicitada
            total = precio * a_cotizar
            estado = "✅ OK"
            badge_estado = "badge-ok"
        
        # ✅ BADGE para MODO GENERAL con breakdown completo
        if modo == ModoCotizacion.XIAOMI:
            if stock_apri004 > 0 and stock_yessica > 0:
                badge_origen = f'<span class="origin-badge origin-both">🟣 APRI.004: {stock_apri004} | 🔵 YESSICA: {stock_yessica}</span>'
            elif stock_apri004 > 0:
                badge_origen = f'<span class="origin-badge origin-apri004">🟣 APRI.004: {stock_apri004}</span>'
            elif stock_yessica > 0:
                badge_origen = f'<span class="origin-badge origin-yessica">🔵 YESSICA: {stock_yessica}</span>'
            else:
                badge_origen = '<span class="badge-danger">❌ Sin stock</span>'
        else:
            # ✅ MODO GENERAL - Badge premium con breakdown
            if stock_total > 0 and stock_columnas:
                # Construir badge con todas las columnas
                badge_parts = []
                for origen, datos in stock_columnas.items():
                    badge_parts.append(
                        f'<div style="font-size:0.7rem; line-height:1.4;">'
                        f'📦 Total: {datos["total"]} | '
                        f'🔒 Comp: {datos["comprometido"]} | '
                        f'📋 Sol: {datos["solicitado"]} | '
                        f'✅ Disp: <strong>{datos["disponible"]}</strong>'
                        f'</div>'
                    )
                badge_origen = f'<div class="origin-badge origin-both" style="background:#E8F5E9; padding:6px 12px; border-radius:12px;">{"".join(badge_parts)}</div>'
            elif stock_total > 0:
                badge_origen = f'<span class="origin-badge origin-both">✅ Stock disponible: {stock_total}</span>'
            else:
                badge_origen = '<span class="badge-danger">❌ Sin stock disponible</span>'
        
        resultados.append({
            'SKU': sku,
            'Descripción': descripcion[:80],
            'Precio': precio,
            'Pedido': cant_solicitada,
            'Stock': stock_total,
            'Stock_APRI004': stock_apri004,
            'Stock_YESSICA': stock_yessica,
            'Stock_Detalle': stock_columnas,  # ✅ Guardar detalle para uso posterior
            'Origen': badge_origen,
            'A Cotizar': a_cotizar,
            'Total': total,
            'Estado': estado,
            'Badge_Estado': badge_estado
        })
    
    return resultados, advertencias

def generar_excel(items: List[Dict], cliente: str, ruc: str) -> bytes:
    """Genera archivo Excel con formato profesional."""
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
        return "Sin stock disponible (columna DISPONIBLE = 0)"
    elif stock <= 5:
        return f"¡Stock bajo! Solo quedan {stock} unidades disponibles"
    return "Stock suficiente"

# ============================================
# CONFIGURACIÓN DE PÁGINA Y CSS COMPLETO
# ============================================

try:
    img_logo = Image.open("logo.png")
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon=img_logo, layout="wide")
except:
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon="💼", layout="wide")

# CSS COMPLETO
st.markdown("""
<style>
/* Fondo general */
.stApp { background: linear-gradient(135deg, #E8F5E9 50%, #C8E6C9 100%) !important; }
.main .block-container { background-color: transparent !important; }

/* Tipografía general */
h1, h2, h3, h4, h5, h6 { color: #0A0A0A !important; font-family: 'Segoe UI', sans-serif; }
p, div, span, label, .stMarkdown { color: #0A0A0A !important; }

/* ========== SIDEBAR MEJORADO ========== */
[data-testid="stSidebar"] { 
    background: linear-gradient(180deg, #3E2723 0%, #4E342E 100%) !important;
}

[data-testid="stSidebar"] * { 
    color: #D7CCC8 !important;
}

[data-testid="stSidebar"] .stMarkdown, 
[data-testid="stSidebar"] p, 
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p {
    color: #D7CCC8 !important;
}

[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #FFCC80 !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea,
[data-testid="stSidebar"] .stNumberInput input {
    color: #3E2723 !important;
    background-color: #FFF8E1 !important;
    border-radius: 10px !important;
    border: 1px solid #FFB74D !important;
}

[data-testid="stSidebar"] .stSelectbox > div > div {
    background-color: #FFF8E1 !important;
    border: 1px solid #FFB74D !important;
    border-radius: 10px !important;
    color: #3E2723 !important;
}

[data-testid="stSidebar"] .stFileUploader > div > div {
    background-color: #FFF8E1 !important;
    border: 1px dashed #FFB74D !important;
    border-radius: 12px !important;
}

[data-testid="stSidebar"] .stFileUploader button {
    background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%) !important;
    color: #3E2723 !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%) !important;
    color: #3E2723 !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #FFB74D 0%, #FF9800 100%) !important;
    color: #3E2723 !important;
}

/* Badges */
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

if "auth" not in st.session_state:
    st.session_state.auth = False
if "tipo_cotizacion" not in st.session_state:
    st.session_state.tipo_cotizacion = None
if "catalogos" not in st.session_state:
    st.session_state.catalogos = []
if "stocks" not in st.session_state:
    st.session_state.stocks = []
if "resultados" not in st.session_state:
    st.session_state.resultados = None
if "cotizaciones" not in st.session_state:
    st.session_state.cotizaciones = 0
if "total_prods" not in st.session_state:
    st.session_state.total_prods = 0
if "productos_seleccionados" not in st.session_state:
    st.session_state.productos_seleccionados = {}

# ============================================
# LOGIN
# ============================================

if not st.session_state.auth:
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #FFF8E1 0%, #FFE0B2 50%, #FFCC80 100%) !important; }
    .login-card { background: #FFFDF5; border-radius: 28px; padding: 2.5rem; box-shadow: 0 25px 50px rgba(0,0,0,0.15); text-align: center; border: 1px solid #FFE0B2; animation: fadeInUp 0.5s ease-out; }
    .stButton button { background: linear-gradient(135deg, #E65100 0%, #FF9800 100%) !important; color: white !important; }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(40px); } to { opacity: 1; transform: translateY(0); } }
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
                st.info("💡 Usuario: admin | Contraseña: qtc2026")
        st.markdown('<div style="margin-top:2rem; font-size:0.7rem; color:#FF9800;">⚡ QTC Smart Sales Pro</div></div>', unsafe_allow_html=True)
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
        <div style="text-align: right; background: white; padding: 8px 15px; border-radius: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
            <span style="font-weight: 600;">👤 admin</span><br>
            <span style="font-size: 0.7rem; color: #4CAF50;">Administrador</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚪 Cerrar Sesión", key="logout"):
            st.session_state.auth = False
            st.rerun()
except:
    st.title("QTC Smart Sales Pro")

st.markdown("---")

# Selección inicial de modo (solo si es None)
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

# Mostrar modo actual
if st.session_state.tipo_cotizacion == ModoCotizacion.XIAOMI:
    st.success("🔋 **Modo XIAOMI** - Stock en APRI.004 + YESSICA")
else:
    st.info("💼 **Modo GENERAL** - Stock desde columna DISPONIBLE (En stock - Comprometido - Solicitado)")

st.markdown("---")

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("### 🎯 Modo de Cotización")
    modo_actual = st.session_state.tipo_cotizacion
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        if st.button("🔋 XIAOMI", use_container_width=True, 
                    type="primary" if modo_actual == ModoCotizacion.XIAOMI else "secondary"):
            if modo_actual != ModoCotizacion.XIAOMI:
                st.session_state.tipo_cotizacion = ModoCotizacion.XIAOMI
                st.session_state.stocks = []
                st.session_state.resultados = None
                st.rerun()
    with col_m2:
        if st.button("💼 GENERAL", use_container_width=True,
                    type="primary" if modo_actual == ModoCotizacion.GENERAL else "secondary"):
            if modo_actual != ModoCotizacion.GENERAL:
                st.session_state.tipo_cotizacion = ModoCotizacion.GENERAL
                st.session_state.stocks = []
                st.session_state.resultados = None
                st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 📂 Archivos")
    
    st.markdown("**📚 Catálogos de Precios**")
    archivos_catalogos = st.file_uploader("Excel o CSV", type=['xlsx', 'xls', 'csv'], accept_multiple_files=True, key="cat_upload")
    if archivos_catalogos:
        st.session_state.catalogos = []
        for archivo in archivos_catalogos:
            resultado = cargar_catalogo(archivo)
            if resultado:
                st.session_state.catalogos.append(resultado)
                st.success(f"✅ {resultado['nombre'][:50]}")
    
    st.markdown("**📦 Reportes de Stock**")
    if st.session_state.tipo_cotizacion == ModoCotizacion.GENERAL:
        st.caption("Modo GENERAL: Busca columna **DISPONIBLE** para stock real")
    else:
        st.caption(f"Modo {st.session_state.tipo_cotizacion}: {', '.join(STOCK_HOJA_MAP[st.session_state.tipo_cotizacion])}")
    
    archivos_stock = st.file_uploader("Excel", type=['xlsx', 'xls'], accept_multiple_files=True, key="stock_upload")
    if archivos_stock:
        st.session_state.stocks = cargar_stocks(archivos_stock, st.session_state.tipo_cotizacion)

# ============================================
# TABS PRINCIPALES
# ============================================

tab_cotizacion, tab_buscar, tab_dashboard = st.tabs(["📦 Cotización", "🔍 Buscar Productos", "📊 Dashboard"])

# ---------- TAB COTIZACIÓN ----------
with tab_cotizacion:
    if not st.session_state.catalogos:
        st.warning("🌿 Carga catálogos en el panel izquierdo")
    else:
        opciones_precio = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio'].keys():
                opciones_precio.add(col)
        
        if not opciones_precio:
            st.error("⚠️ No se detectaron columnas de precio")
            col_precio = None
        else:
            col_precio = st.selectbox("💰 Columna de precio:", sorted(list(opciones_precio)))
        
        st.markdown("---")
        st.markdown("### 📝 Ingresa los productos")
        st.caption("Formato: SKU:CANTIDAD (uno por línea)")
        
        if 'skus_transferidos' in st.session_state:
        texto_defecto = "\n".join([f"{sku}:{cant}" for sku, cant in st.session_state.skus_transferidos.items()])
        # Limpiar SOLO después de usarlo en este rerun
        del st.session_state.skus_transferidos
       else:
        texto_defecto = ""
        
        texto_skus = st.text_area("", height=150, value=texto_defecto, placeholder="Ejemplo:\nRN0200046BK8:5\nCN0900009WH8:2")
        
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
                st.error("❌ Selecciona una columna de precio")
            else:
                with st.spinner("🔍 Procesando..."):
                    resultados, advertencias = procesar_pedidos(
                        pedidos, st.session_state.catalogos, st.session_state.stocks, 
                        col_precio, st.session_state.tipo_cotizacion
                    )
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
            html += '<thead><tr style="background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%); color: white;">'
            html += '<th style="padding: 10px;">SKU</th><th style="padding: 10px;">Descripción</th><th style="padding: 10px;">Precio</th>'
            html += '<th style="padding: 10px;">Pedido</th><th style="padding: 10px;">Stock</th><th style="padding: 10px;">Origen</th>'
            html += '<th style="padding: 10px;">A Cotizar</th><th style="padding: 10px;">Total</th><th style="padding: 10px;">Estado</th></tr></thead><tbody>'
            
            for item in st.session_state.resultados:
                precio_str = f"S/. {item['Precio']:,.2f}" if item['Precio'] > 0 else "Sin precio"
                total_str = f"S/. {item['Total']:,.2f}"
                stock_clase = obtener_clase_stock(item['Stock'])
                stock_icono = obtener_icono_stock(item['Stock'])
                stock_html = f'<span class="{stock_clase}" title="{obtener_mensaje_stock(item["Stock"])}">{stock_icono} {item["Stock"]}</span>'
                
                html += f'<tr style="border-bottom: 1px solid #E8F5E9;">'
                html += f'<td style="padding: 10px; font-family: monospace;">{item["SKU"]}</td>'
                html += f'<td style="padding: 10px;">{item["Descripción"][:60]}{"..." if len(item["Descripción"]) > 60 else ""}</td>'
                html += f'<td style="padding: 10px; text-align: center;">{precio_str}</td>'
                html += f'<td style="padding: 10px; text-align: center;">{item["Pedido"]}</td>'
                html += f'<td style="padding: 10px; text-align: center;">{stock_html}</td>'
                html += f'<td style="padding: 10px;">{item["Origen"]}</td>'
                html += f'<td style="padding: 10px; text-align: center;"><strong>{item["A Cotizar"]}</strong></td>'
                html += f'<td style="padding: 10px; text-align: center;"><strong>{total_str}</strong></td>'
                html += f'<td style="padding: 10px; text-align: center;"><span class="{item["Badge_Estado"]}">{item["Estado"]}</span></td>'
                html += '</tr>'
            
            html += '</tbody></table></div>'
            st.markdown(html, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### ✏️ Ajustar cantidades")
            
            df_ajuste = pd.DataFrame(st.session_state.resultados)[['SKU', 'Descripción', 'Precio', 'Stock', 'A Cotizar']].copy()
            df_ajuste['Precio'] = df_ajuste['Precio'].apply(lambda x: f"S/. {x:,.2f}" if x > 0 else "Sin precio")
            
            edited_df = st.data_editor(
                df_ajuste,
                column_config={
                    "SKU": st.column_config.TextColumn("SKU", disabled=True, width="small"),
                    "Descripción": st.column_config.TextColumn("Descripción", disabled=True, width="large"),
                    "Precio": st.column_config.TextColumn("Precio", disabled=True, width="small"),
                    "Stock": st.column_config.NumberColumn("Stock", disabled=True, width="small"),
                    "A Cotizar": st.column_config.NumberColumn("A Cotizar", min_value=0, step=1, required=True, width="small"),
                },
                use_container_width=True,
                hide_index=True,
                key="ajuste_editor"
            )
            
            for idx, row in edited_df.iterrows():
                if idx < len(st.session_state.resultados):
                    nueva_cant = row['A Cotizar']
                    stock_disponible = st.session_state.resultados[idx]['Stock']
                    if nueva_cant > stock_disponible and stock_disponible > 0:
                        nueva_cant = stock_disponible
                        st.warning(f"⚠️ **{st.session_state.resultados[idx]['SKU']}**: Máximo {stock_disponible} unidades")
                    
                    st.session_state.resultados[idx]['A Cotizar'] = nueva_cant
                    if st.session_state.resultados[idx]['Precio'] > 0:
                        st.session_state.resultados[idx]['Total'] = st.session_state.resultados[idx]['Precio'] * nueva_cant
                        st.session_state.resultados[idx]['Estado'] = "✅ OK" if nueva_cant > 0 else "⚠️ Sin stock"
                        st.session_state.resultados[idx]['Badge_Estado'] = "badge-ok" if nueva_cant > 0 else "badge-warning"
            
            items_validos = [r for r in st.session_state.resultados if r['A Cotizar'] > 0 and r['Precio'] > 0]
            items_con_issues = [r for r in st.session_state.resultados if r['A Cotizar'] == 0 or r['Precio'] == 0]
            total_general = sum(r['Total'] for r in items_validos)
            
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("✅ A cotizar", len(items_validos))
            col_m2.metric("💰 Total", f"S/. {total_general:,.2f}")
            col_m3.metric("⚠️ Excluidos", len(items_con_issues))
            
            if items_validos:
                st.markdown("---")
                st.markdown("### 📥 Generar Cotización")
                col_cli1, col_cli2 = st.columns(2)
                with col_cli1:
                    cliente = st.text_input("🏢 Cliente", "CLIENTE NUEVO", key="cliente_nombre")
                with col_cli2:
                    ruc_cliente = st.text_input("📋 RUC/DNI", "-", key="cliente_ruc")
                
                if st.button("📥 GENERAR EXCEL", use_container_width=True, type="primary"):
                    items_excel = [{'sku': r['SKU'], 'desc': r['Descripción'], 'cant': r['A Cotizar'], 'p_u': r['Precio'], 'total': r['Total']} for r in items_validos]
                    excel = generar_excel(items_excel, cliente, ruc_cliente)
                    st.download_button("💾 DESCARGAR", data=excel, file_name=f"Cotizacion_{cliente}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", use_container_width=True)
                    st.session_state.cotizaciones += 1
                    st.session_state.total_prods = len(items_validos)
                    st.balloons()
                    st.success("✅ Cotización generada")

# ---------- TAB BUSCAR ----------
with tab_buscar:
    st.markdown("### 🔍 Buscar Productos")
    if not st.session_state.catalogos:
        st.warning("🌿 Primero carga catálogos")
    else:
        # Inicializar carrito si no existe
        if 'carrito_seleccionados' not in st.session_state:
            st.session_state.carrito_seleccionados = {}

        opciones_precio_buscar = {col for cat in st.session_state.catalogos for col in cat['columnas_precio'].keys()}
        col_precio_consulta = st.selectbox("💰 Precio: ", ["(No mostrar)"] + sorted(list(opciones_precio_buscar)), key="precio_busqueda")
        
        # 🔹 OPTIMIZACIÓN: Usar botón para buscar y evitar reruns por cada tecla
        col_busq1, col_busq2 = st.columns([3, 1])
        with col_busq1:
            busqueda = st.text_input("🔎 Buscar: ", placeholder="SKU o descripción", key="texto_busqueda")
        with col_busq2:
            btn_buscar = st.button("🔍 Buscar", use_container_width=True)

        if btn_buscar and busqueda and len(busqueda) >= 2:
            with st.spinner("🔍 Buscando..."):
                precio_seleccionado = None if col_precio_consulta == "(No mostrar)" else col_precio_consulta
                resultados_busqueda = []
                skus_vistos = set()
                
                for cat in st.session_state.catalogos:
                    df = cat['df']
                    mask = df[cat['col_sku']].astype(str).str.contains(busqueda, case=False, na=False)
                    mask |= df[cat['col_desc']].astype(str).str.contains(busqueda, case=False, na=False)
                    
                    for _, row in df[mask].iterrows():
                        sku = str(row[cat['col_sku']])
                        if sku in skus_vistos: continue
                        skus_vistos.add(sku)
                        
                        precio = None
                        if precio_seleccionado:
                            col_p = cat['columnas_precio'].get(precio_seleccionado)
                            if col_p: precio = corregir_numero(row[col_p])
                            
                        stock_total, _, stock_apri, stock_yes, stock_col = buscar_stock(st.session_state.stocks, sku, st.session_state.tipo_cotizacion)
                        
                        resultados_busqueda.append({
                            'SKU': sku, 'Descripcion': str(row[cat['col_desc']])[:100],
                            'Precio': precio, 'Stock_Total': stock_total,
                            'Stock_APRI004': stock_apri, 'Stock_YESSICA': stock_yes, 'Stock_Detalle': stock_col
                        })

            if resultados_busqueda:
                st.success(f"✅ {len(resultados_busqueda)} resultados")
                for res in resultados_busqueda:
                    stock_clase = obtener_clase_stock(res['Stock_Total'])
                    stock_icono = obtener_icono_stock(res['Stock_Total'])
                    
                    stock_detalle_html = ''
                    if st.session_state.tipo_cotizacion == ModoCotizacion.GENERAL and res.get('Stock_Detalle'):
                        badge_detalle = '<br>'.join([
                            f'📦 Total: {d["total"]} | 🔒 Comp: {d["comprometido"]} | 📋 Sol: {d["solicitado"]} | ✅ Disp: {d["disponible"]}'
                            for d in res['Stock_Detalle'].values()
                        ])
                        stock_detalle_html = f'<div style="font-size:0.7rem; margin-top:4px;">{badge_detalle}</div>'
                    
                    st.markdown(f"""
                     <div style="background: white; border-radius: 12px; padding: 1rem; margin: 0.5rem 0; border-left: 4px solid #4CAF50;">
                         <div><strong>📦 {res['SKU']}</strong><br><span style="font-size:0.85rem;">{res['Descripcion']}</span><br>
                         <span style="color:#4CAF50;">{f'S/. {res["Precio"]:,.2f}' if res["Precio"] else "💰 Sin precio"}</span></div>
                         <div style="margin-top:8px;"><span class="{stock_clase}">{stock_icono} Stock: {res['Stock_Total']}</span>{stock_detalle_html}</div>
                     </div>
                    """, unsafe_allow_html=True)
                    
                    # 🔹 FIX: Sincronización directa sin acumulación
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown("**➕ Cantidad**")
                    with col2:
                        cant_inicial = st.session_state.carrito_seleccionados.get(res['SKU'], 0)
                        nueva_cant = st.number_input(
                            "Cant", min_value=0, max_value=999, value=cant_inicial, 
                            key=f"qty_{res['SKU']}", label_visibility="collapsed"
                        )
                        # Solo actualiza si cambió para evitar reruns innecesarios
                        if nueva_cant != cant_inicial:
                            st.session_state.carrito_seleccionados[res['SKU']] = nueva_cant
                            st.rerun()
                    st.divider()

        # 🔹 Botón de transferencia seguro
        if st.session_state.carrito_seleccionados:
            st.markdown("---")
            st.markdown(f"### 🛒 Carrito ({len(st.session_state.carrito_seleccionados)} productos)")
            st.dataframe(pd.DataFrame([{'SKU': k, 'Cantidad': v} for k, v in st.session_state.carrito_seleccionados.items()]), use_container_width=True)
            
            if st.button("📋 TRANSFERIR A COTIZACIÓN", use_container_width=True, type="primary"):
                st.session_state.skus_transferidos = st.session_state.carrito_seleccionados.copy()
                st.session_state.carrito_seleccionados = {}
                st.success("✅ Transferido correctamente")
                # Streamlit >= 1.36.0 soporta st.switch_tab
                try: st.switch_tab("📦 Cotización")
                except: st.warning("👉 Ve manualmente a la pestaña 📦 Cotización y presiona PROCESAR")
                st.rerun()
                    # Badge detallado para modo GENERAL en búsqueda
                    if st.session_state.tipo_cotizacion == ModoCotizacion.GENERAL and res.get('Stock_Detalle'):
                        badge_detalle = '<br>'.join([
                            f'📦 Total: {d["total"]} | 🔒 Comp: {d["comprometido"]} | 📋 Sol: {d["solicitado"]} | ✅ Disp: {d["disponible"]}'
                            for d in res['Stock_Detalle'].values()
                        ])
                        stock_detalle_html = f'<div style="font-size:0.7rem; margin-top:4px;">{badge_detalle}</div>'
                    else:
                        stock_detalle_html = ''
                    
                    st.markdown(f"""
                    <div style="background: white; border-radius: 12px; padding: 1rem; margin: 0.5rem 0; border-left: 4px solid #4CAF50;">
                        <div><strong>📦 {res['SKU']}</strong><br><span style="font-size:0.85rem;">{res['Descripcion']}</span><br>
                        <span style="color:#4CAF50;">{f'S/. {res["Precio"]:,.2f}' if res["Precio"] else "💰 Sin precio"}</span></div>
                        <div style="margin-top:8px;"><span class="{stock_clase}">{stock_icono} Stock disponible: {res['Stock_Total']}</span>{stock_detalle_html}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown("**➕ Agregar**")
                    with col2:
                        cantidad = st.number_input("Cant", min_value=0, max_value=999, value=0, key=f"add_{res['SKU']}", label_visibility="collapsed")
                        if cantidad > 0:
                            st.session_state.productos_seleccionados[res['SKU']] = st.session_state.productos_seleccionados.get(res['SKU'], 0) + cantidad
                    st.divider()
        
        if st.session_state.productos_seleccionados:
            st.markdown("---")
            st.markdown(f"### ✅ Seleccionados ({len(st.session_state.productos_seleccionados)})")
            st.dataframe(pd.DataFrame([{'SKU': k, 'Cantidad': v} for k, v in st.session_state.productos_seleccionados.items()]), use_container_width=True)
            
            if st.button("📋 TRANSFERIR A COTIZACIÓN", use_container_width=True, type="primary"):
                st.session_state.skus_transferidos = st.session_state.productos_seleccionados.copy()
                st.session_state.productos_seleccionados = {}
                st.success("✅ Transferido! Ve a Cotización y presiona PROCESAR")

# ---------- TAB DASHBOARD ----------
with tab_dashboard:
    st.markdown("### 📊 Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("📄 Cotizaciones", st.session_state.get('cotizaciones', 0))
    col2.metric("🌿 Productos", st.session_state.get('total_prods', 0))
    col3.metric("📚 Catálogos", len(st.session_state.get('catalogos', [])))
    
    st.markdown("---")
    st.markdown("### 📋 Catálogos Cargados")
    for cat in st.session_state.get('catalogos', []):
        st.markdown(f"- {cat['nombre']} *({cat.get('tipo', 'general').replace('_', ' ')})*")
    
    st.markdown("---")
    st.markdown("### 🎯 Reglas actuales")
    if st.session_state.tipo_cotizacion == ModoCotizacion.XIAOMI:
        st.markdown("🔋 **XIAOMI** → APRI.004 + YESSICA")
    else:
        st.markdown("💼 **GENERAL** → Columna **DISPONIBLE** = Stock real")
        st.markdown("   - En stock (Total) - Comprometido - Solicitado = Disponible")

st.markdown("---")
st.markdown("*💚 QTC Smart Sales Pro - Sistema Profesional de Cotización*")
