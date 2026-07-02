import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8')

def fix_nginx_and_certbot():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("Connecting to VPS...")
        ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
        
        print("Fixing nginx deprecated warnings...")
        # Fix the deprecated http2 directive
        cmd1 = "sed -i 's/listen 443 ssl http2;/listen 443 ssl;\\n\\thttp2 on;/g' /etc/nginx/sites-enabled/api.ayureze.in"
        # The syntax changed from `listen 443 ssl http2;` to `listen 443 ssl;` with a separate `http2 on;` directive.
        # However, `http2 on;` works, or just `listen 443 ssl;` with `http2 on;` in server block.
        # Let's just remove http2 from the listen directive.
        cmd1 = "sed -i 's/ http2//g' /etc/nginx/sites-enabled/api.ayureze.in"
        
        ssh.exec_command(cmd1)[1].channel.recv_exit_status()
        
        print("Reloading Nginx...")
        ssh.exec_command("systemctl reload nginx")[1].channel.recv_exit_status()
        
        print("Checking Nginx Syntax again...")
        stdin, stdout, stderr = ssh.exec_command("nginx -t")
        stderr_str = stderr.read().decode('utf-8', 'ignore')
        print(stderr_str)
        
        print("Running certbot renew --dry-run...")
        stdin, stdout, stderr = ssh.exec_command("certbot renew --dry-run")
        stdout.channel.recv_exit_status() # Wait for completion
        print(stdout.read().decode('utf-8', 'ignore'))
        print(stderr.read().decode('utf-8', 'ignore'))
        
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    fix_nginx_and_certbot()
