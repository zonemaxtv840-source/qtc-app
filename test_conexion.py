# test_conexion.py
from supabase import create_client

# TUS DATOS (cámbialos por los tuyos)
SUPABASE_URL = "https://aolttzscbzckfkceqjey.supabase.co"
SUPABASE_KEY = "aquí_va_tu_clave_anon_public"  # <-- PEGA TU CLAVE AQUÍ

# Intentar conectar
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ ¡Conexión exitosa a Supabase!")
    
    # Probar si podemos leer algo (aunque esté vacío)
    response = supabase.table('usuarios').select("*").limit(1).execute()
    print("✅ Puedo comunicarme con la base de datos")
    
except Exception as e:
    print(f"❌ Error de conexión: {e}")
