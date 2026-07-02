import paramiko

def check_routes():
    host = '82.25.105.156'
    user = 'root'
    password = 'Ayureze@369369'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        
        script = """from app.main import app
for route in app.routes:
    if hasattr(route, 'path') and 'video' in route.path:
        print(route.path, route.methods)"""
        
        commands = [
            f'docker exec aibackend python3 -c "{script}"'
        ]
        
        for cmd in commands:
            print(f"Executing: {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode('utf-8', 'ignore').strip()
            err = stderr.read().decode('utf-8', 'ignore').strip()
            if out: print("STDOUT:\n", out)
            if err: print("STDERR:\n", err)
            
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_routes()
