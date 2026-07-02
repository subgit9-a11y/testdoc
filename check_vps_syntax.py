import paramiko

def check_files():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("Connecting to VPS...")
        ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
        print("Connected successfully. Checking python syntax in /opt/astra...")
        
        # compileall module checks for syntax errors without executing the code
        stdin, stdout, stderr = ssh.exec_command('python3 -m compileall -q /opt/astra')
        
        # Wait for the command to finish
        exit_status = stdout.channel.recv_exit_status()
        
        out = stdout.read().decode('utf-8')
        err = stderr.read().decode('utf-8')
        
        if exit_status != 0:
            print("Syntax Errors Found!")
            if err:
                print(err)
            if out:
                print(out)
        else:
            print("All files in /opt/astra are error less (no python syntax errors).")
            
    except Exception as e:
        print(f"Failed to connect or execute: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_files()
