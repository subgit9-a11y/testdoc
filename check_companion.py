import paramiko
import json

def check_openapi():
    host = '82.25.105.156'
    user = 'root'
    password = 'Ayureze@369369'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        
        # Test openapi json
        cmd = 'docker exec aibackend curl -s http://localhost:5000/openapi.json'
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode('utf-8', 'ignore').strip()
        
        if out:
            try:
                data = json.loads(out)
                paths = data.get('paths', {})
                companion_routes = [p for p in paths.keys() if 'companion' in p or 'chat' in p or 'astra' in p]
                print("Companion/Chat Routes found:")
                for r in companion_routes[:20]:
                    print("  - " + r)
                    
                if not companion_routes:
                    print("No companion routes found. Let's print all routes:")
                    for r in list(paths.keys())[:30]:
                        print("  - " + r)
            except Exception as e:
                print(f"Failed to parse JSON: {e}")
                print(f"Output preview: {out[:200]}")
        else:
            print("No output from curl.")
            
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_openapi()
