
import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.getcwd())

from app.wasabi_client import WasabiClient

def test_wasabi_flow():
    load_dotenv()
    
    client = WasabiClient()
    
    if not client.is_configured():
        print("X Wasabi client not configured correctly. Check .env")
        return

    # Create a dummy file
    dummy_file = "test_document.txt"
    with open(dummy_file, "w") as f:
        f.write("Astra EHR Test Document\n")
        f.write(f"Created at: {os.times()}\n")
    
    print(f"File '{dummy_file}' created.")
    
    # Upload
    patient_id = "test_patient_123"
    doc_type = "lab_report"
    
    print(f"Uploading document for patient {patient_id}...")
    object_key = client.upload_document(dummy_file, patient_id, doc_type)
    
    if object_key:
        print(f"OK Upload successful! Object key: {object_key}")
        
        # Generate link
        print("Generating pre-signed download URL...")
        url = client.generate_download_url(object_key, expiration_hours=24)
        
        if url:
            print(f"OK Download URL: {url}")
        else:
            print("X Failed to generate download URL.")
    else:
        print("X Upload failed.")

    # Cleanup local file
    if os.path.exists(dummy_file):
        os.remove(dummy_file)

if __name__ == "__main__":
    test_wasabi_flow()
