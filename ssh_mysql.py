import sys
sys.stdout.reconfigure(encoding='utf-8')
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect('82.25.105.156', username='root', password='Ayureze@369369', timeout=10)
    cmd = '''docker exec aibackend python -c "
import os
from sqlalchemy import create_engine, text
try:
    engine = create_engine(os.getenv('DATABASE_URL'))
    with engine.connect() as conn:
        print(\\\"--- DOCTORS ---\\\")
        for r in conn.execute(text(\\\"SELECT * FROM doctors WHERE id = 11\\\")).mappings().all(): print(dict(r))
        print(\\\"--- DOCTOR ---\\\")
        for r in conn.execute(text(\\\"SELECT * FROM doctor WHERE id = 11 OR user_id = 11\\\")).mappings().all(): print(dict(r))
        res_settle = conn.execute(text(\\\"SELECT SUM(amount) as total FROM settle WHERE doctor_id = 20\\\")).mappings().first()
        print(\\\"TEST SUBASH WITHDRAWN:\\\", dict(res_settle))
except Exception as e:
    print('DB Error:', e)
"'''
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print("STDOUT:", stdout.read().decode('utf-8', 'ignore'))
    print("STDERR:", stderr.read().decode('utf-8', 'ignore'))
except Exception as e:
    print("SSH Error:", e)
finally:
    ssh.close()
