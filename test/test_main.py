import test.test_qr_camera as test_qr_camera
import test.test_sha_256 as test_sha_256
import json
from datetime import datetime

def register():
    id = input('Enter your student number: ')
    qr_code = test_qr_camera.scan_qr()
    qr_key = test_sha_256.create_key(qr_code)
    with open('test/users.json') as file:
        users = json.load(file)
    users[qr_key] = id
    with open('test/users.json', 'w') as file:
        json.dump(users, file, indent=4)

def log_attendance():
    logs = {}
    today = datetime.now().strftime('%m/%d/%Y')
    now = datetime.now().strftime('%I:%M %p')
    qr_code = test_qr_camera.scan_qr()
    qr_key = test_sha_256.create_key(qr_code)

    with open('test/users.json', 'r') as file:
        users = json.load(file)
    with open('test/logs.json', 'r') as file:
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

    with open('test/logs.json', 'w') as file:
        json.dump(logs, file, indent=4)
        
    print(f'{student_number} at ({logs[today][student_number]["time"]})')


if __name__ == '__main__':
    # register()
    log_attendance()