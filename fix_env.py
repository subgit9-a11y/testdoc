import paramiko
import re

def fix_env():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
        
        # Read .env
        stdin, stdout, stderr = ssh.exec_command('cat /opt/astra/.env')
        env_content = stdout.read().decode('utf-8')
        
        # Find service role key
        service_role_match = re.search(r'SUPABASE_SERVICE_ROLE_KEY=(.+)', env_content)
        if service_role_match:
            service_role_key = service_role_match.group(1).strip()
            
            # Replace SUPABASE_KEY value with service role key
            env_content = re.sub(r'SUPABASE_KEY=.*', f'SUPABASE_KEY={service_role_key}', env_content)
            
            # Write back
            sftp = ssh.open_sftp()
            with sftp.file('/opt/astra/.env', 'w') as f:
                f.write(env_content)
            sftp.close()
            print("Successfully updated SUPABASE_KEY to use Service Role Key in /opt/astra/.env")
            
            # Restart docker container
            print("Restarting aibackend container...")
            ssh.exec_command('cd /opt/astra && docker compose restart aibackend')
            print("Restart command issued.")
        else:
            print("Service role key not found in .env")

    except Exception as e:
        print(f'Failed: {e}')
    finally:
        ssh.close()

if __name__ == '__main__':
    fix_env()
