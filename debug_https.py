import sys
sys.stdout.reconfigure(encoding='utf-8')
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
    # Curl external HTTPS URL from the host
    print("=== CURL HTTPS EXTERNAL ===")
    stdin, stdout, stderr = ssh.exec_command("curl -vv https://astra.ayureze.in/health")
    print("STDOUT:", stdout.read().decode('utf-8', 'ignore'))
    print("STDERR:", stderr.read().decode('utf-8', 'ignore'))
except Exception as e:
    print("SSH Error:", e)
finally:
    ssh.close()
