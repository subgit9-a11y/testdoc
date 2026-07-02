import subprocess
import time

try:
    with open("c:\\Users\\SUBHASH\\Music\\vultr_astra_2\\php_test_out.txt", "w") as f:
        f.write("Trying to find PHP...\n")
        res = subprocess.run(['where', 'php'], capture_output=True, text=True)
        f.write(f"WHERE PHP: stdout={res.stdout} stderr={res.stderr}\n")
        
        if res.stdout.strip():
            f.write("Starting Artisan serve...\n")
            proc = subprocess.Popen([res.stdout.strip().split('\n')[0], 'artisan', 'serve', '--host=127.0.0.1', '--port=8000'], 
                                    cwd=r"c:\Users\SUBHASH\Music\vultr_astra_2\public_html Ayureze",
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            time.sleep(3)
            f.write(f"Server process started with PID: {proc.pid}\n")
            f.write(f"Poll status after 3s: {proc.poll()}\n")
        else:
            f.write("PHP not found in PATH!\n")
except Exception as e:
    with open("c:\\Users\\SUBHASH\\Music\\vultr_astra_2\\php_test_out.txt", "w") as f:
        f.write(f"Error: {e}\n")
