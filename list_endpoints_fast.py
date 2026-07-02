import os
import re

def find_endpoints(directory):
    endpoints = []
    # Regex to find fastapi route decorators like @router.get("/path") or @app.post('/path')
    pattern = re.compile(r'@(?:router|app)\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]')
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f):
                            match = pattern.search(line)
                            if match:
                                method = match.group(1).upper()
                                route = match.group(2)
                                module = os.path.relpath(path, directory)
                                endpoints.append((module, method, route))
                except Exception:
                    pass
    
    # Group by module
    by_module = {}
    for mod, meth, route in endpoints:
        if mod not in by_module:
            by_module[mod] = []
        by_module[mod].append((meth, route))
        
    for mod, routes in sorted(by_module.items()):
        print(f"\n--- {mod} ---")
        for meth, route in sorted(routes):
            print(f"  {meth:6} {route}")

if __name__ == "__main__":
    find_endpoints('c:/Users/SUBHASH/Desktop/astrafinalneed/astra/app')
