import sys
sys.stdout.reconfigure(encoding='utf-8')
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
    # List sites-enabled config files
    stdin, stdout, stderr = ssh.exec_command("ls -la /etc/nginx/sites-enabled/")
    print("=== SITES ENABLED ===")
    print(stdout.read().decode('utf-8', 'ignore'))
    
    # Read the configs to see how astra.ayureze.in is defined
    stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-enabled/*")
    print("=== CONFIG CONTENT ===")
    print(stdout.read().decode('utf-8', 'ignore'))
except Exception as e:
    print("SSH Error:", e)
finally:
    ssh.close()
