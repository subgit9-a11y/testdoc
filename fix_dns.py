import paramiko

def fix_dns():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
        
        # We edit docker-compose.yml to force DNS on aibackend container
        # Since VPS might overwrite resolv.conf
        print("Modifying docker-compose.yml to force Google DNS...")
        edit_cmd = """
        cd /opt/astra && \
        sed -i '/aibackend:/a \\    dns:\\n      - 8.8.8.8\\n      - 1.1.1.1' docker-compose.yml
        """
        ssh.exec_command(edit_cmd)
        
        # Restart docker container
        print("Restarting docker compose...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/astra && docker compose down && docker compose up -d')
        print(stdout.read().decode('utf-8'))
        
        # Test inside container
        print("Testing DNS resolution inside container...")
        stdin, stdout, stderr = ssh.exec_command('docker exec aibackend curl -I https://ykewayjfdanhqtqpziwt.supabase.co')
        print('Curl:', stdout.read().decode('utf-8'))

    except Exception as e:
        print(f'Failed: {e}')
    finally:
        ssh.close()

if __name__ == '__main__':
    fix_dns()
