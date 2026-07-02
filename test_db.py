import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from app.database import db_manager

async def test():
    # Re-initialize to ensure it picks up env vars
    from supabase import create_client
    db_manager.url = os.getenv("SUPABASE_URL")
    db_manager.key = os.getenv("SUPABASE_KEY")
    db_manager.client = create_client(db_manager.url, db_manager.key)
    
    res = db_manager.client.table('doctors').select('*').execute()
    print(res.data)

if __name__ == "__main__":
    asyncio.run(test())
