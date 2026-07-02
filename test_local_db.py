import pymysql

try:
    conn = pymysql.connect(
        host='127.0.0.1', 
        user='u656934180_ayureze_admin', 
        password='nemke2-zokroj-Fibfez', 
        database='u656934180_ayureze', 
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    )
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, name, email, role_id, is_admin FROM users LIMIT 10")
        rows = cursor.fetchall()
        print("--- APP ADMIN DETAILS ---")
        for r in rows:
            print(r)
except Exception as e:
    print(f"Error querying local DB: {e}")
