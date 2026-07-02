"""
Comprehensive Syntax Checker for all Python files
"""
import os
import sys
import py_compile

def check_syntax(directory):
    """Check syntax of all Python files in directory"""
    errors = []
    checked = 0
    
    for root, dirs, files in os.walk(directory):
        # Skip __pycache__ and hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('__') and not d.startswith('.')]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                checked += 1
                try:
                    py_compile.compile(filepath, doraise=True)
                except py_compile.PyCompileError as e:
                    errors.append({
                        'file': filepath,
                        'error': str(e)
                    })

    return checked, errors

if __name__ == '__main__':
    project_dir = '.'
    
    print("=" * 60)
    print("SYNTAX CHECK - All Python Files")
    print("=" * 60)
    
    checked, errors = check_syntax(project_dir)
    
    print("\nFiles checked: {}".format(checked))
    
    if errors:
        print("\n[X] ERRORS FOUND: {}".format(len(errors)))
        print("-" * 60)
        for err in errors:
            print("\nFile: {}".format(err['file']))
            print("Error: {}".format(err['error']))
    else:
        print("\n[OK] NO SYNTAX ERRORS FOUND!")
        print("All {} files passed syntax check.".format(checked))
    
    print("\n" + "=" * 60)
