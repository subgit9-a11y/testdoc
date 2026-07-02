import paramiko
from scp import SCPClient
import sys

def upload_files():
    host = '82.25.105.156'
    user = 'root'
    password = 'Ayureze@369369'
    
    local_main = r'd:\AYUREZE PROJECT\astrafinalneed\astra\app\main.py'
    remote_main = '/opt/astra/app/main.py'
    
    local_agora = r'd:\AYUREZE PROJECT\astrafinalneed\astra\app\agora_routes.py'
    remote_agora = '/opt/astra/app/agora_routes.py'
    
    print(f"Connecting to {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname=host, username=user, password=password, timeout=10)
        print("Connected!")
        
        print("Starting SCP transfer...")
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(local_main, remote_main)
            print(f"Uploaded main.py to {remote_main}")
            
            scp.put(local_agora, remote_agora)
            print(f"Uploaded agora_routes.py to {remote_agora}")
            
        print("Uploads complete! Restarting docker containers...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/astra && docker restart aibackend')
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Restart successful!")
        else:
            print("Restart failed.")
            print(stderr.read().decode())
                
    except Exception as e:
        print(f"Failed to connect or upload: {e}")
        sys.exit(1)
    finally:
        ssh.close()

if __name__ == "__main__":
    upload_files()
