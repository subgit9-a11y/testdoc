import paramiko

def check_git():
    host = '82.25.105.156'
    user = 'root'
    password = 'Ayureze@369369'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        
        commands = [
            'cd /opt/astra && git status',
            'cd /opt/astra && git checkout app/main.py'
        ]
        
        for cmd in commands:
            print(f"Executing: {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode('utf-8', 'ignore').strip()
            err = stderr.read().decode('utf-8', 'ignore').strip()
            if out: print(f"STDOUT:\n{out}")
            if err: print(f"STDERR:\n{err}")
            
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_git()
