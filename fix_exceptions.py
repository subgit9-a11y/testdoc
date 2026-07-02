import os
import re

def fix_http_exceptions(directory):
    print("Fixing broad exception handlers catching HTTPException...")
    
    # We want to replace:
    # except Exception as e:
    #     logger.error(...)
    #     raise HTTPException(status_code=500, detail=str(e))
    # With:
    # except HTTPException:
    #     raise
    # except Exception as e:
    #     logger.error(...)
    #     raise HTTPException(status_code=500, detail=str(e))
    
    pattern = re.compile(r'(\s*)except Exception as e:')
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'except Exception as e:' in content and 'raise HTTPException' in content:
                        new_content = pattern.sub(r'\1except HTTPException:\n\1    raise\n\1except Exception as e:', content)
                        if new_content != content:
                            with open(path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            print(f"Fixed: {path}")
                except Exception:
                    pass

if __name__ == "__main__":
    fix_http_exceptions('c:/Users/SUBHASH/Desktop/astrafinalneed/astra/app')
