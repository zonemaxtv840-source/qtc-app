# app.py - QTC Smart Sales AI v5.0
# 1 SOLO TAB - COTIZADOR INTELIGENTE CON IA
# Funciones inteligentes: Reconocimiento de precios, detección de marca,
# parser universal, matching difuso, corrector de SKU, sistema de confianza

import streamlit as st
import pandas as pd
import numpy as np
import re
import io
from datetime import datetime
import warnings
from typing import List, Dict, Optional, Tuple, Any
from difflib import SequenceMatcher, get_close_matches
import json

warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="QTC Smart Sales AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# CSS PROFESIONAL
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* ══ FONDO ══ */
    .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    }

    /* ══ SIDEBAR ══ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 2px solid #e94560;
    }
    [data-testid="stSidebar"] * {
        color: #eaeaea !important;
    }

    /* ══ TEXTO GENERAL ══ */
    h1, h2, h3 {
        color: #ffffff !important;
    }
    .stMarkdown p {
        color: #eaeaea !important;
    }

    /* ══ CARDS INTELIGENTES ══ */
    .smart-card {
        background: rgba(255,255,255,0.95);
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border-left: 5px solid;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.2s ease;
    }
    .smart-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }

    /* Estados de cards */
    .card-success { border-left-color: #4CAF50; }
    .card-warning { border-left-color: #FF9800; }
    .card-error   { border-left-color: #f44336; }
    .card-info    { border-left-color: #2196F3; }
    .card-neutral { border-left-color: #9e9e9e; }
    .card-ugreen  { border-left-color: #00BCD4; }

    /* ══ BADGES DE STOCK ══ */
    .badge-yessica {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin: 2px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .badge-apri004 {
        background: linear-gradient(135deg, #FF9800, #f57c00);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin: 2px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .badge-apri001 {
        background: linear-gradient(135deg, #f44336, #d32f2f);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin: 2px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .badge-ugreen {
        background: linear-gradient(135deg, #00BCD4, #0097A7);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin: 2px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* ══ INDICADOR DE CONFIANZA ══ */
    .confidence-high   { color: #4CAF50; font-weight: bold; }
    .confidence-medium { color: #FF9800; font-weight: bold; }
    .confidence-low    { color: #f44336; font-weight: bold; }

    /* ══ CONTADORES ══ */
    .counter-summary {
        background: rgba(0,0,0,0.3);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        gap: 10px;
    }
    .counter-item {
        text-align: center;
        padding: 0.5rem 1rem;
        background: rgba(255,255,255,0.1);
        border-radius: 8px;
        min-width: 120px;
    }
    .counter-number {
        font-size: 1.5rem;
        font-weight: bold;
        color: #e94560;
    }

    /* ══ SMART MAPPER UI ══ */
    .mapper-container {
        background: rgba(233, 69, 96, 0.1);
        border: 1px solid #e94560;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }

    /* ══ PREVIEW TABLE ══ */
    .preview-table {
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 0.5rem;
        font-family: monospace;
        font-size: 0.85rem;
    }

    /* ══ SUGGESTION BOX ══ */
    .suggestion-box {
        background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
        border-left: 4px solid #4CAF50;
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.5rem 0;
    }

    /* ══ CARRITO COMPACTO ══ */
    .cart-item {
        background: rgba(255,255,255,0.1);
        border-radius: 8px;
        padding: 0.5rem;
        margin: 0.3rem 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* ══ FOOTER ══ */
    .footer {
        text-align: center;
        padding: 1rem;
        color: rgba(255,255,255,0.5);
        font-size: 0.75rem;
        border-top: 1px solid rgba(255,255,255,0.1);
        margin-top: 2rem;
    }

    /* ══ SCROLLBAR ══ */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.1);
    }
    ::-webkit-scrollbar-thumb {
        background: #e94560;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE UTILIDAD BASE
# ═══════════════════════════════════════════════════════════════════════════════

def corregir_numero(valor) -> float:
    """Convierte cualquier valor a número float, manejando formatos diversos"""
    if pd.isna(valor) or str(valor).strip() in ["", "0", "0.0", "-", "nan", "None"]:
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
    """Detecta y limpia filas de cabecera en archivos mal formateados"""
    if df.empty:
        return df
    for i in range(min(20, len(df))):
        fila = [str(x).upper() for x in df.iloc[i].values if pd.notna(x)]
        if any(h in item for h in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO', 'PRECIO', 'STOCK', 'DISPONIBLE'] for item in fila):
            df.columns = [str(c).strip() for c in df.iloc[i]]
            return df.iloc[i+1:].reset_index(drop=True)
    return df

def cargar_archivo(uploaded_file) -> Optional[pd.DataFrame]:
    """Carga archivo Excel o CSV con manejo de errores"""
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
            df = pd.read_excel(uploaded_file)
        return limpiar_cabeceras(df) if not df.empty else df
    except Exception as e:
        st.error(f"❌ Error cargando archivo: {str(e)[:80]}")
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# MOTOR DE SIMILITUD INTELIGENTE
# ═══════════════════════════════════════════════════════════════════════════════

def normalizar_texto(texto: str) -> str:
    """Normaliza texto para comparación inteligente"""
    if not texto:
        return ""
    texto = texto.lower().strip()
    correcciones = {
        "xioami": "xiaomi", "xiomi": "xiaomi", "xiamoi": "xiaomi",
        "xiaomy": "xiaomi", "xiaimin": "xiaomi",
        "ugreem": "ugreen", "ugren": "ugreen", "ugreeen": "ugreen",
        "earphone": "earphone", "earphones": "earphone",
        "headphone": "headphone", "headphones": "headphone",
        "charger": "charger", "charguer": "charger",
        "cable": "cable", "cble": "cable", "cabble": "cable",
        "adaptador": "adapter", "adapter": "adapter",
        "power bank": "power bank", "powerbank": "power bank",
        "redmi": "redmi", "remi": "redmi", "redmy": "redmi",
        "poco": "poco", "poko": "poco", "pocco": "poco",
        "mi band": "mi band", "miband": "mi band", "smart band": "mi band",
        "watch": "watch", "wach": "watch", "smartwatch": "watch",
        "buds": "buds", "bods": "buds",
    }
    for mal, bien in correcciones.items():
        texto = texto.replace(mal, bien)
    sufijos = [' - rn', ' - es', ' - us', ' - eu', ' - gl', ' - demo', ' - rr', ' (rn)', ' (es)', ' (us)']
    for sufijo in sufijos:
        texto = texto.replace(sufijo, '')
    return texto.strip()

def calcular_similitud_avanzada(texto1: str, texto2: str) -> Dict[str, float]:
    """
    Calcula múltiples métricas de similitud y retorna scores individuales + score agregado
    """
    if not texto1 or not texto2:
        return {'exacto': 0, 'jaccard': 0, 'secuencia': 0, 'combinado': 0, 'confianza': 'baja'}

    t1 = normalizar_texto(texto1)
    t2 = normalizar_texto(texto2)

    # 1. Match exacto
    exacto = 100.0 if t1 == t2 else 0.0

    # 2. Jaccard similarity
    palabras1 = set(t1.split())
    palabras2 = set(t2.split())
    interseccion = len(palabras1.intersection(palabras2))
    union = len(palabras1.union(palabras2))
    jaccard = (interseccion / union * 100) if union > 0 else 0.0

    # 3. SequenceMatcher
    secuencia = SequenceMatcher(None, t1, t2).ratio() * 100

    # 4. Palabras clave compartidas (bonus)
    keywords_tech = ['wireless', 'bluetooth', 'usb', 'type-c', 'hdmi', 'soporte', 'carga', 'fast', 'quick']
    kw_match = sum(1 for kw in keywords_tech if kw in t1 and kw in t2) * 10

    # Score combinado ponderado
    combinado = min(100, (exacto * 0.4) + (jaccard * 0.25) + (secuencia * 0.2) + (kw_match * 0.05))

    # Clasificación de confianza
    if combinado >= 90:
        confianza = 'alta'
    elif combinado >= 70:
        confianza = 'media'
    elif combinado >= 50:
        confianza = 'baja'
    else:
        confianza = 'muy_baja'

    return {
        'exacto': round(exacto, 1),
        'jaccard': round(jaccard, 1),
        'secuencia': round(secuencia, 1),
        'combinado': round(combinado, 1),
        'confianza': confianza
    }

def encontrar_mejor_match(sku_buscado: str, df_catalogo: pd.DataFrame, col_sku: str, 
                          col_desc: str = None, top_n: int = 3) -> List[Dict]:
    """
    Encuentra los mejores matches para un SKU usando múltiples estrategias
    """
    resultados = []
    sku_clean = sku_buscado.strip().upper()

    # Estrategia 1: Match exacto
    df_sku = df_catalogo[col_sku].astype(str).str.strip().str.upper()
    mask_exact = df_sku == sku_clean
    if mask_exact.any():
        row = df_catalogo[mask_exact].iloc[0]
        desc = str(row[col_desc])[:200] if col_desc and pd.notna(row.get(col_desc)) else ""
        resultados.append({
            'sku': sku_clean,
            'descripcion': desc,
            'score': 100.0,
            'confianza': 'alta',
            'metodo': 'exacto'
        })
        return resultados

    # Estrategia 2: Contiene (parcial)
    mask_contains = df_sku.str.contains(sku_clean, case=False, na=False, regex=False)
    if mask_contains.any():
        for _, row in df_catalogo[mask_contains].head(top_n).iterrows():
            desc = str(row[col_desc])[:200] if col_desc and pd.notna(row.get(col_desc)) else ""
            resultados.append({
                'sku': str(row[col_sku]).strip().upper(),
                'descripcion': desc,
                'score': 85.0,
                'confianza': 'media',
                'metodo': 'parcial'
            })
        return resultados

    # Estrategia 3: Fuzzy matching en descripciones
    if col_desc:
        desc_norm_busqueda = normalizar_texto(sku_buscado)
        for _, row in df_catalogo.iterrows():
            desc_cat = normalizar_texto(str(row.get(col_desc, '')))
            scores = calcular_similitud_avanzada(desc_norm_busqueda, desc_cat)
            if scores['combinado'] >= 50:
                resultados.append({
                    'sku': str(row[col_sku]).strip().upper(),
                    'descripcion': str(row[col_desc])[:200],
                    'score': scores['combinado'],
                    'confianza': scores['confianza'],
                    'metodo': 'fuzzy'
                })

    # Estrategia 4: Fuzzy matching en SKUs
    todos_skus = df_catalogo[col_sku].astype(str).str.strip().str.upper().tolist()
    close = get_close_matches(sku_clean, todos_skus, n=top_n, cutoff=0.5)
    for cs in close:
        if not any(r['sku'] == cs for r in resultados):
            row = df_catalogo[df_sku == cs]
            if not row.empty:
                desc = str(row.iloc[0][col_desc])[:200] if col_desc else ""
                score = SequenceMatcher(None, sku_clean, cs).ratio() * 100
                resultados.append({
                    'sku': cs,
                    'descripcion': desc,
                    'score': round(score, 1),
                    'confianza': 'media' if score > 70 else 'baja',
                    'metodo': 'fuzzy_sku'
                })

    resultados.sort(key=lambda x: x['score'], reverse=True)
    return resultados[:top_n]

# ═══════════════════════════════════════════════════════════════════════════════
# MOTOR 01: SMART COLUMN MAPPER (Reconocimiento Inteligente de Precios)
# ═══════════════════════════════════════════════════════════════════════════════

class SmartColumnMapper:
    """
    Sistema inteligente que detecta automáticamente qué columnas del archivo
    corresponden a P. IR, P. BOX y P. VIP. Si no está seguro, permite seleccionar manualmente.
    """

    PATRONES_PRECIO = {
        'P. IR': {
            'exacto': ['P. IR', 'P.IR', 'P_IR', 'PRECIO IR', 'PRICE IR', 'IR'],
            'contiene': ['IR', 'MAYORISTA', 'MAYORITARIO', 'MAYOR', 'MAY', 'MAYORISTA'],
            'similar': ['PIR', 'PRIR', 'PRECIOI', 'MAYORIST', 'MAYORIT']
        },
        'P. BOX': {
            'exacto': ['P. BOX', 'P.BOX', 'P_BOX', 'PRECIO BOX', 'PRICE BOX', 'BOX'],
            'contiene': ['BOX', 'CAJA', 'BULK', 'POR CAJA', 'X CAJA', 'MAYOR CAJA', 'BULKS'],
            'similar': ['PBOX', 'PRBOX', 'PRECIOB', 'CAJA', 'BUL']
        },
        'P. VIP': {
            'exacto': ['P. VIP', 'P.VIP', 'P_VIP', 'PRECIO VIP', 'PRICE VIP', 'VIP'],
            'contiene': ['VIP', 'ESPECIAL', 'DISTRIBUIDOR', 'MAYOR VIP', 'MAY VIP', 'MAYORISTA VIP'],
            'similar': ['PVIP', 'PRVIP', 'PRECIOV', 'ESPECIAL', 'DISTRIB']
        }
    }

    @classmethod
    def calcular_score_columna(cls, nombre_columna: str, tipo_precio: str) -> float:
        """Calcula un score de 0-100 de qué tan probable es que una columna sea un tipo de precio"""
        col_upper = str(nombre_columna).upper().strip()

        if not col_upper or col_upper in ['NAN', 'NONE', '']:
            return 0.0

        patrones = cls.PATRONES_PRECIO.get(tipo_precio, {})

        # Match exacto = 100%
        if col_upper in patrones.get('exacto', []):
            return 100.0

        # Contiene = 80%
        for patron in patrones.get('contiene', []):
            if patron in col_upper:
                return 80.0

        # Similaridad de secuencia = hasta 60%
        for patron in patrones.get('similar', []):
            sim = SequenceMatcher(None, col_upper, patron).ratio()
            if sim > 0.7:
                return 60.0 * sim

        return 0.0

    @classmethod
    def mapear_columnas(cls, df: pd.DataFrame, umbral_auto: float = 75.0) -> Dict:
        """
        Mapea automáticamente las columnas de precio.
        Retorna: {
            'mapeo': {'P. IR': 'col_name', ...},
            'scores': {'P. IR': 85.0, ...},
            'confianza': 'alta' | 'media' | 'baja',
            'requiere_confirmacion': True/False,
            'columnas_disponibles': [...]
        }
        """
        columnas = [str(c) for c in df.columns if pd.notna(c)]
        mapeo = {}
        scores = {}

        for tipo_precio in ['P. IR', 'P. BOX', 'P. VIP']:
            mejor_score = 0
            mejor_col = None

            for col in columnas:
                score = cls.calcular_score_columna(col, tipo_precio)
                if score > mejor_score:
                    mejor_score = score
                    mejor_col = col

            if mejor_col and mejor_score > 0:
                mapeo[tipo_precio] = mejor_col
                scores[tipo_precio] = round(mejor_score, 1)

        # Calcular confianza global
        if scores:
            avg_score = sum(scores.values()) / len(scores)
            min_score = min(scores.values())
        else:
            avg_score = 0
            min_score = 0

        if min_score >= umbral_auto:
            confianza = 'alta'
            requiere = False
        elif avg_score >= umbral_auto:
            confianza = 'media'
            requiere = True
        else:
            confianza = 'baja'
            requiere = True

        return {
            'mapeo': mapeo,
            'scores': scores,
            'confianza': confianza,
            'requiere_confirmacion': requiere,
            'columnas_disponibles': columnas
        }

# ═══════════════════════════════════════════════════════════════════════════════
# MOTOR 02: SMART BRAND DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class SmartBrandDetector:
    """
    Detecta automáticamente la marca/modo basándose en el nombre del archivo,
    patrones de SKU y contenido de las descripciones.
    """

    PATRONES_SKU = {
        'XIAOMI': [r'^RN[0-9]', r'^CN[0-9]', r'^MI[0-9]', r'^REDMI', r'^POCO', r'^BHR', r'^XIAOMI'],
        'UGREEN': [r'^UG[0-9]', r'^UGREEN', r'^CD[0-9]', r'^CM[0-9]', r'^HP[0-9]', r'^LP[0-9]'],
    }

    PALABRAS_CLAVE = {
        'XIAOMI': ['xiaomi', 'redmi', 'poco', 'mi band', 'mi tv', 'mi stick'],
        'UGREEN': ['ugreen', 'ug reen'],
    }

    @classmethod
    def detectar(cls, nombre_archivo: str = None, df_muestra: pd.DataFrame = None, 
                 col_sku: str = None, col_desc: str = None) -> Dict:
        """
        Detecta la marca y retorna un dict con score y confianza
        """
        scores = {'XIAOMI': 0, 'UGREEN': 0, 'OTRAS MARCAS': 10}
        evidencias = []

        # 1. Analizar nombre de archivo
        if nombre_archivo:
            nombre_lower = nombre_archivo.lower()
            if 'xiaomi' in nombre_lower:
                scores['XIAOMI'] += 40
                evidencias.append(f"Nombre de archivo contiene 'xiaomi'")
            if 'ugreen' in nombre_lower:
                scores['UGREEN'] += 40
                evidencias.append(f"Nombre de archivo contiene 'ugreen'")
            if 'redmi' in nombre_lower:
                scores['XIAOMI'] += 30
            if 'poco' in nombre_lower:
                scores['XIAOMI'] += 30

        # 2. Analizar SKUs
        if df_muestra is not None and col_sku and col_sku in df_muestra.columns:
            skus = df_muestra[col_sku].dropna().astype(str).head(50).tolist()
            for sku in skus:
                sku_upper = sku.strip().upper()
                for marca, patrones in cls.PATRONES_SKU.items():
                    for patron in patrones:
                        if re.match(patron, sku_upper):
                            scores[marca] += 5
                            if len(evidencias) < 5:
                                evidencias.append(f"SKU '{sku[:15]}...' coincide con patrón {marca}")
                            break

        # 3. Analizar descripciones
        if df_muestra is not None and col_desc and col_desc in df_muestra.columns:
            descripciones = df_muestra[col_desc].dropna().astype(str).head(50).tolist()
            for desc in descripciones:
                desc_lower = desc.lower()
                for marca, palabras in cls.PALABRAS_CLAVE.items():
                    for palabra in palabras:
                        if palabra in desc_lower:
                            scores[marca] += 3
                            if len(evidencias) < 8:
                                evidencias.append(f"Descripción contiene '{palabra}'")
                            break

        # Determinar ganador
        marca_ganadora = max(scores, key=scores.get)
        score_max = scores[marca_ganadora]

        if score_max >= 40:
            confianza = 'alta'
        elif score_max >= 20:
            confianza = 'media'
        elif score_max > 10:
            confianza = 'baja'
        else:
            confianza = 'muy_baja'

        return {
            'marca_detectada': marca_ganadora,
            'score': score_max,
            'confianza': confianza,
            'scores_detalle': scores,
            'evidencias': evidencias[:5],
            'requiere_confirmacion': confianza in ['baja', 'muy_baja']
        }

# ═══════════════════════════════════════════════════════════════════════════════
# MOTOR 03: SMART INPUT PARSER
# ═══════════════════════════════════════════════════════════════════════════════

class SmartInputParser:
    """
    Parsea cualquier formato de entrada automáticamente:
    SKU:CANT, SKU CANT, CSV, lista simple, etc.
    """

    @classmethod
    def detectar_formato(cls, texto: str) -> Dict:
        """
        Analiza el texto y detecta qué formato tiene.
        Retorna: {'formato': 'sku_cantidad'|'csv'|'lista'|'mixto', 'confianza': float}
        """
        if not texto or not texto.strip():
            return {'formato': 'vacio', 'confianza': 0}

        lineas = [l.strip() for l in texto.strip().split('\n') if l.strip()]
        if not lineas:
            return {'formato': 'vacio', 'confianza': 0}

        total_lineas = len(lineas)

        # Formato CSV: primera línea tiene encabezados conocidos
        primera = lineas[0].upper()
        if any(h in primera for h in ['SKU', 'COD', 'ARTICULO', 'PRODUCTO', 'CANTIDAD', 'QTY']):
            # Segunda línea debe tener datos
            if total_lineas > 1 and ',' in lineas[1]:
                return {'formato': 'csv', 'confianza': 90}

        # Contar patrones por formato
        patron_dos_puntos = 0
        patron_coma = 0
        patron_espacio_numero = 0
        patron_solo_sku = 0
        patron_pipe = 0

        for linea in lineas[1:] if primera.startswith('SKU') else lineas:
            linea = linea.strip()
            if not linea:
                continue

            # Dos puntos: "SKU:CANT"
            if ':' in linea and not linea.startswith('http'):
                partes = linea.split(':')
                if len(partes) == 2 and partes[1].strip().isdigit():
                    patron_dos_puntos += 1

            # Coma: "SKU,CANT"
            if ',' in linea:
                partes = linea.split(',')
                if len(partes) >= 2 and partes[1].strip().isdigit():
                    patron_coma += 1

            # Pipe: "SKU|CANT"
            if '|' in linea:
                partes = linea.split('|')
                if len(partes) >= 2 and partes[1].strip().isdigit():
                    patron_pipe += 1

            # Espacio + número: "SKU 100"
            partes = linea.split()
            if len(partes) >= 2 and partes[-1].isdigit():
                patron_espacio_numero += 1

            # Solo SKU (sin número)
            if len(partes) == 1 and not partes[0].isdigit():
                patron_solo_sku += 1

        lineas_validas = total_lineas - (1 if primera.startswith('SKU') else 0)

        # Determinar formato mayoritario
        scores = {
            'sku_cantidad_dospuntos': patron_dos_puntos,
            'csv': patron_coma,
            'sku_cantidad_espacio': patron_espacio_numero,
            'sku_cantidad_pipe': patron_pipe,
            'lista': patron_solo_sku
        }

        mejor = max(scores, key=scores.get)
        mejor_count = scores[mejor]

        if mejor_count == 0:
            return {'formato': 'mixto', 'confianza': 30}

        ratio = mejor_count / lineas_validas

        if ratio > 0.8:
            confianza = 95
        elif ratio > 0.6:
            confianza = 75
        elif ratio > 0.4:
            confianza = 55
        else:
            confianza = 40

        # Mapear a formatos simplificados
        formato_map = {
            'sku_cantidad_dospuntos': 'sku_cantidad',
            'sku_cantidad_espacio': 'sku_cantidad',
            'sku_cantidad_pipe': 'sku_cantidad',
            'csv': 'csv',
            'lista': 'lista'
        }

        return {
            'formato': formato_map.get(mejor, 'mixto'),
            'subformato': mejor,
            'confianza': confianza,
            'stats': scores,
            'total_lineas': total_lineas
        }

    @classmethod
    def parsear(cls, texto: str) -> List[Dict]:
        """
        Parsea el texto y retorna lista de {sku, cantidad, raw_line}
        """
        info_formato = cls.detectar_formato(texto)
        formato = info_formato['formato']

        resultados = []
        lineas = [l.strip() for l in texto.strip().split('\n') if l.strip()]

        start_idx = 0
        # Saltar header si es CSV
        if lineas and lineas[0].upper().startswith('SKU'):
            start_idx = 1

        for i, linea in enumerate(lineas[start_idx:], 1):
            linea = linea.strip()
            if not linea:
                continue

            sku = None
            cantidad = 1

            try:
                if formato == 'sku_cantidad':
                    # Intentar dos puntos primero
                    if ':' in linea:
                        partes = linea.split(':')
                        if len(partes) == 2 and partes[1].strip().isdigit():
                            sku = partes[0].strip().upper()
                            cantidad = int(partes[1].strip())
                    # Intentar pipe
                    elif '|' in linea:
                        partes = linea.split('|')
                        if len(partes) >= 2 and partes[1].strip().isdigit():
                            sku = partes[0].strip().upper()
                            cantidad = int(partes[1].strip())
                    # Intentar espacio
                    elif ' ' in linea:
                        partes = linea.split()
                        if partes[-1].isdigit():
                            sku = ' '.join(partes[:-1]).strip().upper()
                            cantidad = int(partes[-1])
                    # Intentar coma
                    elif ',' in linea:
                        partes = linea.split(',')
                        if len(partes) >= 2 and partes[1].strip().isdigit():
                            sku = partes[0].strip().upper()
                            cantidad = int(partes[1].strip())

                elif formato == 'csv':
                    partes = linea.split(',')
                    if len(partes) >= 2:
                        sku = partes[0].strip().upper()
                        if partes[1].strip().isdigit():
                            cantidad = int(partes[1].strip())

                elif formato == 'lista':
                    sku = linea.strip().upper()
                    cantidad = 1

                else:  # mixto - intentar todo
                    if ':' in linea:
                        partes = linea.split(':')
                        if len(partes) == 2 and partes[1].strip().isdigit():
                            sku = partes[0].strip().upper()
                            cantidad = int(partes[1].strip())
                    elif '|' in linea:
                        partes = linea.split('|')
                        if len(partes) >= 2 and partes[1].strip().isdigit():
                            sku = partes[0].strip().upper()
                            cantidad = int(partes[1].strip())
                    elif ',' in linea:
                        partes = linea.split(',')
                        if len(partes) >= 2 and partes[1].strip().isdigit():
                            sku = partes[0].strip().upper()
                            cantidad = int(partes[1].strip())
                    elif ' ' in linea:
                        partes = linea.split()
                        if partes[-1].isdigit():
                            sku = ' '.join(partes[:-1]).strip().upper()
                            cantidad = int(partes[-1])
                    else:
                        sku = linea.strip().upper()
                        cantidad = 1

                if sku and sku.replace(' ', ''):
                    resultados.append({
                        'sku': sku,
                        'cantidad': cantidad if cantidad > 0 else 1,
                        'raw_line': linea,
                        'linea': i
                    })
            except:
                continue

        return resultados

# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE DETECCIÓN DE COLUMNAS
# ═══════════════════════════════════════════════════════════════════════════════

def detectar_columna_sku(df: pd.DataFrame) -> str:
    """Detecta la columna SKU con múltiples estrategias"""
    posibles = ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO', 'CODIGO', 'ITEM', 'PART NUMBER']
    for col in df.columns:
        col_upper = str(col).upper().strip()
        for posible in posibles:
            if posible in col_upper:
                return col
    return df.columns[0]

def detectar_columna_descripcion(df: pd.DataFrame) -> str:
    """Detecta la columna de descripción"""
    posibles = ['DESC', 'DESCRIPCION', 'DESCRIPTION', 'NOMBRE', 'PRODUCTO', 'GOODS', 'ITEM NAME', 'TITULO']
    for col in df.columns:
        col_upper = str(col).upper().strip()
        for posible in posibles:
            if posible in col_upper:
                return col
    return None

def detectar_columna_stock(df: pd.DataFrame) -> str:
    """Detecta la columna de stock (Disponible > Cantidad > Stock)"""
    for col in df.columns:
        col_upper = str(col).upper().strip()
        if col_upper == 'DISPONIBLE':
            return col
    for col in df.columns:
        col_upper = str(col).upper().strip()
        if col_upper == 'CANTIDAD' or col_upper == 'CANT':
            return col
    for col in df.columns:
        col_upper = str(col).upper().strip()
        if 'STOCK' in col_upper:
            return col
    return None

# ═══════════════════════════════════════════════════════════════════════════════
# CARGA DE CATÁLOGOS INTELIGENTE
# ═══════════════════════════════════════════════════════════════════════════════

def cargar_catalogo_inteligente(archivo) -> Optional[Dict]:
    """
    Carga un catálogo con detección inteligente de marca y precios
    """
    df = cargar_archivo(archivo)
    if df is None or df.empty:
        return None

    col_sku = detectar_columna_sku(df)
    col_desc = detectar_columna_descripcion(df)

    # Usar Smart Brand Detector
    brand_info = SmartBrandDetector.detectar(
        nombre_archivo=archivo.name,
        df_muestra=df.head(50),
        col_sku=col_sku,
        col_desc=col_desc
    )

    # Usar Smart Column Mapper para precios
    mapper = SmartColumnMapper.mapear_columnas(df)

    return {
        'nombre': archivo.name,
        'df': df,
        'col_sku': col_sku,
        'col_desc': col_desc,
        'mapeo_precios': mapper,
        'brand_detected': brand_info,
        'tipo': brand_info['marca_detectada']
    }

# ═══════════════════════════════════════════════════════════════════════════════
# CARGA DE STOCK INTELIGENTE
# ═══════════════════════════════════════════════════════════════════════════════

def cargar_stock_inteligente(archivos, modo: str) -> List[Dict]:
    """
    Carga archivos de stock con detección inteligente de almacén y columnas
    """
    stocks = []

    for archivo in archivos:
        try:
            xls = pd.ExcelFile(archivo)
            for hoja in xls.sheet_names:
                hoja_upper = hoja.upper()

                # Filtrar hojas según modo
                if modo == "XIAOMI":
                    if not any(h in hoja_upper for h in ['APRI', 'YESSICA']):
                        continue
                elif modo == "UGREEN":
                    if 'APRI.001' not in hoja_upper:
                        continue
                else:  # OTRAS MARCAS
                    if 'APRI.001' not in hoja_upper:
                        continue

                df = pd.read_excel(archivo, sheet_name=hoja)
                df = limpiar_cabeceras(df)

                if df.empty:
                    continue

                col_sku = detectar_columna_sku(df)
                col_cant = detectar_columna_stock(df)

                if not col_cant:
                    st.warning(f"⚠️ Hoja '{hoja}': No se encontró columna de cantidad. Columnas disponibles: {list(df.columns)}")
                    continue

                # Detectar tipo de almacén
                tipo_almacen = 'OTRO'
                if 'YESSICA' in hoja_upper:
                    tipo_almacen = 'YESSICA'
                elif 'APRI.004' in hoja_upper:
                    tipo_almacen = 'APRI.004'
                elif 'APRI.001' in hoja_upper:
                    tipo_almacen = 'APRI.001'

                stocks.append({
                    'nombre': f"{archivo.name} [{hoja}]",
                    'df': df,
                    'col_sku': col_sku,
                    'col_cant': col_cant,
                    'hoja': hoja,
                    'tipo_almacen': tipo_almacen
                })

        except Exception as e:
            st.error(f"❌ Error en {archivo.name}: {str(e)[:80]}")

    return stocks

# ═══════════════════════════════════════════════════════════════════════════════
# BÚSQUEDA INTELIGENTE DE PRODUCTOS
# ═══════════════════════════════════════════════════════════════════════════════

def buscar_stock_por_sku(sku: str, stocks: List[Dict]) -> Dict:
    """
    Busca stock por SKU en cada almacén por separado (NO SUMA)
    """
    sku_limpio = sku.strip().upper()
    resultado = {
        'yessica': 0,
        'apri004': 0,
        'apri001': 0,
        'total': 0,
        'detalle': []
    }

    for stock in stocks:
        df = stock['df']
        col_sku = stock['col_sku']
        col_cant = stock['col_cant']

        df_sku = df[col_sku].astype(str).str.strip().str.upper()
        mask = df_sku == sku_limpio

        if mask.any():
            row = df[mask].iloc[0]
            cantidad = int(corregir_numero(row[col_cant]))
            almacen = stock['tipo_almacen']

            resultado['detalle'].append({
                'almacen': almacen,
                'cantidad': cantidad,
                'hoja': stock['hoja']
            })

            if almacen == 'YESSICA':
                resultado['yessica'] = cantidad
            elif almacen == 'APRI.004':
                resultado['apri004'] = cantidad
            elif almacen == 'APRI.001':
                resultado['apri001'] = cantidad

    resultado['total'] = resultado['yessica'] + resultado['apri004'] + resultado['apri001']
    return resultado

def buscar_producto_inteligente(sku: str, catalogos: List[Dict], stocks: List[Dict], 
                                 precio_key: str) -> Dict:
    """
    Busca un producto de forma inteligente con múltiples estrategias y sugerencias
    """
    sku_limpio = sku.strip().upper()

    # PASO 1: Buscar stock
    stock_info = buscar_stock_por_sku(sku_limpio, stocks)

    # PASO 2: Buscar en catálogos
    descripcion = f"SKU: {sku}"
    precio = 0.0
    precio_equivalente = 0
    sku_equivalente = None
    similitud_equivalente = 0
    confianza_match = 0
    catalogo_encontrado = None

    for cat in catalogos:
        df = cat['df']
        col_sku = cat['col_sku']
        col_desc = cat.get('col_desc')

        # Mapeo de precios (usar confirmado por usuario o el automático)
        mapeo_precios = cat.get('mapeo_precios_confirmado') or cat.get('mapeo_precios', {}).get('mapeo', {})

        df_sku = df[col_sku].astype(str).str.strip().str.upper()
        mask = df_sku == sku_limpio

        if mask.any():
            row = df[mask].iloc[0]

            if precio_key in mapeo_precios:
                col_precio = mapeo_precios[precio_key]
                precio = corregir_numero(row[col_precio])

            if col_desc and pd.notna(row.get(col_desc)):
                descripcion = str(row[col_desc])[:200]

            confianza_match = 100
            catalogo_encontrado = cat['nombre']
            break

    # PASO 3: Si tiene stock pero NO precio → buscar SKU equivalente por descripción
    if precio == 0 and stock_info['total'] > 0:
        # Intentar obtener descripción del stock
        desc_stock = None
        for stock in stocks:
            df = stock['df']
            col_s = stock['col_sku']
            df_s = df[col_s].astype(str).str.strip().str.upper()
            mask = df_s == sku_limpio
            if mask.any():
                row = df[mask].iloc[0]
                for col in df.columns:
                    if any(p in str(col).upper() for p in ['DESC', 'DESCRIPCION', 'PRODUCTO', 'NOMBRE']):
                        val = str(row[col])
                        if val and val != 'nan':
                            desc_stock = val
                            break
                break

        if desc_stock:
            descripcion = desc_stock[:200]
            # Buscar en catálogos por descripción similar
            for cat in catalogos:
                df = cat['df']
                col_desc = cat.get('col_desc')
                mapeo_precios = cat.get('mapeo_precios_confirmado') or cat.get('mapeo_precios', {}).get('mapeo', {})

                if not col_desc or precio_key not in mapeo_precios:
                    continue

                col_precio = mapeo_precios[precio_key]
                mejores = []

                for _, row in df.iterrows():
                    desc_cat = normalizar_texto(str(row.get(col_desc, '')))
                    scores = calcular_similitud_avanzada(desc_stock, desc_cat)
                    if scores['combinado'] >= 60:
                        try:
                            p = corregir_numero(row[col_precio])
                            if p > 0:
                                mejores.append({
                                    'sku': str(row[cat['col_sku']]).strip().upper(),
                                    'descripcion': str(row[col_desc])[:200],
                                    'precio': p,
                                    'score': scores['combinado'],
                                    'confianza': scores['confianza']
                                })
                        except:
                            pass

                if mejores:
                    mejores.sort(key=lambda x: x['score'], reverse=True)
                    mejor = mejores[0]
                    sku_equivalente = mejor['sku']
                    similitud_equivalente = mejor['score']
                    precio_equivalente = mejor['precio']
                    break

    # Si nunca encontró descripción pero hay en stock
    if descripcion == f"SKU: {sku}" and stock_info['total'] > 0:
        for stock in stocks:
            df = stock['df']
            col_s = stock['col_sku']
            df_s = df[col_s].astype(str).str.strip().str.upper()
            mask = df_s == sku_limpio
            if mask.any():
                row = df[mask].iloc[0]
                for col in df.columns:
                    if any(p in str(col).upper() for p in ['DESC', 'DESCRIPCION', 'PRODUCTO', 'NOMBRE']):
                        val = str(row[col])
                        if val and val != 'nan':
                            descripcion = val[:200]
                            break
                break

    return {
        'sku': sku,
        'descripcion': descripcion,
        'precio': precio,
        'precio_equivalente': precio_equivalente,
        'sku_equivalente': sku_equivalente,
        'similitud_equivalente': similitud_equivalente,
        'stock_yessica': stock_info['yessica'],
        'stock_apri004': stock_info['apri004'],
        'stock_apri001': stock_info['apri001'],
        'stock_total': stock_info['total'],
        'tiene_stock': stock_info['total'] > 0,
        'tiene_precio': precio > 0,
        'confianza_match': confianza_match,
        'catalogo': catalogo_encontrado
    }

def procesar_lista_productos(pedidos: List[Dict], catalogos: List[Dict], 
                              stocks: List[Dict], precio_key: str) -> List[Dict]:
    """
    Procesa una lista de pedidos y retorna resultados con metadata de confianza
    """
    resultados = []

    for pedido in pedidos:
        prod = buscar_producto_inteligente(
            pedido['sku'], catalogos, stocks, precio_key
        )

        # Determinar estado y cantidad a cotizar
        cantidad_solicitada = pedido['cantidad']

        if prod['tiene_precio'] and prod['tiene_stock']:
            cantidad_cotizar = min(cantidad_solicitada, prod['stock_total'])
            if cantidad_cotizar < cantidad_solicitada:
                estado = "⚠️ Stock insuficiente"
                estado_clase = "warning"
            else:
                estado = "✅ OK"
                estado_clase = "success"
        elif prod['tiene_stock'] and not prod['tiene_precio']:
            cantidad_cotizar = 0
            estado = "⚠️ Stock sin precio"
            estado_clase = "error"
        elif not prod['tiene_precio'] and not prod['tiene_stock']:
            cantidad_cotizar = 0
            estado = "❌ No encontrado"
            estado_clase = "neutral"
        else:  # tiene precio pero no stock
            cantidad_cotizar = 0
            estado = "📋 Solo precio"
            estado_clase = "info"

        resultados.append({
            **prod,
            'cantidad_solicitada': cantidad_solicitada,
            'cantidad_cotizar': cantidad_cotizar,
            'estado': estado,
            'estado_clase': estado_clase
        })

    return resultados

# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE UI HTML
# ═══════════════════════════════════════════════════════════════════════════════

def badge_stock(yessica: int, apri004: int, apri001: int) -> str:
    """Genera HTML de badges de stock por almacén"""
    return f"""
    <div style="display:flex; flex-wrap:wrap; gap:6px; margin:6px 0;">
        <span class="badge-yessica">🟢 YESSICA: {yessica}</span>
        <span class="badge-apri004">🟡 APRI.004: {apri004}</span>
        <span class="badge-apri001">🔴 APRI.001: {apri001}</span>
    </div>
    """

def badge_confianza(score: float) -> str:
    """Genera badge de confianza"""
    if score >= 90:
        return f'<span style="color:#4CAF50;font-weight:bold;">🟢 {score:.0f}%</span>'
    elif score >= 70:
        return f'<span style="color:#FF9800;font-weight:bold;">🟡 {score:.0f}%</span>'
    elif score >= 50:
        return f'<span style="color:#ff5722;font-weight:bold;">🟠 {score:.0f}%</span>'
    else:
        return f'<span style="color:#f44336;font-weight:bold;">🔴 {score:.0f}%</span>'

def generar_excel_inteligente(items: List[Dict], cliente: str, ruc: str, 
                               vendedor: str = "") -> bytes:
    """Genera Excel profesional con formato inteligente"""
    output = io.BytesIO()

    df = pd.DataFrame(items)

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Cotizacion', index=False, startrow=7)

        workbook = writer.book
        ws = writer.sheets['Cotizacion']

        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers

        # Estilos
        header_font = Font(bold=True, color="FFFFFF", size=11)
        header_fill = PatternFill(start_color="e94560", end_color="e94560", fill_type="solid")
        title_font = Font(bold=True, size=16, color="e94560")
        subtitle_font = Font(bold=True, size=11, color="333333")
        border = Border(
            left=Side(style='thin', color='DDDDDD'),
            right=Side(style='thin', color='DDDDDD'),
            top=Side(style='thin', color='DDDDDD'),
            bottom=Side(style='thin', color='DDDDDD')
        )

        # Título
        ws['A1'] = 'QTC SMART SALES AI'
        ws['A1'].font = title_font
        ws.merge_cells('A1:E1')

        ws['A2'] = 'Cotización Inteligente'
        ws['A2'].font = Font(size=12, color="666666")
        ws.merge_cells('A2:E2')

        # Info
        ws['A4'] = 'FECHA:'
        ws['B4'] = datetime.now().strftime("%d/%m/%Y %H:%M")
        ws['A5'] = 'CLIENTE:'
        ws['B5'] = cliente.upper() if cliente else 'No especificado'
        ws['A6'] = 'RUC:'
        ws['B6'] = ruc if ruc else '-'
        if vendedor:
            ws['A7'] = 'VENDEDOR:'
            ws['B7'] = vendedor

        for r in [4,5,6,7]:
            ws[f'A{r}'].font = subtitle_font

        # Headers de tabla
        headers = ['SKU', 'DESCRIPCIÓN', 'CANTIDAD', 'PRECIO UNIT.', 'TOTAL']
        for i, header in enumerate(headers, start=1):
            cell = ws.cell(row=8, column=i, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border

        # Datos
        for row_idx, item in enumerate(items, start=9):
            ws.cell(row=row_idx, column=1, value=item['sku']).border = border
            ws.cell(row=row_idx, column=2, value=item['descripcion']).border = border
            ws.cell(row=row_idx, column=3, value=item['cantidad']).border = border
            ws.cell(row=row_idx, column=3).alignment = Alignment(horizontal="center")

            precio_cell = ws.cell(row=row_idx, column=4, value=item['precio'])
            precio_cell.number_format = '"S/" #,##0.00'
            precio_cell.border = border
            precio_cell.alignment = Alignment(horizontal="right")

            total_cell = ws.cell(row=row_idx, column=5, value=item['total'])
            total_cell.number_format = '"S/" #,##0.00'
            total_cell.border = border
            total_cell.alignment = Alignment(horizontal="right")

        # Total
        total_row = len(items) + 9
        total_label = ws.cell(row=total_row, column=4, value='TOTAL S/.')
        total_label.font = Font(bold=True, color="FFFFFF", size=12)
        total_label.fill = PatternFill(start_color="e94560", end_color="e94560", fill_type="solid")
        total_label.border = border
        total_label.alignment = Alignment(horizontal="center")

        total_valor = ws.cell(row=total_row, column=5, value=sum(item['total'] for item in items))
        total_valor.number_format = '"S/" #,##0.00'
        total_valor.font = Font(bold=True, size=12)
        total_valor.border = border
        total_valor.alignment = Alignment(horizontal="right")

        # Anchos
        ws.column_dimensions['A'].width = 22
        ws.column_dimensions['B'].width = 100
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 18
        ws.column_dimensions['E'].width = 18

        ws.freeze_panes = 'A9'

    return output.getvalue()

# ═══════════════════════════════════════════════════════════════════════════════
# INICIALIZACIÓN DE SESIÓN
# ═══════════════════════════════════════════════════════════════════════════════

def init_session():
    """Inicializa todas las variables de estado"""
    defaults = {
        'auth': False,
        'modo': 'XIAOMI',
        'precio_key': 'P. VIP',
        'catalogos': [],
        'stocks': [],
        'carrito': [],
        'resultados_inteligentes': [],
        'input_preview': None,
        'input_parsed': None,
        'mapeos_confirmados': {},
        'user_role': 'INVITADO',
        'user_name': 'Invitado'
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()

# ═══════════════════════════════════════════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════════════════════════════════════════

if not st.session_state.auth:
    st.markdown("""
    <style>
        .login-container {
            background: rgba(255,255,255,0.95);
            border-radius: 24px;
            padding: 2.5rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 420px;
            margin: 0 auto;
        }
        .login-title {
            color: #1a1a2e;
            font-size: 1.8rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .login-subtitle {
            color: #666;
            text-align: center;
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
        }
        .login-input label {
            color: #333 !important;
            font-weight: 600;
        }
        .login-input input {
            background: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 0.75rem;
        }
        .login-btn {
            background: linear-gradient(135deg, #e94560 0%, #c73e54 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.75rem;
            font-weight: 600;
            width: 100%;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .login-btn:hover {
            transform: scale(1.02);
        }
        .guest-btn {
            background: transparent;
            color: #666;
            border: 1px solid #ddd;
            border-radius: 12px;
            padding: 0.75rem;
            font-weight: 500;
            width: 100%;
            cursor: pointer;
            margin-top: 0.5rem;
        }
        .version-tag {
            text-align: center;
            color: #999;
            font-size: 0.75rem;
            margin-top: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)

        st.markdown('<div class="login-title">🧠 QTC Smart Sales AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Cotizador Inteligente con IA</div>', unsafe_allow_html=True)

        st.markdown('<div class="login-input">', unsafe_allow_html=True)
        user = st.text_input("👤 Usuario", placeholder="admin / kimberly / vendedor")
        pw = st.text_input("🔒 Contraseña", type="password")
        st.markdown('</div>', unsafe_allow_html=True)

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🚀 Ingresar", use_container_width=True, type="primary"):
                credenciales = {
                    "admin": {"password": "qtc2026", "role": "ADMIN", "name": "Administrador"},
                    "kimberly": {"password": "kam2026", "role": "KAM", "name": "Kimberly"},
                    "vendedor": {"password": "ventas2026", "role": "VENDEDOR", "name": "Vendedor"}
                }
                if user in credenciales and pw == credenciales[user]["password"]:
                    st.session_state.auth = True
                    st.session_state.user_role = credenciales[user]["role"]
                    st.session_state.user_name = credenciales[user]["name"]
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
        with col_btn2:
            if st.button("👤 Invitado", use_container_width=True):
                st.session_state.auth = True
                st.session_state.user_role = "INVITADO"
                st.session_state.user_name = "Invitado"
                st.rerun()

        st.markdown('<div class="version-tag">v5.0 | Motor IA activado</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════

col1, col2, col3 = st.columns([1, 5, 2])
with col1:
    st.markdown("<h1 style='color:#e94560;font-size:2rem;margin:0;'>🧠</h1>", unsafe_allow_html=True)
with col2:
    st.markdown("<h1 style='color:#ffffff;margin:0;font-size:1.5rem;'>QTC Smart Sales AI</h1>", unsafe_allow_html=True)
    st.caption("Cotizador Inteligente | Reconocimiento automático de precios · Detección de marca · Matching difuso")
with col3:
    role_icons = {"ADMIN": "🔧", "KAM": "⭐", "VENDEDOR": "🛒", "INVITADO": "👤"}
    icon = role_icons.get(st.session_state.user_role, "👤")
    st.markdown(f"""
    <div style="background:rgba(233,69,96,0.2);border:1px solid #e94560;border-radius:12px;padding:0.5rem 1rem;text-align:right;">
        <span style="color:#ffffff;font-weight:600;">{icon} {st.session_state.user_name}</span><br>
        <span style="color:#aaa;font-size:0.7rem;">{st.session_state.user_role}</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 Cerrar Sesión", key="logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR INTELIGENTE
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### ⚙️ Panel Inteligente")

    # ── Selector de modo/marca ──
    st.markdown("**📌 Modo / Marca**")
    col_m1, col_m2 = st.columns([3, 1])
    with col_m1:
        modo_sel = st.selectbox(
            "Marca",
            ["XIAOMI", "UGREEN", "OTRAS MARCAS"],
            index=["XIAOMI", "UGREEN", "OTRAS MARCAS"].index(st.session_state.modo),
            label_visibility="collapsed"
        )
        st.session_state.modo = modo_sel
    with col_m2:
        if st.button("🔄", help="Auto-detectar marca de catálogos cargados"):
            if st.session_state.catalogos:
                # Usar el primer catálogo para detectar
                cat = st.session_state.catalogos[0]
                brand = cat.get('brand_detected', {})
                if brand.get('marca_detectada'):
                    st.session_state.modo = brand['marca_detectada']
                    st.success(f"Detectado: {brand['marca_detectada']}")
                    st.rerun()

    # ── Selector de nivel de precio ──
    st.markdown("**💰 Nivel de Precio**")
    precio_sel = st.selectbox(
        "Precio",
        ["P. VIP", "P. BOX", "P. IR"],
        index=["P. VIP", "P. BOX", "P. IR"].index(st.session_state.precio_key),
        label_visibility="collapsed"
    )
    st.session_state.precio_key = precio_sel

    st.markdown("---")

    # ── Carga de Catálogos ──
    st.markdown("**📚 Catálogos de Precios**")
    archivos_cat = st.file_uploader(
        "Subir catálogo(s)",
        type=['xlsx', 'xls', 'csv'],
        accept_multiple_files=True,
        key="cat_upload",
        label_visibility="collapsed"
    )

    if archivos_cat:
        nuevos_catalogos = []
        for archivo in archivos_cat:
            # Verificar si ya está cargado
            ya_cargado = any(c['nombre'] == archivo.name for c in st.session_state.catalogos)
            if ya_cargado:
                continue

            with st.spinner(f"🧠 Analizando {archivo.name[:20]}..."):
                cat = cargar_catalogo_inteligente(archivo)
                if cat:
                    nuevos_catalogos.append(cat)

        if nuevos_catalogos:
            st.session_state.catalogos.extend(nuevos_catalogos)
            st.rerun()

        # Mostrar catálogos cargados con info de detección
        for cat in st.session_state.catalogos:
            brand = cat.get('brand_detected', {})
            marca = brand.get('marca_detectada', 'DESCONOCIDO')
            conf = brand.get('confianza', '?')
            icono = "🟢" if conf == 'alta' else "🟡" if conf == 'media' else "🔴"
            st.markdown(f"{icono} **{cat['nombre'][:25]}** | {marca}")

    # ── SMART COLUMN MAPPER UI ──
    if st.session_state.catalogos:
        st.markdown("---")
        st.markdown("**🎯 Mapeo de Precios**")

        # Verificar si algún catálogo necesita confirmación de mapeo
        necesita_confirmacion = False
        for idx, cat in enumerate(st.session_state.catalogos):
            mapper = cat.get('mapeo_precios', {})
            if mapper.get('requiere_confirmacion', False):
                necesita_confirmacion = True

                st.markdown(f"""
                <div class="mapper-container">
                    <strong>📁 {cat['nombre'][:20]}</strong><br>
                    <span style="font-size:0.8rem;">Confianza: {mapper.get('confianza', '?' ).upper()}</span>
                </div>
                """, unsafe_allow_html=True)

                columnas = ['(No usar)'] + mapper.get('columnas_disponibles', [])

                # Mostrar mapeo actual con selectores
                mapeo_actual = cat.get('mapeo_precios_confirmado') or mapper.get('mapeo', {})

                for precio_tipo in ['P. IR', 'P. BOX', 'P. VIP']:
                    col_actual = mapeo_actual.get(precio_tipo, '(No usar)')
                    score = mapper.get('scores', {}).get(precio_tipo, 0)

                    nuevo_valor = st.selectbox(
                        f"{precio_tipo} (score: {score:.0f}%)",
                        columnas,
                        index=columnas.index(col_actual) if col_actual in columnas else 0,
                        key=f"mapper_{idx}_{precio_tipo}"
                    )

                    if nuevo_valor != '(No usar)':
                        if 'mapeo_precios_confirmado' not in cat:
                            cat['mapeo_precios_confirmado'] = {}
                        cat['mapeo_precios_confirmado'][precio_tipo] = nuevo_valor
                    elif 'mapeo_precios_confirmado' in cat and precio_tipo in cat['mapeo_precios_confirmado']:
                        del cat['mapeo_precios_confirmado'][precio_tipo]

        if not necesita_confirmacion:
            st.success("✅ Mapeo automático confirmado")

        if st.button("✅ Confirmar mapeo de precios", use_container_width=True, type="primary"):
            st.success("Mapeo guardado correctamente")
            st.rerun()

    st.markdown("---")

    # ── Carga de Stock ──
    st.markdown("**📦 Reportes de Stock**")
    st.caption("Hojas: APRI.001, APRI.004, YESSICA")
    archivos_stock = st.file_uploader(
        "Subir stock",
        type=['xlsx', 'xls'],
        accept_multiple_files=True,
        key="stock_upload",
        label_visibility="collapsed"
    )

    if archivos_stock:
        with st.spinner("🧠 Procesando stock..."):
            stocks = cargar_stock_inteligente(archivos_stock, st.session_state.modo)
            if stocks:
                st.session_state.stocks = stocks
                for s in stocks:
                    icono = {"YESSICA": "🟢", "APRI.004": "🟡", "APRI.001": "🔴"}.get(s['tipo_almacen'], "⚪")
                    st.markdown(f"{icono} **{s['tipo_almacen']}**: {s['hoja'][:15]}")

    st.markdown("---")

    # ── Resumen de Carrito ──
    if st.session_state.carrito:
        st.markdown("**🛒 Carrito**")
        total = sum(i['total'] for i in st.session_state.carrito)
        st.metric("Productos", len(st.session_state.carrito))
        st.metric("Total", f"S/ {total:,.2f}")

        if st.button("🧹 Limpiar carrito", use_container_width=True):
            st.session_state.carrito = []
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# ÁREA PRINCIPAL: 1 SOLO TAB - COTIZADOR INTELIGENTE
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="background:linear-gradient(90deg, rgba(233,69,96,0.2) 0%, rgba(233,69,96,0) 100%);padding:1rem;border-left:4px solid #e94560;border-radius:0 8px 8px 0;margin-bottom:1rem;">
    <h2 style="margin:0;color:#ffffff;">🧠 Cotizador Inteligente</h2>
    <p style="margin:0;color:#aaa;font-size:0.85rem;">Ingresa tus productos en cualquier formato. El sistema detecta automáticamente SKUs, precios y stock.</p>
</div>
""", unsafe_allow_html=True)

# Verificar si hay catálogos y stock cargados
hay_catalogos = len(st.session_state.catalogos) > 0
hay_stock = len(st.session_state.stocks) > 0

if not hay_catalogos or not hay_stock:
    col_w1, col_w2, col_w3 = st.columns([1, 3, 1])
    with col_w2:
        st.info("""
        ### 📋 Para empezar:
        1. **Sube tus catálogos de precios** en el panel lateral (Excel o CSV)
        2. **Sube tus reportes de stock** (Excel con hojas APRI.001, APRI.004, YESSICA)
        3. El sistema detectará automáticamente las marcas y columnas de precios
        4. **Ingresa tus productos** en el campo de abajo

        💡 **Tip:** Puedes usar cualquier formato: `SKU:CANTIDAD`, `SKU CANTIDAD`, CSV, o lista simple.
        """)

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1: INPUT INTELIGENTE UNIVERSAL
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="background:rgba(255,255,255,0.05);border-radius:16px;padding:1.5rem;margin:1rem 0;">
    <h3 style="margin:0 0 0.5rem 0;">📝 Ingresa tus productos</h3>
    <p style="color:#aaa;margin:0;font-size:0.8rem;">Acepta: SKU:CANTIDAD | SKU CANTIDAD | CSV | Lista simple</p>
</div>
""", unsafe_allow_html=True)

texto_input = st.text_area(
    "Entrada",
    height=180,
    placeholder="Ejemplos:\nRN9401276NA8:100\nCN0200047BK8:50\nRN0200065BK8:25\n\nO también (CSV):\nSKU,CANTIDAD\nRN9401276NA8,100\nCN0200047BK8,50",
    label_visibility="collapsed"
)

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])

with col_btn1:
    analizar = st.button("🔍 Analizar Entrada", use_container_width=True, type="secondary")

with col_btn2:
    procesar = st.button("⚡ Procesar Todo", use_container_width=True, type="primary", 
                         disabled=not hay_catalogos or not hay_stock)

with col_btn3:
    if st.session_state.resultados_inteligentes:
        validos = [r for r in st.session_state.resultados_inteligentes if r['cantidad_cotizar'] > 0 and r['tiene_precio']]
        if st.button(f"📋 Agregar {len(validos)} válidos al carrito", use_container_width=True):
            agregados = 0
            for prod in st.session_state.resultados_inteligentes:
                if prod['cantidad_cotizar'] > 0 and prod['tiene_precio']:
                    item = {
                        'sku': prod['sku'],
                        'descripcion': prod['descripcion'],
                        'cantidad': prod['cantidad_cotizar'],
                        'precio': prod['precio'],
                        'total': prod['precio'] * prod['cantidad_cotizar'],
                        'stock_yessica': prod.get('stock_yessica', 0),
                        'stock_apri004': prod.get('stock_apri004', 0),
                        'stock_apri001': prod.get('stock_apri001', 0)
                    }
                    st.session_state.carrito.append(item)
                    agregados += 1
            st.success(f"✅ {agregados} productos agregados")
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2: PREVIEW INTELIGENTE
# ═══════════════════════════════════════════════════════════════════════════════

if analizar and texto_input:
    parser = SmartInputParser()
    info_formato = parser.detectar_formato(texto_input)
    parsed = parser.parsear(texto_input)

    st.session_state.input_parsed = parsed
    st.session_state.input_preview = info_formato

    if parsed:
        st.markdown(f"""
        <div style="background:rgba(76,175,80,0.1);border:1px solid #4CAF50;border-radius:12px;padding:1rem;margin:1rem 0;">
            <strong>📋 Vista previa</strong> | Formato detectado: <strong>{info_formato['formato']}</strong> 
            | Confianza: {badge_confianza(info_formato['confianza'])} 
            | Productos detectados: <strong>{len(parsed)}</strong>
        </div>
        """, unsafe_allow_html=True)

        # Mostrar tabla preview
        preview_data = []
        for p in parsed[:20]:  # Mostrar máximo 20
            preview_data.append({
                '#': p['linea'],
                'SKU': p['sku'],
                'Cantidad': p['cantidad']
            })

        col_prev1, col_prev2 = st.columns([2, 1])
        with col_prev1:
            st.dataframe(pd.DataFrame(preview_data), use_container_width=True, height=200, hide_index=True)
        with col_prev2:
            if len(parsed) > 20:
                st.info(f"... y {len(parsed) - 20} más")

            st.markdown("**Estadísticas de detección:**")
            stats = info_formato.get('stats', {})
            for k, v in stats.items():
                st.markdown(f"- {k}: {v}")
    else:
        st.warning("⚠️ No se detectaron productos válidos. Verifica el formato.")

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3: PROCESAMIENTO Y RESULTADOS INTELIGENTES
# ═══════════════════════════════════════════════════════════════════════════════

if procesar and texto_input:
    if not hay_catalogos:
        st.error("❌ Carga al menos un catálogo de precios en el panel lateral")
    elif not hay_stock:
        st.error("❌ Carga al menos un reporte de stock en el panel lateral")
    else:
        parser = SmartInputParser()
        parsed = parser.parsear(texto_input)

        if not parsed:
            st.warning("No se encontraron productos válidos en la entrada")
        else:
            with st.spinner(f"🧠 Procesando {len(parsed)} productos con IA..."):
                resultados = procesar_lista_productos(
                    parsed, 
                    st.session_state.catalogos,
                    st.session_state.stocks,
                    st.session_state.precio_key
                )
                st.session_state.resultados_inteligentes = resultados

            # Contadores
            total = len(resultados)
            con_precio = sum(1 for r in resultados if r['tiene_precio'])
            con_stock = sum(1 for r in resultados if r['tiene_stock'])
            ok_completo = sum(1 for r in resultados if r['tiene_precio'] and r['tiene_stock'])
            sin_precio = total - con_precio
            sin_stock = total - con_stock

            st.markdown(f"""
            <div class="counter-summary">
                <div class="counter-item">📋 Total: <span class="counter-number">{total}</span></div>
                <div class="counter-item" style="background:rgba(76,175,80,0.3);">✅ OK: <span class="counter-number" style="color:#4CAF50;">{ok_completo}</span></div>
                <div class="counter-item">💰 Con precio: <span class="counter-number">{con_precio}</span></div>
                <div class="counter-item">📦 Con stock: <span class="counter-number">{con_stock}</span></div>
                <div class="counter-item" style="background:rgba(244,67,54,0.2);">❌ Sin precio: <span class="counter-number" style="color:#f44336;">{sin_precio}</span></div>
                <div class="counter-item" style="background:rgba(255,152,0,0.2);">⚠️ Sin stock: <span class="counter-number" style="color:#FF9800;">{sin_stock}</span></div>
            </div>
            """, unsafe_allow_html=True)

# Mostrar resultados
if st.session_state.resultados_inteligentes:
    st.markdown("---")
    st.markdown(f"<h3>📊 Resultados ({len(st.session_state.resultados_inteligentes)} productos)</h3>", unsafe_allow_html=True)

    for prod in st.session_state.resultados_inteligentes:
        # Determinar clase de card
        if prod['tiene_precio'] and prod['tiene_stock']:
            if prod['cantidad_cotizar'] < prod['cantidad_solicitada']:
                card_class = "card-warning"
                estado_tag = "⚠️ Stock insuficiente"
                color_tag = "#FF9800"
            else:
                card_class = "card-success"
                estado_tag = "✅ Con stock y precio"
                color_tag = "#4CAF50"
        elif prod['tiene_stock'] and not prod['tiene_precio']:
            card_class = "card-error"
            estado_tag = "⚠️ Stock sin precio"
            color_tag = "#f44336"
        elif not prod['tiene_stock'] and prod['tiene_precio']:
            card_class = "card-info"
            estado_tag = "📋 Solo precio"
            color_tag = "#2196F3"
        else:
            card_class = "card-neutral"
            estado_tag = "❌ No disponible"
            color_tag = "#9e9e9e"

        # Badge de stock
        badge = badge_stock(prod['stock_yessica'], prod['stock_apri004'], prod['stock_apri001'])

        # Card HTML
        html_card = f"""
        <div class="smart-card {card_class}">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <div>
                    <strong style="font-size:1.1rem;color:#1a1a2e;">📦 {prod['sku']}</strong>
                    <span style="background:{color_tag};color:white;padding:2px 10px;border-radius:12px;font-size:0.75rem;margin-left:8px;">{estado_tag}</span>
                </div>
                <div style="text-align:right;">
                    <span style="color:#666;font-size:0.8rem;">Solicitado: <strong>{prod['cantidad_solicitada']}</strong></span>
                </div>
            </div>

            <div style="color:#333;margin-bottom:8px;">
                <strong>📝</strong> {prod['descripcion'][:120]}
            </div>
        """

        if prod['tiene_precio']:
            html_card += f"""
            <div style="color:#333;margin-bottom:8px;">
                💰 <strong style="color:#e67e22;font-size:1.1rem;">S/ {prod['precio']:,.2f}</strong>
                <span style="color:#999;font-size:0.8rem;"> ({st.session_state.precio_key})</span>
            </div>
            """

        html_card += badge

        if prod['cantidad_cotizar'] > 0 and prod['tiene_precio']:
            html_card += f"""
            <div style="margin-top:10px;padding-top:10px;border-top:1px solid #eee;color:#333;">
                ✅ <strong>Cotizar:</strong> {prod['cantidad_cotizar']} unidades | 
                <strong>Subtotal:</strong> <span style="color:#e67e22;font-weight:bold;">S/ {prod['precio'] * prod['cantidad_cotizar']:,.2f}</span>
            </div>
            """

        # Sugerencia de SKU equivalente
        if prod.get('sku_equivalente') and prod['similitud_equivalente'] > 60:
            html_card += f"""
            <div class="suggestion-box" style="margin-top:10px;">
                <strong>💡 ¿Quizás quisiste decir?</strong><br>
                <strong>SKU:</strong> <code>{prod['sku_equivalente']}</code> 
                (confianza: {prod['similitud_equivalente']:.0f}%)<br>
                <strong>Precio:</strong> S/ {prod['precio_equivalente']:,.2f}<br>
                <em>{prod.get('descripcion', '')[:80]}</em>
            </div>
            """

        html_card += "</div>"

        st.markdown(html_card, unsafe_allow_html=True)

        # Botón individual para agregar al carrito
        if prod['cantidad_cotizar'] > 0 and prod['tiene_precio']:
            if st.button(f"➕ Agregar {prod['sku']} al carrito", key=f"add_{prod['sku']}"):
                item = {
                    'sku': prod['sku'],
                    'descripcion': prod['descripcion'],
                    'cantidad': prod['cantidad_cotizar'],
                    'precio': prod['precio'],
                    'total': prod['precio'] * prod['cantidad_cotizar'],
                    'stock_yessica': prod.get('stock_yessica', 0),
                    'stock_apri004': prod.get('stock_apri004', 0),
                    'stock_apri001': prod.get('stock_apri001', 0)
                }
                st.session_state.carrito.append(item)
                st.success(f"✅ {prod['sku']} agregado")
                st.rerun()

        st.markdown("")  # Espacio entre cards

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4: CARRITO INTEGRADO (Acordeón)
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")

with st.expander(f"🛒 Carrito de Cotización ({len(st.session_state.carrito)} productos) | **S/ {sum(i['total'] for i in st.session_state.carrito):,.2f}**", 
                  expanded=len(st.session_state.carrito) > 0):

    if not st.session_state.carrito:
        st.info("No hay productos en el carrito. Procesa productos y agrégalos.")
    else:
        # Headers
        col_h1, col_h2, col_h3, col_h4, col_h5, col_h6 = st.columns([2, 3, 1, 1.2, 1.2, 0.5])
        col_h1.markdown("**SKU**")
        col_h2.markdown("**Descripción**")
        col_h3.markdown("**Cant.**")
        col_h4.markdown("**Precio**")
        col_h5.markdown("**Total**")
        col_h6.markdown("")

        st.markdown("<div style='border-bottom:1px solid rgba(255,255,255,0.2);margin:0.3rem 0;'></div>", unsafe_allow_html=True)

        # Items del carrito
        items_to_remove = []
        for idx, item in enumerate(st.session_state.carrito):
            col_i1, col_i2, col_i3, col_i4, col_i5, col_i6 = st.columns([2, 3, 1, 1.2, 1.2, 0.5])

            with col_i1:
                st.write(f"**{item['sku']}**")
            with col_i2:
                st.write(item['descripcion'][:40])
            with col_i3:
                nueva_cant = st.number_input("Cant", min_value=1, value=item['cantidad'], 
                                              step=1, key=f"cart_cant_{idx}", label_visibility="collapsed")
                if nueva_cant != item['cantidad']:
                    item['cantidad'] = nueva_cant
                    item['total'] = item['precio'] * nueva_cant
                    st.rerun()
            with col_i4:
                st.write(f"S/ {item['precio']:,.2f}")
            with col_i5:
                st.write(f"**S/ {item['total']:,.2f}**")
            with col_i6:
                if st.button("🗑️", key=f"del_cart_{idx}"):
                    items_to_remove.append(idx)

            # Stock badges
            badge = badge_stock(
                item.get('stock_yessica', 0),
                item.get('stock_apri004', 0),
                item.get('stock_apri001', 0)
            )
            st.markdown(f'<div style="margin:-0.5rem 0 0.5rem 0;">{badge}</div>', unsafe_allow_html=True)

            st.markdown("<div style='border-bottom:1px solid rgba(255,255,255,0.1);margin:0.2rem 0;'></div>", unsafe_allow_html=True)

        # Eliminar items marcados
        for idx in sorted(items_to_remove, reverse=True):
            st.session_state.carrito.pop(idx)
        if items_to_remove:
            st.rerun()

        # Total
        total_general = sum(i['total'] for i in st.session_state.carrito)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#e94560 0%,#c73e54 100%);border-radius:12px;padding:1rem;margin:1rem 0;text-align:center;">
            <span style="color:white;font-size:1.5rem;font-weight:bold;">TOTAL: S/ {total_general:,.2f}</span>
        </div>
        """)

        # ═══════════════════════════════════════════════════════════════════
        # EXPORTACIÓN
        # ═══════════════════════════════════════════════════════════════════
        st.markdown("### 📋 Exportar Cotización")

        col_cli1, col_cli2 = st.columns(2)
        with col_cli1:
            cliente = st.text_input("Nombre del cliente", placeholder="Ej: Distribuidores SAC", key="exp_cliente")
        with col_cli2:
            ruc = st.text_input("RUC / DNI", placeholder="Ej: 20123456789", key="exp_ruc")

        col_exp1, col_exp2, col_exp3 = st.columns(3)

        with col_exp1:
            if st.button("📥 Exportar Excel", type="primary", use_container_width=True):
                if cliente:
                    items_export = [
                        {
                            'sku': i['sku'], 
                            'descripcion': i['descripcion'], 
                            'cantidad': i['cantidad'], 
                            'precio': i['precio'], 
                            'total': i['total']
                        } 
                        for i in st.session_state.carrito
                    ]
                    excel = generar_excel_inteligente(
                        items_export, 
                        cliente, 
                        ruc,
                        st.session_state.user_name
                    )
                    filename = f"Cotizacion_{cliente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
                    st.download_button(
                        "💾 Descargar Excel", 
                        data=excel, 
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    st.balloons()
                else:
                    st.warning("⚠️ Ingresa el nombre del cliente")

        with col_exp2:
            if st.button("📋 Copiar CSV", use_container_width=True):
                csv_lines = ["SKU,Descripción,Cantidad,Precio Unit.,Subtotal"]
                for item in st.session_state.carrito:
                    desc = item['descripcion'].replace(',', ' ')
                    csv_lines.append(f"{item['sku']},{desc},{item['cantidad']},{item['precio']:.2f},{item['total']:.2f}")
                csv_lines.append(f"TOTAL,,,,{total_general:.2f}")
                csv_text = "\n".join(csv_lines)
                st.code(csv_text, language="csv")

        with col_exp3:
            if st.button("🧹 Limpiar todo", use_container_width=True):
                st.session_state.carrito = []
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 5: BÚSQUEDA INDIVIDUAL (opcional, colapsada)
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")

with st.expander("🔍 Búsqueda Individual (por SKU o descripción)"):
    busqueda = st.text_input("Buscar", placeholder="Ej: RN0200065 o 'Type-C earphones'", key="search_individual")

    if busqueda and len(busqueda) >= 2 and hay_catalogos:
        with st.spinner("🧠 Buscando..."):
            productos_encontrados = {}

            for cat in st.session_state.catalogos:
                df = cat['df']
                col_sku = cat['col_sku']
                col_desc = cat.get('col_desc')
                mapeo = cat.get('mapeo_precios_confirmado') or cat.get('mapeo_precios', {}).get('mapeo', {})

                # Buscar por SKU
                mask_sku = df[col_sku].astype(str).str.contains(busqueda, case=False, na=False)

                # Buscar por descripción
                mask_desc = pd.Series([False] * len(df))
                if col_desc:
                    mask_desc = df[col_desc].astype(str).str.contains(busqueda, case=False, na=False)

                mask = mask_sku | mask_desc

                for _, row in df[mask].head(20).iterrows():
                    sku = str(row[col_sku]).strip().upper()
                    desc = str(row[col_desc])[:200] if col_desc and pd.notna(row.get(col_desc)) else f"SKU: {sku}"

                    precio = 0.0
                    if st.session_state.precio_key in mapeo:
                        precio = corregir_numero(row[mapeo[st.session_state.precio_key]])

                    # Buscar stock
                    stock_info = buscar_stock_por_sku(sku, st.session_state.stocks)

                    if sku not in productos_encontrados:
                        productos_encontrados[sku] = {
                            'sku': sku,
                            'descripcion': desc,
                            'precio': precio,
                            'stock_yessica': stock_info['yessica'],
                            'stock_apri004': stock_info['apri004'],
                            'stock_apri001': stock_info['apri001'],
                            'stock_total': stock_info['total']
                        }

        if productos_encontrados:
            st.success(f"✅ {len(productos_encontrados)} productos encontrados")

            resultados_lista = list(productos_encontrados.values())
            resultados_lista.sort(key=lambda x: (-x['stock_total'], -x['precio']))

            for prod in resultados_lista:
                badge = badge_stock(prod['stock_yessica'], prod['stock_apri004'], prod['stock_apri001'])

                if prod['stock_total'] > 0 and prod['precio'] > 0:
                    color_borde = "#4CAF50"
                    estado = "✅ DISPONIBLE"
                elif prod['stock_total'] > 0:
                    color_borde = "#f44336"
                    estado = "⚠️ Stock sin precio"
                elif prod['precio'] > 0:
                    color_borde = "#2196F3"
                    estado = "📋 Solo precio"
                else:
                    color_borde = "#9e9e9e"
                    estado = "❌ No info"

                st.markdown(f"""
                <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:0.5rem;border-left:5px solid {color_borde};">
                    <div style="display:flex;justify-content:space-between;">
                        <strong style="color:#1a1a2e;">📦 {prod['sku']}</strong>
                        <span style="background:{color_borde};color:white;padding:2px 8px;border-radius:12px;font-size:0.75rem;">{estado}</span>
                    </div>
                    <div style="color:#333;margin:4px 0;">{prod['descripcion']}</div>
                    <div style="color:#333;">💰 <strong style="color:#e67e22;">S/ {prod['precio']:,.2f}</strong></div>
                    <div>{badge}</div>
                </div>
                """, unsafe_allow_html=True)

                if prod['stock_total'] > 0 and prod['precio'] > 0:
                    col_sc, col_sb = st.columns([1, 3])
                    with col_sc:
                        cant_add = st.number_input("Cantidad", min_value=1, max_value=prod['stock_total'], 
                                                    value=1, key=f"search_cant_{prod['sku']}")
                    with col_sb:
                        if st.button(f"➕ Agregar", key=f"search_add_{prod['sku']}"):
                            st.session_state.carrito.append({
                                'sku': prod['sku'],
                                'descripcion': prod['descripcion'],
                                'cantidad': cant_add,
                                'precio': prod['precio'],
                                'total': prod['precio'] * cant_add,
                                'stock_yessica': prod['stock_yessica'],
                                'stock_apri004': prod['stock_apri004'],
                                'stock_apri001': prod['stock_apri001']
                            })
                            st.success(f"✅ Agregado {prod['sku']}")
                            st.rerun()
        else:
            st.info("No se encontraron productos con ese criterio")

# ═══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown(f"""
<div class="footer">
    🧠 QTC Smart Sales AI v5.0 | Motor de reconocimiento inteligente activado | 
    Modo: {st.session_state.modo} | Precio: {st.session_state.precio_key} | 
    Catálogos: {len(st.session_state.catalogos)} | Stock: {len(st.session_state.stocks)} almacenes | 
    {datetime.now().strftime("%Y-%m-%d %H:%M")}
</div>
""", unsafe_allow_html=True)
