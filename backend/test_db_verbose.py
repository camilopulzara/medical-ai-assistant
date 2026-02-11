"""Script detallado para probar la conexión a PostgreSQL"""
import psycopg2
import sys
import traceback

print("=" * 60)
print("Prueba detallada de conexión a PostgreSQL")
print("=" * 60)

# Verificar psycopg2
print(f"\n✓ psycopg2 version: {psycopg2.__version__}")
print(f"✓ Python version: {sys.version}")

# Parámetros de conexión
params = {
    'host': 'localhost',
    'port': 5432,
    'database': 'medical_ai_db',
    'user': 'medical_user',
    'password': 'medical_password_2026'
}

print(f"\nParámetros de conexión:")
for key, value in params.items():
    if key == 'password':
        print(f"  {key}: {'*' * len(str(value))}")
    else:
        print(f"  {key}: {value}")

try:
    print("\n" + "=" * 60)
    print("Intentando conectar...")
    print("=" * 60)
    
    conn = psycopg2.connect(**params)
    
    print("\n✅ ¡Conexión exitosa!")
    
    # Info de la conexión
    print(f"✓ Status: {conn.status}")
    print(f"✓ Encoding: {conn.encoding}")
    print(f"✓ Server version: {conn.server_version}")
    
    # Probar query
    cur = conn.cursor()
    cur.execute('SELECT version();')
    version = cur.fetchone()
    print(f"\n✓ PostgreSQL: {version[0][:50]}...")
    
    # Probar otra query
    cur.execute('SELECT current_database(), current_user;')
    db_info = cur.fetchone()
    print(f"✓ Base de datos: {db_info[0]}")
    print(f"✓ Usuario: {db_info[1]}")
    
    cur.close()
    conn.close()
    print("\n✅ Conexión cerrada correctamente")
    print("=" * 60)
    
except psycopg2.Warning as w:
    print(f"\n⚠️ Warning: {w}")
    print(f"Type: {type(w)}")

except psycopg2.Error as e:
    print(f"\n❌ Error psycopg2: {e}")
    print(f"Type: {type(e).__name__}")
    print(f"pgcode: {e.pgcode if hasattr(e, 'pgcode') else 'N/A'}")
    print(f"pgerror: {e.pgerror if hasattr(e, 'pgerror') else 'N/A'}")
    print(f"\nTraceback completo:")
    traceback.print_exc()
    
except Exception as e:
    print(f"\n❌ Error inesperado: {e}")
    print(f"Type: {type(e).__name__}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("Fin de la prueba")
print("=" * 60)
