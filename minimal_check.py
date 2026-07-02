import os
from dotenv import load_dotenv
load_dotenv(override=True)
print(f"STORJ_ENABLED={os.getenv('STORJ_ENABLED')}")
print(f"STORJ_ENDPOINT={os.getenv('STORJ_ENDPOINT')}")
print("Credentials present:", bool(os.getenv('STORJ_ACCESS_KEY')))
