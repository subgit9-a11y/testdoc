import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8')

def check_astra():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("Connecting to VPS to check astra.ayureze.in service...")
        ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
        
        commands = [
            ("Checking Nginx config for astra.ayureze.in", "cat /etc/nginx/sites-enabled/astra.ayureze.in || cat /etc/nginx/conf.d/astra.conf"),
            ("Checking what is running on port 5001", "ss -tulpn | grep :5001 || echo 'Nothing running on port 5001'"),
            ("Checking pm2 status (if used)", "pm2 status || echo 'pm2 not installed or not running'"),
            ("Checking systemctl status for astra (if it's a systemd service)", "systemctl status astra* || echo 'No astra service found'"),
            ("Checking docker containers (if it's dockerized)", "docker ps | grep astra || echo 'No astra docker container found'")
        ]
        
        for name, cmd in commands:
            print(f"\n--- {name} ---")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout.channel.recv_exit_status()
            out = stdout.read().decode('utf-8', 'ignore').strip()
            err = stderr.read().decode('utf-8', 'ignore').strip()
            
            if out: print(out)
            if err: print(err)
            
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_astra()
