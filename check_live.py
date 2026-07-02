import paramiko

def check_live_code(host, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)
        
        # Check current main.py on the host
        print("--- Host main.py ---")
        stdin, stdout, stderr = ssh.exec_command("grep 'version=' /opt/vultr_astra_2/main.py")
        print(stdout.read().decode('utf-8'))
        
        # Check currently running code in the container
        print("--- Container Code ---")
        stdin, stdout, stderr = ssh.exec_command("docker exec aibackend grep 'version=' main.py")
        print(stdout.read().decode('utf-8'))
        
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_live_code("82.25.105.156", "root", "Ayureze@369369")
