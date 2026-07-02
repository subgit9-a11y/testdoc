import paramiko

def test():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
        
        script = """
import yaml

with open('/opt/astra/docker-compose.yml', 'r') as f:
    data = yaml.safe_load(f)

if 'backend' in data.get('services', {}):
    data['services']['backend']['dns'] = ['8.8.8.8', '1.1.1.1']

with open('/opt/astra/docker-compose.yml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False)
"""
        ssh.exec_command(f"python3 -c \"{script}\"")
        
        stdin, stdout, stderr = ssh.exec_command('cd /opt/astra && docker compose --project-name astra up -d')
        print('Compose:', stdout.read().decode('utf-8'))
        print('Err:', stderr.read().decode('utf-8'))
        
    except Exception as e:
        print(f'Failed: {e}')
    finally:
        ssh.close()
if __name__ == '__main__':
    test()
