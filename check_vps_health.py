import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8')

def check_vps_health():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("Connecting to VPS to check system health...")
        ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
        
        commands = [
            ("Failed System Services", "systemctl --failed"),
            ("Nginx Syntax Check", "nginx -t"),
            ("Docker Containers Status (Exited/Restarting)", "docker ps -a | grep -iE 'exited|restarting' || echo 'No failed containers'"),
            ("Recent Nginx Errors", "tail -n 15 /var/log/nginx/error.log || echo 'No Nginx error log'"),
            ("Recent Syslog Errors", "grep -i 'error' /var/log/syslog | tail -n 10 || echo 'No syslog errors found'")
        ]
        
        for name, cmd in commands:
            print(f"\n--- {name} ---")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            
            # Wait for command
            exit_status = stdout.channel.recv_exit_status()
            
            out = stdout.read().decode('utf-8', 'ignore').strip()
            err = stderr.read().decode('utf-8', 'ignore').strip()
            
            if out:
                print(out)
            if err:
                # nginx -t logs to stderr even on success, so we just print it
                print(err)
            if not out and not err:
                print("OK / None")
                
    except Exception as e:
        print(f"Failed to connect or execute: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_vps_health()
