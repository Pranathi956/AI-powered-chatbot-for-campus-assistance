import pymysql

def create_database(db_name, host="localhost", user="root", password=""):
    try:
        connection = pymysql.connect(host=host, user=user, password=password ,port=3306)
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")
            print(f"✅ Database '{db_name}' created (or already exists).")
    except pymysql.MySQLError as e:
        print("❌ MySQL Error:", e)
    finally:
        if 'connection' in locals():
            connection.close()
if __name__ == "__main__":
    print("🔁 Running create.py...")
    create_database("college_db")