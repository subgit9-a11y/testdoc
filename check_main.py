import paramiko

def check_main():
    host = '82.25.105.156'
    user = 'root'
    password = 'Ayureze@369369'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        
        commands = [
            'grep -i agora /opt/astra/app/main.py',
            'ls -la /opt/astra/app/agora_routes.py'
        ]
        
        for cmd in commands:
            print(f"Executing: {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            if out: print("STDOUT:", out)
            if err: print("STDERR:", err)
            
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_main()
