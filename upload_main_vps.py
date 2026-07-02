import paramiko
from scp import SCPClient
import sys

def upload_main_vps():
    host = '82.25.105.156'
    user = 'root'
    password = 'Ayureze@369369'
    
    local_main = r'd:\AYUREZE PROJECT\astrafinalneed\astra\main_vps.py'
    remote_main = '/opt/astra/app/main.py'
    
    print(f"Connecting to {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname=host, username=user, password=password, timeout=10)
        print("Connected!")
        
        print("Starting SCP transfer...")
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(local_main, remote_main)
            print(f"Uploaded main_vps.py to {remote_main}")
            
        print("Uploads complete! Restarting docker containers...")
        stdin, stdout, stderr = ssh.exec_command('docker cp /opt/astra/app/main.py aibackend:/app/main.py && docker restart aibackend && sleep 10 && docker exec aibackend curl -s http://localhost:5000/openapi.json | grep generate-token')
        out = stdout.read().decode('utf-8', 'ignore').strip()
        err = stderr.read().decode('utf-8', 'ignore').strip()
        if out: print(f"STDOUT:\n{out}")
        if err: print(f"STDERR:\n{err}")
                
    except Exception as e:
        print(f"Failed to connect or upload: {e}")
        sys.exit(1)
    finally:
        ssh.close()

if __name__ == "__main__":
    upload_main_vps()
