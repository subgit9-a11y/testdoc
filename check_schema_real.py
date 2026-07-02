import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(override=True)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
client = create_client(url, key)

def get_columns():
    try:
        # Try a select * on 1 row - it will return the columns in the dict keys
        res = client.table("medicine_schedules").select("*").limit(1).execute()
        if res.data:
            print(f"Columns: {res.data[0].keys()}")
        else:
            print("No rows in table to extract schema, trying to describe")
            # Maybe use Postgres table reflection if possible? No.
            # Try to insert a row with just prescription_id to see what is missing in the return?
            pass
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_columns()
