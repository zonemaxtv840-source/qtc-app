import streamlit as st
import pandas as pd
import re, io
from datetime import datetime
from PIL import Image
import numpy as np
import warnings
warnings.filterwarnings('ignore')

try:
    img_logo = Image.open("logo.png")
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon=img_logo, layout="wide")
except:
    st.set_page_config(page_title="QTC Smart Sales Pro", page_icon="💼", layout="wide")

# ============================================
# CSS PRINCIPAL - AZUL CORPORATIVO CON TEXTO NEGRO
# ============================================
st.markdown("""
<style>
/* Fondo principal gris muy claro */
.stApp { background-color: #F5F7FA !important; }
.main .block-container { background-color: #F5F7FA !important; }

/* Tipografía NEGRA */
h1, h2, h3, h4, h5, h6 { color: #1A1A2E !important; font-family: 'Segoe UI', sans-serif; }
p, div, span, label, .stMarkdown { color: #A1887F !important; }

/* ============================================ */
/* HEADER Y BOTÓN DEL SIDEBAR - VISIBLE */
/* ============================================ */
/* Header con fondo azul */
.stApp > header {
    background-color: #E65100  !important;
    z-index: 100 !important;
}
/* Botón de hamburguesa (sidebar toggle) */
.stApp > header button {
    background-color: #E65100 !important;
    border-radius: 8px !important;
    border: none !important;
    margin-left: 10px !important;
    padding: 5px 10px !important;
}
.stApp > header button:hover {
    background-color: #E65100 !important;
    transform: scale(1.05);
}
/* Ícono del botón (blanco) */
.stApp > header button svg {
    fill: white !important;
    stroke: white !important;
}
/* Botón cuando el sidebar está colapsado */
.stApp > header button[kind="header"] {
    background-color: #FF9800 !important;
}

/* ============================================ */
/* SIDEBAR AZUL CORPORATIVO */
/* ============================================ */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0D47A1 0%, #1565C0 100%) !important; }
[data-testid="stSidebar"] * { color: #FFFFFF !important; }

/* Botones en sidebar */
[data-testid="stSidebar"] .stButton button {
    background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: linear-gradient(135deg, #F57C00 0%, #E65100 100%) !important;
    transform: translateY(-2px);
}

/* ============================================ */
/* BOTONES PRINCIPALES */
/* ============================================ */
.stButton > button { 
    background: linear-gradient(135deg, #1565C0 0%, #1E88E5 100%) !important; 
    color: white !important; 
    border-radius: 12px; 
    font-weight: 600; 
    border: none; 
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.stButton > button:hover { 
    background: linear-gradient(135deg, #0D47A1 0%, #1565C0 100%) !important; 
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(21,101,192,0.3);
}

/* ============================================ */
/* SELECTORES */
/* ============================================ */
.stSelectbox > div > div { background-color: white !important; border: 1px solid #BBDEFB !important; border-radius: 10px !important; }
.stSelectbox label { color: #1A1A2E !important; }
div[data-baseweb="select"] ul { background-color: white !important; border: 1px solid #BBDEFB !important; border-radius: 10px !important; }
div[data-baseweb="select"] li { color: #1A1A2E !important; background-color: white !important; }
div[data-baseweb="select"] li:hover { background-color: #E3F2FD !important; }
div[data-baseweb="select"] li[aria-selected="true"] { background: linear-gradient(135deg, #1565C0 0%, #1E88E5 100%) !important; color: white !important; }

/* ============================================ */
/* FILE UPLOADER */
/* ============================================ */
.stFileUploader > div > div { background-color: white !important; border: 1px dashed #1E88E5 !important; border-radius: 12px !important; }
.stFileUploader button { background-color: #1565C0 !important; color: white !important; }

/* ============================================ */
/* INPUTS */
/* ============================================ */
.stTextInput input, .stTextArea textarea, .stNumberInput input { 
    color: #1A1A2E !important; 
    background-color: white !important; 
    border: 1px solid #BBDEFB !important; 
    border-radius: 10px !important;
    transition: all 0.3s ease;
}
.stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
    border-color: #1E88E5 !important;
    box-shadow: 0 0 0 2px rgba(30,136,229,0.2);
}

/* Placeholder color */
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #90CAF9 !important;
    opacity: 1;
}

/* ============================================ */
/* TABS */
/* ============================================ */
.stTabs [data-baseweb="tab-list"] { background-color: white !important; border-radius: 12px !important; padding: 6px !important; }
.stTabs [data-baseweb="tab"] { color: #1A1A2E !important; background-color: #F5F7FA !important; border-radius: 10px !important; padding: 10px 20px !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #1565C0 0%, #1E88E5 100%) !important; color: white !important; }

/* ============================================ */
/* BADGES DE ESTADO */
/* ============================================ */
.badge-ok { background-color: #C8E6C9; color: #1B5E20; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
.badge-warning { background-color: #FFF3E0; color: #E65100; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
.badge-danger { background-color: #FFCDD2; color: #C62828; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
.badge-stock-bajo { background-color: #FFE0B2; color: #E65100; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }

/* ============================================ */
/* BADGES DE ORIGEN */
/* ============================================ */
.origin-badge { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; margin-right: 5px; }
.origin-apri004 { background-color: #E1BEE7; color: #4A148C; }
.origin-yessica { background-color: #BBDEFB; color: #0D47A1; }
.origin-both { background-color: #C8E6C9; color: #1B5E20; }

/* ============================================ */
/* MÉTRICAS */
/* ============================================ */
.metric-card { background: white; border-radius: 20px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #BBDEFB; }
.metric-value { font-size: 2.2rem; font-weight: bold; color: #1565C0 !important; }

/* ============================================ */
/* DATA EDITOR */
/* ============================================ */
.stDataFrame { border-radius: 12px !important; overflow: hidden !important; }
.stDataFrame thead th { background: linear-gradient(135deg, #0D47A1 0%, #1565C0 100%) !important; color: white !important; font-weight: 600 !important; }

/* ============================================ */
/* TEXT AREA PARA SKUS */
/* ============================================ */
.stTextArea textarea {
    color: #1A1A2E !important;
    background-color: white !important;
    border: 2px solid #BBDEFB !important;
    border-radius: 12px !important;
    font-family: monospace !important;
    font-size: 14px !important;
}

/* ============================================ */
/* EXPANDER EN SIDEBAR */
/* ============================================ */
[data-testid="stSidebar"] .streamlit-expanderHeader {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] .streamlit-expanderContent {
    color: #FFFFFF !important;
}

/* ============================================ */
/* INDICADORES DE STOCK (SEMÁFORO) */
/* ============================================ */
.stock-verde { color: #2E7D32; font-weight: bold; background-color: #C8E6C9; padding: 2px 8px; border-radius: 20px; display: inline-block; }
.stock-amarillo { color: #E65100; font-weight: bold; background-color: #FFE0B2; padding: 2px 8px; border-radius: 20px; display: inline-block; }
.stock-rojo { color: #C62828; font-weight: bold; background-color: #FFCDD2; padding: 2px 8px; border-radius: 20px; display: inline-block; }
</style>
""", unsafe_allow_html=True)
# ============================================
# INICIALIZACIÓN DE VARIABLES DE SESIÓN
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
# LOGIN AZUL CORPORATIVO
# ============================================
if not st.session_state.auth:
    # Fondo de la página de login
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 50%, #90CAF9 100%) !important;
    }
    .main .block-container {
        background-color: transparent !important;
    }
    .stMarkdown {
        background: transparent !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        background: transparent !important;
    }
    .login-card {
        background: white;
        border-radius: 28px;
        padding: 2.5rem;
        box-shadow: 0 25px 50px rgba(0,0,0,0.15);
        text-align: center;
        border: 1px solid #BBDEFB;
    }
    .login-card h1 {
        color: #1A1A2E !important;
        margin-bottom: 0.25rem;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .login-card p {
        color: #1A1A2E !important;
        margin-bottom: 2rem;
        font-weight: 500;
        font-size: 0.9rem;
    }
    .stButton button {
        background: linear-gradient(135deg, #1565C0 0%, #1E88E5 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.3s ease !important;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #0D47A1 0%, #1565C0 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(21,101,192,0.3) !important;
    }
    .stTextInput input {
        border: 1px solid #BBDEFB !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        color: #1A1A2E !important;
    }
    .stTextInput input:focus {
        border-color: #1E88E5 !important;
        box-shadow: 0 0 0 2px rgba(30,136,229,0.2) !important;
        transform: translateY(-2px);
    }
    .stTextInput label {
        color: #1A1A2E !important;
        font-weight: 500 !important;
    }
    .login-footer {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #BBDEFB;
        font-size: 0.7rem;
        color: #1565C0 !important;
    }
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(40px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    .login-card {
        animation: fadeInUp 0.5s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:
        st.markdown("""
        <div class="login-card">
            <h1>QTC Smart Sales</h1>
            <p>Sistema Profesional de Cotización</p>
        </div>
        """, unsafe_allow_html=True)
        
        user = st.text_input("👤 USUARIO", placeholder="Ingresa tu usuario", key="login_user")
        pw = st.text_input("🔒 CONTRASEÑA", type="password", placeholder="Ingresa tu contraseña", key="login_pass")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 INGRESAR", use_container_width=True):
            if user == "admin" and pw == "qtc2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")
                st.info("💡 Usuario: admin | Contraseña: qtc2026")
        
        st.markdown("""
        <div class="login-footer">
            ⚡ QTC Smart Sales Pro
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.stop()

# ============================================
# FUNCIONES DE LA APLICACIÓN
# ============================================

def corregir_numero(valor):
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

def limpiar_cabeceras(df):
    for i in range(min(20, len(df))):
        fila = [str(x).upper() for x in df.iloc[i].values]
        if any(h in item for h in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO', 'COD SAP'] for item in fila):
            df.columns = [str(c).strip() for c in df.iloc[i]]
            return df.iloc[i+1:].reset_index(drop=True)
    return df

def mapear_columna_precio(columnas, nombre_buscar):
    for col in columnas:
        col_upper = str(col).upper()
        if nombre_buscar.upper() in col_upper:
            return col
        if nombre_buscar.upper() == "P. IR" and "MAYORISTA" in col_upper:
            return col
        if nombre_buscar.upper() == "P. BOX" and "CAJA" in col_upper:
            return col
        if nombre_buscar.upper() == "P. VIP" and ("VIP" in col_upper or "P.VIP" in col_upper):
            return col
        if archivo.name.lower().endswith('.csv'):
            contenido = archivo.getvalue()
    return None
def cargar_catalogo(archivo):
    try:
        # Detectar si es CSV por el nombre
        if archivo.name.lower().endswith('.csv'):
            contenido = archivo.getvalue()
            
            # Leer todo el archivo como líneas para encontrar la cabecera real
            contenido_str = contenido.decode('utf-8', errors='ignore')
            lineas = contenido_str.split('\n')
            
            # Buscar la línea que contiene "Columna1;PICK;BOX;NO.;MODEL MARK" o "SKU"
            header_row_index = None
            for i, linea in enumerate(lineas):
                if 'Columna1;PICK;BOX;NO.;MODEL MARK' in linea or 'SKU' in linea:
                    header_row_index = i
                    break
            
            if header_row_index is not None:
                # Reconstruir CSV desde la fila de cabecera
                lineas_limpias = lineas[header_row_index:]
                contenido_limpio = '\n'.join(lineas_limpias).encode('utf-8')
                
                try:
                    df = pd.read_csv(io.BytesIO(contenido_limpio), encoding='utf-8', sep=';', on_bad_lines='skip')
                except:
                    df = pd.read_csv(io.BytesIO(contenido_limpio), encoding='latin-1', sep=';', on_bad_lines='skip')
            else:
                # Fallback normal
                try:
                    df = pd.read_csv(io.BytesIO(contenido), encoding='utf-8', sep=';', on_bad_lines='skip')
                except:
                    df = pd.read_csv(io.BytesIO(contenido), encoding='latin-1', sep=';', on_bad_lines='skip')
            
            df = limpiar_cabeceras(df)
            hoja_seleccionada = "CSV"
        else:
            xls = pd.ExcelFile(archivo)
            hojas = xls.sheet_names
            hoja_seleccionada = st.sidebar.selectbox(f"📗 Hoja {archivo.name}:", hojas, key=f"cat_{archivo.name}")
            df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)
            df = limpiar_cabeceras(df)
        
        posibles_skus = ['SKU', 'COD', 'CODIGO', 'SAP', 'NUMERO', 'ARTICULO', 'COD SAP']
        posibles_desc = ['DESC', 'DESCRIPCION', 'NOMBRE', 'PRODUCTO', 'NOMBRE PRODUCTO']
        
        col_sku = next((c for c in df.columns if any(p in str(c).upper() for p in posibles_skus)), df.columns[0])
        col_desc = next((c for c in df.columns if any(p in str(c).upper() for p in posibles_desc)), df.columns[1] if len(df.columns) > 1 else df.columns[0])
        
        columnas_precio = {}
        col_ir = mapear_columna_precio(df.columns, "P. IR")
        if col_ir:
            columnas_precio['P. IR'] = col_ir
        col_box = mapear_columna_precio(df.columns, "P. BOX")
        if col_box:
            columnas_precio['P. BOX'] = col_box
        col_vip = mapear_columna_precio(df.columns, "P. VIP")
        if col_vip:
            columnas_precio['P. VIP'] = col_vip
        if not columnas_precio:
            for c in df.columns:
                if 'PRECIO' in str(c).upper():
                    columnas_precio['PRECIO'] = c
                    break
        
        with st.sidebar.expander(f"📋 {archivo.name[:25]}..."):
            st.caption(f"SKU: {col_sku} | Desc: {col_desc}")
            st.caption(f"Precios: {', '.join(columnas_precio.keys()) if columnas_precio else 'No detectados'}")
        
        return {
            'nombre': f"{archivo.name} [{hoja_seleccionada}]",
            'df': df,
            'col_sku': col_sku,
            'col_desc': col_desc,
            'columnas_precio': columnas_precio
        }
    except Exception as e:
        st.error(f"Error en {archivo.name}: {str(e)[:100]}")
        return None

def cargar_stock_completo(archivo):
    try:
        todas_hojas = []
        
        if archivo.name.lower().endswith('.csv'):
            contenido = archivo.getvalue()
            
            contenido_str = contenido.decode('utf-8', errors='ignore')
            lineas = contenido_str.split('\n')
            
            # Buscar línea con SKU o similar
            header_row_index = None
            for i, linea in enumerate(lineas):
                if 'SKU' in linea or 'COD' in linea or 'Columna1' in linea:
                    header_row_index = i
                    break
            
            if header_row_index is not None:
                lineas_limpias = lineas[header_row_index:]
                contenido_limpio = '\n'.join(lineas_limpias).encode('utf-8')
                
                try:
                    df = pd.read_csv(io.BytesIO(contenido_limpio), encoding='utf-8', sep=';', on_bad_lines='skip')
                except:
                    df = pd.read_csv(io.BytesIO(contenido_limpio), encoding='latin-1', sep=';', on_bad_lines='skip')
            else:
                try:
                    df = pd.read_csv(io.BytesIO(contenido), encoding='utf-8', sep=';', on_bad_lines='skip')
                except:
                    df = pd.read_csv(io.BytesIO(contenido), encoding='latin-1', sep=';', on_bad_lines='skip')
            
            df = limpiar_cabeceras(df)
            
            posibles_skus = ['SKU', 'COD', 'CODIGO', 'NUMERO', 'ARTICULO', 'NÚMERO DE ARTÍCULO']
            posibles_stock = ['STOCK', 'DISPONIBLE', 'CANT', 'CANTIDAD', 'SALDO', 'EN STOCK']
            
            col_sku = next((c for c in df.columns if any(p in str(c).upper() for p in posibles_skus)), df.columns[0])
            col_stock = next((c for c in df.columns if any(p in str(c).upper() for p in posibles_stock)), df.columns[1] if len(df.columns) > 1 else df.columns[0])
            
            todas_hojas.append({
                'nombre': f"{archivo.name} [CSV]",
                'df': df,
                'col_sku': col_sku,
                'col_stock': col_stock,
                'hoja': "CSV"
            })
        else:
            xls = pd.ExcelFile(archivo)
            for hoja in xls.sheet_names:
                df = pd.read_excel(archivo, sheet_name=hoja)
                df = limpiar_cabeceras(df)
                
                posibles_skus = ['SKU', 'COD', 'CODIGO', 'NUMERO', 'ARTICULO', 'NÚMERO DE ARTÍCULO']
                posibles_stock = ['STOCK', 'DISPONIBLE', 'CANT', 'CANTIDAD', 'SALDO', 'EN STOCK']
                
                col_sku = next((c for c in df.columns if any(p in str(c).upper() for p in posibles_skus)), df.columns[0])
                col_stock = next((c for c in df.columns if any(p in str(c).upper() for p in posibles_stock)), df.columns[1] if len(df.columns) > 1 else df.columns[0])
                
                todas_hojas.append({
                    'nombre': f"{archivo.name} [{hoja}]",
                    'df': df,
                    'col_sku': col_sku,
                    'col_stock': col_stock,
                    'hoja': hoja
                })
        
        return todas_hojas
    except Exception as e:
        st.error(f"Error cargando {archivo.name}: {str(e)[:100]}")
        return []               

def buscar_precio(catalogos, sku, col_precio_seleccionada):
    sku_limpio = sku.strip().upper()
    for cat in catalogos:
        df = cat['df']
        mask = df[cat['col_sku']].astype(str).str.strip().str.upper() == sku_limpio
        if not df[mask].empty:
            row = df[mask].iloc[0]
            col_precio_real = cat['columnas_precio'].get(col_precio_seleccionada)
            if col_precio_real and col_precio_real in df.columns:
                precio = corregir_numero(row[col_precio_real])
            else:
                precio = 0
            return {
                'encontrado': True,
                'catalogo': cat['nombre'],
                'precio': precio,
                'descripcion': str(row[cat['col_desc']])
            }
        mask = df[cat['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
        if not df[mask].empty:
            row = df[mask].iloc[0]
            col_precio_real = cat['columnas_precio'].get(col_precio_seleccionada)
            if col_precio_real and col_precio_real in df.columns:
                precio = corregir_numero(row[col_precio_real])
            else:
                precio = 0
            return {
                'encontrado': True,
                'catalogo': cat['nombre'],
                'precio': precio,
                'descripcion': str(row[cat['col_desc']])
            }
    return {'encontrado': False, 'precio': 0, 'descripcion': ''}

def buscar_descripcion_en_stock(stocks, sku):
    sku_limpio = sku.strip().upper()
    for stock in stocks:
        df = stock['df']
        col_sku = stock['col_sku']
        mask = df[col_sku].astype(str).str.contains(sku_limpio, case=False, na=False)
        if not df[mask].empty:
            row = df[mask].iloc[0]
            for col in df.columns:
                if any(p in str(col).upper() for p in ['DESC', 'NOMBRE', 'PRODUCTO', 'DESCRIPCION']):
                    desc = str(row[col])
                    if desc and desc != 'nan':
                        return desc[:100]
            return f"SKU: {sku}"
    return f"SKU: {sku}"

def buscar_stock_xiaomi(stocks, sku):
    sku_limpio = sku.strip().upper()
    stock_total = 0
    stock_apri004 = 0
    stock_yessica = 0
    origen_apri004 = ""
    origen_yessica = ""
    
    for stock in stocks:
        hoja = stock['hoja'].upper()
        if 'APRI.004' in hoja:
            mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
            if not stock['df'][mask].empty:
                row = stock['df'][mask].iloc[0]
                stock_apri004 = int(corregir_numero(row[stock['col_stock']]))
                origen_apri004 = stock['nombre']
        elif 'YESSICA' in hoja:
            mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
            if not stock['df'][mask].empty:
                row = stock['df'][mask].iloc[0]
                stock_yessica = int(corregir_numero(row[stock['col_stock']]))
                origen_yessica = stock['nombre']
    
    stock_total = stock_apri004 + stock_yessica
    return stock_total, stock_apri004, stock_yessica

def buscar_stock_general(stocks, sku):
    sku_limpio = sku.strip().upper()
    stock_total = 0
    
    for stock in stocks:
        hoja = stock['hoja'].upper()
        if 'APRI.001' in hoja:
            mask = stock['df'][stock['col_sku']].astype(str).str.contains(sku_limpio, case=False, na=False)
            if not stock['df'][mask].empty:
                row = stock['df'][mask].iloc[0]
                stock_total = int(corregir_numero(row[stock['col_stock']]))
                break
    
    return stock_total, 0, 0

def buscar_en_catalogos(catalogos, termino, stocks, col_precio_consulta=None, tipo_cotizacion="XIAOMI"):
    resultados_dict = {}
    
    if ',' in termino:
        terminos = [t.strip() for t in termino.split(',') if len(t.strip()) >= 2]
    else:
        terminos = [t.strip() for t in termino.split() if len(t.strip()) >= 2]
    
    if not terminos:
        terminos = [termino.strip()]
    
    for cat in catalogos:
        df = cat['df']
        for term in terminos:
            mask_sku = df[cat['col_sku']].astype(str).str.contains(term, case=False, na=False)
            mask_desc = df[cat['col_desc']].astype(str).str.contains(term, case=False, na=False)
            for idx, row in df[mask_sku | mask_desc].iterrows():
                sku = str(row[cat['col_sku']])
                
                if sku not in resultados_dict:
                    precio = None
                    if col_precio_consulta and col_precio_consulta != "(No mostrar precio)":
                        col_precio_real = cat['columnas_precio'].get(col_precio_consulta)
                        if col_precio_real and col_precio_real in df.columns:
                            precio = corregir_numero(row[col_precio_real])
                        else:
                            precio = 0
                    
                    if tipo_cotizacion == "XIAOMI":
                        stock_total, stock_apri004, stock_yessica = buscar_stock_xiaomi(stocks, sku)
                    else:
                        stock_total, stock_apri004, stock_yessica = buscar_stock_general(stocks, sku)
                    
                    resultados_dict[sku] = {
                        'SKU': sku,
                        'Descripcion': str(row[cat['col_desc']])[:100],
                        'Catalogo': cat['nombre'],
                        'Precio': precio,
                        'Stock_Total': stock_total,
                        'Stock_APRI004': stock_apri004,
                        'Stock_YESSICA': stock_yessica,
                    }
    
    return list(resultados_dict.values())

def generar_excel(items, cliente, ruc):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
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
    
    writer.close()
    return output.getvalue()

def obtener_clase_stock(stock):
    if stock == 0:
        return "stock-rojo"
    elif stock <= 5:
        return "stock-amarillo"
    else:
        return "stock-verde"

def obtener_icono_stock(stock):
    if stock == 0:
        return "❌"
    elif stock <= 5:
        return "⚠️"
    else:
        return "✅"

def obtener_mensaje_stock(stock):
    if stock == 0:
        return "Sin stock disponible"
    elif stock <= 5:
        return f"¡Stock bajo! Solo quedan {stock} unidades"
    else:
        return "Stock suficiente"

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
            <span style="font-size: 0.7rem; color: #1565C0;">Administrador</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚪 Cerrar Sesión", key="logout"):
            st.session_state.auth = False
            st.session_state.tipo_cotizacion = None
            st.session_state.resultados = None
            st.rerun()
except:
    st.title("QTC Smart Sales Pro")

st.markdown("---")

# ============================================
# SELECCIÓN DE MODO (solo si no hay modo seleccionado)
# ============================================
if st.session_state.tipo_cotizacion is None:
    st.markdown("### 🎯 ¿Qué vas a cotizar hoy?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔋 XIAOMI", use_container_width=True):
            st.session_state.tipo_cotizacion = "XIAOMI"
            st.rerun()
    with col2:
        if st.button("💼 GENERAL", use_container_width=True):
            st.session_state.tipo_cotizacion = "GENERAL"
            st.rerun()
    st.stop()

# ============================================
# BARRA LATERAL
# ============================================
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.markdown("## 💚 QTC Pro")
    st.markdown("---")
    
    if "cotizaciones" in st.session_state:
        st.metric("📄 Cotizaciones", st.session_state.get("cotizaciones", 0))
        st.metric("📦 Productos", st.session_state.get("total_prods", 0))
    
    st.markdown("---")
    
    # Botón para cambiar de modo
    if st.button("🔄 Cambiar Modo de Cotización", use_container_width=True):
        st.session_state.tipo_cotizacion = None
        st.session_state.resultados = None
        st.rerun()
    
    # Mostrar modo actual
    if st.session_state.tipo_cotizacion == "XIAOMI":
        st.info("🔋 Modo XIAOMI activo")
    else:
        st.info("💼 Modo GENERAL activo")
    
    st.markdown("---")
    
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False
    st.session_state.debug_mode = st.checkbox("🔧 Modo Depuración", value=st.session_state.debug_mode)

# Mostrar modo actual en la página principal
if st.session_state.tipo_cotizacion == "XIAOMI":
    st.success("🔋 **Modo XIAOMI** - Buscará stock en: **APRI.004** y **YESSICA SEPARADO** (suma ambas)")
else:
    st.info("💼 **Modo GENERAL** - Buscará stock en: **APRI.001**")

st.markdown("---")

# ============================================
# TABS PRINCIPALES
# ============================================
tab_cotizacion, tab_buscar, tab_dashboard = st.tabs(["📦 Cotización", "🔍 Buscar Productos", "📊 Dashboard"])

with tab_cotizacion:
    with st.sidebar:
        st.markdown("### 📂 Archivos")
        
        st.markdown("**📚 Catálogos de Precios**")
        archivos_catalogos = st.file_uploader("Sube catálogos", type=['xlsx', 'xls', 'csv'], accept_multiple_files=True, key="cat_upload")
        if archivos_catalogos:
            st.session_state.catalogos = []
            for archivo in archivos_catalogos:
                resultado = cargar_catalogo(archivo)
                if resultado:
                    st.session_state.catalogos.append(resultado)
                    st.success(f"✅ {resultado['nombre'][:50]}")
        
        st.markdown("**📦 Reportes de Stock**")
        st.caption("💡 El sistema cargará TODAS las hojas automáticamente")
        archivos_stock = st.file_uploader("Sube stocks", type=['xlsx', 'xls', 'csv'], accept_multiple_files=True, key="stock_upload")
        if archivos_stock:
            st.session_state.stocks = []
            for archivo in archivos_stock:
                hojas_cargadas = cargar_stock_completo(archivo)
                if hojas_cargadas:
                    st.session_state.stocks.extend(hojas_cargadas)
                    st.success(f"✅ {archivo.name}: {len(hojas_cargadas)} hojas")
                    for h in hojas_cargadas:
                        st.caption(f"   └─ {h['hoja']}")
    
    if not st.session_state.catalogos:
        st.warning("🌿 Carga catálogos en el panel izquierdo")
    else:
        with st.expander("📋 Catálogos cargados"):
            for cat in st.session_state.catalogos:
                st.caption(f"• {cat['nombre']}")
        
        if st.session_state.stocks:
            with st.expander("📋 Stock cargado (todas las hojas)"):
                for stock in st.session_state.stocks:
                    st.caption(f"   📄 {stock['nombre']}")
        
        opciones_precio = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio'].keys():
                opciones_precio.add(col)
        
        if opciones_precio:
            col_precio = st.selectbox("💰 Columna de precio:", sorted(list(opciones_precio)))
        else:
            col_precio = None
            st.warning("⚠️ No se detectaron columnas de precio")
        
        st.markdown("---")
        st.markdown("### 📝 Ingresa los productos")
        st.caption("Formato: SKU:CANTIDAD (uno por línea) - Los SKUs duplicados se suman automáticamente")
        
        if 'skus_transferidos' in st.session_state:
            texto_defecto = "\n".join([f"{sku}:{cant}" for sku, cant in st.session_state.skus_transferidos.items()])
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
                                if sku in pedidos_dict:
                                    pedidos_dict[sku] += cantidad
                                else:
                                    pedidos_dict[sku] = cantidad
                        except:
                            pass
                elif line:
                    sku = line.strip().upper()
                    if sku in pedidos_dict:
                        pedidos_dict[sku] += 1
                    else:
                        pedidos_dict[sku] = 1
        
        pedidos = [{'sku': sku, 'cantidad': cant} for sku, cant in pedidos_dict.items()]
        
        if st.button("🚀 PROCESAR", use_container_width=True, type="primary") and pedidos:
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
                            stock_total, stock_apri004, stock_yessica = buscar_stock_xiaomi(st.session_state.stocks, sku)
                        else:
                            stock_total, stock_apri004, stock_yessica = buscar_stock_general(st.session_state.stocks, sku)
                        
                        if cant > stock_total and stock_total > 0:
                            advertencias_stock.append(f"⚠️ **{sku}**: Stock insuficiente. Solicitado: {cant} | Disponible: {stock_total}. Se cotizarán {stock_total} unidades.")
                            badge_estado = "badge-stock-bajo"
                            estado_texto = "⚠️ Stock insuficiente"
                        elif cant > stock_total and stock_total == 0:
                            advertencias_stock.append(f"❌ **{sku}**: Sin stock disponible. Producto no se puede cotizar.")
                            badge_estado = "badge-danger"
                            estado_texto = "❌ Sin stock"
                        else:
                            badge_estado = "badge-ok"
                            estado_texto = "✅ OK"
                        
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
                        
                        if precio_info['encontrado'] and stock_total > 0:
                            a_cotizar = min(cant, stock_total)
                            total = precio_info['precio'] * a_cotizar
                        else:
                            a_cotizar = 0
                            total = 0
                            if not precio_info['encontrado'] and stock_total > 0:
                                badge_estado = "badge-warning"
                                estado_texto = "⚠️ Sin precio"
                            elif stock_total == 0:
                                badge_estado = "badge-warning"
                                estado_texto = "⚠️ Sin stock"
                        
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
                    
                    for adv in advertencias_stock:
                        if "⚠️" in adv:
                            st.warning(adv)
                        else:
                            st.error(adv)
                    
                    st.session_state.resultados = resultados
        
        if st.session_state.resultados:
            st.markdown("---")
            st.markdown("### 📊 Resultados")
            
            html = '<div style="overflow-x: auto;"><table style="width:100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; table-layout: fixed;">'
            html += '<thead><tr style="background: linear-gradient(135deg, #0D47A1 0%, #1565C0 100%); color: white;">'
            html += '<th style="width: 12%; padding: 10px; text-align: left;">SKU</th>'
            html += '<th style="width: 28%; padding: 10px; text-align: left;">Descripción</th>'
            html += '<th style="width: 10%; padding: 10px; text-align: center;">Precio</th>'
            html += '<th style="width: 5%; padding: 10px; text-align: center;">Pedido</th>'
            html += '<th style="width: 8%; padding: 10px; text-align: center;">Stock</th>'
            html += '<th style="width: 18%; padding: 10px; text-align: left;">Origen</th>'
            html += '<th style="width: 8%; padding: 10px; text-align: center;">A Cotizar</th>'
            html += '<th style="width: 8%; padding: 10px; text-align: center;">Total</th>'
            html += '<th style="width: 8%; padding: 10px; text-align: center;">Estado</th>'
            html += '</tr></thead><tbody>'
            
            for item in st.session_state.resultados:
                precio_str = f"S/. {item['Precio']:,.2f}" if item['Precio'] > 0 else "Sin precio"
                total_str = f"S/. {item['Total']:,.2f}"
                stock_clase = obtener_clase_stock(item['Stock'])
                stock_icono = obtener_icono_stock(item['Stock'])
                stock_html = f'<span class="{stock_clase}" title="{obtener_mensaje_stock(item["Stock"])}">{stock_icono} {item["Stock"]}</span>'
                
                html += f'<tr style="border-bottom: 1px solid #E8F5E9;">'
                html += f'<td style="padding: 10px; font-family: monospace; word-wrap: break-word;">{item["SKU"]}</td>'
                html += f'<td style="padding: 10px; word-wrap: break-word;">{item["Descripción"][:60]}{"..." if len(item["Descripción"]) > 60 else ""}</td>'
                html += f'<td style="padding: 10px; text-align: center;">{precio_str}</td>'
                html += f'<td style="padding: 10px; text-align: center;">{item["Pedido"]}</td>'
                html += f'<td style="padding: 10px; text-align: center;">{stock_html}</td>'
                html += f'<td style="padding: 10px;">{item["Origen"]}</td>'
                html += f'<td style="padding: 10px; text-align: center;"><strong>{item["A Cotizar"]}</strong></td>'
                html += f'<td style="padding: 10px; text-align: center;"><strong>{total_str}</strong></td>'
                html += f'<td style="padding: 10px; text-align: center;"><span class="{item["Badge_Estado"]}" style="display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600;">{item["Estado"]}</span></td>'
                html += '</tr>'
            
            html += '</tbody></table></div>'
            st.markdown(html, unsafe_allow_html=True)
            
            # ============================================
            # TABLA DE AJUSTAR CANTIDADES
            # ============================================
            st.markdown("---")
            st.markdown("### ✏️ Ajustar cantidades")
            st.caption("💡 Modifica las cantidades aquí - Los totales se actualizarán automáticamente")
            
            df_ajuste = pd.DataFrame(st.session_state.resultados)
            
            df_editor = df_ajuste[[
                'SKU', 'Descripción', 'Precio', 'Stock', 'A Cotizar'
            ]].copy()
            
            df_editor['Precio'] = df_editor['Precio'].apply(lambda x: f"S/. {x:,.2f}" if x > 0 else "Sin precio")
            df_editor['Stock/Estado'] = df_editor['Stock'].apply(lambda x: f"{obtener_icono_stock(x)} {x} - {obtener_mensaje_stock(x)}" if x > 0 else f"{obtener_icono_stock(x)} {x} - {obtener_mensaje_stock(x)}")
            
            edited_df = st.data_editor(
                df_editor,
                column_config={
                    "SKU": st.column_config.TextColumn("SKU", width="small", disabled=True),
                    "Descripción": st.column_config.TextColumn("Descripción", width="large", disabled=True),
                    "Precio": st.column_config.TextColumn("Precio", width="small", disabled=True),
                    "Stock": st.column_config.NumberColumn("Stock", width="small", disabled=True),
                    "Stock/Estado": st.column_config.TextColumn("Stock", width="medium", disabled=True),
                    "A Cotizar": st.column_config.NumberColumn(
                        "A Cotizar",
                        width="small",
                        min_value=0,
                        step=1,
                        required=True
                    ),
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
                        st.warning(f"⚠️ **{st.session_state.resultados[idx]['SKU']}**: No puede cotizar más de {stock_disponible} unidades (stock disponible)")
                    
                    st.session_state.resultados[idx]['A Cotizar'] = nueva_cant
                    if st.session_state.resultados[idx]['Precio'] > 0:
                        st.session_state.resultados[idx]['Total'] = st.session_state.resultados[idx]['Precio'] * nueva_cant
                        if nueva_cant > 0:
                            st.session_state.resultados[idx]['Estado'] = "✅ OK"
                            st.session_state.resultados[idx]['Badge_Estado'] = "badge-ok"
                        else:
                            st.session_state.resultados[idx]['Estado'] = "⚠️ Sin stock"
                            st.session_state.resultados[idx]['Badge_Estado'] = "badge-warning"
                    else:
                        st.session_state.resultados[idx]['Total'] = 0
            
            items_validos = [r for r in st.session_state.resultados if r['A Cotizar'] > 0 and r['Precio'] > 0]
            items_con_issues = [r for r in st.session_state.resultados if r['A Cotizar'] == 0 or r['Precio'] == 0]
            total_general = sum(r['Total'] for r in items_validos)
            
            st.markdown("---")
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("✅ A cotizar", len(items_validos))
            col_m2.metric("💰 Total", f"S/. {total_general:,.2f}")
            col_m3.metric("⚠️ Excluidos", len(items_con_issues))
            
            if items_con_issues:
                st.markdown("---")
                st.markdown("### ⚠️ Productos con Issues (No Cotizables)")
                for item in items_con_issues:
                    if item['Precio'] == 0:
                        motivo = "💰 Sin precio en catálogo"
                    elif item['Stock'] == 0:
                        motivo = "📦 Sin stock disponible"
                    else:
                        motivo = "❓ Error en datos"
                    st.warning(f"**{item['SKU']}** - {item['Descripción'][:60]} → `{motivo}`")
            
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
                    st.download_button("💾 DESCARGAR", data=excel, file_name=f"Cotizacion_{cliente}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", use_container_width=True, key="download_btn")
                    st.session_state.cotizaciones += 1
                    st.session_state.total_prods = len(items_validos)
                    st.balloons()
                    st.success("✅ Cotización generada")

with tab_buscar:
    st.markdown("### 🔍 Buscar Productos")
    st.caption("💡 Busca por SKU o descripción - Muestra stock y precio en tiempo real")
    
    if not st.session_state.catalogos:
        st.warning("🌿 Primero carga catálogos en la pestaña Cotización")
    else:
        opciones_precio_buscar = set()
        for cat in st.session_state.catalogos:
            for col in cat['columnas_precio'].keys():
                opciones_precio_buscar.add(col)
        
        col_precio_consulta = st.selectbox(
            "💰 Mostrar precios en columna:",
            options=["(No mostrar precio)"] + sorted(list(opciones_precio_buscar)),
            key="precio_busqueda"
        )
        
        busqueda = st.text_input("🔎 Buscar:", placeholder="Ej: cable cargador RN0200046BK8")
        
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
                st.success(f"✅ {len(resultados)} resultados encontrados")
                
                for res in resultados:
                    stock_clase = obtener_clase_stock(res['Stock_Total'])
                    stock_icono = obtener_icono_stock(res['Stock_Total'])
                    
                    stock_detalle = ""
                    if st.session_state.tipo_cotizacion == "XIAOMI":
                        if res.get('Stock_APRI004', 0) > 0:
                            stock_detalle += f'<span class="origin-badge origin-apri004">📦 APRI.004: {res["Stock_APRI004"]}</span> '
                        if res.get('Stock_YESSICA', 0) > 0:
                            stock_detalle += f'<span class="origin-badge origin-yessica">📋 YESSICA: {res["Stock_YESSICA"]}</span> '
                    else:
                        pass
                    
                    st.markdown(f"""
                    <div style="background: white; border-radius: 12px; padding: 1rem; margin: 0.5rem 0; border-left: 4px solid #1565C0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <div><span style="font-family: monospace; font-weight: bold; font-size: 1rem;">📦 {res['SKU']}</span><br><span style="font-size: 0.85rem; color: #555;">{res['Descripcion']}</span><br><span style="font-weight: bold; color: #1565C0;">{f'S/. {res["Precio"]:,.2f}' if res["Precio"] else "💰 Sin precio"}</span></div>
                        <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #eee;">
                            <span class="{stock_clase}" title="{obtener_mensaje_stock(res['Stock_Total'])}">{stock_icono} Stock: {res['Stock_Total']}</span><br>
                            {stock_detalle}
                            <div style="font-size:0.7rem; color:#888; margin-top:5px;">📁 Catálogo: {res['Catalogo'][:50]}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown("**➕ Agregar a cotización**")
                    with col2:
                        cantidad = st.number_input("Cant", min_value=0, max_value=999, value=0, key=f"add_{res['SKU']}", label_visibility="collapsed")
                        if cantidad > 0:
                            st.session_state.productos_seleccionados[res['SKU']] = st.session_state.productos_seleccionados.get(res['SKU'], 0) + cantidad
                    st.divider()
            else:
                st.warning("No se encontraron productos")
        
        if st.session_state.productos_seleccionados:
            st.markdown("---")
            st.markdown(f"### ✅ Productos seleccionados ({len(st.session_state.productos_seleccionados)})")
            
            seleccionados_lista = []
            for sku, cant in st.session_state.productos_seleccionados.items():
                if st.session_state.tipo_cotizacion == "XIAOMI":
                    stock_total, _, _ = buscar_stock_xiaomi(st.session_state.stocks, sku)
                else:
                    stock_total, _, _ = buscar_stock_general(st.session_state.stocks, sku)
                seleccionados_lista.append({'SKU': sku, 'Cantidad': cant, 'Stock disponible': stock_total})
            
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
                    st.info("👉 Ve a la pestaña Cotización y haz clic en PROCESAR")

with tab_dashboard:
    st.markdown("### 📊 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📄 Cotizaciones", st.session_state.get('cotizaciones', 0))
    col2.metric("🌿 Productos", st.session_state.get('total_prods', 0))
    col3.metric("📚 Catálogos", len(st.session_state.get('catalogos', [])))
    
    st.markdown("---")
    st.markdown("### 📋 Catálogos Cargados")
    for cat in st.session_state.get('catalogos', []):
        st.markdown(f"- {cat['nombre']}")
    
    st.markdown("---")
    st.markdown("### 📋 Stocks Cargados (Todas las hojas)")
    if st.session_state.get('stocks'):
        for stock in st.session_state.stocks:
            st.markdown(f"- {stock['nombre']}")
    else:
        st.info("No hay stocks cargados")
    
    st.markdown("---")
    st.markdown("### 🎯 Reglas actuales")
    if st.session_state.tipo_cotizacion == "XIAOMI":
        st.markdown("""
        🔋 **Modo XIAOMI** → Stock en APRI.004 y YESSICA SEPARADO (suma ambas)
        - 📦 **APRI.004**: Stock físico disponible
        - 📋 **YESSICA**: Stock apartado (también disponible)
        """)
    else:
        st.markdown("💼 **Modo GENERAL** → Stock en APRI.001")

st.markdown("---")
st.markdown("*💚 QTC Smart Sales Pro - Sistema Robusto de Cotización*")
