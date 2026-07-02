import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8')

def find_nginx_config():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("Connecting to VPS to grep nginx configs...")
        ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
        
        stdin, stdout, stderr = ssh.exec_command("grep -rn 'astra.ayureze.in' /etc/nginx/")
        stdout.channel.recv_exit_status()
        out = stdout.read().decode('utf-8', 'ignore').strip()
        print("--- Nginx Configs for astra.ayureze.in ---")
        print(out if out else "Not found in /etc/nginx/")
        
        # also check docker logs for astra backend
        stdin, stdout, stderr = ssh.exec_command("docker logs --tail 20 aibackend")
        stdout.channel.recv_exit_status()
        out = stdout.read().decode('utf-8', 'ignore').strip()
        err = stderr.read().decode('utf-8', 'ignore').strip()
        print("\n--- Docker logs for aibackend ---")
        if out: print(out)
        if err: print(err)
        
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    find_nginx_config()
