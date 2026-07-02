import os
import zipfile
import shutil

def create_deployment_package():
    print("📦 Preparing Astra Deployment Package...")
    
    # 1. Define ignore list (dirs/files)
    IGNORED_DIRS = {
        '__pycache__', 'venv', '.git', '.idea', '.vscode', 'node_modules',
        'tests', 'tmp', 'audio_cache', 'static' # exclude large static/cache assets to keep zip small?
        # Actually, static might be needed. audio_cache is temp.
    }
    IGNORED_EXTENSIONS = {'.pyc', '.pyo', '.pyd', '.zip', '.tar.gz', '.log', '.ps1'}
    
    zip_filename = "vultr_astra_deploy.zip"
    
    if os.path.exists(zip_filename):
        os.remove(zip_filename)
        
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through the current directory
        for root, dirs, files in os.walk("."):
            # Exclude ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            
            for file in files:
                # Check extension
                if any(file.endswith(ext) for ext in IGNORED_EXTENSIONS):
                    continue
                if file == zip_filename:
                    continue
                
                # Get the relative path
                file_path = os.path.join(root, file)
                # Write to zip
                zipf.write(file_path, arcname=os.path.relpath(file_path, "."))
                
    print(f"[SUCCESS] Package created: {zip_filename}")
    print(f"   Size: {os.path.getsize(zip_filename) / 1024 / 1024:.2f} MB")
    print("\n[READY] READY TO DEPLOY!")
    print("\n[Step 1] Upload: SCP the zip file to your server")
    print(f"   scp {zip_filename} root@<YOUR_VULTR_IP>:/root/astrabackend/")
    print("\n[Step 2] Unzip & Run:")
    print("   ssh root@<YOUR_VULTR_IP>")
    print("   cd /root/astrabackend")
    print(f"   unzip -o {zip_filename}")
    print("   docker compose down")
    print("   docker compose up -d --build")

if __name__ == "__main__":
    create_deployment_package()
