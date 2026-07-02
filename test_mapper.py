import sys
import os
from dotenv import load_dotenv
sys.path.append(os.getcwd())
load_dotenv()

from app.enhanced_product_mapper import enhanced_product_mapper

names = ["mahanarayana tailam", "aswagandha choornam", "Mahanarayan Oil", "Ashwagandha"]

for name in names:
    info = enhanced_product_mapper.get_product_info(name)
    print(f"Name: {name}")
    print(f"  ID: {info.get('shopify_variant_id')}")
    print(f"  Title: {info.get('shopify_product_title')}")
    print(f"  Available: {info.get('is_available')}")
    print("-" * 20)
