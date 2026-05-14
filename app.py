import streamlit as st
import pandas as pd
import re
import io
import json
import os
from datetime import datetime
from difflib import SequenceMatcher
import warnings

warnings.filterwarnings('ignore')

# ============================================
# 1. CONFIGURACIÓN Y ESTILO PREMIUM (CSS)
# ============================================
st.set_page_config(
    page_title="QTC Smart Sales Pro v5.0",
    page_icon="💎",
    layout="wide"
)

def apply_styles():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        /* Contenedor Principal */
        .stApp {
            background-color: #0f172a;
            font-family: 'Inter', sans-serif;
            color: #f1f5f9;
        }

        /* Sidebar Moderno */
        [data-testid="stSidebar"] {
            background-color: #1e293b;
            border-right: 1px solid rgba(255,255,255,0.1);
        }

        /* Tarjetas de Producto (Glassmorphism) */
        .product-card {
            background: rgba(30, 41, 59, 0.7);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: transform 0.2s;
        }
        .product-card:hover {
            border-color: #e11d48;
        }

        /* Botones Estilo Linear/Stripe */
        .stButton>button {
            border-radius: 8px;
            background: linear-gradient(135deg, #e11d48 0%, #be123c 100%);
            color: white;
            border: none;
            font-weight: 600;
            padding: 10px 20px;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            box-shadow: 0 4px 15px rgba(225, 29, 72, 0.4);
            transform: translateY(-1px);
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #1e293b;
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
            color: #94a3b8;
        }
        .stTabs [aria-selected="true"] {
            background-color: #e11d48 !important;
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)

# ============================================
# 2. GESTIÓN DE USUARIOS Y PERSISTENCIA
# ============================================
USER_DB = "usuarios.json"

def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f: return json.load(f)
    return {"admin": {"pw": "qtc2026", "role": "admin"}}

def save_user(user, pw):
    users = load_users()
    if user in users: return False
    users[user] = {"pw": pw, "role": "vendedor"}
    with open(USER_DB, "w") as f: json.dump(users, f)
    return True

# ============================================
# 3. MOTOR DE BÚSQUEDA UNIFICADO (TAB 1 + TAB 2)
# ============================================
def buscar_producto_inteligente(sku_buscado, catalogos, stocks, precio_key):
    sku_limpio = sku_buscado.strip().upper()
    
    # A. Búsqueda de Stock (Multialmacén)
    res_stock = {"TOTAL": 0, "ALMACENES": {}, "DESC_STOCK": ""}
    for s in stocks:
        df = s['df']
        match = df[df[s['col_sku']].astype(str).str.upper() == sku_limpio]
        if not match.empty:
            cant = int(match.iloc[0].filter(like='CANT').iloc[0] if not match.iloc[0].filter(like='CANT').empty else 0)
            res_stock['ALMACENES'][s['hoja']] = cant
            res_stock['TOTAL'] += cant
            # Capturar descripción si el catálogo falla
            for c in df.columns:
                if any(x in str(c).upper() for x in ['DESC', 'PRODUCTO', 'NAME']):
                    res_stock['DESC_STOCK'] = str(match.iloc[0][c])

    # B. Búsqueda en Catálogo
    res_cat = {"sku_oficial": sku_limpio, "desc": res_stock['DESC_STOCK'], "precio": 0.0, "status": "ERROR"}
    
    found = False
    for cat in catalogos:
        df = cat['df']
        match_cat = df[df[cat['col_sku']].astype(str).str.upper() == sku_limpio]
        if not match_cat.empty:
            row = match_cat.iloc[0]
            res_cat['precio'] = float(re.sub(r'[^\d.]', '', str(row[cat['precios'][precio_key]])))
            res_cat['desc'] = str(row[cat['col_desc']]) if cat['col_desc'] else res_cat['desc']
            res_cat['status'] = "OK"
            found = True
            break

    # C. LÓGICA DE COMPLEMENTO (Antigua Tab 2 integrada)
    if not found and res_stock['TOTAL'] > 0:
        mejor_match = {"sku": None, "sim": 0, "precio": 0, "desc": ""}
        for cat in catalogos:
            for _, r in cat['df'].iterrows():
                sim = SequenceMatcher(None, res_cat['desc'].lower(), str(r.get(cat['col_desc'], '')).lower()).ratio()
                if sim > mejor_match['sim'] and sim > 0.70:
                    mejor_match = {
                        "sku": str(r[cat['col_sku']]),
                        "desc": str(r[cat['col_desc']]),
                        "precio": float(re.sub(r'[^\d.]', '', str(r[cat['precios'][precio_key]]))),
                        "sim": sim
                    }
        if mejor_match['sku']:
            res_cat['sugerencia'] = mejor_match
            res_cat['status'] = "SUGERENCIA"

    return {**res_cat, **res_stock}

# ============================================
# 4. COMPONENTES DE INTERFAZ
# ============================================
def login_page():
    apply_styles()
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<h1 style='text-align:center;'>💎 QTC SMART SALES</h1>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Ingresar", "Registrarse"])
        with t1:
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.button("ACCEDER"):
                users = load_users()
                if u in users and users[u]['pw'] == p:
                    st.session_state.auth = True
                    st.session_state.user = u
                    st.rerun()
                else: st.error("Datos incorrectos")
        with t2:
            nu = st.text_input("Nuevo Usuario")
            np = st.text_input("Nueva Contraseña", type="password")
            if st.button("CREAR CUENTA"):
                if save_user(nu, np): st.success("Registrado correctamente")
                else: st.error("El usuario ya existe")

def main_app():
    apply_styles()
    
    # Inicializar estados
    if 'carrito' not in st.session_state: st.session_state.carrito = []
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.title("⚙️ Panel Control")
        st.write(f"Vendedor: **{st.session_state.user}**")
        precio_sel = st.selectbox("Tarifa", ["P. VIP", "P. BOX", "P. IR"])
        st.divider()
        
        # Carga de archivos (igual a tu lógica original)
        up_cats = st.file_uploader("Catálogos (Excel)", accept_multiple_files=True)
        up_stocks = st.file_uploader("Stocks (Excel)", accept_multiple_files=True)
        
        catalogos_procesados = []
        if up_cats:
            for f in up_cats:
                df = pd.read_excel(f)
                catalogos_procesados.append({
                    'df': df, 
                    'col_sku': 'SKU', # Ajustar según tus columnas reales o usar tu selector original
                    'col_desc': 'PRODUCTO',
                    'precios': {"P. VIP": "VIP", "P. BOX": "BOX", "P. IR": "IR"}
                })
        
        stocks_procesados = []
        if up_stocks:
            for f in up_stocks:
                xl = pd.ExcelFile(f)
                for sheet in xl.sheet_names:
                    stocks_procesados.append({'df': xl.parse(sheet), 'col_sku': 'SKU', 'hoja': sheet})

        if st.button("Cerrar Sesión"):
            st.session_state.auth = False
            st.rerun()

    # --- CUERPO PRINCIPAL ---
    tab_masivo, tab_carrito = st.tabs(["🚀 PEDIDO MASIVO", "🛒 MI CARRITO"])

    with tab_masivo:
        st.markdown("### Entrada de Productos")
        input_txt = st.text_area("Formato: SKU:CANTIDAD (uno por línea)", height=150, placeholder="RN12345:10\nCN67890:5")
        
        if st.button("ANALIZAR DISPONIBILIDAD"):
            lineas = [l for l in input_txt.split('\n') if ':' in l]
            for l in lineas:
                sku_in, cant_in = l.split(':')
                res = buscar_producto_inteligente(sku_in, catalogos_procesados, stocks_procesados, precio_sel)
                
                # Visualización Premium de Resultados
                color = "#059669" if res['status'] == "OK" else "#d97706" if res['status'] == "SUGERENCIA" else "#dc2626"
                
                with st.container():
                    st.markdown(f"""
                    <div class="product-card" style="border-left: 5px solid {color};">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:700; font-size:1.1em;">{res['sku_oficial']}</span>
                            <span style="background:{color}; padding:2px 8px; border-radius:5px; font-size:0.8em;">{res['status']}</span>
                        </div>
                        <div style="color:#94a3b8; font-size:0.9em; margin:5px 0;">{res['desc']}</div>
                        <div style="display:flex; gap:15px; margin-top:10px;">
                            <span>💰 <b>S/ {res['precio']:,.2f}</b></span>
                            <span>📦 Stock: {res['TOTAL']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if res['status'] == "SUGERENCIA":
                        st.warning(f"Sugerencia: Se encontró match con {res['sugerencia']['sku']} ({int(res['sugerencia']['sim']*100)}%)")
                        if st.button(f"Usar sugerencia para {sku_in}", key=f"btn_{sku_in}"):
                            # Agregar sugerencia al carrito
                            st.session_state.carrito.append({
                                'sku': res['sugerencia']['sku'],
                                'desc': res['sugerencia']['desc'],
                                'precio': res['sugerencia']['precio'],
                                'cant': int(cant_in),
                                'total': res['sugerencia']['precio'] * int(cant_in)
                            })
                            st.success("Sugerencia agregada")
                    
                    elif res['status'] == "OK":
                        if st.button(f"Confirmar {sku_in}", key=f"ok_{sku_in}"):
                            st.session_state.carrito.append({
                                'sku': res['sku_oficial'],
                                'desc': res['desc'],
                                'precio': res['precio'],
                                'cant': int(cant_in),
                                'total': res['precio'] * int(cant_in)
                            })
                            st.success("Agregado al carrito")

    with tab_carrito:
        if not st.session_state.carrito:
            st.info("El carrito está vacío")
        else:
            df_cart = pd.DataFrame(st.session_state.carrito)
            st.table(df_cart)
            total_g = df_cart['total'].sum()
            st.markdown(f"## Total: S/ {total_g:,.2f}")
            if st.button("LIMPIAR CARRITO"):
                st.session_state.carrito = []
                st.rerun()

# --- ARRANQUE ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    login_page()
else:
    main_app()
