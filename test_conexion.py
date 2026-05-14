# test_conexion.py
from supabase import create_client

# TUS DATOS (cámbialos por los tuyos)
SUPABASE_URL = "https://aolttzscbzckfkceqjey.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFvbHR0enNjYnpja2ZrY2VxamV5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg3ODMzOTIsImV4cCI6MjA5NDM1OTM5Mn0.5cDNWqZ1YRBs_MHNZntKjNJ-kApiyOtwNb0xaifire0"  # <-- PEGA TU CLAVE AQUÍ

# Intentar conectar
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ ¡Conexión exitosa a Supabase!")
    
    # Probar si podemos leer algo (aunque esté vacío)
    response = supabase.table('usuarios').select("*").limit(1).execute()
    print("✅ Puedo comunicarme con la base de datos")
    
except Exception as e:
    print(f"❌ Error de conexión: {e}")
