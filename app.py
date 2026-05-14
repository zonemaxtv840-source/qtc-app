# archivo: app_production.py
import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
from datetime import datetime
import os

# ============================================
# CONEXIÓN A POSTGRESQL GRATIS (Supabase)
# ============================================
DATABASE_URL = os.environ.get("DATABASE_URL")  # Variables de entorno en Streamlit Cloud

@st.cache_resource
def get_db_connection():
    """Conexión persistente a PostgreSQL"""
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# ============================================
# MODELO SIMPLE PERO ESCALABLE
# ============================================
def init_database():
    """Crea las tablas si no existen (ejecutar una vez)"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Tabla de productos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            sku TEXT PRIMARY KEY,
            description TEXT,
            price_vip DECIMAL(10,2),
            price_box DECIMAL(10,2),
            price_ir DECIMAL(10,2),
            category TEXT,
            last_updated TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Tabla de stock
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            id SERIAL PRIMARY KEY,
            sku TEXT REFERENCES products(sku),
            source TEXT,
            quantity INTEGER,
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Tabla de cotizaciones
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quotations (
            id TEXT PRIMARY KEY,
            client_name TEXT,
            client_ruc TEXT,
            total DECIMAL(10,2),
            items JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()

# ============================================
# CACHÉ SIMPLE CON STREAMLIT (GRATIS)
# ============================================
@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_product(sku: str):
    """Obtiene producto con caché automático"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT * FROM products WHERE sku = %s", (sku,))
    product = cur.fetchone()
    
    cur.execute("SELECT source, quantity FROM stock WHERE sku = %s", (sku,))
    stocks = cur.fetchall()
    
    cur.close()
    conn.close()
    
    if product:
        product['stock'] = {s['source']: s['quantity'] for s in stocks}
    
    return product

# ============================================
# UI SIMPLIFICADA (MUCHO MÁS RÁPIDA)
# ============================================
def main():
    st.set_page_config(page_title="QTC Pro", layout="wide")
    
    # Sidebar con métricas
    with st.sidebar:
        st.markdown("## QTC Smart Sales")
        
        # Selector de precio
        price_level = st.selectbox("Precio", ["VIP", "BOX", "IR"])
        
        # Mostrar estadísticas desde DB
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM products")
        total_products = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        st.metric("Productos", total_products)
    
    # Tabs principales
    tab1, tab2 = st.tabs(["🔍 Búsqueda", "🛒 Carrito"])
    
    with tab1:
        query = st.text_input("Buscar por SKU o descripción")
        
        if query:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT * FROM products 
                WHERE sku ILIKE %s OR description ILIKE %s
                LIMIT 20
            """, (f'%{query}%', f'%{query}%'))
            
            products = cur.fetchall()
            cur.close()
            conn.close()
            
            for product in products:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"**{product['sku']}**")
                        st.caption(product['description'][:100])
                    with col2:
                        price = product[f'price_{price_level.lower()}'] or 0
                        st.markdown(f"💰 S/ {price:,.2f}")
                    with col3:
                        if st.button("➕ Agregar", key=product['sku']):
                            st.session_state.setdefault('cart', []).append({
                                'sku': product['sku'],
                                'description': product['description'],
                                'price': price,
                                'quantity': 1
                            })
                            st.rerun()
                    st.divider()
    
    with tab2:
        if 'cart' not in st.session_state or not st.session_state.cart:
            st.info("Carrito vacío")
        else:
            total = 0
            for item in st.session_state.cart:
                col1, col2, col3, col4 = st.columns([2, 3, 1, 1])
                with col1:
                    st.write(item['sku'])
                with col2:
                    st.write(item['description'][:40])
                with col3:
                    st.write(f"S/ {item['price']:,.2f}")
                with col4:
                    st.write(f"S/ {item['price'] * item['quantity']:,.2f}")
                total += item['price'] * item['quantity']
            
            st.markdown(f"### TOTAL: S/ {total:,.2f}")
            
            if st.button("📄 Guardar Cotización"):
                # Guardar en PostgreSQL
                conn = get_db_connection()
                cur = conn.cursor()
                quotation_id = f"COT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                cur.execute(
                    "INSERT INTO quotations (id, client_name, items, total) VALUES (%s, %s, %s, %s)",
                    (quotation_id, "Cliente", str(st.session_state.cart), total)
                )
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"Cotización {quotation_id} guardada")
                st.balloons()

if __name__ == "__main__":
    init_database()  # Solo la primera vez
    main()
