import paramiko
import os

def upload_and_restart():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("Connecting to VPS...")
        ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
        
        # Package the app directory
        os.system('tar -czf app_update.tar.gz app')
        print("Created app_update.tar.gz locally")
        
        sftp = ssh.open_sftp()
        print("Uploading app_update.tar.gz...")
        sftp.put('app_update.tar.gz', '/opt/astra/app_update.tar.gz')
        sftp.close()
        
        print("Extracting on VPS...")
        ssh.exec_command('cd /opt/astra && tar -xzf app_update.tar.gz')[1].channel.recv_exit_status()
        
        print("Restarting docker container aibackend...")
        ssh.exec_command('docker restart aibackend')[1].channel.recv_exit_status()
        
        print("Successfully deployed exception fixes and restarted backend.")
        
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    upload_and_restart()
