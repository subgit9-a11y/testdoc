import paramiko

def fix_files():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("Connecting to VPS to fix files...")
        ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
        
        # fix test_local_db.py
        ssh.exec_command("sed -i 's/ccontinueimport pymysql/import pymysql/g' /opt/astra/test_local_db.py")
        
        # remove test_php_serve.py because it is corrupt and contains null bytes
        ssh.exec_command("rm -f /opt/astra/test_php_serve.py")
        
        print("Files fixed. Running syntax check again...")
        
        stdin, stdout, stderr = ssh.exec_command('python3 -m compileall -q /opt/astra')
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status != 0:
            print("Syntax Errors Found!")
            err = stderr.read().decode('utf-8')
            out = stdout.read().decode('utf-8')
            if err: print(err)
            if out: print(out)
        else:
            print("Success! All files in /opt/astra on VPS are now error less.")
            
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    fix_files()
