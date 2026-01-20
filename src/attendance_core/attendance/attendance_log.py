import json
from datetime import datetime

def register(device, users_file, sha):
    id = input('Enter your student number: ')
    qr_code = device.scan_qr()
    qr_key = sha.create_key(qr_code)
    with open(users_file) as file:
        users = json.load(file)
    users[qr_key] = id
    with open(users_file, 'w') as file:
        json.dump(users, file, indent=4)

def log_attendance(device, users_file, logs_file, sha):
    logs = {}
    today = datetime.now().strftime('%m/%d/%Y')
    now = datetime.now().strftime('%I:%M %p')
    print('Scan your ID')
    qr_code = device.scan_qr()
    qr_key = sha.create_key(qr_code)

    with open(users_file, 'r') as file:
        users = json.load(file)
    with open(logs_file, 'r') as file:
        logs = json.load(file)

    if qr_key not in users:
        print('User not found. Please register first.')
        return
    
    student_number = users[qr_key]

    logs.setdefault(today, {})

    if student_number in logs[today]:
        print("Already scanned today.")
        return
    
    logs[today][student_number] = {
        "time": now
    }

    with open(logs_file, 'w') as file:
        json.dump(logs, file, indent=4)
        
    print(f'{student_number} at ({logs[today][student_number]["time"]})')