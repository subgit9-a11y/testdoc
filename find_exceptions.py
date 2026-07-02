import os

def search_text(directory, text):
    print(f"Searching for '{text}'...")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f):
                            if text.lower() in line.lower():
                                print(f"{path}:{i+1}:{line.strip()}")
                except Exception:
                    pass

if __name__ == "__main__":
    search_text('c:/Users/SUBHASH/Desktop/astrafinalneed/astra/app', 'case not found')
