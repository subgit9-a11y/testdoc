import paramiko

def check_vps():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
        stdin, stdout, stderr = ssh.exec_command('grep -A 5 "except HTTPException:" /opt/astra/app/companion_api.py')
        print(stdout.read().decode())
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_vps()
