import sys
sys.stdout.reconfigure(encoding='utf-8')
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
    # Curl localhost:5001
    stdin, stdout, stderr = ssh.exec_command("curl -I http://127.0.0.1:5001/health")
    print("=== CURL LOCALHOST:5001/health ===")
    print(stdout.read().decode('utf-8', 'ignore'))
    print(stderr.read().decode('utf-8', 'ignore'))
    
    # Check host Nginx error logs (last 30 lines)
    stdin, stdout, stderr = ssh.exec_command("tail -n 30 /var/log/nginx/error.log")
    print("=== HOST NGINX ERROR LOGS ===")
    print(stdout.read().decode('utf-8', 'ignore'))
    print(stderr.read().decode('utf-8', 'ignore'))
except Exception as e:
    print("SSH Error:", e)
finally:
    ssh.close()
