import os
import sys
from fastapi import APIRouter

# Mock what we can to avoid heavy imports
sys.modules["app.enhanced_inference"] = __import__('unittest.mock').mock.MagicMock()

def list_router_endpoints(router, prefix=""):
    endpoints = []
    for route in router.routes:
        methods = ", ".join(route.methods)
        endpoints.append(f"{methods:10} {prefix}{route.path}")
    return endpoints

all_endpoints = []

# List of routers from main.py
routers_to_check = [
    ("auth_router", "app.auth_routes", ""),
    ("auth_chat_router", "app.auth_routes", ""),
    ("doctor_router", "app.doctors.doctor_routes", ""),
    ("patient_router", "app.patient_management", ""),
    ("prescription_router", "app.prescriptions.prescription_routes", ""),
    ("catchy_router", "app.catchy_prescription.routes", ""),
    ("workflow_router", "app.unified_prescription_workflow", ""),
    ("shopify_router", "app.smart_auto_cart", ""),
    ("astra_fill_router", "app.astra_fill.routes", ""),
    ("document_router", "app.documents.routes", ""),
    ("notification_router", "app.notification_routes", ""),
    ("reminder_router", "app.medicine_reminders.routes", ""),
    ("translate_router", "app.indictrans2_routes", ""),
    ("ai_agent_router", "app.ai_agent_api", ""),
    ("treatment_router", "app.treatment_centers.center_routes", ""),
    ("api_brain_router", "app.brain_api", ""),
]

v1_prefix = "/api/v1"

for router_name, module_path, local_prefix in routers_to_check:
    try:
        module = __import__(module_path, fromlist=[router_name])
        router = getattr(module, router_name if hasattr(module, router_name) else "router")
        combined_prefix = v1_prefix + local_prefix
        all_endpoints.extend(list_router_endpoints(router, combined_prefix))
    except Exception as e:
        print(f"Error loading {router_name} from {module_path}: {e}")

print("\n".join(sorted(list(set(all_endpoints)))))
