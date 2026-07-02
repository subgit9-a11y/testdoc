import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv('.env')
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("NO DB URL")
    exit()

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        res = conn.execute(text("SELECT id, name, email, phone FROM doctors WHERE name LIKE '%Testsubash%' OR email LIKE '%Testsubash%'")).mappings().all()
        if not res:
            print("Doctor not found in MySQL.")
        for row in res:
            print(f"Found in MySQL -> ID: {row['id']}, Name: {row['name']}, Email: {row['email']}")
except Exception as e:
    print(f"Error: {e}")
