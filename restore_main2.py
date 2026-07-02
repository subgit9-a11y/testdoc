import paramiko

def restore_main():
    host = '82.25.105.156'
    user = 'root'
    password = 'Ayureze@369369'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        
        commands = [
            'docker images | grep astra',
            'docker inspect aibackend | grep Image',
            # create a temporary container from the image and copy main.py
            'IMAGE=$(docker inspect --format="{{.Config.Image}}" aibackend) && docker create --name temp_astra $IMAGE && docker cp temp_astra:/app/main.py /opt/astra/app/main.py_restored && docker rm temp_astra',
            'cat /opt/astra/app/main.py_restored > /opt/astra/app/main.py',
            'docker cp /opt/astra/app/main.py aibackend:/app/main.py',
            'docker restart aibackend',
            'sleep 5',
            'docker ps | grep aibackend'
        ]
        
        for cmd in commands:
            print(f"Executing: {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode('utf-8', 'ignore').strip()
            err = stderr.read().decode('utf-8', 'ignore').strip()
            if out: print(f"STDOUT:\n{out}")
            if err: print(f"STDERR:\n{err}")
            
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    restore_main()
