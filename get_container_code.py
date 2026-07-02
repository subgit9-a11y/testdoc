import paramiko

def get_container_version(host, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)
        
        # Check current main.py contents inside aibackend
        print("--- Container main.py Start ---")
        stdin, stdout, stderr = ssh.exec_command("docker exec aibackend head -n 30 main.py")
        print(stdout.read().decode('utf-8'))
        
        # Check end to see the root endpoint
        print("--- Container main.py End (Root) ---")
        stdin, stdout, stderr = ssh.exec_command("docker exec aibackend tail -n 50 main.py")
        print(stdout.read().decode('utf-8'))
        
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_container_version("82.25.105.156", "root", "Ayureze@369369")
