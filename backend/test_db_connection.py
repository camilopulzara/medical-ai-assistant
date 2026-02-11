"""Script para probar la conexión a PostgreSQL"""
import psycopg2
import traceback

hosts = ["localhost", "host.docker.internal", "172.19.0.2"]
for host in hosts:
    try:
        print(f"Intentando conectar a PostgreSQL en host: {host}...")
        conn = psycopg2.connect(
            host=host,
            port=5432,
            database="medical_ai_db",
            user="medical_user",
            password="medical_password_2026"
        )
        print(f"✅ ¡Conexión exitosa en {host}!")
        cur = conn.cursor()
        cur.execute('SELECT version();')
        version = cur.fetchone()
        print(f"PostgreSQL version: {version[0]}")
        cur.close()
        conn.close()
        print("✅ Conexión cerrada correctamente")
        break
    except psycopg2.OperationalError as e:
        print(f"❌ Error de conexión en {host}: {e}")
        print(f"Tipo de error: {type(e)}")
        print(f"Args: {e.args}")
        traceback.print_exc()
    except Exception as e:
        print(f"❌ Error inesperado en {host}: {e}")
        traceback.print_exc()
