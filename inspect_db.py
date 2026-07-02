import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("DATABASE_URL not found in .env")
    exit(1)

try:
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    tables = inspector.get_table_names()
    print(f"Tables in database: {tables}")
    
    for table_name in ["users", "doctors", "prescribed_medicines"]:
        if table_name in tables:
            print(f"\nStructure of '{table_name}' table:")
            columns = inspector.get_columns(table_name)
            for column in columns:
                print(f" - {column['name']}: {column['type']}")
        else:
            print(f"\n'{table_name}' table not found.")

except Exception as e:
    print(f"Error connecting to database: {e}")
