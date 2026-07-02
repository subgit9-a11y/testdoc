import pymysql

try:
    conn = pymysql.connect(
        host='82.25.125.50', 
        user='u656934180_ayureze_admin', 
        password='nemke2-zokroj-Fibfez', 
        database='u656934180_ayureze', 
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10
    )
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, name, email, role, phone FROM users LIMIT 10")
        rows = cursor.fetchall()
        print("Users Found:")
        for r in rows:
            print(r)
except Exception as e:
    print(f"Error: {e}")
