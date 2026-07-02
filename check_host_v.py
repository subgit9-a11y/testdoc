import paramiko

def check_host_main_py_v(host, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)
        
        print("--- Host File: /opt/vultr_astra_2/main.py ---")
        stdin, stdout, stderr = ssh.exec_command("head -n 5 /opt/vultr_astra_2/main.py")
        print(stdout.read().decode('utf-8'))
        
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_host_main_py_v("82.25.105.156", "root", "Ayureze@369369")
