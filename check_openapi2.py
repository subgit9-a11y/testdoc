import paramiko
import json

def get_openapi():
    host = '82.25.105.156'
    user = 'root'
    password = 'Ayureze@369369'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        
        # We can just fetch it from the host since it's proxying to Nginx or exposed
        # Nginx is at https://astra.ayureze.in/openapi.json
        commands = [
            'curl -s https://astra.ayureze.in/openapi.json'
        ]
        
        for cmd in commands:
            print(f"Executing: {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode('utf-8', 'ignore').strip()
            err = stderr.read().decode('utf-8', 'ignore').strip()
            
            if out:
                try:
                    data = json.loads(out)
                    paths = data.get('paths', {})
                    for p in paths:
                        if 'video' in p or 'generate' in p:
                            print(f"Found path: {p}")
                except Exception as ex:
                    print("Could not parse JSON:", ex)
                    
            if err: print(f"STDERR:\n{err}")
            
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    get_openapi()
