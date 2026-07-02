import os
import zipfile
import paramiko
import time

def create_deployment_package(zip_filename):
    print("Preparing Astra Deployment Package...")
    
    # Define ignore list
    IGNORED_DIRS = {
        '__pycache__', 'venv', '.git', '.idea', '.vscode', 'node_modules',
        'tests', 'tmp', 'audio_cache'
    }
    IGNORED_EXTENSIONS = {'.pyc', '.pyo', '.pyd', '.zip', '.tar.gz', '.log', '.ps1'}
    
    if os.path.exists(zip_filename):
        os.remove(zip_filename)
        
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for file in files:
                if any(file.endswith(ext) for ext in IGNORED_EXTENSIONS):
                    continue
                if file == zip_filename:
                    continue
                file_path = os.path.join(root, file)
                zipf.write(file_path, arcname=os.path.relpath(file_path, "."))
                
    print(f"[SUCCESS] Package created: {zip_filename}")
    print(f"   Size: {os.path.getsize(zip_filename) / 1024 / 1024:.2f} MB")

def deploy_to_vultr(zip_filename, host, username, password, remote_dir):
    print(f"Connecting to {host}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)
        
        print(f"Ensuring remote directory {remote_dir} exists...")
        ssh.exec_command(f"mkdir -p {remote_dir}")
        
        print(f"Uploading {zip_filename}...")
        sftp = ssh.open_sftp()
        sftp.put(zip_filename, f"{remote_dir}/{zip_filename}")
        sftp.close()
        
        print("Extracting and restarting Docker...")
        commands = [
            f"cd {remote_dir}",
            "rm -rf nginx.conf",
            f"unzip -o {zip_filename}",
            "docker rm -f aibackend aibackend_proxy || true",
            "docker compose down",
            "docker compose up -d --build"
        ]
        
        full_command = " && ".join(commands)
        stdin, stdout, stderr = ssh.exec_command(full_command)
        
        # Monitor output
        print("Remote logs:")
        exit_status = stdout.channel.recv_exit_status()
        out_text = stdout.read().decode('utf-8', errors='replace')
        err_text = stderr.read().decode('utf-8', errors='replace')
        
        with open("deploy.log", "w", encoding="utf-8") as f:
            f.write("STDOUT:\n")
            f.write(out_text)
            f.write("\nSTDERR:\n")
            f.write(err_text)
            
        print("Logs saved to deploy.log")
        if err_text:
            print("Errors from remote (see deploy.log for details)")
            
        if exit_status == 0:
            print("\n[SUCCESS] Deployment complete and Docker restarted!")
        else:
            print(f"\n[ERROR] Deployment failed with exit code {exit_status}")
            
        ssh.close()
    except Exception as e:
        print(f"[ERROR] Connection or deployment failed: {e}")

if __name__ == "__main__":
    ZIP_NAME = "vultr_astra_deploy.zip"
    H = "82.25.105.156"
    U = "root"
    P = "Ayureze@369369"
    RD = "/opt/vultr_astra_2"
    
    create_deployment_package(ZIP_NAME)
    deploy_to_vultr(ZIP_NAME, H, U, P, RD)
