import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests

r = requests.get('https://astra.ayureze.in/api/v1/shopify/products/available', timeout=20)
d = r.json()
meds = d.get('medicines', [])

print("=" * 60)
print("  SHOPIFY PRODUCT CATALOG - COMPLETE AUDIT")
print("=" * 60)
print(f"Total Products Fetched : {d.get('total_count', 0)}")
print(f"Priced Products        : {d.get('priced_count', 0)}  (ready for prescription)")
print(f"Price Pending          : {d.get('price_pending_count', 0)}  (flagged with badge)")
print(f"Last Updated           : {d.get('last_updated', 'N/A')}")
print(f"Catalog Version        : {d.get('catalog_version', 'N/A')}")
print()

# Show sample price pending
pending = [m for m in meds if m.get('price_status') == 'price_pending']
print(f"SAMPLE PRICE PENDING PRODUCTS (first 3):")
print("-" * 60)
for m in pending[:3]:
    print(f"  ⚠️  {m['name']} | {m['price']} | status: {m['price_status']}")

print()
print(f"SAMPLE PRICED PRODUCTS (first 5):")
print("-" * 60)
priced = [m for m in meds if m.get('price_status') == 'available']
for m in priced[:5]:
    print(f"  ✅ {m['name']} | {m['price']} | Stock: {m['inventory_quantity']}")
