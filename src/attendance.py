import json
from datetime import datetime
from sha import sha_256

def register(device):
    id = input('Enter your student number: ')
    qr_code = device.scan_qr()
    qr_key = sha_256.create_key(qr_code)
    with open('src/users.json') as file:
        users = json.load(file)
    users[qr_key] = id
    with open('src/users.json', 'w') as file:
        json.dump(users, file, indent=4)

def log_attendance(device):
    logs = {}
    today = datetime.now().strftime('%m/%d/%Y')
    now = datetime.now().strftime('%I:%M %p')
    print('Scan your ID')
    qr_code = device.scan_qr()
    qr_key = sha_256.create_key(qr_code)

    with open('src/users.json', 'r') as file:
        users = json.load(file)
    with open('src/logs.json', 'r') as file:
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

    with open('src/logs.json', 'w') as file:
        json.dump(logs, file, indent=4)
        
    print(f'{student_number} at ({logs[today][student_number]["time"]})')