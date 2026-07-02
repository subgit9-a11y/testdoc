import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8')

def fix_certbot():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("Connecting to VPS to fix certbot...")
        ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
        
        print("Killing existing certbot processes...")
        ssh.exec_command("killall -9 certbot")[1].channel.recv_exit_status()
        
        print("Removing lock files if any...")
        ssh.exec_command("rm -f /var/log/letsencrypt/.certbot.lock")[1].channel.recv_exit_status()
        ssh.exec_command("find /etc/letsencrypt -name '.certbot.lock' -delete")[1].channel.recv_exit_status()
        
        print("Running certbot renew...")
        # Since it's broken, let's just run it for real without dry-run, or dry-run first
        stdin, stdout, stderr = ssh.exec_command("certbot renew --dry-run")
        stdout.channel.recv_exit_status() # Wait for completion
        print(stdout.read().decode('utf-8', 'ignore'))
        print(stderr.read().decode('utf-8', 'ignore'))
        
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    fix_certbot()
