import paramiko

def download_main():
    host = '82.25.105.156'
    user = 'root'
    password = 'Ayureze@369369'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        sftp = client.open_sftp()
        sftp.get('/opt/astra/app/main.py', r'd:\AYUREZE PROJECT\astrafinalneed\astra\main_vps.py')
        sftp.close()
        print("Downloaded main_vps.py successfully!")
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    download_main()
