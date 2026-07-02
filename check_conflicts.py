import paramiko

def check_nginx_running(host, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)
        
        print("--- Host Processes (Nginx) ---")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep nginx")
        print(stdout.read().decode('utf-8'))
        
        print("--- Docker Containers ---")
        stdin, stdout, stderr = ssh.exec_command("docker ps")
        print(stdout.read().decode('utf-8'))
        
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_nginx_running("82.25.105.156", "root", "Ayureze@369369")
