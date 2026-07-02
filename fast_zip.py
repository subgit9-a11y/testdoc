import shutil
import os

print("Starting compression...")
shutil.make_archive('fast_update', 'zip', '.', base_dir='app')
# we also need main.py, Dockerfile, docker-compose.yml, requirements.txt, nginx.conf, setup_swap.sh, .dockerignore
import zipfile
with zipfile.ZipFile('fast_update.zip', 'a') as zipf:
    for f in ['main.py', 'Dockerfile', 'docker-compose.yml', 'requirements.txt', 'nginx.conf', 'setup_swap.sh', '.dockerignore', '.env']:
        if os.path.exists(f):
            zipf.write(f)
            
print("Compression complete. Size:", os.path.getsize('fast_update.zip'))
