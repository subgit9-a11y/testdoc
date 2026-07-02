import paramiko

def update_env():
    host = '82.25.105.156'
    user = 'root'
    password = 'Ayureze@369369'
    
    app_id = 'aaf7c4d9c2d849368b79b1583e5023ed'
    app_cert = '669fcfe648894e709af71efd7f2068ae'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        
        # Check if they exist, if not append
        commands = [
            f'grep -q AGORA_APP_ID /var/www/astra/.env || echo -e "\\nAGORA_APP_ID={app_id}\\nAGORA_APP_CERTIFICATE={app_cert}" >> /var/www/astra/.env',
            f'sed -i "s/^AGORA_APP_ID=.*/AGORA_APP_ID={app_id}/" /var/www/astra/.env',
            f'sed -i "s/^AGORA_APP_CERTIFICATE=.*/AGORA_APP_CERTIFICATE={app_cert}/" /var/www/astra/.env',
            'systemctl restart astra'
        ]
        
        for cmd in commands:
            print(f"Executing: {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            if out: print("STDOUT:", out)
            if err: print("STDERR:", err)
            
        print("Updated .env and restarted service successfully.")
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    update_env()
