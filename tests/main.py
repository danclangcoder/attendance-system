import json
from time import sleep
from datetime import datetime
from qr_scanner import start_scan
from sha_256 import hash_key

if __name__ == '__main__':
    print('Running app... Please wait.')
    sleep(1)
    print('Scan QR')
    while True:
        try:
            qr = start_scan()
            hash_val = hash_key(qr)
            current_time = datetime.now().strftime('%I:%M %p')
            print(qr)
            print(hash_val)
            student_number = 'A123F0025'
            with open('registered_users.json', 'w') as file:
                data = json.load(file)
                if hash_val not in data:
                    file.writelines()

        except KeyboardInterrupt:
            break