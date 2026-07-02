import sys
sys.stdout.reconfigure(encoding='utf-8')
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
    # Check what is listening on port 80/443 on the host
    stdin, stdout, stderr = ssh.exec_command("ss -tulpn | grep -E ':80|:443'")
    print("=== PORTS LISTENING ===")
    print(stdout.read().decode('utf-8', 'ignore'))
    print(stderr.read().decode('utf-8', 'ignore'))
    
    # Check if there is an nginx running on host
    stdin, stdout, stderr = ssh.exec_command("systemctl status nginx")
    print("=== HOST NGINX STATUS ===")
    print(stdout.read().decode('utf-8', 'ignore'))
    print(stderr.read().decode('utf-8', 'ignore'))
    
    # Check cloudflared service status if it exists
    stdin, stdout, stderr = ssh.exec_command("systemctl status cloudflared")
    print("=== CLOUDFLARED STATUS ===")
    print(stdout.read().decode('utf-8', 'ignore'))
    print(stderr.read().decode('utf-8', 'ignore'))
except Exception as e:
    print("SSH Error:", e)
finally:
    ssh.close()
