import requests

def test_supabase_connection():
    url = "https://ykewayjfdanhqtqpziwt.supabase.co/rest/v1/doctors"
    headers = {
        "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlrZXdheWpmZGFuaHF0cXB6aXd0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU5NDc2OTIsImV4cCI6MjA3MTUyMzY5Mn0.OJDr91V4He1zv0k3Dn88-ZgErOOo1eeUtee23qh6G7s",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlrZXdheWpmZGFuaHF0cXB6aXd0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU5NDc2OTIsImV4cCI6MjA3MTUyMzY5Mn0.OJDr91V4He1zv0k3Dn88-ZgErOOo1eeUtee23qh6G7s"
    }
    
    print(f"Testing connection to: {url}")
    try:
        # Just try to get the first row or check if table exists
        response = requests.get(url, headers=headers, params={"select": "*", "limit": 1})
        if response.status_code == 200:
            print("Connection successful!")
            data = response.json()
            if data:
                print(f"Columns found: {list(data[0].keys())}")
                print(f"Data sample: {data[0]}")
            else:
                print("Table is empty.")
        else:
            print(f"Connection failed with status code: {response.status_code}")
            print(f"Error message: {response.text}")
            return

        # Test Upsert
        print("\nTesting Upsert access...")
        upsert_data = {
            "unique_id": "TEST-DOC-123",
            "name": "Test Connection Doctor",
            "email": "test@connection.com",
            "phone": "1234567890",
            "is_face_verified": True
        }
        upsert_response = requests.post(
            url, 
            headers={**headers, "Prefer": "return=representation"}, 
            json=upsert_data
        )
        if upsert_response.status_code in [200, 201]:
            print("Upsert successful!")
            print(f"Upserted data: {upsert_response.json()}")
        else:
            print(f"Upsert failed with status code: {upsert_response.status_code}")
            print(f"Error message: {upsert_response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_supabase_connection()
