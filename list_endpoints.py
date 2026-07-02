import os
import sys
from unittest.mock import MagicMock

# Mock the model loading to avoid delays and memory usage
sys.modules["app.enhanced_inference"] = MagicMock()
mock_inference = MagicMock()
sys.modules["app.enhanced_inference"].AstraModelInference.return_value = mock_inference

# Add current directory to path
sys.path.append(os.getcwd())

from main import app

print("List of all endpoints in Astra:")
print("=" * 60)
for route in app.routes:
    if hasattr(route, "methods"):
        methods = ", ".join(route.methods)
        print(f"{methods:15} {route.path}")
    else:
        # Check for mounted apps or static files
        print(f"MOUNT           {route.path}")
