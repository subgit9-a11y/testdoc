import paramiko

def force_env():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
        
        script = """
        cd /opt/astra
        SR_KEY=$(grep SUPABASE_SERVICE_ROLE_KEY .env | cut -d '=' -f 2-)
        sed -i "/PYTHONUNBUFFERED: 1/a \\      SUPABASE_KEY: ${SR_KEY}" docker-compose.yml
        docker compose down
        docker compose up -d
        """
        stdin, stdout, stderr = ssh.exec_command(script)
        print('Logs:', stdout.read().decode('utf-8'))
        print('Err:', stderr.read().decode('utf-8'))
        
    except Exception as e:
        print(f'Failed: {e}')
    finally:
        ssh.close()

if __name__ == '__main__':
    force_env()
