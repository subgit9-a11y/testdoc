import paramiko

def inspect_docker_paths(host, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)
        
        print("--- Docker Inspections ---")
        # Find where the 'aibackend' container is getting its files
        stdin, stdout, stderr = ssh.exec_command("docker inspect aibackend --format='{{range .Mounts}}{{.Source}} -> {{.Destination}}{{end}}'")
        print(f"Mounts: {stdout.read().decode('utf-8')}")
        
        # Check running version vs file content in /opt/vultr_astra_2
        print("--- Host File: /opt/vultr_astra_2/main.py (Version Check) ---")
        stdin, stdout, stderr = ssh.exec_command("grep -n 'version=' /opt/vultr_astra_2/main.py")
        print(stdout.read().decode('utf-8'))

        print("--- Host File: /opt/vultr_astra_2/app/main.py (Version Check) ---")
        stdin, stdout, stderr = ssh.exec_command("grep -n 'version=' /opt/vultr_astra_2/app/main.py")
        print(stdout.read().decode('utf-8'))

        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_docker_paths("82.25.105.156", "root", "Ayureze@369369")
