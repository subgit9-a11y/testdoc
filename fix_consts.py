import re

# 1. Fix Preferences.doctor_id in wallet_screen.dart
path_wallet = 'lib/screens/wallet/wallet_screen.dart'
try:
    with open(path_wallet, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('Preferences.doctor_id', 'Preferences.doctorId')
    with open(path_wallet, 'w', encoding='utf-8') as f:
        f.write(content)
except Exception as e:
    print('Failed wallet_screen.dart:', e)

# 2. Fix const issues by reading the files and removing 'const ' before widgets having Theme.of(context)
def remove_const(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'Theme.of(context)' in line:
                lines[i] = lines[i].replace('const ', '')
                if i > 0:
                    lines[i-1] = lines[i-1].replace('const ', '')
                    if i > 1 and lines[i-1].strip() == '':
                        lines[i-2] = lines[i-2].replace('const ', '')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    except Exception as e:
        print('Failed', filepath, e)

remove_const('lib/chat/pages/chat_page.dart')
remove_const('lib/screens/auth/SignIn.dart')
remove_const('lib/chat/pages/home_page.dart')
remove_const('lib/screens/appointment/cancel_appointment.dart')
remove_const('lib/screens/videoCall/video_Call.dart')
remove_const('lib/widgets/osler_card.dart')

print('Done')
