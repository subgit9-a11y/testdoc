import os
import zipfile
import paramiko

def create_and_deploy(zip_filename, host, username, password, remote_dir):
    print("Bundling Astra package (v4.5.0)...")
    IGNORED_DIRS = {'__pycache__', 'venv', '.git', '.idea', '.vscode', 'node_modules', 'audio_cache'}
    IGNORED_EXTENSIONS = {'.pyc', '.pyo', '.pyd', '.zip', '.tar.gz', '.log', '.ps1'}
    
    if os.path.exists(zip_filename): os.remove(zip_filename)
        
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for file in files:
                if any(file.endswith(ext) for ext in IGNORED_EXTENSIONS): continue
                if file == zip_filename: continue
                file_path = os.path.join(root, file)
                zipf.write(file_path, arcname=os.path.relpath(file_path, "."))
                
    print(f"Uploading {zip_filename} to {host}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)
        
        sftp = ssh.open_sftp()
        sftp.put(zip_filename, f"{remote_dir}/{zip_filename}")
        sftp.close()
        
        print("Finalizing update and restarting Docker...")
        # Use --build to force pick up of changed root main.py
        cmd = f"cd {remote_dir} && unzip -o {zip_filename} && docker compose down && docker compose up -d --build"
        
        stdin, stdout, stderr = ssh.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("[SUCCESS] Deployment version 4.5.0 complete!")
        else:
            print(f"[FAILED] Exit code {exit_status}")
            print(stderr.read().decode('utf-8'))
            
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_and_deploy("vultr_astra_deploy_v4.zip", "82.25.105.156", "root", "Ayureze@369369", "/opt/vultr_astra_2")
