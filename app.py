# app.py - QTC Smart Sales Pro v2.2
import streamlit as st
import pandas as pd
import re
import io
from datetime import datetime
import warnings
from typing import List, Dict, Optional
from difflib import SequenceMatcher

warnings.filterwarnings('ignore')

# ============================================
# CONFIGURACIÓN & CREDENCIALES
# ============================================

st.set_page_config(
    page_title="QTC Smart Sales Pro",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

USERS = {
    "admin": "qtc2026",
    "kimqtc": "qtc2412"
}

# ============================================
# CSS MINIMALISTA MODERNO
# ============================================

st.markdown("""
<style>
    :root {
        --bg-main: #f8fafc;
        --bg-card: #ffffff;
        --bg-sidebar: #f1f5f9;
        --text-primary: #0f172a;
        --text-secondary: #64748b;
        --accent: #0f172a;
        --accent-hover: #1e293b;
        --border: #e2e8f0;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.06);
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
    }
    
    .stApp { background: var(--bg-main); color: var(--text-primary); }
    [data-testid="stSidebar"] { background: var(--bg-sidebar); border-right: 1px solid var(--border); }
    [data-testid="stSidebar"] * { color: var(--text-primary) !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: var(--accent) !important; }
    
    .card {
        background: var(--bg-card); border-radius: 12px; padding: 1rem;
        box-shadow: var(--shadow-sm); border: 1px solid var(--border);
        transition: all 0.2s ease;
    }
    .card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
    .card, .card * { color: var(--text-primary) !important; }
    .card strong { font-weight: 600; }
    .card .desc { font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.25rem; }
    
    .badge {
        display: inline-block; padding: 0.2rem 0.6rem; border-radius: 20px;
        font-size: 0.7rem; font-weight: 600; margin: 2px;
    }
    .badge.green { background: #dcfce7; color: #166534; }
    .badge.yellow { background: #fef3c7; color: #92400e; }
    .badge.red { background: #fee2e2; color: #991b1b; }
    .badge.gray { background: #f1f5f9; color: #475569; }
    .badge.info { background: #e0f2fe; color: #0369a1; }
    
    .login-box {
        background: white; border-radius: 16px; padding: 2.5rem;
        box-shadow: var(--shadow-md); max-width: 400px; margin: 0 auto;
        border: 1px solid var(--border);
    }
    
    .counter {
        display: flex; gap: 1rem; flex-wrap: wrap; background: white;
        padding: 1rem; border-radius: 12px; border: 1px solid var(--border);
    }
    .counter-item { background: #f8fafc; padding: 0.5rem 1rem; border-radius: 8px; font-size: 0.85rem; }
    .counter-item span { font-weight: 600; }
    
    .stButton > button {
        background: var(--accent); color: white; border: none;
        border-radius: 8px; padding: 0.5rem 1rem; font-weight: 500;
        transition: all 0.2s;
    }
    .stButton > button:hover { background: var(--accent-hover); transform: translateY(-1px); }
    .stButton > button:disabled { background: #cbd5e1; color: #64748b; }
    
    input, textarea, .stSelectbox, .stNumberInput {
        background: white !important; border: 1px solid var(--border) !important;
        border-radius: 8px !important; color: var(--text-primary) !important;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0; background: white; border: 1px solid var(--border);
        color: var(--text-secondary); font-weight: 500;
    }
    .stTabs [aria-selected="true"] { background: var(--accent); color: white; border-color: var(--accent); }
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNCIONES UTILITARIAS
# ============================================

def corregir_numero(valor) -> float:
    if pd.isna(valor) or str(valor).strip() in ["", "0", "0.0", "-"]: return 0.0
    s = str(valor).replace('S/', '').replace('$', '').replace(' ', '').strip()
    if ',' in s and '.' in s: s = s.replace(',', '')
    elif ',' in s:
        partes = s.split(',')
        if len(partes[-1]) <= 2: s = s.replace(',', '.')
        else: s = s.replace(',', '')
    s = re.sub(r'[^\d.]', '', s)
    try: return float(s)
    except: return 0.0

def limpiar_cabeceras(df: pd.DataFrame) -> pd.DataFrame:
    for i in range(min(15, len(df))):
        fila = [str(x).upper().strip() for x in df.iloc[i].values]
        if any(h in item for h in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO'] for item in fila):
            df.columns = [str(c).strip().upper() for c in df.iloc[i]]
            return df.iloc[i+1:].reset_index(drop=True)
    return df

def cargar_archivo(uploaded_file) -> Optional[pd.DataFrame]:
    try:
        if uploaded_file.name.lower().endswith('.csv'):
            try: df = pd.read_csv(uploaded_file, encoding='utf-8')
            except: df = pd.read_csv(uploaded_file, encoding='latin-1')
        else: df = pd.read_excel(uploaded_file)
        return limpiar_cabeceras(df)
    except Exception as e:
        st.error(f"Error al cargar: {str(e)[:100]}")
        return None

def detectar_columna_sku(df: pd.DataFrame) -> str:
    for col in df.columns:
        if any(k in col for k in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO']): return col
    return df.columns[0]

def detectar_columna_descripcion(df: pd.DataFrame) -> Optional[str]:
    for col in df.columns:
        if any(k in col for k in ['DESC', 'NOMBRE', 'PRODUCTO', 'GOODS']): return col
    return None

def detectar_columnas_precio(df: pd.DataFrame) -> Dict:
    precios = {}
    mapeo = {'P. IR': ['IR', 'MAYORISTA', 'MAYOR'], 
             'P. BOX': ['BOX', 'CAJA'], 
             'P. VIP': ['VIP']}
    for key, patrones in mapeo.items():
        for col in df.columns:
            if any(p in col for p in patrones):
                precios[key] = col
                break
    if not precios and any('PRECIO' in c for c in df.columns):
        precios['P. VIP'] = next(c for c in df.columns if 'PRECIO' in c)
    return precios

def cargar_catalogo(archivo) -> Optional[Dict]:
    df = cargar_archivo(archivo)
    return None if df is None else {
        'nombre': archivo.name, 'df': df,
        'col_sku': detectar_columna_sku(df),
        'col_desc': detectar_columna_descripcion(df),
        'precios': detectar_columnas_precio(df)
    }

def cargar_stock(archivos, modo: str) -> List[Dict]:
    stocks = []
    for archivo in archivos:
        try:
            xls = pd.ExcelFile(archivo)
            for hoja in xls.sheet_names:
                h = hoja.upper()
                if modo == "XIAOMI" and not any(x in h for x in ['APRI', 'YESSICA', 'SOFIA', 'DJI']): continue
                if modo == "GENERAL" and not any(x in h for x in ['APRI.001', 'YESSICA']): continue
                
                df = pd.read_excel(archivo, sheet_name=hoja)
                df = limpiar_cabeceras(df)
                
                # Normalización inteligente de columna de cantidad
                col_cant = next((c for c in df.columns if any(x in c.upper() for x in ['DISPONIBLE', 'STOCK', 'CANT', 'UNIDADES'])), None)
                if col_cant and col_cant.upper() != 'DISPONIBLE':
                    df.rename(columns={col_cant: 'DISPONIBLE'}, inplace=True)
                    
                stocks.append({'nombre': f"{archivo.name} [{hoja}]", 'df': df, 'col_sku': detectar_columna_sku(df), 'hoja': hoja})
                st.success(f"✅ {archivo.name} → {hoja}")
        except Exception as e:
            st.error(f"Error stock: {str(e)[:80]}")
    return stocks

def calcular_similitud(t1: str, t2: str) -> float:
    if not t1 or not t2: return 0.0
    t1, t2 = t1.lower().strip(), t2.lower().strip()
    if t1 == t2: return 100.0
    w1, w2 = set(t1.split()), set(t2.split())
    union = len(w1.union(w2))
    if union == 0: return 0.0
    return round(((len(w1.intersection(w2))/union * 0.7) + SequenceMatcher(None, t1, t2).ratio() * 0.3) * 100, 1)

# ============================================
# LÓGICA DE BÚSQUEDA & PRECIOS
# ============================================

def buscar_producto(sku: str, catalogos: List[Dict], stocks: List[Dict], precio_key: str, buscar_alt: bool = True) -> Dict:
    sku_l = sku.strip().upper()
    precio, desc, precio_inferido = 0.0, "", False
    
    # 1. Buscar en catálogo de precios
    for cat in catalogos:
        df = cat['df']
        mask = df[cat['col_sku']].astype(str).str.strip().str.upper() == sku_l
        if mask.any():
            row = df[mask].iloc[0]
            if precio_key in cat['precios']:
                precio = corregir_numero(row[cat['precios'][precio_key]])
            if cat['col_desc']:
                desc = str(row[cat['col_desc']])[:200]
            break
            
    if not desc: desc = f"SKU: {sku}"
    
    # 2. Calcular stock
    s_y, s_a4, s_a1 = 0, 0, 0
    for stck in stocks:
        df = stck['df']
        mask = df[stck['col_sku']].astype(str).str.strip().str.upper() == sku_l
        if mask.any():
            cant = int(corregir_numero(df.loc[mask, 'DISPONIBLE'].sum())) if 'DISPONIBLE' in df.columns else 0
            h = stck['hoja'].upper()
            if 'YESSICA' in h: s_y += cant
            elif 'APRI.004' in h: s_a4 += cant
            elif 'APRI.001' in h: s_a1 += cant
            
    stock_total = s_y + s_a4 + s_a1
    
    # 3. Fallback: Si hay stock pero no precio, buscar por descripción
    if stock_total > 0 and precio == 0 and buscar_alt:
        for cat in catalogos:
            for _, row in cat['df'].iterrows():
                sku_alt = str(row[cat['col_sku']]).strip().upper()
                if sku_alt == sku_l: continue
                desc_alt = str(row[cat['col_desc']])[:200] if cat['col_desc'] else ""
                sim = calcular_similitud(desc, desc_alt)
                if sim >= 80 and cat['precios'].get(precio_key):
                    precio = corregir_numero(row[cat['precios'][precio_key]])
                    desc = desc  # Mantenemos descripción original
                    precio_inferido = True
                    break
    
    res = {
        'sku': sku, 'descripcion': desc, 'precio': precio,
        'stock_yessica': s_y, 'stock_apri004': s_a4, 'stock_apri001': s_a1,
        'stock_total': stock_total, 'tiene_stock': stock_total > 0,
        'tiene_precio': precio > 0, 'precio_inferido': precio_inferido,
        'alternativas': []
    }
    
    # 4. Alternativas si no hay stock
    if not res['tiene_stock'] and buscar_alt and desc and desc != f"SKU: {sku}":
        for cat in catalogos:
            for _, row in cat['df'].iterrows():
                sku_alt = str(row[cat['col_sku']]).strip().upper()
                if sku_alt == sku_l: continue
                desc_alt = str(row[cat['col_desc']])[:200] if cat['col_desc'] else ""
                sim = calcular_similitud(desc, desc_alt)
                if sim >= 70:
                    alt = buscar_producto(sku_alt, catalogos, stocks, precio_key, buscar_alt=False)
                    if alt['tiene_stock']:
                        res['alternativas'].append({**alt, 'similitud': sim})
        res['alternativas'].sort(key=lambda x: (-x['similitud'], -x['stock_total']))
        res['alternativas'] = res['alternativas'][:5]
        
    return res

def badge_stock(s_y, s_a4, s_a1):
    parts = []
    if s_y > 0: parts.append(f'<span class="badge green">YESSICA: {s_y}</span>')
    if s_a4 > 0: parts.append(f'<span class="badge yellow">APRI.004: {s_a4}</span>')
    if s_a1 > 0: parts.append(f'<span class="badge red">APRI.001: {s_a1}</span>')
    return ' '.join(parts) if parts else '<span class="badge gray">Sin stock</span>'

def generar_excel(items: List[Dict], cliente: str, ruc: str) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pd.DataFrame(items).to_excel(writer, sheet_name='Cotizacion', index=False, startrow=5)
        wb, ws = writer.book, writer.sheets['Cotizacion']
        
        fmt_hdr = wb.add_format({'bg_color': '#0f172a', 'bold': True, 'border': 1, 'align': 'center', 'font_color': 'white'})
        fmt_money = wb.add_format({'num_format': '"S/." #,##0.00', 'border': 1, 'align': 'right'})
        fmt_border = wb.add_format({'border': 1})
        fmt_bold = wb.add_format({'bold': True})
        
        for c, v in [('A1', 'FECHA:'), ('B1', datetime.now().strftime("%d/%m/%Y")), ('A2', 'CLIENTE:'), ('B2', cliente.upper()), ('A3', 'RUC:'), ('B3', ruc)]:
            ws.write(c, v, fmt_bold)
            
        headers = ['SKU', 'Descripción', 'Cantidad', 'Precio Unit.', 'Total']
        for i, h in enumerate(headers): ws.write(5, i, h, fmt_hdr)
        
        for idx, item in enumerate(items):
            row = idx + 6
            ws.write(row, 0, item['sku'], fmt_border)
            ws.write(row, 1, item['descripcion'], fmt_border)
            ws.write(row, 2, item['cantidad'], fmt_border)
            ws.write(row, 3, item['precio'], fmt_money)
            ws.write(row, 4, item['total'], fmt_money)
            
        total_row = len(items) + 6
        ws.write(total_row, 3, 'TOTAL S/.', fmt_hdr)
        ws.write(total_row, 4, sum(i['total'] for i in items), fmt_money)
    return output.getvalue()

# ============================================
# AUTENTICACIÓN & UI
# ============================================

for key in ['auth', 'modo', 'precio_key', 'catalogos', 'stocks', 'carrito']:
    if key not in st.session_state: st.session_state[key] = False if key=='auth' else "XIAOMI" if key=='modo' else "P. VIP" if key=='precio_key' else []

if not st.session_state.auth:
    st.markdown("""<style>.stApp { background: #e2e8f0 !important; }</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; margin-bottom:1rem;'>📦 QTC Sales</h2>", unsafe_allow_html=True)
        u = st.text_input("Usuario", placeholder="Ingresa tu usuario")
        p = st.text_input("Contraseña", type="password", placeholder="••••••••")
        if st.button("Iniciar Sesión", use_container_width=True):
            if u in USERS and USERS[u] == p:
                st.session_state.auth = True; st.rerun()
            else: st.error("Credenciales incorrectas")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# HEADER
c1, c2 = st.columns([0.8, 4])
with c1: st.markdown("<h2 style='color:#0f172a;'>📦 QTC</h2>", unsafe_allow_html=True)
with c2:
    st.markdown("# Smart Sales Pro")
    st.caption("Cotizaciones rápidas • Stock unificado • Exportación profesional")
    if st.button("🚪 Cerrar Sesión"): st.session_state.auth = False; st.session_state.carrito = []; st.rerun()

# SIDEBAR
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    st.session_state.modo = st.radio("Modo", ["XIAOMI", "GENERAL"], index=0 if st.session_state.modo=="XIAOMI" else 1)
    st.session_state.precio_key = st.radio("💰 Nivel", ["P. VIP", "P. BOX", "P. IR"], index=0)
    
    st.markdown("### 📂 Archivos")
    cats = st.file_uploader("Catálogos de precios", type=['xlsx','xls','csv'], accept_multiple_files=True, key="cat")
    if cats:
        st.session_state.catalogos = []
        for c in cats:
            res = cargar_catalogo(c)
            if res: st.session_state.catalogos.append(res); st.success(f"✅ {c.name}")
            
    st.session_files = st.file_uploader("Reportes de Stock", type=['xlsx','xls'], accept_multiple_files=True, key="stk")
    if st.session_files:
        st.session_state.stocks = cargar_stock(st.session_files, st.session_state.modo)
        
    if st.session_state.carrito:
        st.markdown("---")
        st.metric("🛒 Carrito", f"{len(st.session_state.carrito)} items")
        if st.button("Limpiar carrito", use_container_width=True): st.session_state.carrito = []; st.rerun()

# TABS
tab1, tab2, tab3 = st.tabs(["📦 Carga Masiva", "🔍 Búsqueda", "🛒 Cotización"])

with tab1:
    st.markdown("### Carga Masiva de SKUs")
    st.caption("Formato: `SKU:CANTIDAD` (uno por línea)")
    txt = st.text_area("", height=150, placeholder="Ej:\nRN9401276NA8:100\nCN0200047BK8:50")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Procesar", type="primary", use_container_width=True):
            if txt and st.session_state.catalogos and st.session_state.stocks:
                pedidos = []
                for l in txt.strip().split('\n'):
                    if ':' in l:
                        try:
                            s, c = l.split(':')
                            if int(c.strip())>0: pedidos.append({'sku':s.strip().upper(), 'cant':int(c.strip())})
                        except: pass
                
                if pedidos:
                    with st.spinner("Analizando stock y precios..."):
                        res_bulk = []
                        for p in pedidos:
                            prod = buscar_producto(p['sku'], st.session_state.catalogos, st.session_state.stocks, st.session_state.precio_key)
                            c_final = min(p['cant'], prod['stock_total']) if prod['tiene_stock'] and prod['tiene_precio'] else 0
                            estado = "✅ Listo" if c_final==p['cant'] else f"⚠️ {c_final}/{p['cant']}" if c_final>0 else "❌ No cotizable"
                            res_bulk.append({**prod, 'pedida': p['cant'], 'cotizar': c_final, 'estado': estado})
                        st.session_state.resultados_bulk = res_bulk
                        st.rerun()
    with c2:
        if st.button("Agregar al carrito", use_container_width=True):
            if hasattr(st.session_state, 'resultados_bulk'):
                added = sum(1 for r in st.session_state.resultados_bulk if r['cotizar']>0 and st.session_state.carrito.append({
                    'sku': r['sku'], 'descripcion': r['descripcion'], 'cantidad': r['cotizar'],
                    'precio': r['precio'], 'total': r['precio']*r['cotizar'],
                    'stock_yessica': r['stock_yessica'], 'stock_apri004': r['stock_apri004'], 'stock_apri001': r['stock_apri001']
                }) or True)
                st.success(f"✅ {added} productos agregados"); st.rerun()
                
    if hasattr(st.session_state, 'resultados_bulk'):
        st.markdown('<div class="counter">', unsafe_allow_html=True)
        for k,v,c in [("📋 Ingresados", len(st.session_state.resultados_bulk), "#0f172a"), ("✅ Cotizables", sum(1 for r in st.session_state.resultados_bulk if r['cotizar']>0), "#10b981"), ("❌ Rechazados", sum(1 for r in st.session_state.resultados_bulk if r['cotizar']==0), "#ef4444")]:
            st.markdown(f'<div class="counter-item"><span>{k}: {v}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        for r in st.session_state.resultados_bulk:
            badge_inf = '<span class="badge info">🔍 Precio inferido</span> ' if r.get('precio_inferido') else ''
            st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <strong>📦 {r['sku']}</strong>
                    <span style="font-size:0.85rem; color:{'#10b981' if 'Listo' in r['estado'] else '#ef4444'}">{r['estado']}</span>
                </div>
                <div class="desc">{r['descripcion']}</div>
                <div style="margin-top:8px; display:flex; justify-content:space-between; align-items:center;">
                    <span>💰 S/ {r['precio']:,.2f} | 📦 Total: {r['stock_total']}</span>
                    <span style="font-weight:600;">A cotizar: {r['cotizar']}</span>
                </div>
                <div style="margin-top:6px;">{badge_inf}{badge_stock(r['stock_yessica'], r['stock_apri004'], r['stock_apri001'])}</div>
            </div>""", unsafe_allow_html=True)

with tab2:
    q = st.text_input("", placeholder="Buscar por SKU o descripción...")
    if q and len(q)>=2 and st.session_state.catalogos and st.session_state.stocks:
        with st.spinner("Buscando..."):
            vistos, res = set(), []
            for cat in st.session_state.catalogos:
                mask = cat['df'][cat['col_sku']].astype(str).str.contains(q, case=False, na=False)
                if cat['col_desc']: mask |= cat['df'][cat['col_desc']].astype(str).str.contains(q, case=False, na=False)
                for _, row in cat['df'][mask].iterrows():
                    s = str(row[cat['col_sku']]).strip().upper()
                    if s not in vistos: vistos.add(s); res.append(buscar_producto(s, st.session_state.catalogos, st.session_state.stocks, st.session_state.precio_key))
                    
            if res:
                for r in res:
                    badge_inf = '<span class="badge info">🔍 Precio inferido</span> ' if r.get('precio_inferido') else ''
                    st.markdown(f"""
                    <div class="card">
                        <strong>📦 {r['sku']}</strong> 
                        <span style="background:{'#dcfce7' if r['tiene_stock'] else '#fee2e2'}; padding:2px 8px; border-radius:12px; font-size:0.7rem; margin-left:8px;">
                            {'Con Stock' if r['tiene_stock'] else 'Sin Stock'}
                        </span><br>
                        <span class="desc">{r['descripcion']}</span>
                        <div style="margin-top:6px;">{badge_inf}{badge_stock(r['stock_yessica'], r['stock_apri004'], r['stock_apri001'])}</div>
                    </div>""", unsafe_allow_html=True)
                    
                    if r['alternativas']:
                        st.markdown("<div style='color:#f59e0b; font-weight:600; margin:0.5rem 0;'>💡 Alternativas sugeridas:</div>", unsafe_allow_html=True)
                        for alt in r['alternativas']:
                            st.markdown(f"""
                            <div class="card" style="border-left: 3px solid #f59e0b; margin-left:1rem;">
                                <strong>{alt['sku']}</strong> <span style="color:#f59e0b; font-size:0.8rem;">({alt['similitud']}%)</span><br>
                                <span class="desc">{alt['descripcion'][:60]}</span>
                                <div style="margin-top:4px;">{badge_stock(alt['stock_yessica'], alt['stock_apri004'], alt['stock_apri001'])}</div>
                            </div>""", unsafe_allow_html=True)
                            
                    if r['tiene_stock'] and r['tiene_precio']:
                        c1, c2 = st.columns([1,3])
                        with c1: cant = st.number_input("Cant", 0, r['stock_total'], 1, key=f"b_{r['sku']}")
                        with c2:
                            if cant>0 and st.button("➕ Agregar", key=f"a_{r['sku']}"):
                                st.session_state.carrito.append({**{k:r[k] for k in ['sku','descripcion','precio','stock_yessica','stock_apri004','stock_apri001']}, 'cantidad':cant, 'total':r['precio']*cant})
                                st.success(f"✅ Agregado {cant}x {r['sku']}"); st.rerun()

with tab3:
    if not st.session_state.carrito:
        st.info("El carrito está vacío. Agrega productos desde las otras pestañas.")
    else:
        total_gen = 0
        for idx, it in enumerate(st.session_state.carrito):
            c1, c2, c3, c4, c5, c6 = st.columns([2,3,1,1,1,0.5])
            with c1: st.write(f"**{it['sku']}**")
            with c2: st.write(it['descripcion'][:50])
            with c3:
                nc = st.number_input("", 0, it['stock_yessica']+it['stock_apri004']+it['stock_apri001'], it['cantidad'], step=1, key=f"e_{idx}_{it['sku']}", label_visibility="collapsed")
                if nc != it['cantidad']: it['cantidad']=nc; it['total']=it['precio']*nc; st.rerun()
            with c4: st.write(f"S/ {it['precio']:,.2f}")
            with c5: st.write(f"S/ {it['total']:,.2f}")
            with c6:
                if st.button("🗑️", key=f"d_{idx}_{it['sku']}"): st.session_state.carrito.pop(idx); st.rerun()
            st.markdown(f'<div style="margin-bottom:0.5rem;">{badge_stock(it["stock_yessica"], it["stock_apri004"], it["stock_apri001"])}</div>', unsafe_allow_html=True)
            st.divider()
            total_gen += it['total']
            
        st.markdown(f"""
        <div style="background: #0f172a; border-radius:12px; padding:1rem; text-align:center; margin:1rem 0; color:white;">
            <span style="font-size:1.5rem; font-weight:600;">TOTAL: S/ {total_gen:,.2f}</span>
        </div>""", unsafe_allow_html=True)
        
        cli = st.text_input("Cliente", placeholder="Nombre o Razón Social")
        ruc = st.text_input("RUC/DNI", placeholder="20XXXXXXXXX")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("📥 Exportar Excel", type="primary", use_container_width=True):
                if cli:
                    st.download_button("💾 Descargar", data=generar_excel(st.session_state.carrito, cli, ruc), file_name=f"Cotizacion_{cli.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.xlsx", use_container_width=True)
                    st.balloons()
                else: st.warning("Ingresa nombre del cliente")
        with c2:
            if st.button("📋 Copiar CSV", use_container_width=True):
                txt = "SKU,Desc,Cant,Precio,Total\n"
                for i in st.session_state.carrito: txt += f"{i['sku']},{i['descripcion']},{i['cantidad']},{i['precio']:.2f},{i['total']:.2f}\n"
                st.code(txt)
        with c3:
            if st.button("🧹 Limpiar", use_container_width=True): st.session_state.carrito=[]; st.rerun()

st.markdown("---")
st.markdown('<div style="text-align:center; color:#64748b; font-size:0.75rem; padding:1rem;">⚡ QTC Smart Sales Pro v2.2</div>', unsafe_allow_html=True)
