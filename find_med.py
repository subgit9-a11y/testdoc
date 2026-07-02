import os
from dotenv import load_dotenv
load_dotenv()
from app.shopify_api_service import shopify_api

products = shopify_api.get_all_products()
for p in products:
    if "mahanarayana" in p['title'].lower():
        print(f"Title: {p['title']}, ID: {p['variants'][0]['id']}")
