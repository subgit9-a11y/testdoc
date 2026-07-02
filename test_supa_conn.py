import paramiko

def test():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
        
        script = "import requests\ntry:\n    print('Status:', requests.get('https://ykewayjfdanhqtqpziwt.supabase.co/rest/v1/').status_code)\nexcept Exception as e:\n    print('Error:', e)\n"
        
        # Write to a file locally first
        with open('test_supa.py', 'w') as f:
            f.write(script)
            
        # upload
        sftp = ssh.open_sftp()
        sftp.put('test_supa.py', '/tmp/test_supa.py')
        sftp.close()
        
        stdin, stdout, stderr = ssh.exec_command('docker cp /tmp/test_supa.py aibackend:/app/test_supa.py')
        stdin, stdout, stderr = ssh.exec_command('docker exec aibackend python /app/test_supa.py')
        logs = stdout.read().decode('utf-8')
        print('Supabase Request:', logs)
        print('Err:', stderr.read().decode('utf-8'))
        
    except Exception as e:
        print(f'Failed: {e}')
    finally:
        ssh.close()
        
if __name__ == '__main__':
    test()
