import os
import asyncio
from sqlalchemy import create_engine, MetaData, Table, select
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def test_doctors():
    if not DATABASE_URL:
        print("DATABASE_URL not found")
        return

    try:
        engine = create_engine(DATABASE_URL)
        metadata = MetaData()
        
        # Try to reflect the 'doctors' table
        try:
            doctors_table = Table('doctors', metadata, autoload_with=engine)
            print("Successfully reflected 'doctors' table.")
            
            with engine.connect() as conn:
                # Get the first 5 doctors
                query = select(doctors_table).limit(5)
                result = conn.execute(query)
                doctors = result.fetchall()
                
                print(f"Found {len(doctors)} doctors.")
                for doc in doctors:
                    print(dict(doc._mapping))
                    
        except Exception as e:
            print(f"Error reflecting 'doctors' table: {e}")
            
    except Exception as e:
        print(f"Error connecting: {e}")

if __name__ == "__main__":
    asyncio.run(test_doctors())
