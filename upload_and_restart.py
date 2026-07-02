import paramiko
import os

def deploy():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("Connecting to VPS...")
        ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
        
        print("Connected. Uploading update_package.zip...")
        sftp = ssh.open_sftp()
        local_path = 'fast_update.zip'
        remote_path = '/opt/astra/fast_update.zip'
        sftp.put(local_path, remote_path)
        sftp.close()
        print("Upload complete.")
        
        commands = [
            'cd /opt/astra && apt-get install unzip -y > /dev/null 2>&1',
            'cd /opt/astra && unzip -o fast_update.zip > /dev/null 2>&1',
            'cd /opt/astra && rm fast_update.zip',
            'cd /opt/astra && docker compose build > /dev/null 2>&1',
            'cd /opt/astra && docker compose up -d > /dev/null 2>&1'
        ]
        
        for cmd in commands:
            print(f"Executing: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            # wait for command to finish
            exit_status = stdout.channel.recv_exit_status() 
            print(stdout.read().decode('utf-8'))
            err = stderr.read().decode('utf-8')
            if err:
                print("Error output:", err)
            
        print("Deployment and restart successful!")
        
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy()
