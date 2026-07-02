import paramiko
import os

def deploy():
    host = "82.25.105.156"
    username = "root"
    password = "Ayureze@369369"
    remote_dir = "/var/www/astra"
    zip_file = "fast_update.zip"

    try:
        print(f"Connecting to {host}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)

        print(f"Uploading {zip_file}...")
        sftp = ssh.open_sftp()
        sftp.put(zip_file, f"{remote_dir}/{zip_file}")
        sftp.put("requirements.txt", f"{remote_dir}/requirements.txt")
        sftp.close()

        print("Extracting and restarting Astra service...")
        commands = [
            f"cd {remote_dir}",
            f"unzip -o {zip_file}",
            "source venv/bin/activate",
            "pip install -r requirements.txt",
            "sudo systemctl restart astra"
        ]
        
        full_command = " && ".join(commands)
        stdin, stdout, stderr = ssh.exec_command(full_command)
        
        exit_status = stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        err = stderr.read().decode('utf-8')
        if err:
            print("Errors:")
            print(err)
            
        if exit_status == 0:
            print("\n[SUCCESS] Deployment complete!")
        else:
            print(f"\n[ERROR] Deployment failed with exit code {exit_status}")
            
        ssh.close()
    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == "__main__":
    deploy()
