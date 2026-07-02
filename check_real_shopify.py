import os
import sys
from dotenv import load_dotenv
sys.path.append(os.getcwd())
load_dotenv()

from app.shopify_api_service import shopify_api

products = shopify_api.get_all_products()
print(f"Total Products: {len(products)}")
for p in products[:5]:
    print(f"Title: {p.get('title')}")
    for v in p.get('variants', []):
        print(f"  Variant ID: {v.get('id')}")
