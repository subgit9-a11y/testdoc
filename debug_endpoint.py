import sys
sys.stdout.reconfigure(encoding='utf-8')
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
    
    # 1. Test curl `/api/v1/api/prescriptions/patient/PAT-001` on localhost:5001
    print("=== CURL /api/v1/api/prescriptions/patient/PAT-001 ===")
    stdin, stdout, stderr = ssh.exec_command("curl -vv http://127.0.0.1:5001/api/v1/api/prescriptions/patient/PAT-001")
    print("STDOUT:", stdout.read().decode('utf-8', 'ignore'))
    print("STDERR:", stderr.read().decode('utf-8', 'ignore'))
    
    # 2. Check docker logs for the crash traceback
    print("=== DOCKER LOGS FOR CRASH ===")
    stdin, stdout, stderr = ssh.exec_command("docker logs --tail 30 aibackend")
    print(stdout.read().decode('utf-8', 'ignore'))
    print(stderr.read().decode('utf-8', 'ignore'))
except Exception as e:
    print("SSH Error:", e)
finally:
    ssh.close()
