
try:
    import app.auth_routes
    print("app.auth_routes: OK")
except Exception as e:
    print(f"app.auth_routes: FAILED {e}")

try:
    import app.enhanced_inference
    print("app.enhanced_inference: OK")
except Exception as e:
    print(f"app.enhanced_inference: FAILED {e}")

try:
    import app.astra.capability_agent
    print("app.astra.capability_agent: OK")
except Exception as e:
    print(f"app.astra.capability_agent: FAILED {e}")

try:
    import app.astra_fill.routes
    print("app.astra_fill.routes: OK")
except Exception as e:
    print(f"app.astra_fill.routes: FAILED {e}")
