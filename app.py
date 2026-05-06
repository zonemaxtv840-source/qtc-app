def cargar_excel_completo(archivo):
    """Carga TODAS las hojas de un Excel y las devuelve como diccionario"""
    try:
        xls = pd.ExcelFile(archivo)
        hojas_data = {}
        
        for hoja in xls.sheet_names:
            try:
                df = pd.read_excel(archivo, sheet_name=hoja)
                df = limpiar_cabeceras(df)
                
                if df.empty or len(df.columns) < 2:
                    continue
                
                # Detectar columnas automáticamente
                col_sku = None
                col_desc = None
                columnas_precio = []
                
                for c in df.columns:
                    c_str = str(c).upper()
                    if any(p in c_str for p in ['SKU', 'COD', 'SAP', 'NUMERO']):
                        if col_sku is None:
                            col_sku = c
                    if any(p in c_str for p in ['DESC', 'NOMBRE', 'PRODUCTO']):
                        if col_desc is None:
                            col_desc = c
                    if any(p in c_str for p in ['PRECIO', 'CAJA', 'VIP', 'MAYOR', 'IR', 'BOX', 'SUGERIDO']):
                        columnas_precio.append(c)
                
                # Fallback si no se detectaron
                if col_sku is None and len(df.columns) > 0:
                    col_sku = df.columns[0]
                if col_desc is None and len(df.columns) > 1:
                    col_desc = df.columns[1]
                if not columnas_precio and len(df.columns) > 2:
                    columnas_precio = [df.columns[2]]
                
                if col_sku and col_desc:
                    hojas_data[hoja] = {
                        'df': df,
                        'col_sku': col_sku,
                        'col_desc': col_desc,
                        'columnas_precio': columnas_precio
                    }
            except Exception as e:
                st.warning(f"Error en hoja {hoja}: {str(e)[:50]}")
                continue
        
        if hojas_data:
            return {
                'nombre': archivo.name,
                'hojas': hojas_data,
                'total_hojas': len(hojas_data)
            }
        return None
    except Exception as e:
        st.error(f"Error leyendo {archivo.name}: {str(e)[:100]}")
        return None
