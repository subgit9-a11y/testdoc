import pymysql
import json

# Database configuration from USER
DB_CONFIG = {
    'host': '82.25.125.50',
    'user': 'u656934180_ayureze_admin',
    'password': 'nemke2-zokroj-Fibfez',
    'database': 'u656934180_ayureze',
    'port': 3306,
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def sync_doctor_to_mysql(doctor_data):
    """
    Syncs a verified doctor profile from the app/supabase to the MySQL admin panel.
    """
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            # Create table if not exists in the admin panel DB
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS astra_verified_doctors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                unique_id VARCHAR(50) UNIQUE,
                name VARCHAR(255),
                email VARCHAR(255) UNIQUE,
                phone VARCHAR(20),
                is_face_verified BOOLEAN DEFAULT FALSE,
                photo_url TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_sql)

            # Upsert the doctor record
            upsert_sql = """
            INSERT INTO astra_verified_doctors (unique_id, name, email, phone, is_face_verified, photo_url)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            name=VALUES(name),
            is_face_verified=VALUES(is_face_verified),
            photo_url=VALUES(photo_url)
            """
            cursor.execute(upsert_sql, (
                doctor_data['unique_id'],
                doctor_data['name'],
                doctor_data['email'],
                doctor_data['phone'],
                doctor_data['is_face_verified'],
                doctor_data['photo_url']
            ))
            
        connection.commit()
        print(f"Successfully synced Doctor {doctor_data['name']} to Super Admin MySQL.")
    except Exception as e:
        print(f"Sync Error: {e}")
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    # Example usage for manual sync or testing
    mock_data = {
        'unique_id': 'DOC-2026-SUBBU-1',
        'name': 'Subbu',
        'email': 'subbu@ayureze.in',
        'phone': '+919876543210',
        'is_face_verified': True,
        'photo_url': 'https://ykewayjfdanhqtqpziwt.supabase.co/storage/v1/object/public/doctor-profiles/...'
    }
    sync_doctor_to_mysql(mock_data)
