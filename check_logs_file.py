import paramiko

def check_logs():
    host = '82.25.105.156'
    user = 'root'
    password = 'Ayureze@369369'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        
        commands = [
            'docker logs aibackend > /opt/astra/backend_error.log 2>&1'
        ]
        for cmd in commands:
            print(f"Executing: {cmd}")
            client.exec_command(cmd)
            
        sftp = client.open_sftp()
        sftp.get('/opt/astra/backend_error.log', 'backend_error.log')
        sftp.close()
        print("Log downloaded.")
            
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_logs()
