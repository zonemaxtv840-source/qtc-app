# crear_bd.py
import sqlite3
import os

DB_PATH = "qtc_database.db"

def inicializar_bd():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Tabla de productos (catálogo maestro)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            sku TEXT PRIMARY KEY,
            codigo_sap TEXT,
            descripcion TEXT NOT NULL,
            categoria TEXT DEFAULT 'GENERAL',
            imagen_ruta TEXT,
            precio_ir REAL DEFAULT 0,
            precio_box REAL DEFAULT 0,
            precio_vip REAL DEFAULT 0,
            activo INTEGER DEFAULT 1
        )
    """)
    
    # 2. Tabla de clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nombre_empresa TEXT,
            ruc TEXT,
            tipo_precio TEXT DEFAULT 'P. IR',  -- IR, BOX o VIP
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 3. Tabla de órdenes de compra
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_username TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado TEXT DEFAULT 'PENDIENTE',
            total REAL,
            FOREIGN KEY (cliente_username) REFERENCES clientes(username)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orden_detalle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orden_id INTEGER,
            sku TEXT,
            descripcion TEXT,
            cantidad INTEGER,
            precio_unitario REAL,
            subtotal REAL,
            FOREIGN KEY (orden_id) REFERENCES ordenes(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Base de datos creada: qtc_database.db")
    print("📁 Estructura lista para importar datos.")

if __name__ == "__main__":
    inicializar_bd()
