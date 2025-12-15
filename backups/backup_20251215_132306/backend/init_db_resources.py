import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def init_resources():
    print("🔄 Connecting to PostgreSQL (Port 5433) as 'postgres'...")
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="postgres",
            user="postgres",
            password="123456" 
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        print("✅ Connected to Postgres 18!")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return

    # 1. Create User
    try:
        cur.execute("CREATE USER usuario WITH PASSWORD '12345';")
        print("✅ User 'usuario' created.")
    except Exception as e:
        if "already exists" in str(e) or "ya existe" in str(e):
             print("ℹ️ User 'usuario' already exists. Updating password...")
             try:
                cur.execute("ALTER USER usuario WITH PASSWORD '12345';")
                print("✅ Password updated.")
             except:
                pass
        else:
            print(f"⚠️ Error creating user: {e}")

    # 2. Grant rights
    try:
        cur.execute("ALTER USER usuario CREATEDB;")
    except:
        pass

    # 3. Create Database
    try:
        cur.execute("CREATE DATABASE asistentehandling OWNER usuario;")
        print("✅ Database 'asistentehandling' created.")
    except Exception as e:
        if "already exists" in str(e) or "ya existe" in str(e):
            print("ℹ️ Database 'asistentehandling' already exists.")
        else:
            print(f"⚠️ Error creating database: {e}")

    conn.close()

if __name__ == "__main__":
    init_resources()
