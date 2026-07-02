import paramiko
import sys

def check_astra_nginx():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("Connecting to VPS...")
        ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
        
        print("Checking Nginx config for astra...")
        stdin, stdout, stderr = ssh.exec_command('cat /etc/nginx/sites-available/astra')
        out = stdout.read().decode('utf-8')
        if 'listen 443 ssl http2' in out:
            print("Found deprecated http2 in astra config. Fixing...")
            ssh.exec_command("sed -i 's/listen 443 ssl http2;/listen 443 ssl;/g' /etc/nginx/sites-available/astra")
            ssh.exec_command("sed -i 's/listen \\[::\\]:443 ssl http2;/listen \\[::\\]:443 ssl;/g' /etc/nginx/sites-available/astra")
            ssh.exec_command("systemctl reload nginx")
            print("Fixed and reloaded.")
        else:
            print("No deprecated http2 found in astra config.")
            
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_astra_nginx()
