import paramiko
import os
import zipfile

def zip_app():
    zip_path = "deploy_app.zip"
    if os.path.exists(zip_path):
        os.remove(zip_path)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("app"):
            if "__pycache__" in root: continue
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, file_path)
    return zip_path

def deploy():
    host = '82.25.105.156'
    user = 'root'
    password = 'Ayureze@369369'
    
    zip_file = zip_app()
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        sftp = client.open_sftp()
        print("Uploading deploy_app.zip...")
        sftp.put(zip_file, '/opt/astra/deploy_app.zip')
        sftp.close()
        
        commands = [
            'cd /opt/astra && unzip -o deploy_app.zip',
            'cd /opt/astra && docker compose restart backend'
        ]
        
        for cmd in commands:
            print(f"Executing: {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode('utf-8', 'ignore').strip()
            err = stderr.read().decode('utf-8', 'ignore').strip()
            if out: print("STDOUT:\n", out)
            if err: print("STDERR:\n", err)
            
        print("Deployment successful.")
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy()
