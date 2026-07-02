import paramiko

def fetch_logs():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
        stdin, stdout, stderr = ssh.exec_command('docker logs --tail 50 aibackend')
        
        with open('docker_logs.txt', 'wb') as f:
            f.write(stdout.read())
            f.write(stderr.read())
            
        print("Logs saved to docker_logs.txt")
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    fetch_logs()
