import paramiko

def check_vps():
    host = '82.25.105.156'
    user = 'root'
    password = 'Ayureze@369369'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        
        commands = [
            'pwd',
            'ls -la',
            'docker ps',
            'find / -name ".env" -path "*/astra*" 2>/dev/null | head -n 5'
        ]
        
        for cmd in commands:
            print(f"--- Executing: {cmd} ---")
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            if out: print("STDOUT:\n", out)
            if err: print("STDERR:\n", err)
            
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_vps()
