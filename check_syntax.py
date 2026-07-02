import os
import subprocess
import glob

def check_php_syntax(directory):
    php_files = glob.glob(os.path.join(directory, '**/*.php'), recursive=True)
    all_clean = True
    errors = []
    print(f"Checking {len(php_files)} PHP files...")
    
    for count, file in enumerate(php_files):
        try:
            result = subprocess.run(['php', '-l', file], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error in {file}: {result.stdout}")
                errors.append(file)
                all_clean = False
        except Exception as e:
            print(f"Failed to check {file}: {e}")
            all_clean = False
            
        if count > 0 and count % 500 == 0:
            print(f"Checked {count} files...")

    if all_clean:
        print("All PHP files are clean!")
    else:
        print(f"Found errors in {len(errors)} files.")

if __name__ == '__main__':
    check_php_syntax('C:/Users/SUBHASH/Music/vultr_astra_2/public_html Ayureze')
