import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def reset_user():
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
        print("✅ Connected.")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return

    # Terminate connections to DB to allow drop
    try:
        cur.execute("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = 'asistentehandling'
              AND pid <> pg_backend_pid();
        """)
        print("Required active connections terminated.")
    except:
        pass

    # 1. Drop Database
    print("🗑️ Dropping database 'asistentehandling'...")
    try:
        cur.execute("DROP DATABASE IF EXISTS asistentehandling;")
        print("✅ Database dropped.")
    except Exception as e:
        print(f"⚠️ Error dropping database: {e}")

    # 2. Drop User
    print("🗑️ Dropping user 'usuario'...")
    try:
        cur.execute("DROP USER IF EXISTS usuario;")
        print("✅ User dropped.")
    except Exception as e:
        print(f"⚠️ Error dropping user: {e}")

    # 3. Recreate User
    print("🆕 Creating user 'usuario'...")
    try:
        cur.execute("CREATE USER usuario WITH PASSWORD '12345' LOGIN CREATEDB;")
        print("✅ User created.")
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return

    # 4. Recreate Database
    print("🆕 Creating database 'asistentehandling'...")
    try:
        cur.execute("CREATE DATABASE asistentehandling OWNER usuario;")
        print("✅ Database created.")
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return

    conn.close()
    
    # 5. Verify Connection
    print("\n🕵️ Verifying connection as 'usuario'...")
    try:
        conn_user = psycopg2.connect(
             host="localhost",
             port=5433,
             database="asistentehandling",
             user="usuario",
             password="12345"
        )
        print("✅✅ LOGIN SUCCESSFUL as 'usuario'!")
        conn_user.close()
    except Exception as e:
        print("❌❌ LOGIN FAILED as 'usuario'!")
        print(e)

if __name__ == "__main__":
    reset_user()
