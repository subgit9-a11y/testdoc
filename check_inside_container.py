import paramiko

def check_inside_container():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
        # We look for the exact line in companion_api.py inside the container
        stdin, stdout, stderr = ssh.exec_command('docker exec aibackend grep -A 5 "except HTTPException:" /app/app/companion_api.py')
        print(stdout.read().decode())
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_inside_container()
