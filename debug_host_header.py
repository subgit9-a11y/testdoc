import sys
sys.stdout.reconfigure(encoding='utf-8')
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
    # Curl with Host header
    stdin, stdout, stderr = ssh.exec_command("curl -vv -H 'Host: astra.ayureze.in' http://127.0.0.1:5001/health")
    print("=== CURL WITH HOST HEADER ===")
    print("STDOUT:", stdout.read().decode('utf-8', 'ignore'))
    print("STDERR:", stderr.read().decode('utf-8', 'ignore'))
    
    # Check docker logs
    print("=== DOCKER LOGS FOR HOST HEADER CURL ===")
    stdin, stdout, stderr = ssh.exec_command("docker logs --tail 20 aibackend")
    print(stdout.read().decode('utf-8', 'ignore'))
    print(stderr.read().decode('utf-8', 'ignore'))
except Exception as e:
    print("SSH Error:", e)
finally:
    ssh.close()
