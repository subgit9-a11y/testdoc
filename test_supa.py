import requests
try:
    print('Status:', requests.get('https://ykewayjfdanhqtqpziwt.supabase.co/rest/v1/').status_code)
except Exception as e:
    print('Error:', e)
