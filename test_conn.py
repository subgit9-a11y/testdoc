
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"URL: {url}")
print(f"Key starts with: {key[:10] if key else 'None'}")

if not url or not key:
    print("Missing credentials!")
else:
    try:
        supabase: Client = create_client(url, key)
        print("Successfully created Supabase client!")
        res = supabase.table("doctors").select("*").limit(1).execute()
        print(f"Data found: {res.data}")
    except Exception as e:
        print(f"Error: {e}")
