# importar_excel.py
import pandas as pd
import sqlite3
import os
import sys
from pathlib import Path

DB_PATH = "qtc_database.db"
IMAGES_DIR = Path("productos_imgs")
IMAGES_DIR.mkdir(exist_ok=True)

def limpiar_precio(valor):
    """Limpia y convierte valores de precio a float."""
    if pd.isna(valor):
        return 0.0
    s = str(valor).replace("S/", "").replace("$", "").replace(",", "").strip()
    # Maneja formatos como "1,200.50" o "1.200,50"
    if s.count(".") > 1: s = s.replace(".", "")
    if s.count(",") > 1: s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return 0.0

def encontrar_columna(df, candidatos):
    """Busca la primera columna que coincida con una lista de nombres."""
    for col in df.columns:
        col_limpio = str(col).strip().upper()
        for cand in candidatos:
            if cand.upper() in col_limpio or col_limpio in cand.upper():
                return col
    return None

def importar_excel(ruta_excel):
    if not os.path.exists(ruta_excel):
        print(f"❌ Archivo no encontrado: {ruta_excel}")
        return False

    print(f"📖 Leyendo: {ruta_excel}")
    df = pd.read_excel(ruta_excel)
    
    # 🔍 Mapeo flexible de columnas según tu estructura
    col_sku = encontrar_columna(df, ["SKU", "CODIGO", "ARTICULO"])
    col_desc = encontrar_columna(df, ["GOODS DESCRITPION", "GOODS DESCRIPTION", "DESCRIPCION", "DESC"])
    col_pir = encontrar_columna(df, ["MAYOR"])
    col_pbox = encontrar_columna(df, ["CAJA"])
    col_pvip = encontrar_columna(df, ["VIP"])
    col_stock = encontrar_columna(df, ["STOCK", "CANTIDAD", "SALDO"])
    col_img = encontrar_columna(df, ["IMAGEN", "FOTO", "IMG", "URL IMAGEN"])

    if not col_sku:
        print("❌ No se encontró columna de SKU. Verifica el archivo.")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    importados = 0
    errores = 0

    print(f"🔄 Procesando {len(df)} filas...")
    for idx, row in df.iterrows():
        try:
            sku = str(row.get(col_sku, "")).strip().upper()
            if not sku or sku in ["nan", "NAN", ""]:
                continue

            desc = str(row.get(col_desc, "")).strip() if col_desc else f"Producto {sku}"
            if desc in ["nan", "NAN", ""]:
                desc = f"Producto {sku}"

            pir = limpiar_precio(row.get(col_pir, 0) if col_pir else 0)
            pbox = limpiar_precio(row.get(col_pbox, 0) if col_pbox else 0)
            pvip = limpiar_precio(row.get(col_pvip, 0) if col_pvip else 0)
            stock = int(limpiar_precio(row.get(col_stock, 0) if col_stock else 0))

            # 🖼️ Lógica de imágenes
            img_ruta = None
            if col_img and pd.notna(row.get(col_img)):
                img_nombre = str(row[col_img]).strip()
                if img_nombre and img_nombre != "nan":
                    img_ruta = f"productos_imgs/{img_nombre}"
                    if not (IMAGES_DIR / img_nombre).exists():
                        img_ruta = None  # Si no existe físicamente, se ignorará

            # Fallback: buscar imagen por nombre de SKU en carpeta
            if not img_ruta:
                for ext in ['.jpg', '.jpeg', '.png']:
                    if (IMAGES_DIR / f"{sku}{ext}").exists():
                        img_ruta = f"productos_imgs/{sku}{ext}"
                        break

            # 💾 Insertar o actualizar en SQLite
            cursor.execute("""
                INSERT OR REPLACE INTO productos 
                (sku, codigo_sap, descripcion, categoria, imagen_ruta, precio_ir, precio_box, precio_vip, stock_actual, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (sku, sku[:8], desc, "GENERAL", img_ruta, pir, pbox, pvip, stock))
            importados += 1

        except Exception as e:
            errores += 1
            if errores <= 5:  # Mostrar solo los primeros 5 errores para no saturar consola
                print(f"⚠️ Fila {idx} (SKU: {row.get(col_sku, '?')}): {e}")

    conn.commit()
    conn.close()
    print("\n" + "="*40)
    print(f"✅ IMPORTACIÓN COMPLETADA")
    print(f"📦 Productos guardados: {importados}")
    print(f"❌ Errores omitidos: {errores}")
    print(f"📁 Base de datos: {DB_PATH}")
    print("="*40)
    return True

if __name__ == "__main__":
    # Uso: python importar_excel.py [ruta_del_excel]
    ruta = sys.argv[1] if len(sys.argv) > 1 else "catalogo.xlsx"
    importar_excel(ruta)
